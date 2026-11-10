import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

driver_manager = importlib.import_module("chromedriver_manager")
报工 = importlib.import_module("直接报工")
新增任务 = importlib.import_module("新增任务_排产_报工")


class CreateDriverTest(unittest.TestCase):
    def test_chromedriver_manager_is_local(self):
        self.assertEqual(报工.get_chromedriver_path.__module__, "chromedriver_manager")

    def test_driver_cache_is_inside_project(self):
        self.assertEqual(
            报工.DRIVER_CACHE_DIR,
            os.path.join(HERE, "driver_cache", "chromedriver"),
        )

    @mock.patch.object(报工.webdriver, "Chrome")
    @mock.patch.object(
        报工,
        "get_chromedriver_path",
        return_value=r"C:\driver-cache\chromedriver.exe",
        create=True,
    )
    def test_create_driver_uses_explicit_chromedriver_service(self, resolve, chrome):
        driver = 报工.create_driver()

        self.assertIs(driver, chrome.return_value)
        kwargs = chrome.call_args.kwargs
        self.assertIn(
            "service",
            kwargs,
            "未显式指定 ChromeDriver，启动可能卡在 Selenium Manager 自动发现",
        )
        self.assertEqual(kwargs["service"].path, r"C:\driver-cache\chromedriver.exe")
        resolve.assert_called_once_with()
        driver.set_script_timeout.assert_called_once_with(60)


class ChromeDriverManagerTest(unittest.TestCase):
    def test_cached_driver_uses_current_cache_after_migration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            driver = cache_dir / "157.0.8103.38" / "chromedriver.exe"
            driver.parent.mkdir(parents=True)
            driver.write_bytes(b"driver")
            old_path = cache_dir.parent / "old-location" / "chromedriver.exe"
            (cache_dir / "meta.json").write_text(json.dumps({
                "chrome_version": "157.0.8103.39",
                "driver_version": "157.0.8103.38",
                "path": str(old_path),
            }), encoding="utf-8")
            with mock.patch.multiple(
                driver_manager,
                detect_chrome_version=mock.DEFAULT,
                _get_cache_dir=mock.DEFAULT,
                resolve_download=mock.DEFAULT,
            ) as mocks:
                mocks["detect_chrome_version"].return_value = "157.0.8103.39"
                mocks["_get_cache_dir"].return_value = cache_dir
                mocks["resolve_download"].return_value = (
                    "157.0.8103.38",
                    "https://example.com/driver.zip",
                    "chromedriver.exe",
                )
                result = driver_manager.get_chromedriver_path()

            self.assertEqual(result, str(driver))
            mocks["resolve_download"].assert_not_called()

    def test_metadata_path_is_relative_to_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)

            def create_driver(_url, target_dir, exe_name):
                target_dir.mkdir(parents=True, exist_ok=True)
                (target_dir / exe_name).write_bytes(b"driver")

            with mock.patch.multiple(
                driver_manager,
                detect_chrome_version=mock.DEFAULT,
                _get_cache_dir=mock.DEFAULT,
                resolve_download=mock.DEFAULT,
                _download_and_extract=mock.DEFAULT,
            ) as mocks:
                mocks["detect_chrome_version"].return_value = "157.0.8103.39"
                mocks["_get_cache_dir"].return_value = cache_dir
                mocks["resolve_download"].return_value = (
                    "157.0.8103.38",
                    "https://example.com/driver.zip",
                    "chromedriver.exe",
                )
                mocks["_download_and_extract"].side_effect = create_driver
                driver_manager.get_chromedriver_path()

            meta = json.loads((cache_dir / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["path"], os.path.join("157.0.8103.38", "chromedriver.exe"))
            self.assertFalse(os.path.isabs(meta["path"]))

    @mock.patch.object(driver_manager, "_http_get_json")
    def test_google_fallback_uses_full_version_index(self, get_json):
        get_json.return_value = {"versions": [{"version": "157.0.8103.38"}]}

        versions = driver_manager._fetch_google_cft_versions()

        self.assertEqual(versions, ["157.0.8103.38"])
        get_json.assert_called_once_with(
            "https://googlechromelabs.github.io/chrome-for-testing/"
            "known-good-versions-with-downloads.json"
        )

    @mock.patch.object(driver_manager, "_list_mirror_versions", return_value=["114.0.5735.90"])
    @mock.patch.object(
        driver_manager,
        "_platform_assets",
        return_value=("win64", "chromedriver-win64.zip", "chromedriver.exe"),
    )
    def test_legacy_windows_download_always_uses_win32(self, platform_assets, versions):
        _version, url, _exe = driver_manager.resolve_download("114.0.5735.90")

        self.assertTrue(url.endswith("/chromedriver_win32.zip"))


class TemplateConfigTest(unittest.TestCase):
    def test_parent_template_is_inside_template_directory(self):
        expected = os.path.join(HERE, "template", "开发任务填报-父任务模版.md")

        self.assertEqual(新增任务.TEMPLATE_PATH, expected)
        self.assertTrue(os.path.isfile(expected))


class RepositoryConfigTest(unittest.TestCase):
    @mock.patch.object(新增任务.os.path, "isdir", return_value=False)
    def test_find_repos_rejects_missing_root(self, isdir):
        with self.assertRaisesRegex(RuntimeError, "Git 仓库目录不存在"):
            新增任务.find_repos(r"D:\missing-repos")

    @mock.patch.object(新增任务, "find_repos", return_value=[])
    @mock.patch.object(新增任务, "load_env", return_value={"REPO_ROOT": r"D:\repos"})
    def test_collect_commits_uses_configured_repo_root(self, load_env, find_repos):
        result = 新增任务.collect_commits(None)

        self.assertEqual(result, {"前端": [], "后端": []})
        find_repos.assert_called_once_with(r"D:\repos")


class WorkDescriptionTest(unittest.TestCase):
    @mock.patch.object(新增任务, "call_llm")
    def test_llm_description_has_no_dangling_number_after_limit(self, call_llm):
        first_line = "1." + "一" * 55
        call_llm.return_value = first_line + "\n2.补充自动化测试"
        grouped = {"前端": [{"subject": "完成订单统计", "files": []}], "后端": []}

        result = 新增任务.build_work_description(grouped, "订单统计")

        self.assertEqual(result, first_line)
        self.assertLessEqual(len(result), 60)

    def test_task_file_description_is_limited_before_reporting(self):
        description = "1." + "工" * 70
        with mock.patch.multiple(
            新增任务,
            collect_commits=mock.DEFAULT,
            create_driver=mock.DEFAULT,
            login=mock.DEFAULT,
            find_today_task=mock.DEFAULT,
            commit_ids=mock.DEFAULT,
            schedule_task=mock.DEFAULT,
            report_created_task=mock.DEFAULT,
        ) as mocks:
            mocks["collect_commits"].return_value = {"前端": [], "后端": []}
            mocks["find_today_task"].return_value = {"id": "task-1", "taskName": "订单统计"}
            mocks["commit_ids"].return_value = "abc"
            task_file = mock.mock_open(read_data=json.dumps({"workDescription": description}))
            with mock.patch("builtins.open", task_file):
                新增任务.main(["--task-file", "task.json"])

            actual = mocks["report_created_task"].call_args.args[2]

        self.assertEqual(actual, "1." + "工" * 58)
        self.assertLessEqual(len(actual), 60)


if __name__ == "__main__":
    unittest.main()
