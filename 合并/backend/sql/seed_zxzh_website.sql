-- 国家中小学智慧教育平台（ZXZH）网站种子
-- 可在网站管理 UI 手动新增，或执行本脚本：
--   mysql -u root -p task_manager < backend/sql/seed_zxzh_website.sql

INSERT INTO website (name, code, url, enable_sms_code, remark, create_time, update_time)
SELECT '国家中小学智慧教育平台', 'ZXZH', 'https://basic.smartedu.cn/', '0', '账号密码+腾讯滑块登录', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM website WHERE code = 'ZXZH');
