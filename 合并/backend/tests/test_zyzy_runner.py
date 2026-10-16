"""ZYZY 张掖专业课：注册表与 trainingId 解析。"""
import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.runners.zyzy_runner import parse_training_id
from services.task_runner import _runner_registry

import services.runners  # noqa: F401


class ZyzyTrainingIdParseTest(unittest.TestCase):
    def test_numeric_id(self):
        self.assertEqual(parse_training_id('1513942790160490496'), '1513942790160490496')

    def test_course_url(self):
        self.assertEqual(
            parse_training_id(
                'https://zjjy-zy.ceivs.cn/training-detail?trainingId=1513942790160490496'
            ),
            '1513942790160490496',
        )

    def test_empty_rejected(self):
        with self.assertRaises(RuntimeError):
            parse_training_id('')

    def test_runner_registered(self):
        self.assertIn('ZYZY', _runner_registry)
