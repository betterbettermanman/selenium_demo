import logging
import threading
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

_running_threads = {}
_lock = threading.Lock()
_runner_registry = {}


def register_runner(website_code):
    """按网站编码注册任务执行器。"""

    def decorator(cls):
        _runner_registry[website_code] = cls
        return cls

    return decorator


def is_task_running(task_id):
    with _lock:
        thread = _running_threads.get(task_id)
        return thread is not None and thread.is_alive()


class BaseTaskRunner(ABC):
    def __init__(self, task, website):
        self.task = task
        self.website = website

    @abstractmethod
    def run(self):
        pass


@register_runner('__default__')
class DefaultTaskRunner(BaseTaskRunner):
    """默认执行器：记录任务上下文，供后续按网站扩展具体自动化逻辑。"""

    def run(self):
        logger.info(
            '启动任务 id=%s website=%s user=%s class_id=%s courses=%s enable_sms=%s',
            self.task.id,
            self.website.code,
            self.task.username,
            self.task.class_id,
            self.task.courses,
            self.website.enable_sms_code,
        )
        # 此处可接入各网站 Selenium 脚本，按 website.code 分发


def _get_runner_class(website_code):
    return _runner_registry.get(website_code) or _runner_registry['__default__']


def update_task_fields(task, **fields):
    """更新任务字段并提交（在 runner 线程内、已有 app_context 时调用）。"""
    from models import db
    from models.task import Task

    task_id = task.id if hasattr(task, 'id') else task
    db_task = db.session.get(Task, task_id)
    if not db_task:
        logger.warning('任务 %s 不存在，无法更新状态', task_id)
        return False

    for key, value in fields.items():
        setattr(db_task, key, value)

    try:
        db.session.commit()
        if hasattr(task, 'id'):
            for key, value in fields.items():
                setattr(task, key, value)
        return True
    except Exception:
        logger.exception('任务 %s 更新失败 fields=%s', task_id, fields)
        db.session.rollback()
        return False


def start_task(task_id, app):
    from models.task import Task
    from models.website import Website

    if is_task_running(task_id):
        return False, '任务正在执行中'

    task = Task.query.get(task_id)
    if not task:
        return False, '任务不存在'

    if not task.website_code:
        return False, '任务未关联网站，无法启动'

    website = Website.query.filter_by(code=task.website_code).first()
    if not website:
        return False, f'网站编码 {task.website_code} 不存在'

    runner_cls = _get_runner_class(website.code)
    runner = runner_cls(task, website)

    def _target():
        with app.app_context():
            try:
                logger.info('任务 %s 开始执行', task_id)
                runner.run()
                logger.info('任务 %s 执行完成', task_id)
            except Exception:
                logger.exception('任务 %s 执行失败', task_id)
            finally:
                with _lock:
                    _running_threads.pop(task_id, None)

    thread = threading.Thread(target=_target, daemon=True, name=f'task-{task_id}')
    with _lock:
        _running_threads[task_id] = thread
    thread.start()
    return True, '任务已启动'
