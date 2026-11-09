"""LSGX 乐山公需：新站课程 ID 与小节完成状态。"""
import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.runners.lsgx_runner import (
    lesson_is_finished,
    lsgx_study_url,
    normalize_captcha_code,
    resolve_lsgx_course_id,
    summarize_lesson_status,
)


class LsgxCourseIdTest(unittest.TestCase):
    def test_old_course_page(self):
        self.assertEqual(
            resolve_lsgx_course_id('https://www.ls1018.com.cn/course/118.html'),
            '118',
        )

    def test_new_detail_and_study_url(self):
        self.assertEqual(
            resolve_lsgx_course_id('http://lssjjw.63ym.cn/coursedetail.aspx?id=118'),
            '118',
        )
        self.assertEqual(
            resolve_lsgx_course_id('http://lssjjw.63ym.cn/study.aspx?id=90'),
            '90',
        )

    def test_plain_id_and_default(self):
        self.assertEqual(resolve_lsgx_course_id('118'), '118')
        self.assertEqual(resolve_lsgx_course_id('', None), '118')

    def test_first_candidate_wins(self):
        self.assertEqual(
            resolve_lsgx_course_id(
                'http://lssjjw.63ym.cn/coursedetail.aspx?id=90',
                'https://www.ls1018.com.cn/course/118.html',
            ),
            '90',
        )

    def test_study_url(self):
        self.assertEqual(
            lsgx_study_url('118'),
            'http://lssjjw.63ym.cn/study.aspx?id=118',
        )


class LsgxCaptchaCodeTest(unittest.TestCase):
    def test_keep_four_chars(self):
        self.assertEqual(normalize_captcha_code('1136'), '1136')
        self.assertEqual(normalize_captcha_code(' 11 36 '), '1136')

    def test_drop_noise_and_truncate(self):
        self.assertEqual(normalize_captcha_code('ab-12xy'), 'ab12')
        self.assertEqual(normalize_captcha_code(''), '')
        self.assertEqual(normalize_captcha_code('12'), '12')


class LsgxLessonStatusTest(unittest.TestCase):
    def test_finished_and_in_progress(self):
        self.assertTrue(lesson_is_finished('已学完'))
        self.assertFalse(lesson_is_finished('未学习'))
        self.assertFalse(lesson_is_finished('已学至00:12:03'))

    def test_summarize(self):
        self.assertEqual(
            summarize_lesson_status(['已学完', '已学至00:01:00', '未学习', '']),
            (1, 3),
        )

    def test_summarize_all_done(self):
        self.assertEqual(summarize_lesson_status(['已学完', '已学完']), (2, 2))


if __name__ == '__main__':
    unittest.main()
