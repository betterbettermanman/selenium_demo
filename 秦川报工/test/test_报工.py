import importlib
import json
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

driver_manager = importlib.import_module("chromedriver_manager")
报工 = importlib.import_module("直接报工")
新增任务 = importlib.import_module("新增任务_排产_报工")
生成任务 = importlib.import_module("生成任务")


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
    NON_DEVELOPMENT_TEXT = """【任务名称】：生产数据核对
工作类别：数据核对
工作场景：订单数据差异核对
工作内容及边界：核对指定范围的订单数据，不包含数据修正
交付内容：数据核对结论和差异清单
交付方式：两者结合
交付要求：描述记录核对范围和结论，附件提供差异清单
评估标准（基线工时）：待确认"""

    def build_non_development_task(self, responses):
        grouped = {"前端": [], "后端": [{"subject": "核对生产订单数据", "files": []}]}
        with mock.patch.multiple(
            新增任务,
            load_env=mock.DEFAULT,
            call_llm=mock.DEFAULT,
        ) as mocks:
            mocks["load_env"].return_value = {"TASK_TEMPLATE": "非开发工作场景与交付要求填报说明.md"}
            mocks["call_llm"].side_effect = responses
            result = 新增任务.build_task(grouped, date(2026, 11, 3))
        return result, mocks["call_llm"]

    def test_parent_template_is_inside_template_directory(self):
        expected = os.path.join(HERE, "template", "开发任务填报-父任务模版.md")

        self.assertEqual(新增任务.TEMPLATE_PATH, expected)
        self.assertTrue(os.path.isfile(expected))

    def test_child_template_generates_child_task_content(self):
        child_text = """【任务名称】：订单统计页面与接口
【涉及端】：全栈
订单统计：
- 前端：实现订单统计页面
- 后端：实现订单统计接口
不做范围：
- 无"""
        parent_text = """【父任务名称】：旧父任务
1. 需求背景
旧内容
2. 技术性描述
旧内容"""
        grouped = {"前端": [{"subject": "完成订单统计", "files": []}], "后端": []}
        with mock.patch.multiple(
            新增任务,
            load_env=mock.DEFAULT,
            call_llm=mock.DEFAULT,
        ) as mocks:
            mocks["load_env"].return_value = {"TASK_TEMPLATE": "开发任务填报-子任务模版.md"}
            mocks["call_llm"].side_effect = [child_text, parent_text]

            result = 新增任务.build_task(grouped, date(2026, 11, 3))

        self.assertEqual(result["name"], "订单统计页面与接口")
        self.assertIn("订单统计：", result["description"])
        self.assertEqual(mocks["call_llm"].call_count, 1)

    def test_non_development_template_generates_seven_field_task(self):
        non_development_text = """【任务名称】：生产数据核对
工作类别：数据核对
工作场景：订单数据差异核对
工作内容及边界：核对指定范围的订单数据，不包含数据修正
交付内容：数据核对结论和差异清单
交付方式：两者结合
交付要求：描述记录核对范围和结论，附件提供差异清单
评估标准（基线工时）：待确认"""
        parent_text = """【父任务名称】：旧父任务
1. 需求背景
旧内容
2. 技术性描述
旧内容"""
        grouped = {"前端": [], "后端": [{"subject": "核对生产订单数据", "files": []}]}
        with mock.patch.multiple(
            新增任务,
            load_env=mock.DEFAULT,
            call_llm=mock.DEFAULT,
        ) as mocks:
            mocks["load_env"].return_value = {"TASK_TEMPLATE": "非开发工作场景与交付要求填报说明.md"}
            mocks["call_llm"].side_effect = [non_development_text, parent_text]

            result = 新增任务.build_task(grouped, date(2026, 11, 3))

        self.assertEqual(result["name"], "生产数据核对")
        self.assertIn("工作类别：数据核对", result["description"])
        self.assertIn("评估标准（基线工时）：待确认", result["description"])
        self.assertEqual(mocks["call_llm"].call_count, 1)

    def test_non_development_template_retries_when_field_value_is_empty(self):
        invalid_text = self.NON_DEVELOPMENT_TEXT.replace(
            "交付内容：数据核对结论和差异清单", "交付内容："
        )

        result, call_llm = self.build_non_development_task([
            invalid_text,
            self.NON_DEVELOPMENT_TEXT,
        ])

        self.assertEqual(call_llm.call_count, 2)
        self.assertIn("交付内容：数据核对结论和差异清单", result["description"])

    def test_non_development_template_rejects_invalid_delivery_method(self):
        invalid_text = self.NON_DEVELOPMENT_TEXT.replace(
            "交付方式：两者结合", "交付方式：口头说明"
        )

        result, call_llm = self.build_non_development_task([
            invalid_text,
            self.NON_DEVELOPMENT_TEXT,
        ])

        self.assertEqual(call_llm.call_count, 2)
        self.assertIn("交付方式：两者结合", result["description"])

    def test_non_development_baseline_is_pending_without_workhour_input(self):
        response = self.NON_DEVELOPMENT_TEXT.replace("待确认", "8人时")

        result, call_llm = self.build_non_development_task([response])

        self.assertEqual(call_llm.call_count, 1)
        self.assertIn("评估标准（基线工时）：待确认", result["description"])
        self.assertNotIn("8人时", result["description"])

    def test_unknown_template_is_rejected(self):
        with mock.patch.object(
            新增任务, "load_env", return_value={"TASK_TEMPLATE": "../其他模板.md"}
        ):
            with self.assertRaisesRegex(RuntimeError, "不支持的模板"):
                新增任务.load_template()

    def test_existing_task_recognizes_all_supported_templates(self):
        descriptions = {
            "父任务": "【父任务名称】：订单统计\n1. 需求背景\n背景\n2. 技术性描述\n方案",
            "子任务": "【任务名称】：订单统计\n【涉及端】：全栈\n订单统计：\n- 前端：页面",
            "非开发": (
                "【任务名称】：生产数据核对\n工作类别：数据核对\n工作场景：订单数据差异核对\n"
                "工作内容及边界：核对数据\n交付内容：核对结论\n交付方式：任务描述中写明即可\n"
                "交付要求：记录结论\n评估标准（基线工时）：待确认"
            ),
        }
        driver = mock.Mock()
        with mock.patch.multiple(
            新增任务,
            USERNAME="tester",
            WebDriverWait=mock.DEFAULT,
            wait_project=mock.DEFAULT,
        ):
            for template_type, description in descriptions.items():
                with self.subTest(template_type=template_type):
                    driver.execute_async_script.return_value = [{
                        "id": "task-1",
                        "taskName": "订单统计",
                        "createTime": "2026-11-03 10:00:00",
                        "createBy": "tester",
                        "parentTaskId": None,
                        "schedulingStatus": "0",
                        "description": description,
                    }]

                    result = 新增任务.find_today_task(driver, date(2026, 11, 3))

                    self.assertIsNotNone(result)
                    self.assertEqual(result["id"], "task-1")


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


