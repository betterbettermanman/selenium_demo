"""任务周期调度：扫描并启动 daily/monthly 任务。"""
from __future__ import annotations

import logging
import threading
import time

from services.scheduler_config import get_scheduler_config, parse_hhmm
from services.task_runner import get_running_task_count, is_task_running, start_task

logger = logging.getLogger(__name__)

VALID_SCHEDULE_TYPES = ('manual', 'daily', 'monthly')
_SCHEDULER = None
_SCHEDULER_LOCK = threading.Lock()
_APP = None

# 任务结束释放并发槽后的补扫（按调度类型分别补，合并连续结束）
_slot_fill_lock = threading.Lock()
_slot_fill_scheduled = False
_slot_fill_pending_types: set[str] = set()


def normalize_schedule_type(value) -> str:
    text = (value or 'manual').strip().lower()
    if text not in VALID_SCHEDULE_TYPES:
        return ''
    return text


def notify_slot_freed(app=None, schedule_type=None):
    """
    定时任务结束/停止释放并发槽后调用。
    仅补扫「同一调度类型」，避免执行每月时把每日任务也拉起。
    """
    global _slot_fill_scheduled

    st = normalize_schedule_type(schedule_type)
    if st not in ('daily', 'monthly'):
        return

    flask_app = app or _APP
    if flask_app is None:
        return

    with _slot_fill_lock:
        _slot_fill_pending_types.add(st)
        if _slot_fill_scheduled:
            return
        _slot_fill_scheduled = True

    def _worker():
        global _slot_fill_scheduled
        try:
            while True:
                # 短暂等待，合并连续结束，并让 _remove_runner 完全落稳
                time.sleep(1)
                with _slot_fill_lock:
                    types = list(_slot_fill_pending_types)
                    _slot_fill_pending_types.clear()
                for item_type in types:
                    try:
                        summary = run_schedule_scan(item_type, app=flask_app)
                        started = int(summary.get('started') or 0)
                        if started:
                            logger.info(
                                '并发槽释放后补启动 type=%s started=%s attempted=%s',
                                item_type,
                                started,
                                summary.get('attempted'),
                            )
                    except Exception:
                        logger.exception('并发槽释放后补扫失败 type=%s', item_type)
                with _slot_fill_lock:
                    if _slot_fill_pending_types:
                        continue
                    _slot_fill_scheduled = False
                    return
        except Exception:
            logger.exception('并发槽释放补扫 worker 异常')
            with _slot_fill_lock:
                _slot_fill_scheduled = False
                _slot_fill_pending_types.clear()

    threading.Thread(
        target=_worker,
        daemon=True,
        name='schedule-slot-fill',
    ).start()


def run_schedule_scan(schedule_type: str, app=None) -> dict:
    """扫描并启动一类定时任务，返回摘要。"""
    from models.task import Task

    schedule_type = normalize_schedule_type(schedule_type)
    if schedule_type not in ('daily', 'monthly'):
        return {
            'ok': False,
            'message': 'type 须为 daily 或 monthly',
            'started': 0,
            'attempted': 0,
            'skipped_running': 0,
            'slots': 0,
            'candidates': 0,
        }

    flask_app = app or _APP
    if flask_app is None:
        return {
            'ok': False,
            'message': '调度器未绑定 Flask app',
            'started': 0,
            'attempted': 0,
            'skipped_running': 0,
            'slots': 0,
            'candidates': 0,
        }

    cfg = get_scheduler_config()
    max_running = int(cfg.get('max_running_tasks') or 5)
    running = get_running_task_count()
    slots = max(max_running - running, 0)

    with flask_app.app_context():
        candidates = (
            Task.query
            .filter(
                Task.schedule_type == schedule_type,
                Task.status == '1',
            )
            .order_by(Task.id.asc())
            .all()
        )
        candidate_ids = [t.id for t in candidates]

    idle_ids = [tid for tid in candidate_ids if not is_task_running(tid)]
    skipped_running = len(candidate_ids) - len(idle_ids)

    summary = {
        'ok': True,
        'message': 'ok',
        'type': schedule_type,
        'max_running_tasks': max_running,
        'running': running,
        'slots': slots,
        'candidates': len(candidate_ids),
        'skipped_running': skipped_running,
        'attempted': 0,
        'started': 0,
        'failed': 0,
        'task_ids': [],
        'errors': [],
    }

    if slots <= 0:
        summary['message'] = f'已达并发上限 {max_running}，本轮不启动'
        logger.info(
            '调度扫描 type=%s running=%s/%s slots=0 candidates=%s',
            schedule_type, running, max_running, len(candidate_ids),
        )
        return summary

    to_start = idle_ids[:slots]
    summary['attempted'] = len(to_start)

    # start_task 内会查库，后台线程/补扫必须带 app_context
    with flask_app.app_context():
        for task_id in to_start:
            ok, result = start_task(task_id, flask_app, source='scheduler')
            if ok:
                summary['started'] += 1
                summary['task_ids'].append(task_id)
                logger.info('调度启动成功 type=%s task_id=%s', schedule_type, task_id)
            else:
                summary['failed'] += 1
                msg = (result or {}).get('message', '启动失败')
                summary['errors'].append({'task_id': task_id, 'message': msg})
                logger.warning('调度启动失败 type=%s task_id=%s msg=%s', schedule_type, task_id, msg)

    summary['message'] = (
        f'扫描完成：候选 {summary["candidates"]}，尝试 {summary["attempted"]}，'
        f'成功 {summary["started"]}，失败 {summary["failed"]}'
    )
    return summary


def _job_scan(schedule_type: str):
    try:
        summary = run_schedule_scan(schedule_type)
        logger.info('定时任务触发 type=%s result=%s', schedule_type, summary.get('message'))
    except Exception:
        logger.exception('定时任务执行失败 type=%s', schedule_type)


def reschedule_jobs(app=None):
    """按当前配置重建 APScheduler jobs。"""
    global _SCHEDULER, _APP
    flask_app = app or _APP
    if flask_app is None:
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.error('未安装 APScheduler，无法启用定时调度：pip install APScheduler')
        return

    cfg = get_scheduler_config()
    daily_h, daily_m = parse_hhmm(cfg.get('daily_time', '08:00'))
    monthly_h, monthly_m = parse_hhmm(cfg.get('monthly_time', '08:00'))
    monthly_day = int(cfg.get('monthly_day') or 1)

    with _SCHEDULER_LOCK:
        _APP = flask_app
        if _SCHEDULER is None:
            _SCHEDULER = BackgroundScheduler(daemon=True)
            _SCHEDULER.start()
            logger.info('APScheduler 已启动')

        for job_id in ('schedule_daily', 'schedule_monthly'):
            try:
                _SCHEDULER.remove_job(job_id)
            except Exception:
                pass

        _SCHEDULER.add_job(
            _job_scan,
            CronTrigger(hour=daily_h, minute=daily_m),
            args=['daily'],
            id='schedule_daily',
            replace_existing=True,
        )
        _SCHEDULER.add_job(
            _job_scan,
            CronTrigger(day=monthly_day, hour=monthly_h, minute=monthly_m),
            args=['monthly'],
            id='schedule_monthly',
            replace_existing=True,
        )
        logger.info(
            '调度任务已注册 daily=%02d:%02d monthly=day%s %02d:%02d max=%s',
            daily_h, daily_m, monthly_day, monthly_h, monthly_m,
            cfg.get('max_running_tasks'),
        )


def init_scheduler(app):
    """应用启动时初始化调度器。"""
    global _APP
    _APP = app
    reschedule_jobs(app)
