# ZXZH 课程学习 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 扩展 `ZxzhTaskRunner`：登录后按 `courses` 播课，专题页学时满 10 标记完成。

**Architecture:** 在现有登录流程后接入播课循环；专题页保留主窗口，课程新标签播放；学时检测驱动结束条件。

**Tech Stack:** Python、Selenium、已有 ZXZH 登录/滑块

## Global Constraints

- `task.class_id` = 专题页 URL
- `task.courses` = `[{title, url}, ...]`
- 完成条件：专题页累计学时达到 10
- 禁止另起 WebDriver
- 对齐 `寒暑假期教师研修/main.py` 播放交互

---

### Task 1: 扩展 run_main + 学时检测 + 播课循环

**Files:**
- Modify: `backend/services/runners/zxzh_runner.py`

- [x] **Step 1: 改 run_main：登录 → 校验配置 → 播课循环 → 完成/失败**
- [x] **Step 2: 实现专题页学时解析 `_hours_reached` / `_read_training_hours`**
- [x] **Step 3: 实现单课播放（新标签、目录、视频、2x、「再学一遍」）**
- [x] **Step 4: 实现外层循环：学时未满则下一节/下一门；耗尽则失败**
- [x] **Step 5: 冒烟导入 ZXZH 仍注册成功**

---

### Task 2: 本地联调说明

- [x] 提供任务配置示例（class_id + courses JSON，来自参考 config）→ `docs/zxzh_2026jjsqpx_task_sample.json`
- [x] 清理临时脚本（如有）