class TaskDateConfigTest(unittest.TestCase):
    def test_target_day_reads_task_date_from_env(self):
        with mock.patch.object(新增任务, "load_env", return_value={"TASK_DATE": "2026-11-03"}):
            result = 新增任务.target_day()

        self.assertEqual(result, date(2026, 11, 3))

    def test_generate_task_uses_configured_date(self):
        with mock.patch.multiple(
            新增任务,
            load_env=mock.DEFAULT,
            collect_commits=mock.DEFAULT,
            build_task=mock.DEFAULT,
        ) as mocks:
            mocks["load_env"].return_value = {"TASK_DATE": "2026-11-03"}
            mocks["collect_commits"].return_value = {"前端": [], "后端": []}
            mocks["build_task"].return_value = None

            生成任务.main()

        mocks["collect_commits"].assert_called_once_with(date(2026, 11, 3))


class WorkflowDateTest(unittest.TestCase):
    def test_main_passes_configured_date_to_scheduling_and_reporting(self):
        grouped = {"前端": [], "后端": []}
        with mock.patch.multiple(
            新增任务,
            load_env=mock.DEFAULT,
            collect_commits=mock.DEFAULT,
            create_driver=mock.DEFAULT,
            login=mock.DEFAULT,
            find_today_task=mock.DEFAULT,
            build_work_description=mock.DEFAULT,
            commit_ids=mock.DEFAULT,
            schedule_task=mock.DEFAULT,
            report_created_task=mock.DEFAULT,
        ) as mocks:
            mocks["load_env"].return_value = {"TASK_DATE": "2026-11-03"}
            mocks["collect_commits"].return_value = grouped
            mocks["find_today_task"].return_value = {"id": "task-1", "taskName": "订单统计"}
            mocks["build_work_description"].return_value = "完成订单统计"
            mocks["commit_ids"].return_value = "abc"
            driver = mocks["create_driver"].return_value

            新增任务.main([])

        day = date(2026, 11, 3)
        mocks["schedule_task"].assert_called_once_with(driver, "订单统计", day)
        mocks["report_created_task"].assert_called_once_with(
            driver, "订单统计", "完成订单统计", "abc", grouped, day
        )

    def test_schedule_task_uses_selected_date(self):
        driver = mock.Mock()
        driver.execute_async_script.return_value = {"ok": True}
        with mock.patch.multiple(
            新增任务,
            WebDriverWait=mock.DEFAULT,
            wait_project=mock.DEFAULT,
            find_task_record=mock.DEFAULT,
        ) as mocks:
            mocks["find_task_record"].return_value = {"id": "task-1", "schedulingStatus": "0"}

            新增任务.schedule_task(driver, "订单统计", date(2026, 11, 3))

        plan = driver.execute_async_script.call_args.args[2]
        self.assertEqual(plan, {
            "start": "2026-11-03 08:30:00",
            "end": "2026-11-07 17:30:00",
        })

    def test_report_created_task_uses_selected_date(self):
        driver = mock.Mock()
        driver.execute_async_script.return_value = False
        driver.execute_script.side_effect = [
            None,
            {"id": "task-1", "taskName": "订单统计"},
            {
                "duration": 8,
                "remaining": 0,
                "description": "完成订单统计",
                "commitId": "abc",
                "isStorage": 1,
                "finalOutputFlag": 1,
                "documentVersion": "V20261103",
            },
        ]
        with mock.patch.multiple(
            新增任务,
            WebDriverWait=mock.DEFAULT,
            select_assignee_and_search=mock.DEFAULT,
            render_commit_screenshot=mock.DEFAULT,
            click_work_hour=mock.DEFAULT,
            upload_output=mock.DEFAULT,
        ) as mocks:
            mocks["render_commit_screenshot"].return_value = "commits.png"

            新增任务.report_created_task(
                driver,
                "订单统计",
                "完成订单统计",
                "abc",
                {"前端": [], "后端": []},
                date(2026, 11, 3),
            )

        self.assertEqual(driver.execute_async_script.call_args.args[2], "2026-11-03")
        mocks["render_commit_screenshot"].assert_called_once_with(
            driver, {"前端": [], "后端": []}, date(2026, 11, 3)
        )
        fill_arguments = driver.execute_script.call_args_list[2].args
        self.assertEqual(fill_arguments[2:4], ("2026-11-03 08:30:00", "2026-11-03 17:30:00"))


