-- 乐山公需（LSGX）用户账号导入
-- 可重复执行：已存在同 website_code+username 则更新姓名/密码
--   mysql -u root -p task_manager < backend/sql/seed_lsgx_user_accounts.sql

SET NAMES utf8mb4;

-- 吴树英 / 511132198110230020
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '吴树英', NULL, '511132198110230020', 'ls1018@123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511132198110230020'
);
UPDATE `user_account`
SET `nick_name` = '吴树英', `password` = 'ls1018@123', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511132198110230020';

-- 朱燕 / 511132198602233228
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '朱燕', NULL, '511132198602233228', 'ls1018@123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511132198602233228'
);
UPDATE `user_account`
SET `nick_name` = '朱燕', `password` = 'ls1018@123', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511132198602233228';

-- 邹雪梅 / 511132198103082322
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '邹雪梅', NULL, '511132198103082322', 'ls1018@123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511132198103082322'
);
UPDATE `user_account`
SET `nick_name` = '邹雪梅', `password` = 'ls1018@123', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511132198103082322';

-- 陈菊兰 / 51111219750508032X
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '陈菊兰', NULL, '51111219750508032X', 'Aa@15983368088', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '51111219750508032X'
);
UPDATE `user_account`
SET `nick_name` = '陈菊兰', `password` = 'Aa@15983368088', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '51111219750508032X';

-- 李旭梅 / 511112197310103026
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '李旭梅', NULL, '511112197310103026', 'Aa@13540545615', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511112197310103026'
);
UPDATE `user_account`
SET `nick_name` = '李旭梅', `password` = 'Aa@13540545615', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511112197310103026';

-- 潘军 / 511112197109143018
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '潘军', NULL, '511112197109143018', 'Aa@13540908772', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511112197109143018'
);
UPDATE `user_account`
SET `nick_name` = '潘军', `password` = 'Aa@13540908772', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511112197109143018';

-- 傅晶 / 511129200107190023
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '傅晶', NULL, '511129200107190023', 'Aa@17341726186', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511129200107190023'
);
UPDATE `user_account`
SET `nick_name` = '傅晶', `password` = 'Aa@17341726186', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511129200107190023';

-- 潘慧 / 511129199507305429
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '潘慧', NULL, '511129199507305429', 'Aa@18781362449', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511129199507305429'
);
UPDATE `user_account`
SET `nick_name` = '潘慧', `password` = 'Aa@18781362449', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511129199507305429';

-- 李霞 / 李霞LX
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '李霞', NULL, '李霞LX', 'LX18383313866', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '李霞LX'
);
UPDATE `user_account`
SET `nick_name` = '李霞', `password` = 'LX18383313866', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '李霞LX';

-- 胡佳敏 / 511124199801301726
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '胡佳敏', NULL, '511124199801301726', 'ls1018@123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511124199801301726'
);
UPDATE `user_account`
SET `nick_name` = '胡佳敏', `password` = 'ls1018@123', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511124199801301726';

-- 胡悦 / 13108979560
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '胡悦', NULL, '13108979560', '19970602hy.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '13108979560'
);
UPDATE `user_account`
SET `nick_name` = '胡悦', `password` = '19970602hy.', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '13108979560';

-- 陈珍羽 / 511129198504150025
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '陈珍羽', NULL, '511129198504150025', 'ls1018@123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511129198504150025'
);
UPDATE `user_account`
SET `nick_name` = '陈珍羽', `password` = 'ls1018@123', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511129198504150025';

-- 王倩 / 511129199201125628
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '王倩', NULL, '511129199201125628', 'Hechuan123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511129199201125628'
);
UPDATE `user_account`
SET `nick_name` = '王倩', `password` = 'Hechuan123', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511129199201125628';

-- 陈华 / 511123198311150047
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '陈华', NULL, '511123198311150047', 'Aa@18980262625', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511123198311150047'
);
UPDATE `user_account`
SET `nick_name` = '陈华', `password` = 'Aa@18980262625', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511123198311150047';

-- 王艳 / 511129198409104047
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'LSGX', '王艳', NULL, '511129198409104047', 'Aa@15984360690', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'LSGX' AND `username` = '511129198409104047'
);
UPDATE `user_account`
SET `nick_name` = '王艳', `password` = 'Aa@15984360690', `update_time` = NOW()
WHERE `website_code` = 'LSGX' AND `username` = '511129198409104047';

-- 共 15 个账号
