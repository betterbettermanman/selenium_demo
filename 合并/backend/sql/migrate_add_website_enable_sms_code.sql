-- 为已有 website 表添加 enable_sms_code 字段
USE `task_manager`;

ALTER TABLE `website`
  ADD COLUMN `enable_sms_code` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '0' COMMENT '是否启用手机验证码（1：启用，0：不启用）' AFTER `code`;
