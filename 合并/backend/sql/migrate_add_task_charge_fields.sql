-- 为 task 表添加是否收费、价格字段
USE `task_manager`;

ALTER TABLE `task`
  ADD COLUMN `is_charged` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '0' COMMENT '是否收费（1：收费，0：不收费）' AFTER `is_head`,
  ADD COLUMN `price` int DEFAULT NULL COMMENT '价格' AFTER `is_charged`;
