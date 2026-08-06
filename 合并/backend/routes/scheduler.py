"""调度配置与立即执行扫描 API。"""
from flask import Blueprint, current_app, request

from services.scheduler_config import get_scheduler_config, save_scheduler_config
from services.task_scheduler import normalize_schedule_type, reschedule_jobs, run_schedule_scan

scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')


@scheduler_bp.route('/config', methods=['GET'])
def get_config():
    return {
        'code': 200,
        'data': get_scheduler_config(),
        'message': 'success',
    }


@scheduler_bp.route('/config', methods=['PUT'])
def update_config():
    data = request.get_json() or {}
    cfg, err = save_scheduler_config(data)
    if err:
        return {'code': 400, 'message': err}, 400
    try:
        reschedule_jobs(current_app._get_current_object())
    except Exception:
        return {
            'code': 200,
            'data': cfg,
            'message': '配置已保存，但刷新定时任务失败，请重启服务',
        }
    return {'code': 200, 'data': cfg, 'message': '配置已保存并刷新定时任务'}


@scheduler_bp.route('/run', methods=['POST'])
def run_now():
    data = request.get_json() or {}
    schedule_type = normalize_schedule_type(data.get('type'))
    if schedule_type not in ('daily', 'monthly'):
        return {'code': 400, 'message': 'type 须为 daily 或 monthly'}, 400

    app = current_app._get_current_object()
    summary = run_schedule_scan(schedule_type, app=app)
    if not summary.get('ok'):
        return {'code': 400, 'message': summary.get('message', '扫描失败'), 'data': summary}, 400
    return {
        'code': 200,
        'data': summary,
        'message': summary.get('message', '扫描完成'),
    }
