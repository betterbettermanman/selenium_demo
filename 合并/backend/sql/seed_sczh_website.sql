-- 四川智慧中小学平台（SCZH）网站种子
-- 可在网站管理 UI 手动新增，或执行本脚本：
--   mysql -u root -p task_manager < backend/sql/seed_sczh_website.sql

INSERT INTO website (name, code, url, enable_sms_code, remark, create_time, update_time)
SELECT '四川智慧中小学平台', 'SCZH', 'https://basic.sc.smartedu.cn/', '0', '账号密码登录+教师研修播课', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM website WHERE code = 'SCZH');
