# GYGX 广元公需课 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增广元公需课（GYGX）执行器：自动登录 + 按 class_id(planId) 播放未完成课件，全程同浏览器窗口句柄切换。

**Architecture:** 新建 `GygxTaskRunner(SeleniumTaskRunner)` 并 `@register_runner('GYGX')`。登录写 sessionStorage（accessToken）；学习保留列表页 window，播放由站点 `window.open('/player')`，监控线程读进度，100% 后关播放页回列表点「查询」。

**Tech Stack:** Python、Selenium、ddddocr、Flask runner 注册表

## Global Constraints

- 网站编码必须为 `GYGX`
- 站点 URL：`https://www.gysjxjy.com:90/`
- `enable_sms_code=0`，不做考试
- `class_id` 映射站点 `planId`
- 禁止为播放另起 WebDriver；禁止用无关 `driver.get` 重建会话
- 播放页由站点新开，用 window handles 切换

---

### Task 1: 创建 GygxTaskRunner 骨架并注册

**Files:**
- Create: `backend/services/runners/gygx_runner.py`
- Modify: `backend/services/runners/__init__.py`
- Create: `backend/sql/seed_gygx_website.sql`

- [x] **Step 1: 实现 runner（登录 + 选课播放循环）并注册**
- [x] **Step 2: 增加网站种子 SQL**
- [x] **Step 3: 冒烟导入注册表含 GYGX**

Run: `python -c "from services.runners import *; from services.task_runner import _runner_registry; print('GYGX' in _runner_registry)"`（在 backend 目录）

Expected: `True`（已验证）

---

### Task 2: 清理临时探测脚本

- [x] 删除 `_tmp_parse_gygx*.py` / `_tmp_gygx*_out.txt`
