"""清理长期未使用的 Chrome user-data-dir。

目录布局与执行器一致：
- 任务：browser_data/{website_code}/{task_id}/{username}
- 网站预览：browser_data/WEBSITE_PREVIEW/{website_code}

按「超过 retention 天未被浏览器写过」删除，而不是按任务创建/完成时间。
每日、每月任务可能创建很久但仍在跑，登录态就在这些目录里；
按任务年龄删除会清掉仍在使用的登录态。已删除任务和预览目录也没有可靠的任务时间。

Windows 上改子文件不会更新父目录的修改时间，因此取目录内文件的最新 mtime。
Cache 一类目录文件很多且不能代表登录态，扫描时跳过。
"""
from __future__ import annotations

import logging
import os
import shutil
import stat
import sys
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

RETENTION_DAYS = 15
CLEANUP_HOUR = 3
CLEANUP_MINUTE = 30

# Chromium 缓存目录，体积大，mtime 不能代表这份配置还在被任务使用
_SKIP_DIR_NAMES = {
    'Cache',
    'Code Cache',
    'GPUCache',
    'DawnGraphiteCache',
    'DawnWebGPUCache',
    'GrShaderCache',
    'ShaderCache',
    'GraphiteDawnCache',
    'Service Worker',
    'blob_storage',
    'optimization_guide_hint_cache_store',
    'Shared Dictionary',
    'VideoDecodeStats',
}

_cleanup_lock = threading.Lock()


def browser_data_root() -> str:
    """与 Selenium user-data-dir 相同，跟随进程工作目录。"""
    return os.path.join(os.getcwd(), 'browser_data')


def profile_last_used(profile_dir: str) -> float:
    """返回 profile 内（不含缓存目录）最新修改时间；读不到则返回 0。"""
    latest = 0.0
    if not os.path.isdir(profile_dir):
        return latest
    for dirpath, dirnames, filenames in os.walk(profile_dir):
        dirnames[:] = [name for name in dirnames if name not in _SKIP_DIR_NAMES]
        latest = max(latest, _mtime(dirpath))
        for name in filenames:
            latest = max(latest, _mtime(os.path.join(dirpath, name)))
    return latest


def cleanup_browser_data(
    root: str | None = None,
    *,
    retention_days: int = RETENTION_DAYS,
    now: datetime | None = None,
    protected_task_ids: set[int] | None = None,
    protected_preview_names: set[str] | None = None,
) -> dict:
    """删除超过 retention_days 未被使用的浏览器用户目录。

    protected_* 为 None 时，按当前进程里正在跑的任务和已打开的预览浏览器跳过。
    传入集合时只按该集合判断占用（便于测试）。
    """
    if not _cleanup_lock.acquire(blocking=False):
        logger.info('浏览器数据清理已在进行，跳过本次')
        return _summary(root or browser_data_root(), retention_days, skipped_busy=True)

    try:
        return _cleanup_browser_data(
            root,
            retention_days=retention_days,
            now=now,
            protected_task_ids=protected_task_ids,
            protected_preview_names=protected_preview_names,
        )
    finally:
        _cleanup_lock.release()


def _cleanup_browser_data(
    root: str | None,
    *,
    retention_days: int,
    now: datetime | None,
    protected_task_ids: set[int] | None,
    protected_preview_names: set[str] | None,
) -> dict:
    data_root = root or browser_data_root()
    summary = _summary(data_root, retention_days)
    if retention_days < 1:
        summary['ok'] = False
        summary['message'] = '保留天数须 >= 1'
        return summary
    if not os.path.isdir(data_root):
        summary['message'] = 'browser_data 不存在，无需清理'
        return summary

    current = now or datetime.now()
    cutoff = (current - timedelta(days=retention_days)).timestamp()
    protect_all_previews = False
    if protected_preview_names is None:
        protected_preview_names, protect_all_previews = _live_protected_preview_names()

    for profile in _iter_profiles(data_root):
        summary['scanned'] += 1
        if _is_in_use(profile, protected_task_ids, protected_preview_names, protect_all_previews):
            summary['kept_in_use'] += 1
            continue
        last_used = profile_last_used(profile['path'])
        if last_used <= 0:
            summary['kept_unknown'] += 1
            continue
        if last_used > cutoff:
            summary['kept_recent'] += 1
            continue
        if _remove_tree(profile['path']):
            summary['deleted'] += 1
            if len(summary['deleted_paths']) < 20:
                summary['deleted_paths'].append(profile['path'])
            logger.info(
                '已删除超过 %s 天未使用的浏览器目录 kind=%s path=%s',
                retention_days, profile['kind'], profile['path'],
            )
        else:
            summary['failed'] += 1

    summary['pruned_dirs'] = _prune_empty_dirs(data_root)
    summary['message'] = (
        f'扫描 {summary["scanned"]}，删除 {summary["deleted"]}，'
        f'近期仍使用 {summary["kept_recent"]}，无法判断跳过 {summary["kept_unknown"]}，'
        f'占用中跳过 {summary["kept_in_use"]}，'
        f'删除失败 {summary["failed"]}'
    )
    return summary