class WorkDescriptionTest(unittest.TestCase):
    @mock.patch.object(新增任务, "call_llm")
    def test_overlong_llm_description_is_rewritten(self, call_llm):
        original = "1." + "一" * 70
        rewritten = "1.完成订单统计并补充测试"
        call_llm.side_effect = [original, rewritten]
        grouped = {"前端": [{"subject": "完成订单统计", "files": []}], "后端": []}

        with mock.patch.object(新增任务, "load_env", return_value={}):
            result = 新增任务.build_work_description(grouped, "订单统计")

        self.assertEqual(result, rewritten)
        self.assertEqual(call_llm.call_count, 2)
        self.assertIn("压缩改写", call_llm.call_args_list[1].args[1])

    @mock.patch.object(新增任务, "call_llm")
    def test_overlong_rewrite_keeps_complete_entries(self, call_llm):
        first_line = "1." + "一" * 55
        original = first_line + "\n2.补充自动化测试"
        call_llm.side_effect = [original, original]
        grouped = {"前端": [{"subject": "完成订单统计", "files": []}], "后端": []}

        with mock.patch.object(新增任务, "load_env", return_value={}):
            result = 新增任务.build_work_description(grouped, "订单统计")

        self.assertEqual(result, first_line)
        self.assertLessEqual(len(result), 60)
        self.assertEqual(call_llm.call_count, 2)

    def test_task_file_description_keeps_complete_entries_before_reporting(self):
        first_line = "1." + "工" * 55
        description = first_line + "\n2.补充自动化测试"
        with mock.patch.multiple(
            新增任务,
            collect_commits=mock.DEFAULT,
            create_driver=mock.DEFAULT,
            login=mock.DEFAULT,
            find_today_task=mock.DEFAULT,
            commit_ids=mock.DEFAULT,
            schedule_task=mock.DEFAULT,
            report_created_task=mock.DEFAULT,
            load_env=mock.DEFAULT,
        ) as mocks:
            mocks["collect_commits"].return_value = {"前端": [], "后端": []}
            mocks["find_today_task"].return_value = {"id": "task-1", "taskName": "订单统计"}
            mocks["commit_ids"].return_value = "abc"
            mocks["load_env"].return_value = {}
            task_file = mock.mock_open(read_data=json.dumps({"workDescription": description}))
            with mock.patch("builtins.open", task_file):
                新增任务.main(["--task-file", "task.json"])

            actual = mocks["report_created_task"].call_args.args[2]

        self.assertEqual(actual, first_line)
        self.assertLessEqual(len(actual), 60)

    def test_env_length_controls_complete_entry_limit(self):
        description = "1.完成订单统计\n2.补充接口和页面自动化测试"
        with mock.patch.object(
            新增任务,
            "load_env",
            return_value={"WORK_DESCRIPTION_MAX_LENGTH": "20"},
        ):
            result = 新增任务.limit_work_description(description)

        self.assertEqual(result, "1.完成订单统计")

    def test_single_overlong_entry_is_rejected(self):
        with mock.patch.object(新增任务, "load_env", return_value={}):
            with self.assertRaisesRegex(
                RuntimeError,
                "WORK_DESCRIPTION_MAX_LENGTH",
            ):
                新增任务.limit_work_description("1." + "工" * 70)

    @mock.patch.object(新增任务, "call_llm")
    def test_env_length_is_used_in_llm_prompt(self, call_llm):
        call_llm.return_value = "1.完成订单统计"
        grouped = {"前端": [{"subject": "完成订单统计", "files": []}], "后端": []}

        with mock.patch.object(
            新增任务,
            "load_env",
            return_value={"WORK_DESCRIPTION_MAX_LENGTH": "80"},
        ):
            新增任务.build_work_description(grouped, "订单统计")

        prompt = call_llm.call_args.args[0]
        self.assertIn("80 字内", prompt)
        self.assertIn("80 个字符", prompt)
        self.assertNotIn("60 字内", prompt)

    def test_invalid_env_length_is_rejected(self):
        for value in ("abc", "0", "-1", "1.5"):
            with self.subTest(value=value), mock.patch.object(
                新增任务,
                "load_env",
                return_value={"WORK_DESCRIPTION_MAX_LENGTH": value},
            ):
                with self.assertRaisesRegex(RuntimeError, "正整数"):
                    新增任务.limit_work_description("1.完成订单统计")


if __name__ == "__main__":
    unittest.main()
