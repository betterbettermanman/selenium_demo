-- 泸州公需课（LZGX）网站种子
-- 可在网站管理 UI 手动新增，或执行本脚本：
--   mysql -u root -p task_manager < backend/sql/seed_lzgx_website.sql

INSERT INTO website (name, code, url, enable_sms_code, remark, create_time, update_time)
SELECT '泸州公需课', 'LZGX', 'https://jxjy.lzy.edu.cn/', '0', '身份证+密码+图形验证码登录，按courseId播课', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM website WHERE code = 'LZGX');
