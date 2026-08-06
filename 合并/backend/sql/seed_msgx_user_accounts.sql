-- 眉山公需（MSGX）用户账号导入
-- 可重复执行：已存在同 website_code+username 则更新姓名/密码
--   mysql -u root -p task_manager < backend/sql/seed_msgx_user_accounts.sql

SET NAMES utf8mb4;

-- 周婷 / 513821199508129083
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '周婷', NULL, '513821199508129083', 'Aa@18783363361', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513821199508129083'
);
UPDATE `user_account`
SET `nick_name` = '周婷', `password` = 'Aa@18783363361', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513821199508129083';

-- 吴梁平 / 吴梁平好
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '吴梁平', NULL, '吴梁平好', 'fdrxqw', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '吴梁平好'
);
UPDATE `user_account`
SET `nick_name` = '吴梁平', `password` = 'fdrxqw', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '吴梁平好';

-- (无姓名) / 15928511228
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '', NULL, '15928511228', 'sgdq4g', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '15928511228'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'sgdq4g', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '15928511228';

-- 辛志明 / 511122197501269013
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '辛志明', NULL, '511122197501269013', 'kb123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197501269013'
);
UPDATE `user_account`
SET `nick_name` = '辛志明', `password` = 'kb123456', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197501269013';

-- 商欧 / 51382119880726490X
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '商欧', NULL, '51382119880726490X', 'Dhxx123456!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '51382119880726490X'
);
UPDATE `user_account`
SET `nick_name` = '商欧', `password` = 'Dhxx123456!', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '51382119880726490X';

-- 陈亚林 / 511122197609055754
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '陈亚林', NULL, '511122197609055754', 'qqmm8018', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197609055754'
);
UPDATE `user_account`
SET `nick_name` = '陈亚林', `password` = 'qqmm8018', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197609055754';

-- 颜凤飞 / 颜凤飞1995810
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '颜凤飞', NULL, '颜凤飞1995810', '1995810Ff', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '颜凤飞1995810'
);
UPDATE `user_account`
SET `nick_name` = '颜凤飞', `password` = '1995810Ff', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '颜凤飞1995810';

-- 万娟 / 513822198606114565
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '万娟', NULL, '513822198606114565', 'Aa@13568253671', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513822198606114565'
);
UPDATE `user_account`
SET `nick_name` = '万娟', `password` = 'Aa@13568253671', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513822198606114565';

-- 任忠秀 / 513822198509192465
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '任忠秀', NULL, '513822198509192465', 'Aa@13795509554', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513822198509192465'
);
UPDATE `user_account`
SET `nick_name` = '任忠秀', `password` = 'Aa@13795509554', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513822198509192465';

-- 肖燕 / 510182198501014627
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '肖燕', NULL, '510182198501014627', 'Aa@13378354796', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '510182198501014627'
);
UPDATE `user_account`
SET `nick_name` = '肖燕', `password` = 'Aa@13378354796', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '510182198501014627';

-- 李莉英 / 511122196711155167
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '李莉英', NULL, '511122196711155167', 'Aa@13890387859', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122196711155167'
);
UPDATE `user_account`
SET `nick_name` = '李莉英', `password` = 'Aa@13890387859', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122196711155167';

-- 王群 / 511122197802165162
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '王群', NULL, '511122197802165162', 'Aa@13778826032', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197802165162'
);
UPDATE `user_account`
SET `nick_name` = '王群', `password` = 'Aa@13778826032', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197802165162';

-- 陈菊红 / 511121197209144321
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '陈菊红', NULL, '511121197209144321', 'Aa@18980369616', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511121197209144321'
);
UPDATE `user_account`
SET `nick_name` = '陈菊红', `password` = 'Aa@18980369616', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511121197209144321';

-- 张琪君 / 513821198412031271
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '张琪君', NULL, '513821198412031271', 'Aa@18384708567', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513821198412031271'
);
UPDATE `user_account`
SET `nick_name` = '张琪君', `password` = 'Aa@18384708567', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513821198412031271';

