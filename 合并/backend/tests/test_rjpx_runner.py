"""RJPX 人教教师服务培训平台：注册表与 pxid 解析。"""
import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.runners.rjpx_runner import DEFAULT_PXID, parse_pxid


class RjpxPxidParseTest(unittest.TestCase):
    def test_empty_uses_default(self):
        self.assertEqual(parse_pxid(''), DEFAULT_PXID)
        self.assertEqual(parse_pxid(None), DEFAULT_PXID)

    def test_numeric_pxid(self):
        self.assertEqual(parse_pxid('196'), '196')
        self.assertEqual(parse_pxid('0'), '0')

    def test_url_pxid(self):
        self.assertEqual(
            parse_pxid('https://wp.pep.com.cn/web/index.php?/px/index/196'),
            '196',
        )
        self.assertEqual(
            parse_pxid('https://wp.pep.com.cn/web/index.php?/login/index/196/1'),
            '196',
        )
        self.assertEqual(
            parse_pxid('https://wp.pep.com.cn/web/index.php?/pxcom/index/0'),
            '0',
        )

    def test_homepage_url_uses_default(self):
        self.assertEqual(parse_pxid('https://wp.pep.com.cn/'), DEFAULT_PXID)
        self.assertEqual(parse_pxid('https://t.pep.com.cn/xjcq2026'), DEFAULT_PXID)


class RjpxRegistryTest(unittest.TestCase):
    def test_runner_registered(self):
        from services.runners import RjpxTaskRunner  # noqa: F401
        from services.task_runner import _runner_registry

        self.assertIn('RJPX', _runner_registry)
        self.assertIs(_runner_registry['RJPX'], RjpxTaskRunner)


if __name__ == '__main__':
    unittest.main()
