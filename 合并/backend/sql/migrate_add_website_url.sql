-- 为 website 表添加 url 字段
USE `task_manager`;

ALTER TABLE `website`
  ADD COLUMN `url` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '网站URL' AFTER `code`;
