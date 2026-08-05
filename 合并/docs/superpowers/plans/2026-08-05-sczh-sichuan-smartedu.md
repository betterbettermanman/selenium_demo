# SCZH 四川智慧中小学平台 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 SCZH 执行器：ThirdPortal 账号密码自动登录，按 `class_id` 课程详情 URL 自动播未学小节，并用 `chapterProcess` 接口轮询进度直至全部学完。

**Architecture:** 新建 `SczhTaskRunner(SeleniumTaskRunner)` 并 `@register_runner('SCZH')`。登录与播课主路径移植自 `四川智慧教育平台2/main.py`，纳入合并项目任务状态与浏览器隔离。

**Tech Stack:** Python、Selenium、requests、Flask runner 注册表

## Global Constraints

- 网站编码必须为 `SCZH`
- 站点：`https://basic.sc.smartedu.cn/`
- `enable_sms_code=0`
- 任务 `class_id` = 课程详情完整 URL（含 courseId）；不依赖 `task.courses`
- 登录 Cookie：`Teaching_Autonomic_Learning_Token` → Header `x-token`
- 进度接口：`/hd/teacherTraining/api/studyCourseUser/chapterProcess?chapterId=`
- 不做考试/答题；凭据不硬编码进仓库

---

### Task 1: 实现 SczhTaskRunner 并注册 + 种子

**Files:**
- Create: `backend/services/runners/sczh_runner.py`
- Modify: `backend/services/runners/__init__.py`
- Create: `backend/sql/seed_sczh_website.sql`

- [x] **Step 1: 实现 runner：登录、打开课程、播未学小节、解析 chapterId/subsectionId、轮询进度、完成标记**
- [x] **Step 2: 在 `__init__.py` 注册导入**
- [x] **Step 3: 编写 `seed_sczh_website.sql`**
- [x] **Step 4: 冒烟导入验证 `SCZH` 在 runner 注册表中**

Run: `python -c "from services.runners import *; from services.task_runner import _runner_registry; print('SCZH' in _runner_registry)"`（在 backend 目录）

Expected: `True`

---

## Spec coverage

| Spec 要求 | Task |
|---|---|
| 网站 SCZH + URL | Task 1 seed |
| ThirdPortal 自动登录 | Task 1 |
| class_id 课程页扫未学小节 | Task 1 |
| chapterProcess 进度轮询 | Task 1 |
| 全部学完 status=2 | Task 1 |
| 不做考试 / 不用 courses | 全期遵守 |
