-- 国家智慧中小学（ZXZH）用户账号导入
-- 可重复执行：已存在同 website_code+username 则更新姓名/密码
--   mysql -u root -p task_manager < backend/sql/seed_zxzh_user_accounts.sql

SET NAMES utf8mb4;

-- 龚秀梅 / 13550500561
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '龚秀梅', NULL, '13550500561', 'Gxm147258', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13550500561'
);
UPDATE `user_account`
SET `nick_name` = '龚秀梅', `password` = 'Gxm147258', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13550500561';

-- 商欧 / 18080395300
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '商欧', NULL, '18080395300', 'Dhxx147258', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '18080395300'
);
UPDATE `user_account`
SET `nick_name` = '商欧', `password` = 'Dhxx147258', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '18080395300';

-- 辛志明 / 13890314739
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '辛志明', NULL, '13890314739', 'Kb850609', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13890314739'
);
UPDATE `user_account`
SET `nick_name` = '辛志明', `password` = 'Kb850609', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13890314739';

-- 张丽舒 / 15196486409
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '张丽舒', NULL, '15196486409', 'Hhy13778801922', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '15196486409'
);
UPDATE `user_account`
SET `nick_name` = '张丽舒', `password` = 'Hhy13778801922', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '15196486409';

-- 朱华英 / 18382174077
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '朱华英', NULL, '18382174077', 'Zhying0521', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '18382174077'
);
UPDATE `user_account`
SET `nick_name` = '朱华英', `password` = 'Zhying0521', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '18382174077';

-- 胡春 / 15378348663  （全角叹号！）
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '胡春', NULL, '15378348663', 'Hc860830！', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '15378348663'
);
UPDATE `user_account`
SET `nick_name` = '胡春', `password` = 'Hc860830！', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '15378348663';

-- 颜凤飞 / 17381757207
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '颜凤飞', NULL, '17381757207', '1995810Ff', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '17381757207'
);
UPDATE `user_account`
SET `nick_name` = '颜凤飞', `password` = '1995810Ff', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '17381757207';

-- 陈另斌 / 13550519358  （全角叹号！）
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '陈另斌', NULL, '13550519358', 'Clb13550！', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13550519358'
);
UPDATE `user_account`
SET `nick_name` = '陈另斌', `password` = 'Clb13550！', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13550519358';

-- 刘欣 / 15775960726
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '刘欣', NULL, '15775960726', '19971129Lx@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '15775960726'
);
UPDATE `user_account`
SET `nick_name` = '刘欣', `password` = '19971129Lx@', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '15775960726';

-- 曾艳 / 13618045535
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '曾艳', NULL, '13618045535', 'nizainali12.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13618045535'
);
UPDATE `user_account`
SET `nick_name` = '曾艳', `password` = 'nizainali12.', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13618045535';

-- 乐淑婷 / 13547919803
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '乐淑婷', NULL, '13547919803', 'Yst070809#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13547919803'
);
UPDATE `user_account`
SET `nick_name` = '乐淑婷', `password` = 'Yst070809#', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13547919803';

-- 汪雪琴 / 15184434368
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '汪雪琴', NULL, '15184434368', 'Wangxueqin135', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '15184434368'
);
UPDATE `user_account`
SET `nick_name` = '汪雪琴', `password` = 'Wangxueqin135', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '15184434368';

-- 陈怡芩 / 18683495167
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '陈怡芩', NULL, '18683495167', 'Cyq18683495167', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '18683495167'
);
UPDATE `user_account`
SET `nick_name` = '陈怡芩', `password` = 'Cyq18683495167', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '18683495167';

-- 杨敏 / 13678212435
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '杨敏', NULL, '13678212435', 'yousmile00', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13678212435'
);
UPDATE `user_account`
SET `nick_name` = '杨敏', `password` = 'yousmile00', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13678212435';

-- 蒲艳红 / 13350535011
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '蒲艳红', NULL, '13350535011', 'Pyh13350535011', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13350535011'
);
UPDATE `user_account`
SET `nick_name` = '蒲艳红', `password` = 'Pyh13350535011', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13350535011';

-- 张磊 / 13708163960
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '张磊', NULL, '13708163960', 'Zl13708163960', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13708163960'
);
UPDATE `user_account`
SET `nick_name` = '张磊', `password` = 'Zl13708163960', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13708163960';

-- 徐思源 / 13679644177
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '徐思源', NULL, '13679644177', 'Xsy@147258369', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13679644177'
);
UPDATE `user_account`
SET `nick_name` = '徐思源', `password` = 'Xsy@147258369', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13679644177';

-- 彭露 / 13778887730
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '彭露', NULL, '13778887730', 'penglu666', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13778887730'
);
UPDATE `user_account`
SET `nick_name` = '彭露', `password` = 'penglu666', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13778887730';

-- 刘丽英 / 13980370361
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '刘丽英', NULL, '13980370361', 'Qtxx821209', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13980370361'
);
UPDATE `user_account`
SET `nick_name` = '刘丽英', `password` = 'Qtxx821209', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13980370361';

-- 杨皓月 / 18228194942
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '杨皓月', NULL, '18228194942', 'YHYinfinite328', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '18228194942'
);
UPDATE `user_account`
SET `nick_name` = '杨皓月', `password` = 'YHYinfinite328', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '18228194942';

-- 吴俊熹 / 13608184845
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '吴俊熹', NULL, '13608184845', 'Wjx19702@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13608184845'
);
UPDATE `user_account`
SET `nick_name` = '吴俊熹', `password` = 'Wjx19702@', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13608184845';

-- 陈恬妮 / 13890679772
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '陈恬妮', NULL, '13890679772', 'aptx4869/', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13890679772'
);
UPDATE `user_account`
SET `nick_name` = '陈恬妮', `password` = 'aptx4869/', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13890679772';

-- lzx / 18328282873
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', 'lzx', NULL, '18328282873', 'Lzx18328282873!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '18328282873'
);
UPDATE `user_account`
SET `nick_name` = 'lzx', `password` = 'Lzx18328282873!', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '18328282873';

-- (无姓名) / 18608058726
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '', NULL, '18608058726', '1063032335gjm', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '18608058726'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = '1063032335gjm', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '18608058726';

-- 李彩玉 / 18328193982
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '李彩玉', NULL, '18328193982', 'Aa135246', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '18328193982'
);
UPDATE `user_account`
SET `nick_name` = '李彩玉', `password` = 'Aa135246', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '18328193982';

-- (无姓名) / 17808052455
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '', NULL, '17808052455', 'cC@17808052455', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '17808052455'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'cC@17808052455', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '17808052455';

-- (无姓名) / 13795713134
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '', NULL, '13795713134', 'Wo3235812', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13795713134'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'Wo3235812', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13795713134';

-- (无姓名) / 13540571571
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'ZXZH', '', NULL, '13540571571', 'cky105607CKY', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'ZXZH' AND `username` = '13540571571'
);
UPDATE `user_account`
SET `nick_name` = '', `password` = 'cky105607CKY', `update_time` = NOW()
WHERE `website_code` = 'ZXZH' AND `username` = '13540571571';

-- 共 28 个账号
