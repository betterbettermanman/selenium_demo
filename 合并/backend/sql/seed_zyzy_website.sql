-- 张掖专业课（ZYZY）网站种子
-- 可在网站管理 UI 手动新增，或执行本脚本：
--   mysql -u root -p task_manager < backend/sql/seed_zyzy_website.sql

INSERT INTO website (name, code, url, enable_sms_code, remark, create_time, update_time)
SELECT '张掖专业课', 'ZYZY', 'https://zjjy-zy.ceivs.cn/', '0', '公需站登录后单点进入，按trainingId播课', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM website WHERE code = 'ZYZY');
