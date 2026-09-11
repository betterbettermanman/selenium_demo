"""ZXZH 专题页学时解析：占位 0.00 与真实进度文案。"""
import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.runners.zxzh_runner import ZxzhTaskRunner


class ZxzhCourseProgressParseTest(unittest.TestCase):
    def test_parse_course_progress(self):
        body = (
            '大力弘扬教育家精神\n'
            '已学习 1.80\n'
            '已认定 1.50 / 认定 2 学时\n'
            '其他课程'
        )
        progress = ZxzhTaskRunner._parse_course_progress_from_body(body, '大力弘扬教育家精神')
        self.assertIsNotNone(progress)
        self.assertEqual(progress['learned'], 1.8)
        self.assertEqual(progress['accredited'], 1.5)
        self.assertEqual(progress['required'], 2.0)

    def test_parse_missing_credit_returns_none(self):
        body = '大力弘扬教育家精神\n暂无学时'
        self.assertIsNone(
            ZxzhTaskRunner._parse_course_progress_from_body(body, '大力弘扬教育家精神')
        )

    def test_parse_total_accredited(self):
        text = '继续加油吧！ 0.0%\n已学习 0.00学时\n已认定 / 要求认定 0.00 / 10学时'
        self.assertEqual(ZxzhTaskRunner._parse_total_accredited_text(text), (0.0, 10.0))
        text2 = '已认定 / 要求认定 2.00 / 10学时'
        self.assertEqual(ZxzhTaskRunner._parse_total_accredited_text(text2), (2.0, 10.0))

    def test_all_zero_progress_snapshot(self):
        zero_snap = (0.0, 10.0, (('大力弘扬教育家精神', 0.0, 0.0, 2.0),))
        self.assertTrue(ZxzhTaskRunner._is_all_zero_progress(zero_snap))
        real_snap = (2.0, 10.0, (('大力弘扬教育家精神', 1.8, 1.5, 2.0),))
        self.assertFalse(ZxzhTaskRunner._is_all_zero_progress(real_snap))
        course_nonzero = (0.0, 10.0, (('大力弘扬教育家精神', 0.5, 0.0, 2.0),))
        self.assertFalse(ZxzhTaskRunner._is_all_zero_progress(course_nonzero))


if __name__ == '__main__':
    unittest.main()
