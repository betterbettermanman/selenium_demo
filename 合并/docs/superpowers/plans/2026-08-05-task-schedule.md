# 任务周期调度 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 任务支持 manual/daily/monthly 调度；定时与「立即执行」扫描启动；daily/monthly 禁止普通手动启动；全局并发上限。

**Architecture:** Task.schedule_type + JSON 调度配置 + APScheduler + scheduler 服务复用 start_task(source=scheduler)。

**Tech Stack:** Flask、APScheduler、Vue/Ant Design Vue、MySQL ALTER 迁移

## Global Constraints

- schedule_type 默认 `manual`
- daily/monthly 禁止 `POST /tasks/:id/start`
- 扫描仅 `status=1` + 匹配类型 + 未运行；受 `max_running_tasks` 限制
- 不自动重置、不自动换课

---

### Task 1: 数据模型与迁移 + 调度配置

**Files:**
- Modify: `backend/models/task.py`
- Create: `backend/sql/migrate_add_task_schedule_type.sql`
- Create: `backend/services/scheduler_config.py`（读写 `data/scheduler_config.json`）

- [x] 增加 `schedule_type` 字段与 to_dict
- [x] 迁移 SQL
- [x] 配置读写：max_running_tasks、daily_time、monthly_day、monthly_time

### Task 2: 调度服务 + API + 启动拦截

**Files:**
- Modify: `backend/services/task_runner.py`（running count、start source）
- Create: `backend/services/task_scheduler.py`
- Create: `backend/routes/scheduler.py`
- Modify: `backend/routes/task.py`（CRUD schedule_type、start 拦截）
- Modify: `backend/app.py`（注册蓝图、启动 scheduler）
- Modify: `backend/requirements.txt`（APScheduler）

- [x] start_task(source=manual|scheduler)
- [x] run_schedule_scan(type)
- [x] GET/PUT /api/scheduler/config；POST /api/scheduler/run
- [x] 应用启动注册 daily/monthly job

### Task 3: 前端

**Files:**
- Modify: `frontend/src/api/index.js`
- Modify: `frontend/src/views/TaskList.vue`
- Modify: `frontend/src/views/mobile/MobileTaskList.vue`（同步调度字段与启动禁用）

- [x] 表单/列表 schedule_type
- [x] daily/monthly 禁用启动
- [x] 立即执行每日/每月扫描 + 简单调度设置弹窗

### Task 4: 冒烟

- [x] 导入与接口校验；迁移说明

---

## Spec coverage

| Spec | Task |
|---|---|
| schedule_type | 1–3 |
| 手动启动拦截 | 2–3 |
| 定时/立即扫描 | 2–3 |
| max_running_tasks | 1–2 |
| 不重置不换课 | 全期 |
