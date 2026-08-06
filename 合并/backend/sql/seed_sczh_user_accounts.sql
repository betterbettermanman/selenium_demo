-- 四川智慧中小学平台（SCZH）用户账号导入
-- 可重复执行：已存在同 website_code+username 则更新姓名/密码
--   mysql -u root -p task_manager < backend/sql/seed_sczh_user_accounts.sql

SET NAMES utf8mb4;

-- 陈朝辉 / 13981366603
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈朝辉', NULL, '13981366603', 'Ll147258', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13981366603'
);
UPDATE `user_account`
SET `nick_name` = '陈朝辉', `password` = 'Ll147258', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13981366603';

-- 肖利芬 / 18080602366
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '肖利芬', NULL, '18080602366', 'Ll147258', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18080602366'
);
UPDATE `user_account`
SET `nick_name` = '肖利芬', `password` = 'Ll147258', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18080602366';

-- 帅四光 / 18080602348
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '帅四光', NULL, '18080602348', 'Ll147258', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18080602348'
);
UPDATE `user_account`
SET `nick_name` = '帅四光', `password` = 'Ll147258', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18080602348';

-- 徐思源 / 13679644177
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '徐思源', NULL, '13679644177', 'Xsy_147258369', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13679644177'
);
UPDATE `user_account`
SET `nick_name` = '徐思源', `password` = 'Xsy_147258369', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13679644177';

-- 陈治安 / 13890688046
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈治安', NULL, '13890688046', 'Ll147258', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890688046'
);
UPDATE `user_account`
SET `nick_name` = '陈治安', `password` = 'Ll147258', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890688046';

-- 范晓文 / 18080602367
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '范晓文', NULL, '18080602367', 'Ll147258', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18080602367'
);
UPDATE `user_account`
SET `nick_name` = '范晓文', `password` = 'Ll147258', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18080602367';

-- 余嘉丽 / 18781336833
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '余嘉丽', NULL, '18781336833', 'YJL93171hy', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18781336833'
);
UPDATE `user_account`
SET `nick_name` = '余嘉丽', `password` = 'YJL93171hy', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18781336833';

-- 胡佳敏 / 18284340207
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '胡佳敏', NULL, '18284340207', 'Hjm199708@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18284340207'
);
UPDATE `user_account`
SET `nick_name` = '胡佳敏', `password` = 'Hjm199708@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18284340207';

-- 万琴 / 15892819175
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '万琴', NULL, '15892819175', 'A067785woaiwan', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15892819175'
);
UPDATE `user_account`
SET `nick_name` = '万琴', `password` = 'A067785woaiwan', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15892819175';

-- 傅晶 / 17341726186
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '傅晶', NULL, '17341726186', 'Ff529719', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17341726186'
);
UPDATE `user_account`
SET `nick_name` = '傅晶', `password` = 'Ff529719', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17341726186';

-- 周婷 / 18783363361
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '周婷', NULL, '18783363361', 'ZTzt1219089650', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18783363361'
);
UPDATE `user_account`
SET `nick_name` = '周婷', `password` = 'ZTzt1219089650', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18783363361';

-- (无姓名) / 18384708567
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18384708567', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18384708567'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18384708567';

-- (无姓名) / 13378354796
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13378354796', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13378354796'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13378354796';

-- (无姓名) / 15183318006
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '15183318006', 'Fnxx124578', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15183318006'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx124578', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15183318006';

-- (无姓名) / 18090060545
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18090060545', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18090060545'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18090060545';

-- (无姓名) / 13778832903
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13778832903', 'Chen0712', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13778832903'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Chen0712', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13778832903';

-- (无姓名) / 13795509554
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13795509554', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13795509554'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13795509554';

-- (无姓名) / 15884341518
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '15884341518', 'Aa@15884341518', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15884341518'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Aa@15884341518', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15884341518';

-- (无姓名) / 18990322662
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18990322662', 'Yjf@90807060', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18990322662'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Yjf@90807060', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18990322662';

-- (无姓名) / 13982801769
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13982801769', 'Lxb729295@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13982801769'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Lxb729295@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13982801769';

-- (无姓名) / 18215604763
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18215604763', 'Fnxx123456@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18215604763'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18215604763';

-- (无姓名) / 13990355642
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13990355642', 'FNxx13579', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13990355642'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'FNxx13579', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13990355642';

-- (无姓名) / 15182231165
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '15182231165', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15182231165'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15182231165';

-- (无姓名) / 18090067075
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18090067075', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18090067075'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18090067075';

