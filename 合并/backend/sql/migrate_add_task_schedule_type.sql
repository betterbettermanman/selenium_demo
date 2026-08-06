-- 任务调度类型字段（可重复执行：已有列则跳过需人工确认）
--   mysql -u root -p task_manager < backend/sql/migrate_add_task_schedule_type.sql

ALTER TABLE `task`
  ADD COLUMN `schedule_type` VARCHAR(16) NOT NULL DEFAULT 'manual'
  COMMENT '调度类型（manual：手动，daily：每日，monthly：每月）'
  AFTER `status`;
