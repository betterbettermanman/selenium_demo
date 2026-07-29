# ZXZH 国家中小学智慧教育平台登录 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 ZXZH 执行器：账号密码 + 滑块验证码自动登录，登录成功后标记任务完成并关闭浏览器。

**Architecture:** 新建 `ZxzhTaskRunner(SeleniumTaskRunner)` 并 `@register_runner('ZXZH')`。滑块优先 ddddocr 缺口匹配 + 拟人拖拽；连续失败则切换 OpenCV/其它开源缺口方案。本期不做听课业务。

**Tech Stack:** Python、Selenium、ddddocr、（兜底）OpenCV、Flask runner 注册表

## Global Constraints

- 网站编码必须为 `ZXZH`
- 站点 URL：`https://basic.smartedu.cn/`
- `enable_sms_code=0`
- 登录成功 → `status=2` 并关浏览器；失败 → `status=1`
- 测试账号密码不得硬编码进仓库
- 滑块：ddddocr 优先，无效则换其它方案

---

### Task 1: 探测登录页与滑块 DOM

**Files:**
- Create (临时): `backend/_tmp_probe_zxzh.py`（测完可删）

- [x] **Step 1: 用 Selenium 有头打开站点，定位登录入口、账号密码框、滑块元素/iframe**
- [x] **Step 2: 记录选择器、验证码厂商特征、登录态判定字段到实现注释/日志**

---

### Task 2: 实现 ZxzhTaskRunner（登录 + 滑块）并注册

**Files:**
- Create: `backend/services/runners/zxzh_runner.py`
- Modify: `backend/services/runners/__init__.py`
- Create: `backend/sql/seed_zxzh_website.sql`
- Modify (如需): `backend/requirements.txt`（兜底依赖 opencv-python-headless）

**Interfaces:**
- Consumes: `SeleniumTaskRunner._init_browser / _ensure_logged_in / _mark_course_complete / _sync_task_status / _finalize_run`
- Produces: `@register_runner('ZXZH') class ZxzhTaskRunner`，实现 `_is_logged_in` / `_auto_login` / 滑块通过

- [x] **Step 1: 实现 runner 主流程：init → ensure login → mark complete → sync → cleanup**
- [x] **Step 2: 实现滑块：ddddocr slide_match + ActionChains 拟人轨迹；失败重试 5 次**
- [x] **Step 3: 实现兜底缺口算法（OpenCV 模板/边缘匹配），ddddocr 无效时切换**
- [x] **Step 4: 注册 runner + 网站种子 SQL**
- [x] **Step 5: 冒烟导入**

Run: `python -c "from services.runners import *; from services.task_runner import _runner_registry; print('ZXZH' in _runner_registry)"`（在 backend 目录）

Expected: `True`（已验证）

---

### Task 3: 用测试账号联调登录

**Files:** 无代码提交凭据

- [x] **Step 1: 本地创建网站/任务（或临时脚本），账号来自用户提供的测试号**
- [x] **Step 2: 有头跑通登录；失败则根据截图调整选择器/轨迹/缺口算法**
- [x] **Step 3: 清理临时探测脚本；提交实现代码（不含账号密码）**

备注：腾讯滑块跨域 iframe 下 ActionChains 无效，已改为 CDP `Input.dispatchMouseEvent`；缺口优先 OpenCV 暗色轮廓，ddddocr 为辅。联调已验证可跳转 `https://www.smartedu.cn/` 并标记完成。

---

## Spec coverage

| Spec 要求 | Task |
|---|---|
| 网站 ZXZH + URL | Task 2 seed |
| 账号密码 + 滑块登录 | Task 2–3 |
| 成功 status=2 关浏览器 | Task 2 run_main |
| ddddocr → 其它方案兜底 | Task 2 Step 2–3 |
| 凭据不进仓库 | Task 3 |
| 不做听课 | 全期遵守 |
