import logging
import threading
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)

_running_threads = {}
_running_runners = {}
_lock = threading.Lock()
_runner_registry = {}


class RunnerPhase(str, Enum):
    IDLE = 'idle'
    WAITING_SMS = 'waiting_sms'
    RUNNING = 'running'
    FAILED = 'failed'
    DONE = 'done'


def register_runner(website_code):
    def decorator(cls):
        _runner_registry[website_code] = cls
        return cls
    return decorator


def is_task_running(task_id):
    with _lock:
        thread = _running_threads.get(task_id)
        if thread is not None and thread.is_alive():
            return True
        runner = _running_runners.get(task_id)
        return runner is not None and runner.phase in (
            RunnerPhase.WAITING_SMS, RunnerPhase.RUNNING
        )


def get_runner(task_id):
    with _lock:
        return _running_runners.get(task_id)


class BaseTaskRunner(ABC):
    def __init__(self, task, website):
        self.task = task
        self.website = website
        self.phase = RunnerPhase.IDLE
        self.driver = None
        self._app = None
        self._stopped = False

    def bind_app(self, app):
        self._app = app

    def prepare_login(self):
        """登录准备阶段。返回 waiting_sms / ready / failed。"""
        return 'ready'

    def submit_sms_code(self, code: str):
        """提交手机验证码。返回 (success, message)。"""
        return False, '当前网站不支持手机验证码'

    def resend_sms_code(self):
        """重发手机验证码。返回 (success, message)。"""
        return False, '当前网站不支持重发验证码'

    @abstractmethod
    def run_main(self):
        """验证码通过后的主流程。"""
        pass

    def run(self):
        """默认执行入口（无短信流程的网站可直接实现 run_main）。"""
        self.run_main()

    def _run_with_context(self, target):
        if not self._app:
            target()
            return
        with self._app.app_context():
            target()

    def _set_phase(self, phase: RunnerPhase):
        self.phase = phase

    def request_stop(self):
        """用户手动停止：终止循环并关闭浏览器。"""
        self._stopped = True
        self._set_phase(RunnerPhase.DONE)
        if hasattr(self, 'is_running'):
            self.is_running = False
        self._cleanup()

    def _cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info('任务 %s 浏览器已关闭', getattr(self.task, 'id', '?'))
            except Exception:
                logger.exception('任务 %s 关闭浏览器失败', getattr(self.task, 'id', '?'))
            finally:
                self.driver = None


@register_runner('__default__')
class DefaultTaskRunner(BaseTaskRunner):
    def run_main(self):
        logger.info(
            '启动任务 id=%s website=%s user=%s',
            self.task.id, self.website.code, self.task.username,
        )


def _get_runner_class(website_code):
    return _runner_registry.get(website_code) or _runner_registry['__default__']


def update_task_fields(task, **fields):
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


def _remove_runner(task_id):
    with _lock:
        _running_runners.pop(task_id, None)
        _running_threads.pop(task_id, None)


def _start_main_thread(task_id, runner, app):
    def _target():
        with app.app_context():
            try:
                runner._set_phase(RunnerPhase.RUNNING)
                logger.info('任务 %s 开始执行主流程', task_id)
                runner.run_main()
                runner._set_phase(RunnerPhase.DONE)
                logger.info('任务 %s 主流程执行完成', task_id)
            except Exception:
                runner._set_phase(RunnerPhase.FAILED)
                logger.exception('任务 %s 执行失败', task_id)
            finally:
                _remove_runner(task_id)
                if not runner._stopped:
                    try:
                        runner._cleanup()
                    except Exception:
                        logger.exception('任务 %s 清理失败', task_id)

    thread = threading.Thread(target=_target, daemon=True, name=f'task-{task_id}')
    with _lock:
        _running_threads[task_id] = thread
    thread.start()


def start_task(task_id, app):
    from models.task import Task
    from models.website import Website

    if is_task_running(task_id):
        return False, {'message': '任务正在执行中'}

    task = Task.query.get(task_id)
    if not task:
        return False, {'message': '任务不存在'}

    if not task.website_code:
        return False, {'message': '任务未关联网站，无法启动'}

    website = Website.query.filter_by(code=task.website_code).first()
    if not website:
        return False, {'message': f'网站编码 {task.website_code} 不存在'}

    runner_cls = _get_runner_class(website.code)
    runner = runner_cls(task, website)
    runner.bind_app(app)

    with _lock:
        _running_runners[task_id] = runner

    need_sms_flow = website.enable_sms_code == '1'

    if need_sms_flow:
        try:
            with app.app_context():
                login_result = runner.prepare_login()
        except Exception as exc:
            logger.exception('任务 %s 登录准备失败', task_id)
            _remove_runner(task_id)
            try:
                runner._cleanup()
            except Exception:
                pass
            return False, {'message': f'登录失败: {exc}'}

        if login_result == 'waiting_sms':
            runner._set_phase(RunnerPhase.WAITING_SMS)
            return True, {
                'need_sms': True,
                'message': '请输入手机验证码',
                'task_id': task_id,
            }
        if login_result == 'failed':
            _remove_runner(task_id)
            try:
                runner._cleanup()
            except Exception:
                pass
            return False, {'message': '登录失败，请检查账号密码'}

    _start_main_thread(task_id, runner, app)
    return True, {'need_sms': False, 'message': '任务已启动', 'task_id': task_id}


def submit_sms_code(task_id, code, app):
    runner = get_runner(task_id)
    if not runner:
        return False, '任务未运行或已结束'
    if runner.phase != RunnerPhase.WAITING_SMS:
        return False, '当前任务不在等待验证码状态'

    code = (code or '').strip()
    if not code:
        return False, '请输入手机验证码'

    try:
        with app.app_context():
            ok, msg = runner.submit_sms_code(code)
    except Exception as exc:
        logger.exception('任务 %s 提交验证码失败', task_id)
        return False, f'验证码提交失败: {exc}'

    if not ok:
        return False, msg or '验证码错误'

    _start_main_thread(task_id, runner, app)
    return True, msg or '验证成功，任务继续执行'


def stop_task(task_id, app):
    with _lock:
        runner = _running_runners.get(task_id)

    if not runner or not is_task_running(task_id):
        return False, '任务未在运行'

    logger.info('用户手动停止任务 %s', task_id)
    try:
        runner.request_stop()
    except Exception:
        logger.exception('停止任务 %s 时关闭浏览器失败', task_id)

    _remove_runner(task_id)

    with app.app_context():
        update_task_fields(runner.task, status='1')

    return True, '任务已关闭'


def resend_sms_code(task_id, app):
    runner = get_runner(task_id)
    if not runner:
        return False, '任务未运行或已结束'
    if runner.phase != RunnerPhase.WAITING_SMS:
        return False, '当前任务不在等待验证码状态'

    try:
        with app.app_context():
            return runner.resend_sms_code()
    except Exception as exc:
        logger.exception('任务 %s 重发验证码失败', task_id)
        return False, f'重发失败: {exc}'