def _summary(root: str, retention_days: int, *, skipped_busy: bool = False) -> dict:
    return {
        'ok': True,
        'skipped_busy': skipped_busy,
        'message': '清理已在进行' if skipped_busy else '',
        'root': root,
        'retention_days': retention_days,
        'scanned': 0,
        'deleted': 0,
        'kept_recent': 0,
        'kept_unknown': 0,
        'kept_in_use': 0,
        'failed': 0,
        'pruned_dirs': 0,
        'deleted_paths': [],
    }


def _iter_profiles(root: str):
    for site in _child_dirs(root):
        if site.name == 'WEBSITE_PREVIEW':
            for code in _child_dirs(site.path):
                yield {
                    'path': code.path,
                    'kind': 'preview',
                    'task_id': None,
                    'name': code.name,
                }
            continue
        for task_dir in _child_dirs(site.path):
            if not task_dir.name.isdigit():
                continue
            task_id = int(task_dir.name)
            for user_dir in _child_dirs(task_dir.path):
                yield {
                    'path': user_dir.path,
                    'kind': 'task',
                    'task_id': task_id,
                    'name': user_dir.name,
                }


def _child_dirs(path: str):
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    yield entry
    except OSError:
        logger.warning('读取目录失败 path=%s', path, exc_info=True)


def _is_in_use(profile: dict, protected_task_ids, protected_preview_names, protect_all_previews: bool) -> bool:
    if profile['kind'] == 'task':
        task_id = profile['task_id']
        if protected_task_ids is not None:
            return task_id in protected_task_ids
        return _task_profile_in_use(task_id)
    if protect_all_previews:
        return True
    return profile['name'] in (protected_preview_names or set())


def _task_profile_in_use(task_id: int) -> bool:
    from services.task_browser import is_task_browser_open
    from services.task_runner import has_live_task_thread, is_task_running

    return (
        is_task_running(task_id)
        or has_live_task_thread(task_id)
        or is_task_browser_open(task_id)
    )


def _live_protected_preview_names() -> tuple[set[str], bool]:
    """返回 (需保留的预览目录名, 是否保留全部预览)。无法确认占用时全部保留。"""
    from services.website_browser import list_open_website_ids

    open_ids = list_open_website_ids()
    if not open_ids:
        return set(), False
    try:
        from models.website import Website
    except Exception:
        logger.exception('无法加载网站模型，预览目录本次全部保留')
        return set(), True

    protected: set[str] = set()
    for website_id in open_ids:
        try:
            website = Website.query.get(website_id)
        except Exception:
            logger.exception('查询打开中的网站失败，预览目录本次全部保留 website_id=%s', website_id)
            return set(), True
        if website is None:
            logger.warning('预览浏览器对应网站不存在，预览目录本次全部保留 website_id=%s', website_id)
            return set(), True
        protected.add(website.code or f'web{website.id}')
    return protected, False


def _mtime(path: str) -> float:
    try:
        return os.stat(path).st_mtime
    except OSError:
        return 0.0


def _remove_tree(path: str) -> bool:
    def _retry(func, target):
        os.chmod(target, stat.S_IWRITE)
        func(target)

    try:
        if sys.version_info >= (3, 12):
            def _onexc(func, target, exc):
                try:
                    _retry(func, target)
                except OSError:
                    raise exc

            shutil.rmtree(path, onexc=_onexc)
        else:
            def _onerror(func, target, _exc_info):
                _retry(func, target)

            shutil.rmtree(path, onerror=_onerror)
        return True
    except OSError:
        logger.warning('删除浏览器目录失败 path=%s', path, exc_info=True)
        return False


def _prune_empty_dirs(root: str) -> int:
    removed = 0
    for dirpath, _dirnames, _filenames in os.walk(root, topdown=False):
        if os.path.abspath(dirpath) == os.path.abspath(root):
            continue
        try:
            if os.listdir(dirpath):
                continue
            os.rmdir(dirpath)
            removed += 1
        except OSError:
            continue
    return removed
