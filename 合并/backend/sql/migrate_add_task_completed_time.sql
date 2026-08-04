-- 为 task 表添加完成时间字段
USE `task_manager`;

ALTER TABLE `task`
  ADD COLUMN `completed_time` datetime DEFAULT NULL COMMENT '完成时间' AFTER `update_time`;
