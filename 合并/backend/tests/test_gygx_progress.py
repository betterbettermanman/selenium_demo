"""GYGX 广元公需课：课表进度解析与汇总。"""
import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.runners.gygx_runner import extract_progress_percent, summarize_course_progress


class GygxProgressParseTest(unittest.TestCase):
    def test_extract_last_percent(self):
        self.assertEqual(extract_progress_percent('习近平新时代 35.5%\n去学习'), 35.5)
        self.assertEqual(extract_progress_percent('已完成 100%'), 100.0)
        self.assertIsNone(extract_progress_percent('去学习'))
        self.assertIsNone(extract_progress_percent(''))

    def test_summarize_done_total(self):
        rows = [
            '课程A\n100%',
            '课程B\n35.5%\n去学习',
            '课程C\n0%\n去学习',
        ]
        self.assertEqual(summarize_course_progress(rows), (1, 3))

    def test_summarize_all_done(self):
        self.assertEqual(summarize_course_progress(['A 100%', 'B 100.0%']), (2, 2))

    def test_summarize_skips_blank(self):
        self.assertEqual(summarize_course_progress(['', '  ', '课 12%']), (0, 1))


if __name__ == '__main__':
    unittest.main()
