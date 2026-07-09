USE `task_manager`;

ALTER TABLE `course`
  ADD COLUMN `price` int DEFAULT NULL COMMENT '价格' AFTER `courses`,
  ADD COLUMN `credit_hours` decimal(10, 1) DEFAULT NULL COMMENT '学时' AFTER `price`;
