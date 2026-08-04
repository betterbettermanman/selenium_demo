# Task Completed Time Implementation Plan

> **For agentic workers:** Implement sequentially; mark tasks complete as you go.

**Goal:** Add `completed_time` to tasks; set on status→完成; show in list/export; keep value when reverting to 未完成.

**Architecture:** DB column + model field; auto-set in `update_task_fields` and task PUT when status becomes `'2'`; frontend column.

**Tech Stack:** Flask/SQLAlchemy, Vue/Ant Design Vue, manual SQL migrate.

## Tasks

1. SQL migrate + init.sql
2. Model `to_dict` + `update_task_fields` + PUT route
3. Export column
4. TaskList.vue + MobileTaskList.vue
5. Build frontend to backend/static
6. Remind user to run migrate SQL