-- (无姓名) / 15282339270
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '15282339270', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15282339270'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15282339270';

-- (无姓名) / 18728325705
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18728325705', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18728325705'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18728325705';

-- (无姓名) / 13990328300
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13990328300', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13990328300'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13990328300';

-- (无姓名) / 18090465575
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18090465575', 'Fnxx123456@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18090465575'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18090465575';

-- (无姓名) / 18090077289
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18090077289', 'Brc196718', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18090077289'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Brc196718', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18090077289';

-- (无姓名) / 15182249409
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '15182249409', 'Fnxx9409', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15182249409'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx9409', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15182249409';

-- (无姓名) / 13568253671
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13568253671', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13568253671'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13568253671';

-- (无姓名) / 13890387859
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13890387859', 'Fnxx124578+', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890387859'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx124578+', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890387859';

-- (无姓名) / 13778802507
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13778802507', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13778802507'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13778802507';

-- (无姓名) / 13696082636
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13696082636', 'Wqs369118@!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13696082636'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Wqs369118@!', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13696082636';

-- (无姓名) / 18728379768
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18728379768', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18728379768'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18728379768';

-- (无姓名) / 13548237769
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13548237769', 'Lh820916', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13548237769'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Lh820916', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13548237769';

-- (无姓名) / 13778826032
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13778826032', 'FNxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13778826032'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'FNxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13778826032';

-- (无姓名) / 18980369616
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18980369616', 'Fnxx02468@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18980369616'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx02468@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18980369616';

-- (无姓名) / 18381457998
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18381457998', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18381457998'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18381457998';

-- (无姓名) / 18080398918
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18080398918', 'Xujie9661089', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18080398918'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Xujie9661089', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18080398918';

-- (无姓名) / 13419076678
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13419076678', '810412wgH', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13419076678'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = '810412wgH', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13419076678';

-- (无姓名) / 13778839913
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13778839913', 'Hanxiao139?', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13778839913'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Hanxiao139?', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13778839913';

-- (无姓名) / 13778889248
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13778889248', 'FNxx!@12', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13778889248'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'FNxx!@12', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13778889248';

-- (无姓名) / 18090077522
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18090077522', 'Aa18090077522', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18090077522'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Aa18090077522', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18090077522';

-- (无姓名) / 15282324126
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '15282324126', 'Fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15282324126'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15282324126';

-- (无姓名) / 13320952300
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13320952300', 'Zsj13579?', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13320952300'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Zsj13579?', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13320952300';

-- (无姓名) / 15892719990
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '15892719990', 'Yj123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15892719990'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Yj123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15892719990';

-- (无姓名) / 13890360580
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13890360580', 'Lz123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890360580'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Lz123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890360580';

-- 李丹 / 13558551739
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李丹', NULL, '13558551739', 'Ld13558551739', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13558551739'
);
UPDATE `user_account`
SET `nick_name` = '李丹', `password` = 'Ld13558551739', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13558551739';

-- 周彬玉 / 18040433828
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '周彬玉', NULL, '18040433828', 'Mqy123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18040433828'
);
UPDATE `user_account`
SET `nick_name` = '周彬玉', `password` = 'Mqy123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18040433828';

-- 李旭志 / 13308132851
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李旭志', NULL, '13308132851', 'Aa@13308132851', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13308132851'
);
UPDATE `user_account`
SET `nick_name` = '李旭志', `password` = 'Aa@13308132851', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13308132851';

-- 陈菊兰 / 15983368088
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈菊兰', NULL, '15983368088', 'Aa15983368088', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15983368088'
);
UPDATE `user_account`
SET `nick_name` = '陈菊兰', `password` = 'Aa15983368088', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15983368088';

-- 梁秋萍 / 18090356131
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '梁秋萍', NULL, '18090356131', 'Aa18090356131', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18090356131'
);
UPDATE `user_account`
SET `nick_name` = '梁秋萍', `password` = 'Aa18090356131', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18090356131';

-- 成丽 / 17766086782
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '成丽', NULL, '17766086782', 'Aa17766086782', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17766086782'
);
UPDATE `user_account`
SET `nick_name` = '成丽', `password` = 'Aa17766086782', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17766086782';

-- 邵娜 / 18381395636
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '邵娜', NULL, '18381395636', 'Sn18381395636.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18381395636'
);
UPDATE `user_account`
SET `nick_name` = '邵娜', `password` = 'Sn18381395636.', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18381395636';

