"""SCGX 四川公需：学员端页面与小节进度判定。"""
import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.runners.scgx_runner import is_student_portal, lesson_percent_done


class ScgxPageGuardTest(unittest.TestCase):
    def test_student_portal_is_not_player(self):
        self.assertTrue(is_student_portal('https://www.sedu.net/student/#/our-course'))
        self.assertTrue(is_student_portal('https://www.sedu.net/student/#/gxkm-detail?id=1'))
        self.assertFalse(is_student_portal('https://study.example.com/#/play'))
        self.assertFalse(is_student_portal(''))

    def test_lesson_percent_done(self):
        self.assertFalse(lesson_percent_done('学习进度：1.421%'))
        self.assertFalse(lesson_percent_done('学习进度：0%'))
        self.assertTrue(lesson_percent_done('学习进度：100%'))
        self.assertTrue(lesson_percent_done('学习进度：100.00%'))
        self.assertFalse(lesson_percent_done('去学习'))


if __name__ == '__main__':
    unittest.main()
