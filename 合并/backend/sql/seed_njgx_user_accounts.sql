-- 内江公需（NJGX）用户账号导入
-- 可重复执行：已存在同 website_code+username 则更新密码
--   mysql -u root -p task_manager < backend/sql/seed_njgx_user_accounts.sql

SET NAMES utf8mb4;

-- 511025199506215287
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'NJGX', '', NULL, '511025199506215287', 'Aa@18783906863', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'NJGX' AND `username` = '511025199506215287'
);
UPDATE `user_account`
SET `password` = 'Aa@18783906863', `update_time` = NOW()
WHERE `website_code` = 'NJGX' AND `username` = '511025199506215287';

-- 511025197509171700
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'NJGX', '', NULL, '511025197509171700', 'Aa@13568029486', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'NJGX' AND `username` = '511025197509171700'
);
UPDATE `user_account`
SET `password` = 'Aa@13568029486', `update_time` = NOW()
WHERE `website_code` = 'NJGX' AND `username` = '511025197509171700';

-- 511023198211086118
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'NJGX', '', NULL, '511023198211086118', '$Aa123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'NJGX' AND `username` = '511023198211086118'
);
UPDATE `user_account`
SET `password` = '$Aa123456', `update_time` = NOW()
WHERE `website_code` = 'NJGX' AND `username` = '511023198211086118';

-- 511002198905197224
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'NJGX', '', NULL, '511002198905197224', 'Njez+1925', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'NJGX' AND `username` = '511002198905197224'
);
UPDATE `user_account`
SET `password` = 'Njez+1925', `update_time` = NOW()
WHERE `website_code` = 'NJGX' AND `username` = '511002198905197224';

-- 共 4 个账号（仅账号/密码，姓名留空）