-- 杨琼 / 1643379003
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '杨琼', NULL, '1643379003', '2wsx+2WSX', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '1643379003'
);
UPDATE `user_account`
SET `nick_name` = '杨琼', `password` = '2wsx+2WSX', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '1643379003';

-- 文艳红 / 18628998777
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '文艳红', NULL, '18628998777', '131452081399Aaa', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18628998777'
);
UPDATE `user_account`
SET `nick_name` = '文艳红', `password` = '131452081399Aaa', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18628998777';

-- 李彩玉 / 18328193982
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李彩玉', NULL, '18328193982', '1995Licaiyu@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18328193982'
);
UPDATE `user_account`
SET `nick_name` = '李彩玉', `password` = '1995Licaiyu@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18328193982';

-- 陈燕慧 / 18228512993
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈燕慧', NULL, '18228512993', 'Cyh123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18228512993'
);
UPDATE `user_account`
SET `nick_name` = '陈燕慧', `password` = 'Cyh123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18228512993';

-- 吴树英 / 13890640183
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '吴树英', NULL, '13890640183', 'Wsy19811023@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890640183'
);
UPDATE `user_account`
SET `nick_name` = '吴树英', `password` = 'Wsy19811023@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890640183';

-- 李首燕 / 13408245536
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李首燕', NULL, '13408245536', 'Lsy52526@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13408245536'
);
UPDATE `user_account`
SET `nick_name` = '李首燕', `password` = 'Lsy52526@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13408245536';

-- 郑向福 / 18113431968
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '郑向福', NULL, '18113431968', 'Aa18113431968', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18113431968'
);
UPDATE `user_account`
SET `nick_name` = '郑向福', `password` = 'Aa18113431968', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18113431968';

-- 段永惠 / 13608163023
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '段永惠', NULL, '13608163023', 'Szxx@123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13608163023'
);
UPDATE `user_account`
SET `nick_name` = '段永惠', `password` = 'Szxx@123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13608163023';

-- 彭亚睇 / 13540522958
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '彭亚睇', NULL, '13540522958', 'Pydfml1227.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13540522958'
);
UPDATE `user_account`
SET `nick_name` = '彭亚睇', `password` = 'Pydfml1227.', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13540522958';

-- 杨镜榕 / 15700368576
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '杨镜榕', NULL, '15700368576', 'Yjr102266', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15700368576'
);
UPDATE `user_account`
SET `nick_name` = '杨镜榕', `password` = 'Yjr102266', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15700368576';

-- 左艳 / 17721908614
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '左艳', NULL, '17721908614', 'Zy17721908614', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17721908614'
);
UPDATE `user_account`
SET `nick_name` = '左艳', `password` = 'Zy17721908614', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17721908614';

-- 张晓敏 / 13350705408
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '张晓敏', NULL, '13350705408', 'Zxm123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13350705408'
);
UPDATE `user_account`
SET `nick_name` = '张晓敏', `password` = 'Zxm123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13350705408';

-- 鲍艮方 / 18381175360
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '鲍艮方', NULL, '18381175360', 'Bgf123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18381175360'
);
UPDATE `user_account`
SET `nick_name` = '鲍艮方', `password` = 'Bgf123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18381175360';

-- 徐艺钊 / 13008151661
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '徐艺钊', NULL, '13008151661', 'Xyzsdmn123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13008151661'
);
UPDATE `user_account`
SET `nick_name` = '徐艺钊', `password` = 'Xyzsdmn123', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13008151661';

-- 徐艳萍 / 18380442322
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '徐艳萍', NULL, '18380442322', 'Xyp18380442322', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18380442322'
);
UPDATE `user_account`
SET `nick_name` = '徐艳萍', `password` = 'Xyp18380442322', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18380442322';

-- 阚婷 / 18090462086
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '阚婷', NULL, '18090462086', 'Kk13547685520', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18090462086'
);
UPDATE `user_account`
SET `nick_name` = '阚婷', `password` = 'Kk13547685520', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18090462086';

-- 宋媛媛 / 18228086660
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '宋媛媛', NULL, '18228086660', 'Song1314520@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18228086660'
);
UPDATE `user_account`
SET `nick_name` = '宋媛媛', `password` = 'Song1314520@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18228086660';

-- 刘锦 / 17628410830
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '刘锦', NULL, '17628410830', '001128Aa', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17628410830'
);
UPDATE `user_account`
SET `nick_name` = '刘锦', `password` = '001128Aa', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17628410830';

