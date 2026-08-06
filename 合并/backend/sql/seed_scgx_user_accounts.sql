-- 四川公需（SCGX）用户账号导入
-- 可重复执行：已存在同 website_code+username 则更新姓名/密码
--   mysql -u root -p task_manager < backend/sql/seed_scgx_user_accounts.sql

SET NAMES utf8mb4;

-- 李霞 / 18383313866
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '李霞', NULL, '18383313866', 'LIxia12345*', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '18383313866'
);
UPDATE `user_account`
SET `nick_name` = '李霞', `password` = 'LIxia12345*', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '18383313866';

-- 邓佳佳 / 18282235439
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '邓佳佳', NULL, '18282235439', 'Jia930320@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '18282235439'
);
UPDATE `user_account`
SET `nick_name` = '邓佳佳', `password` = 'Jia930320@', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '18282235439';

-- 方英俊 / 15196852345
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '方英俊', NULL, '15196852345', 'Fyj871007@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '15196852345'
);
UPDATE `user_account`
SET `nick_name` = '方英俊', `password` = 'Fyj871007@', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '15196852345';

-- 冯欢 / 18010674923
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '冯欢', NULL, '18010674923', '54Fenghuan@123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '18010674923'
);
UPDATE `user_account`
SET `nick_name` = '冯欢', `password` = '54Fenghuan@123', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '18010674923';

-- 王兴高 / 15881818676
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '王兴高', NULL, '15881818676', 'Wxg123456@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '15881818676'
);
UPDATE `user_account`
SET `nick_name` = '王兴高', `password` = 'Wxg123456@', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '15881818676';

-- 祝东 / 18781791870
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '祝东', NULL, '18781791870', 'Zd123456@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '18781791870'
);
UPDATE `user_account`
SET `nick_name` = '祝东', `password` = 'Zd123456@', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '18781791870';

-- 黄竞 / 18990839590
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '黄竞', NULL, '18990839590', 'Aa@18990839590', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '18990839590'
);
UPDATE `user_account`
SET `nick_name` = '黄竞', `password` = 'Aa@18990839590', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '18990839590';

-- 魏超艳 / 18328439710
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '魏超艳', NULL, '18328439710', 'Wcy858585.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '18328439710'
);
UPDATE `user_account`
SET `nick_name` = '魏超艳', `password` = 'Wcy858585.', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '18328439710';

-- 李伟 / 13696013669
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '李伟', NULL, '13696013669', 'Aa@13696013669', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '13696013669'
);
UPDATE `user_account`
SET `nick_name` = '李伟', `password` = 'Aa@13696013669', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '13696013669';

-- 齐小清 / 15082864428
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '齐小清', NULL, '15082864428', 'Aa@15082864428', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '15082864428'
);
UPDATE `user_account`
SET `nick_name` = '齐小清', `password` = 'Aa@15082864428', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '15082864428';

-- 王杨 / 13890616871
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '王杨', NULL, '13890616871', 'Wy13890616871@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '13890616871'
);
UPDATE `user_account`
SET `nick_name` = '王杨', `password` = 'Wy13890616871@', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '13890616871';

-- 王洪 / 18081598988
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '王洪', NULL, '18081598988', 'Aa@18081598988', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '18081598988'
);
UPDATE `user_account`
SET `nick_name` = '王洪', `password` = 'Aa@18081598988', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '18081598988';

-- 张小军 / 13882854693
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGX', '张小军', NULL, '13882854693', 'Zxj1234@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGX' AND `username` = '13882854693'
);
UPDATE `user_account`
SET `nick_name` = '张小军', `password` = 'Zxj1234@', `update_time` = NOW()
WHERE `website_code` = 'SCGX' AND `username` = '13882854693';

-- 共 13 个账号（黄竞重复 3 次已去重）