-- 韩秀兰 / 511025198509091609
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '韩秀兰', NULL, '511025198509091609', 'fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511025198509091609'
);
UPDATE `user_account`
SET `nick_name` = '韩秀兰', `password` = 'fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511025198509091609';

-- 张丝怡 / 18215604763
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '张丝怡', NULL, '18215604763', 'Aa@18215604763', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '18215604763'
);
UPDATE `user_account`
SET `nick_name` = '张丝怡', `password` = 'Aa@18215604763', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '18215604763';

-- 龚燕茹 / 511121199211074560
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '龚燕茹', NULL, '511121199211074560', 'Aa@15282324126', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511121199211074560'
);
UPDATE `user_account`
SET `nick_name` = '龚燕茹', `password` = 'Aa@15282324126', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511121199211074560';

-- 杨娟 / 511122197311195164
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '杨娟', NULL, '511122197311195164', 'yj123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197311195164'
);
UPDATE `user_account`
SET `nick_name` = '杨娟', `password` = 'yj123456', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197311195164';

-- 李智 / 511122197706259046
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '李智', NULL, '511122197706259046', '5y5n38', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197706259046'
);
UPDATE `user_account`
SET `nick_name` = '李智', `password` = '5y5n38', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197706259046';

-- 唐光强 / 511121197402080016
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '唐光强', NULL, '511121197402080016', 'Aa@13990355642', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511121197402080016'
);
UPDATE `user_account`
SET `nick_name` = '唐光强', `password` = 'Aa@13990355642', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511121197402080016';

-- 万前山 / 51112219690306901x
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '万前山', NULL, '51112219690306901x', 'Aa@13696082636', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '51112219690306901x'
);
UPDATE `user_account`
SET `nick_name` = '万前山', `password` = 'Aa@13696082636', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '51112219690306901x';

-- 悦琼英 / 511129199111133026
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '悦琼英', NULL, '511129199111133026', 'Aa@18381457998', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511129199111133026'
);
UPDATE `user_account`
SET `nick_name` = '悦琼英', `password` = 'Aa@18381457998', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511129199111133026';

-- 陈素梅 / 513723198609223127
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '陈素梅', NULL, '513723198609223127', 'csm!245917', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513723198609223127'
);
UPDATE `user_account`
SET `nick_name` = '陈素梅', `password` = 'csm!245917', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513723198609223127';

-- 杨世超 / 511122197806265179
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '杨世超', NULL, '511122197806265179', 'fnxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197806265179'
);
UPDATE `user_account`
SET `nick_name` = '杨世超', `password` = 'fnxx123456', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197806265179';

-- 徐杰 / 513821198812147652
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '徐杰', NULL, '513821198812147652', 'xujie9661089', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513821198812147652'
);
UPDATE `user_account`
SET `nick_name` = '徐杰', `password` = 'xujie9661089', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513821198812147652';

-- 王镒 / 513821198809196920
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '王镒', NULL, '513821198809196920', 'Aa@18728325705', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513821198809196920'
);
UPDATE `user_account`
SET `nick_name` = '王镒', `password` = 'Aa@18728325705', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513821198809196920';

-- 杨丽 / 513822198510307645
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '杨丽', NULL, '513822198510307645', 'Aa@15884341518', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513822198510307645'
);
UPDATE `user_account`
SET `nick_name` = '杨丽', `password` = 'Aa@15884341518', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513822198510307645';

-- 何静 / 513824198409070922
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '何静', NULL, '513824198409070922', 'Aa@13778802507', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '513824198409070922'
);
UPDATE `user_account`
SET `nick_name` = '何静', `password` = 'Aa@13778802507', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '513824198409070922';

-- 汤志勇 / 511122197312205272
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '汤志勇', NULL, '511122197312205272', 'Aa@13990328300', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197312205272'
);
UPDATE `user_account`
SET `nick_name` = '汤志勇', `password` = 'Aa@13990328300', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197312205272';

