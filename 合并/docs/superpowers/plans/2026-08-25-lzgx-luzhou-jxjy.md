# LZGX 泸州公需课 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增泸州公需课（LZGX）执行器：自动登录 + 按 `class_id`（courseId）播放未完成课件，列表页与播放页窗口句柄切换。

**Architecture:** 新建 `LzgxTaskRunner(SeleniumTaskRunner)` 并 `@register_runner('LZGX')`。首页身份证+密码+图形验证码登录；打开 `/reg/userStudy?courseId=`；点击「学习」由站点新开 `/reg/userStudy/videoStudy/{id}`；监控 `#video` 与「继续学习」弹窗；列表全部 100% 后 `status=2`。

**Tech Stack:** Python、Selenium、ddddocr、Flask runner 注册表

## Global Constraints

- 网站编码必须为 `LZGX`
- 站点 URL：`https://jxjy.lzy.edu.cn/`
- `enable_sms_code=0`，不做考试
- `class_id` = 课程 `courseId`（非完整 URL）
- 禁止为播放另起 WebDriver；禁止无关 `driver.get` 重建会话
- 播放页由站点新开，用 window handles 切换；不要 seek 进度条

---

### Task 1: 创建 LzgxTaskRunner 并注册 + 网站种子

**Files:**
- Create: `backend/services/runners/lzgx_runner.py`
- Modify: `backend/services/runners/__init__.py`
- Create: `backend/sql/seed_lzgx_website.sql`

**Interfaces:**
- Consumes: `SeleniumTaskRunner`（`_init_browser` / `_ensure_logged_in` / `_recognize_captcha_screenshot` / `_mark_course_complete` / `_start_monitor_thread` / `_sync_task_status`）
- Produces: `@register_runner('LZGX')` 的 `LzgxTaskRunner`

- [x] **Step 1: 实现 `lzgx_runner.py`（登录 + 列表 + 播放循环）**
- [x] **Step 2: 在 `__init__.py` 注册导入**
- [x] **Step 3: 增加 `seed_lzgx_website.sql`**
- [x] **Step 4: 冒烟验证注册表含 LZGX**

Run（backend 目录）:

```bash
python -c "from services.runners import *; from services.task_runner import _runner_registry; print('LZGX' in _runner_registry)"
```

Expected: `True`