-- 李成晟 / 13778309069
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李成晟', NULL, '13778309069', 'Lcs291920', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13778309069'
);
UPDATE `user_account`
SET `nick_name` = '李成晟', `password` = 'Lcs291920', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13778309069';

-- 兰阳 / 19140187989
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '兰阳', NULL, '19140187989', 'Ly19140187989', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '19140187989'
);
UPDATE `user_account`
SET `nick_name` = '兰阳', `password` = 'Ly19140187989', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '19140187989';

-- 李霞 / 18383313866
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李霞', NULL, '18383313866', 'LIxia18383313866', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18383313866'
);
UPDATE `user_account`
SET `nick_name` = '李霞', `password` = 'LIxia18383313866', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18383313866';

-- 许玉梅 / 13778876475
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '许玉梅', NULL, '13778876475', 'Szxx@8109', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13778876475'
);
UPDATE `user_account`
SET `nick_name` = '许玉梅', `password` = 'Szxx@8109', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13778876475';

-- 陈素梅 / 13688450750
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈素梅', NULL, '13688450750', 'Csm!245917', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13688450750'
);
UPDATE `user_account`
SET `nick_name` = '陈素梅', `password` = 'Csm!245917', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13688450750';

-- 廖子鑫 / 18328282873
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '廖子鑫', NULL, '18328282873', 'Lzx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18328282873'
);
UPDATE `user_account`
SET `nick_name` = '廖子鑫', `password` = 'Lzx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18328282873';

-- 商鸥 / 18080395300
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '商鸥', NULL, '18080395300', 'Dhxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18080395300'
);
UPDATE `user_account`
SET `nick_name` = '商鸥', `password` = 'Dhxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18080395300';

-- 胡春 / 15378348663
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '胡春', NULL, '15378348663', 'Wl1234567!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15378348663'
);
UPDATE `user_account`
SET `nick_name` = '胡春', `password` = 'Wl1234567!', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15378348663';

-- 王丹 / 18228512137
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '王丹', NULL, '18228512137', '831218Wydlch', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18228512137'
);
UPDATE `user_account`
SET `nick_name` = '王丹', `password` = '831218Wydlch', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18228512137';

-- 辛志明 / 13890314739
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '辛志明', NULL, '13890314739', 'Kb460609', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890314739'
);
UPDATE `user_account`
SET `nick_name` = '辛志明', `password` = 'Kb460609', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890314739';

-- 颜凤飞 / 17381757207
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '颜凤飞', NULL, '17381757207', '1995810Ff', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17381757207'
);
UPDATE `user_account`
SET `nick_name` = '颜凤飞', `password` = '1995810Ff', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17381757207';

-- 黄朝文 / 18080393528
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '黄朝文', NULL, '18080393528', 'Amwyygy1029@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18080393528'
);
UPDATE `user_account`
SET `nick_name` = '黄朝文', `password` = 'Amwyygy1029@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18080393528';

-- 王霞 / 13990396354
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '王霞', NULL, '13990396354', '88Wangxia', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13990396354'
);
UPDATE `user_account`
SET `nick_name` = '王霞', `password` = '88Wangxia', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13990396354';

-- 陈另斌 / 13550519358
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈另斌', NULL, '13550519358', 'Clb13550', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13550519358'
);
UPDATE `user_account`
SET `nick_name` = '陈另斌', `password` = 'Clb13550', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13550519358';

-- 汪雪琴 / 15184434368
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '汪雪琴', NULL, '15184434368', 'Wangxueqin1357', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15184434368'
);
UPDATE `user_account`
SET `nick_name` = '汪雪琴', `password` = 'Wangxueqin1357', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15184434368';

-- 龚秀梅 / 13550500561
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '龚秀梅', NULL, '13550500561', 'Dhxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13550500561'
);
UPDATE `user_account`
SET `nick_name` = '龚秀梅', `password` = 'Dhxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13550500561';

-- 齐小清 / 15082864428
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '齐小清', NULL, '15082864428', 'Dzqxq864428', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15082864428'
);
UPDATE `user_account`
SET `nick_name` = '齐小清', `password` = 'Dzqxq864428', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15082864428';

-- 张丽舒 / 15196486409
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '张丽舒', NULL, '15196486409', 'Hhy13778801922', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15196486409'
);
UPDATE `user_account`
SET `nick_name` = '张丽舒', `password` = 'Hhy13778801922', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15196486409';