-- 陶祥 / 511122196702164133
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '陶祥', NULL, '511122196702164133', 'Aa@18090465575', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122196702164133'
);
UPDATE `user_account`
SET `nick_name` = '陶祥', `password` = 'Aa@18090465575', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122196702164133';

-- 陈亚林 / 511122197809309069
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '陈亚林', NULL, '511122197809309069', 'qqmm8018', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197809309069'
);
UPDATE `user_account`
SET `nick_name` = '陈亚林', `password` = 'qqmm8018', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197809309069';

-- 刘欣 / DHXXLX
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '刘欣', NULL, 'DHXXLX', '19971129Lx@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = 'DHXXLX'
);
UPDATE `user_account`
SET `nick_name` = '刘欣', `password` = '19971129Lx@', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = 'DHXXLX';

-- 黄朝文 / 511122197912189018
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '黄朝文', NULL, '511122197912189018', 'Amwyygy1029', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197912189018'
);
UPDATE `user_account`
SET `nick_name` = '黄朝文', `password` = 'Amwyygy1029', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197912189018';

-- 王丹 / 21ms00173813
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '王丹', NULL, '21ms00173813', '4jtq8x', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '21ms00173813'
);
UPDATE `user_account`
SET `nick_name` = '王丹', `password` = '4jtq8x', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '21ms00173813';

-- 胡春 / 胡15378348663
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '胡春', NULL, '胡15378348663', 'hc15378348663', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '胡15378348663'
);
UPDATE `user_account`
SET `nick_name` = '胡春', `password` = 'hc15378348663', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '胡15378348663';

-- 陈另斌 / 511122197912263361
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '陈另斌', NULL, '511122197912263361', 'Clb13550', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197912263361'
);
UPDATE `user_account`
SET `nick_name` = '陈另斌', `password` = 'Clb13550', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197912263361';

-- 黄泽勤 / 511122197908285314
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '黄泽勤', NULL, '511122197908285314', 'hzq18990325678', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122197908285314'
);
UPDATE `user_account`
SET `nick_name` = '黄泽勤', `password` = 'hzq18990325678', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122197908285314';

-- 张丽舒 / zls7528
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '张丽舒', NULL, 'zls7528', 'HHY13778801922', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = 'zls7528'
);
UPDATE `user_account`
SET `nick_name` = '张丽舒', `password` = 'HHY13778801922', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = 'zls7528';

-- 白汝成 / 511122196701185151
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '白汝成', NULL, '511122196701185151', 'brc196718', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '511122196701185151'
);
UPDATE `user_account`
SET `nick_name` = '白汝成', `password` = 'brc196718', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '511122196701185151';

-- 龚秀梅 / 51112219720609904X
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '龚秀梅', NULL, '51112219720609904X', 'Dhxx123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '51112219720609904X'
);
UPDATE `user_account`
SET `nick_name` = '龚秀梅', `password` = 'Dhxx123456', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '51112219720609904X';

-- 汪雪琴 / haohao234
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '汪雪琴', NULL, 'haohao234', '%meimei234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = 'haohao234'
);
UPDATE `user_account`
SET `nick_name` = '汪雪琴', `password` = '%meimei234', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = 'haohao234';

-- 刘洁静 / 谁丢了尾巴
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '刘洁静', NULL, '谁丢了尾巴', '20220707a', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '谁丢了尾巴'
);
UPDATE `user_account`
SET `nick_name` = '刘洁静', `password` = '20220707a', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '谁丢了尾巴';

-- 王璐瑶 / 18228557481
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'MSGX', '王璐瑶', NULL, '18228557481', 'sc123456*', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'MSGX' AND `username` = '18228557481'
);
UPDATE `user_account`
SET `nick_name` = '王璐瑶', `password` = 'sc123456*', `update_time` = NOW()
WHERE `website_code` = 'MSGX' AND `username` = '18228557481';

-- 共 43 个账号（同 username 已按最后一条去重）
