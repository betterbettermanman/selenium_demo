-- 四川公需课程学习网站种子数据（可重复执行）
USE `task_manager`;

INSERT INTO `website` (`name`, `code`, `url`, `enable_sms_code`, `remark`, `create_time`, `update_time`)
SELECT '四川公需课程学习', 'SCGX', 'https://www.sedu.net/student/#/login', '0', '四川省继续教育网', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `website` WHERE `code` = 'SCGX'
);