-- 蒲艳红 / 13350535011
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '蒲艳红', NULL, '13350535011', 'Houwang88', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13350535011'
);
UPDATE `user_account`
SET `nick_name` = '蒲艳红', `password` = 'Houwang88', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13350535011';

-- 黄晓丽 / 17828896966
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '黄晓丽', NULL, '17828896966', 'Huang178#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17828896966'
);
UPDATE `user_account`
SET `nick_name` = '黄晓丽', `password` = 'Huang178#', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17828896966';

-- 蒲朝波 / 18982820061
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '蒲朝波', NULL, '18982820061', 'Aa18982820061', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18982820061'
);
UPDATE `user_account`
SET `nick_name` = '蒲朝波', `password` = 'Aa18982820061', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18982820061';

-- 赵志刚 / 13540929772
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '赵志刚', NULL, '13540929772', 'Aa13540929772', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13540929772'
);
UPDATE `user_account`
SET `nick_name` = '赵志刚', `password` = 'Aa13540929772', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13540929772';

-- 范笑寒 / 18227896206
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '范笑寒', NULL, '18227896206', 'Aa18227896206', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18227896206'
);
UPDATE `user_account`
SET `nick_name` = '范笑寒', `password` = 'Aa18227896206', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18227896206';

-- 莫铭芝 / 15328610635
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '莫铭芝', NULL, '15328610635', 'Mmz710511', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15328610635'
);
UPDATE `user_account`
SET `nick_name` = '莫铭芝', `password` = 'Mmz710511', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15328610635';

-- 张雪萍 / 13219278026
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '张雪萍', NULL, '13219278026', 'Zxp19930909', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13219278026'
);
UPDATE `user_account`
SET `nick_name` = '张雪萍', `password` = 'Zxp19930909', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13219278026';

-- 杜苑嘉 / 18328423217
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '杜苑嘉', NULL, '18328423217', 'SNxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18328423217'
);
UPDATE `user_account`
SET `nick_name` = '杜苑嘉', `password` = 'SNxx123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18328423217';

-- 吕力 / 13698397595
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '吕力', NULL, '13698397595', '929920Xx', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13698397595'
);
UPDATE `user_account`
SET `nick_name` = '吕力', `password` = '929920Xx', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13698397595';

-- 罗鸿杰 / 18728819437
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '罗鸿杰', NULL, '18728819437', '011014Lhj', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18728819437'
);
UPDATE `user_account`
SET `nick_name` = '罗鸿杰', `password` = '011014Lhj', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18728819437';

-- 谭珏麒 / 18683380745
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '谭珏麒', NULL, '18683380745', 'Tjq5203884', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18683380745'
);
UPDATE `user_account`
SET `nick_name` = '谭珏麒', `password` = 'Tjq5203884', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18683380745';

-- 梁亚丽 / 18784537092
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '梁亚丽', NULL, '18784537092', 'Pyw3559689@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18784537092'
);
UPDATE `user_account`
SET `nick_name` = '梁亚丽', `password` = 'Pyw3559689@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18784537092';

-- 吴冬梅 / 13890622332
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '吴冬梅', NULL, '13890622332', 'Wdm13890622332', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890622332'
);
UPDATE `user_account`
SET `nick_name` = '吴冬梅', `password` = 'Wdm13890622332', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890622332';

-- 彭思 / 18188333484
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '彭思', NULL, '18188333484', 'Ps15196459032', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18188333484'
);
UPDATE `user_account`
SET `nick_name` = '彭思', `password` = 'Ps15196459032', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18188333484';

-- 刘琪 / 18728837186
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '刘琪', NULL, '18728837186', 'Routuoer520@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18728837186'
);
UPDATE `user_account`
SET `nick_name` = '刘琪', `password` = 'Routuoer520@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18728837186';

-- 龚新颜 / 13708135362
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '龚新颜', NULL, '13708135362', 'Aa@13708135362', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13708135362'
);
UPDATE `user_account`
SET `nick_name` = '龚新颜', `password` = 'Aa@13708135362', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13708135362';

-- 杜慧容 / 13890602568
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '杜慧容', NULL, '13890602568', 'Aa13890602568', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890602568'
);
UPDATE `user_account`
SET `nick_name` = '杜慧容', `password` = 'Aa13890602568', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890602568';

-- 许美琼 / 18283385896
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '许美琼', NULL, '18283385896', 'Aa18283385896', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18283385896'
);
UPDATE `user_account`
SET `nick_name` = '许美琼', `password` = 'Aa18283385896', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18283385896';

