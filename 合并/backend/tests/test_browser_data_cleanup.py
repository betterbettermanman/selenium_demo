"""浏览器用户目录：超过 15 天未被使用才删除。"""
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.browser_data_cleanup import cleanup_browser_data


NOW = datetime(2026, 10, 16, 12, 0, 0)


def _write(path: Path, when: datetime):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('x', encoding='utf-8')
    os.utime(path, (when.timestamp(), when.timestamp()))


def _freeze_tree(path: Path, when: datetime, keep: dict | None = None):
    """把整棵目录的时间改旧，仅保留 keep 里指定文件的时间。"""
    kept = {os.path.normcase(str(item)): moment for item, moment in (keep or {}).items()}
    old_ts = when.timestamp()
    for dirpath, _dirnames, filenames in os.walk(path):
        os.utime(dirpath, (old_ts, old_ts))
        for name in filenames:
            file_path = os.path.join(dirpath, name)
            moment = kept.get(os.path.normcase(file_path), when)
            os.utime(file_path, (moment.timestamp(), moment.timestamp()))


class BrowserDataCleanupTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'browser_data'
        self.root.mkdir()
        self.old = datetime(2026, 9, 1, 8, 0, 0)
        self.recent = datetime(2026, 10, 10, 8, 0, 0)

    def tearDown(self):
        self.tmp.cleanup()

    def _cleanup(self, **kwargs):
        kwargs.setdefault('protected_task_ids', set())
        kwargs.setdefault('protected_preview_names', set())
        return cleanup_browser_data(str(self.root), now=NOW, **kwargs)

    def test_deletes_task_profile_unused_over_15_days(self):
        profile = self.root / 'SCGX' / '12' / 'alice'
        _write(profile / 'Local State', self.old)
        _write(profile / 'Default' / 'Preferences', self.old)
        _freeze_tree(profile, self.old)

        summary = self._cleanup()

        self.assertEqual(summary['deleted'], 1)
        self.assertFalse(profile.exists())
        self.assertFalse((self.root / 'SCGX').exists())
        self.assertTrue(self.root.exists())

    def test_keeps_profile_when_cookie_file_is_recent(self):
        profile = self.root / 'SCGX' / '12' / 'alice'
        _write(profile / 'Local State', self.old)
        cookie = profile / 'Default' / 'Network' / 'Cookies'
        _write(cookie, self.recent)
        _freeze_tree(profile, self.old, keep={cookie: self.recent})

        summary = self._cleanup()

        self.assertEqual(summary['deleted'], 0)
        self.assertEqual(summary['kept_recent'], 1)
        self.assertTrue(cookie.exists())

    def test_cache_mtime_does_not_keep_unused_profile(self):
        profile = self.root / 'SCGX' / '9' / 'bob'
        _write(profile / 'Default' / 'Preferences', self.old)
        cache = profile / 'Default' / 'Cache' / 'data_0'
        _write(cache, self.recent)
        _freeze_tree(profile, self.old, keep={cache: self.recent})

        summary = self._cleanup()

        self.assertEqual(summary['deleted'], 1)
        self.assertFalse(profile.exists())

    def test_keeps_in_use_task_even_if_old(self):
        profile = self.root / 'ZXZH' / '7' / 'carol'
        _write(profile / 'Local State', self.old)
        _freeze_tree(profile, self.old)

        summary = self._cleanup(protected_task_ids={7})

        self.assertEqual(summary['kept_in_use'], 1)
        self.assertEqual(summary['deleted'], 0)
        self.assertTrue(profile.exists())

    def test_deletes_old_preview_and_keeps_open_preview(self):
        old_preview = self.root / 'WEBSITE_PREVIEW' / 'SCGX'
        open_preview = self.root / 'WEBSITE_PREVIEW' / 'ZXZH'
        _write(old_preview / 'Local State', self.old)
        _write(open_preview / 'Local State', self.old)
        _freeze_tree(old_preview, self.old)
        _freeze_tree(open_preview, self.old)

        summary = self._cleanup(protected_preview_names={'ZXZH'})

        self.assertFalse(old_preview.exists())
        self.assertTrue(open_preview.exists())
        self.assertEqual(summary['deleted'], 1)
        self.assertEqual(summary['kept_in_use'], 1)

    def test_missing_root_is_noop(self):
        shutil.rmtree(self.root)
        summary = self._cleanup()
        self.assertTrue(summary['ok'])
        self.assertEqual(summary['deleted'], 0)
        self.assertEqual(summary['scanned'], 0)


if __name__ == '__main__':
    unittest.main()
