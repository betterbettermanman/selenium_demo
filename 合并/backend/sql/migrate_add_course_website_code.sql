-- 为已有 course 表添加 website_code 字段
USE `task_manager`;

ALTER TABLE `course`
  ADD COLUMN `website_code` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '网站编码' AFTER `class_id`;