-- 阳金宏 / 17382983261
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '阳金宏', NULL, '17382983261', 'Yjh123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17382983261'
);
UPDATE `user_account`
SET `nick_name` = '阳金宏', `password` = 'Yjh123456', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17382983261';

-- 许芹 / 18113436418
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '许芹', NULL, '18113436418', 'Xq878632', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18113436418'
);
UPDATE `user_account`
SET `nick_name` = '许芹', `password` = 'Xq878632', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18113436418';

-- 朱思瑶 / 17780897042
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '朱思瑶', NULL, '17780897042', '979920Zsy@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17780897042'
);
UPDATE `user_account`
SET `nick_name` = '朱思瑶', `password` = '979920Zsy@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17780897042';

-- 牟明慧 / 13540906439
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '牟明慧', NULL, '13540906439', 'moumh8687mmhMMJ', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13540906439'
);
UPDATE `user_account`
SET `nick_name` = '牟明慧', `password` = 'moumh8687mmhMMJ', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13540906439';

-- 郑 / 18908134956
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '郑', NULL, '18908134956', 'ZSj1016......', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18908134956'
);
UPDATE `user_account`
SET `nick_name` = '郑', `password` = 'ZSj1016......', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18908134956';

-- 刘 / 18981372707
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '刘', NULL, '18981372707', 'Lcx@mrzx123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18981372707'
);
UPDATE `user_account`
SET `nick_name` = '刘', `password` = 'Lcx@mrzx123', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18981372707';

-- 蔡 / 15082220477
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '蔡', NULL, '15082220477', '@Cainina66', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15082220477'
);
UPDATE `user_account`
SET `nick_name` = '蔡', `password` = '@Cainina66', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15082220477';

-- 李 / 18328675416
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李', NULL, '18328675416', 'Ll08020314', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18328675416'
);
UPDATE `user_account`
SET `nick_name` = '李', `password` = 'Ll08020314', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18328675416';

-- 魏媛媛 / 13881368430
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '魏媛媛', NULL, '13881368430', 'Yy820220@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13881368430'
);
UPDATE `user_account`
SET `nick_name` = '魏媛媛', `password` = 'Yy820220@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13881368430';

-- 梁涛 / 13419414062
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '梁涛', NULL, '13419414062', 'Lt13419414062@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13419414062'
);
UPDATE `user_account`
SET `nick_name` = '梁涛', `password` = 'Lt13419414062@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13419414062';

-- 朱燕 / 18142521691
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '朱燕', NULL, '18142521691', 'Aa18142521691', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18142521691'
);
UPDATE `user_account`
SET `nick_name` = '朱燕', `password` = 'Aa18142521691', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18142521691';

-- 邹雪梅 / 13890609190
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '邹雪梅', NULL, '13890609190', 'Aa13890609190', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890609190'
);
UPDATE `user_account`
SET `nick_name` = '邹雪梅', `password` = 'Aa13890609190', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890609190';

-- 潘慧 / 18781362449
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '潘慧', NULL, '18781362449', 'Ph484520', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18781362449'
);
UPDATE `user_account`
SET `nick_name` = '潘慧', `password` = 'Ph484520', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18781362449';

-- 徐琴 / 13378338766
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '徐琴', NULL, '13378338766', 'Aa13378338766', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13378338766'
);
UPDATE `user_account`
SET `nick_name` = '徐琴', `password` = 'Aa13378338766', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13378338766';

-- 黄海媚 / 13540575982
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '黄海媚', NULL, '13540575982', 'Aa13540575982', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13540575982'
);
UPDATE `user_account`
SET `nick_name` = '黄海媚', `password` = 'Aa13540575982', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13540575982';

-- 钟文胜 / 18080659391
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '钟文胜', NULL, '18080659391', 'Zws024680!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18080659391'
);
UPDATE `user_account`
SET `nick_name` = '钟文胜', `password` = 'Zws024680!', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18080659391';

-- 吴梁平 / 17808052455
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '吴梁平', NULL, '17808052455', 'Wlp5201314', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17808052455'
);
UPDATE `user_account`
SET `nick_name` = '吴梁平', `password` = 'Wlp5201314', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17808052455';

-- 莫小琼 / 13700932900
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '莫小琼', NULL, '13700932900', 'XIAduo060821', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13700932900'
);
UPDATE `user_account`
SET `nick_name` = '莫小琼', `password` = 'XIAduo060821', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13700932900';

