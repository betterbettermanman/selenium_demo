"""任务启动/停止生命周期：防止旧线程清掉新任务注册。"""
import sys
import threading
import time
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services import task_runner as tr
from services.task_runner import (
    RunnerPhase,
    _remove_runner,
    _running_runners,
    _running_threads,
    has_live_task_thread,
    is_task_running,
)


class _FakeRunner:
    def __init__(self):
        self.phase = RunnerPhase.RUNNING
        self._stopped = False
        self.driver = object()
        self.task = types.SimpleNamespace(id=1, schedule_type='manual', nick_name='t', username='u')
        self.is_running = True

    def request_stop(self):
        self._stopped = True
        self.phase = RunnerPhase.DONE
        self.is_running = False
        self.driver = None


class TaskRunnerLifecycleTest(unittest.TestCase):
    def setUp(self):
        with tr._lock:
            _running_runners.clear()
            _running_threads.clear()

    def tearDown(self):
        with tr._lock:
            _running_runners.clear()
            _running_threads.clear()

    def test_old_finally_does_not_clear_new_registration(self):
        task_id = 12669
        old_runner = _FakeRunner()
        new_runner = _FakeRunner()
        old_thread = threading.Thread(target=lambda: None)
        new_thread = threading.Thread(target=lambda: None)

        with tr._lock:
            _running_runners[task_id] = new_runner
            _running_threads[task_id] = new_thread

        # 模拟旧线程 finally：只应清理自己，不能动新注册
        _remove_runner(task_id, runner=old_runner, thread=old_thread)

        self.assertIs(_running_runners.get(task_id), new_runner)
        self.assertIs(_running_threads.get(task_id), new_thread)
        self.assertTrue(is_task_running(task_id))

    def test_stop_keeps_thread_until_exit_blocks_restart(self):
        task_id = 12669
        runner = _FakeRunner()
        hold = threading.Event()

        def _work():
            hold.wait(timeout=2)

        thread = threading.Thread(target=_work, daemon=True)
        with tr._lock:
            _running_runners[task_id] = runner
            _running_threads[task_id] = thread
        thread.start()

        runner.request_stop()
        with tr._lock:
            if _running_runners.get(task_id) is runner:
                _running_runners.pop(task_id, None)

        self.assertFalse(is_task_running(task_id))
        self.assertTrue(has_live_task_thread(task_id))

        hold.set()
        thread.join(timeout=2)
        _remove_runner(task_id, runner=runner, thread=thread)
        self.assertFalse(has_live_task_thread(task_id))


if __name__ == '__main__':
    unittest.main()
