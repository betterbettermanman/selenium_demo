-- 为 task.create_time 增加索引，加速按接单日统计
USE `task_manager`;

ALTER TABLE `task`
  ADD INDEX `idx_task_create_time` (`create_time`);