-- 杨冬梅 / 13890600869
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '杨冬梅', NULL, '13890600869', 'YANGDONGmei5', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890600869'
);
UPDATE `user_account`
SET `nick_name` = '杨冬梅', `password` = 'YANGDONGmei5', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890600869';

-- 徐叶丹 / 15183386707
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '徐叶丹', NULL, '15183386707', 'Dandan19920713', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15183386707'
);
UPDATE `user_account`
SET `nick_name` = '徐叶丹', `password` = 'Dandan19920713', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15183386707';

-- 邓颖 / 13551681309
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '邓颖', NULL, '13551681309', 'Dy900821!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13551681309'
);
UPDATE `user_account`
SET `nick_name` = '邓颖', `password` = 'Dy900821!', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13551681309';

-- 张富美 / 18228237529
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '张富美', NULL, '18228237529', 'Zm@19961214', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18228237529'
);
UPDATE `user_account`
SET `nick_name` = '张富美', `password` = 'Zm@19961214', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18228237529';

-- 胡宋琴 / 13330936709
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '胡宋琴', NULL, '13330936709', 'Hsq13579@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13330936709'
);
UPDATE `user_account`
SET `nick_name` = '胡宋琴', `password` = 'Hsq13579@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13330936709';

-- 谭弦 / 18909065635
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '谭弦', NULL, '18909065635', 'Aa18909065635', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18909065635'
);
UPDATE `user_account`
SET `nick_name` = '谭弦', `password` = 'Aa18909065635', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18909065635';

-- 李林 / 18398856991
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李林', NULL, '18398856991', 'Lin123456789', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18398856991'
);
UPDATE `user_account`
SET `nick_name` = '李林', `password` = 'Lin123456789', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18398856991';

-- 余思蒙 / 13618180117
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '余思蒙', NULL, '13618180117', 'Yusm19931006', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13618180117'
);
UPDATE `user_account`
SET `nick_name` = '余思蒙', `password` = 'Yusm19931006', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13618180117';

-- 黄竞 / 18990839590
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '黄竞', NULL, '18990839590', 'Aa18990839590', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18990839590'
);
UPDATE `user_account`
SET `nick_name` = '黄竞', `password` = 'Aa18990839590', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18990839590';

-- 秦碧辉 / 13219139990
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '秦碧辉', NULL, '13219139990', 'Aa13219139990', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13219139990'
);
UPDATE `user_account`
SET `nick_name` = '秦碧辉', `password` = 'Aa13219139990', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13219139990';

-- 秦永军 / 17721937817
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '秦永军', NULL, '17721937817', 'Qyj!147258369', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '17721937817'
);
UPDATE `user_account`
SET `nick_name` = '秦永军', `password` = 'Qyj!147258369', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '17721937817';

-- 何林芝 / 15298204132
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '何林芝', NULL, '15298204132', 'HLZqq013020550', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15298204132'
);
UPDATE `user_account`
SET `nick_name` = '何林芝', `password` = 'HLZqq013020550', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15298204132';

-- 李荣娟 / 13198189661
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李荣娟', NULL, '13198189661', 'Aa13198189661', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13198189661'
);
UPDATE `user_account`
SET `nick_name` = '李荣娟', `password` = 'Aa13198189661', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13198189661';

-- 曾晓红 / 15183360859
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '曾晓红', NULL, '15183360859', 'Zeng19980804@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15183360859'
);
UPDATE `user_account`
SET `nick_name` = '曾晓红', `password` = 'Zeng19980804@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15183360859';

-- 苟云宵 / 18224495396
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '苟云宵', NULL, '18224495396', 'Gyx12345678,', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18224495396'
);
UPDATE `user_account`
SET `nick_name` = '苟云宵', `password` = 'Gyx12345678,', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18224495396';

-- 罗雅萌 / 18384602471
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '罗雅萌', NULL, '18384602471', 'Luo1226a', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18384602471'
);
UPDATE `user_account`
SET `nick_name` = '罗雅萌', `password` = 'Luo1226a', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18384602471';

-- 唐川 / 15282284356
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '唐川', NULL, '15282284356', '15282284356Tc@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15282284356'
);
UPDATE `user_account`
SET `nick_name` = '唐川', `password` = '15282284356Tc@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15282284356';

-- 黄元君 / 18283612098
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '黄元君', NULL, '18283612098', 'Hyj710809@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18283612098'
);
UPDATE `user_account`
SET `nick_name` = '黄元君', `password` = 'Hyj710809@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18283612098';

