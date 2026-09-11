-- 人教教师服务培训平台（RJPX）网站种子
-- 可在网站管理 UI 手动新增，或执行本脚本：
--   mysql -u root -p task_manager < backend/sql/seed_rjpx_website.sql
--
-- 任务 class_id 填培训项目 pxid（2026 秋季新教材培训为 196，对应 t.pep.com.cn/xjcq2026）。
-- 为空时执行器默认 196。学习目标：学习数据中全部必修/必学回放。

INSERT INTO website (name, code, url, enable_sms_code, remark, create_time, update_time)
SELECT '人教教师服务培训平台', 'RJPX', 'https://wp.pep.com.cn/', '0', '密码+图形验证码登录，学习数据中全部必修回放', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM website WHERE code = 'RJPX');
