-- 为 task 表添加学习进度字段
USE `task_manager`;

ALTER TABLE `task`
  ADD COLUMN `progress` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    DEFAULT '' COMMENT '学习进度（按网站不同：学时或完成数/总数）'
    AFTER `status`;