-- 李蕊岑 / 18011676567
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李蕊岑', NULL, '18011676567', 'Aa18011676567', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18011676567'
);
UPDATE `user_account`
SET `nick_name` = '李蕊岑', `password` = 'Aa18011676567', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18011676567';

-- 欧阳李奕 / 18113455653
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '欧阳李奕', NULL, '18113455653', '202024adgA@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18113455653'
);
UPDATE `user_account`
SET `nick_name` = '欧阳李奕', `password` = '202024adgA@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18113455653';

-- 陈坤英 / 13540571571
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈坤英', NULL, '13540571571', 'qwer105607CK', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13540571571'
);
UPDATE `user_account`
SET `nick_name` = '陈坤英', `password` = 'qwer105607CK', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13540571571';

-- (无姓名) / 18584905112
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '18584905112', 'Lx02@5112', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18584905112'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Lx02@5112', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18584905112';

-- (无姓名) / 13990679105
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '', NULL, '13990679105', 'Wyx521314', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13990679105'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Wyx521314', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13990679105';

-- 陈维 / 18381578692
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈维', NULL, '18381578692', 'Cw369147', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18381578692'
);
UPDATE `user_account`
SET `nick_name` = '陈维', `password` = 'Cw369147', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18381578692';

-- 蒋晨悦 / 15181260750
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '蒋晨悦', NULL, '15181260750', 'Jcy15181260750.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15181260750'
);
UPDATE `user_account`
SET `nick_name` = '蒋晨悦', `password` = 'Jcy15181260750.', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15181260750';

-- 魏超艳 / 18328439710
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '魏超艳', NULL, '18328439710', 'Wcy858585.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18328439710'
);
UPDATE `user_account`
SET `nick_name` = '魏超艳', `password` = 'Wcy858585.', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18328439710';

-- 李明静 / 18117922828
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '李明静', NULL, '18117922828', 'Aa@18117922828', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18117922828'
);
UPDATE `user_account`
SET `nick_name` = '李明静', `password` = 'Aa@18117922828', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18117922828';

-- 殷兴均 / 18608231007
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '殷兴均', NULL, '18608231007', 'Aa@18608231007', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18608231007'
);
UPDATE `user_account`
SET `nick_name` = '殷兴均', `password` = 'Aa@18608231007', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18608231007';

-- 杨溢 / 18200383698
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '杨溢', NULL, '18200383698', 'Aa@18200383698', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18200383698'
);
UPDATE `user_account`
SET `nick_name` = '杨溢', `password` = 'Aa@18200383698', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18200383698';

-- 姚刚 / 19983743417
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '姚刚', NULL, '19983743417', 'Aa@19983743417', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '19983743417'
);
UPDATE `user_account`
SET `nick_name` = '姚刚', `password` = 'Aa@19983743417', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '19983743417';

-- 丁慧君 / 18381986575
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '丁慧君', NULL, '18381986575', 'Dhj13579', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18381986575'
);
UPDATE `user_account`
SET `nick_name` = '丁慧君', `password` = 'Dhj13579', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18381986575';

-- 吴春霞 / 13778352833
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '吴春霞', NULL, '13778352833', 'Aa@13778352833', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13778352833'
);
UPDATE `user_account`
SET `nick_name` = '吴春霞', `password` = 'Aa@13778352833', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13778352833';

-- 冯云霞 / 18381848437
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '冯云霞', NULL, '18381848437', 'Aa@18381848437', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18381848437'
);
UPDATE `user_account`
SET `nick_name` = '冯云霞', `password` = 'Aa@18381848437', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18381848437';

-- 杨贞燕 / 15082424089
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '杨贞燕', NULL, '15082424089', 'Aa@15082424089', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '15082424089'
);
UPDATE `user_account`
SET `nick_name` = '杨贞燕', `password` = 'Aa@15082424089', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '15082424089';

-- 陈园 / 18683339086
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '陈园', NULL, '18683339086', '09084067cY@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '18683339086'
);
UPDATE `user_account`
SET `nick_name` = '陈园', `password` = '09084067cY@', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '18683339086';

-- 王杨 / 13890616871
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCZH', '王杨', NULL, '13890616871', 'Wy13890616871', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCZH' AND `username` = '13890616871'
);
UPDATE `user_account`
SET `nick_name` = '王杨', `password` = 'Wy13890616871', `update_time` = NOW()
WHERE `website_code` = 'SCZH' AND `username` = '13890616871';

-- 共 163 个账号（同 username 已按最后一条去重）
