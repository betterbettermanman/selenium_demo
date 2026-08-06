-- 四川干部（SCGB）用户账号导入
-- 格式：姓名 / 单位 / 账号 / 密码；可重复执行
--   mysql -u root -p task_manager < backend/sql/seed_scgb_user_accounts.sql

SET NAMES utf8mb4;

-- 徐杰 / 富牛小学 / 18080398918
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '徐杰', '富牛小学', '18080398918', 'xujie9661089*', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080398918'
);
UPDATE `user_account`
SET `nick_name` = '徐杰', `organ_name` = '富牛小学', `password` = 'xujie9661089*', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080398918';

-- 周婷 / 富牛小学 / 18783363361
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '周婷', '富牛小学', '18783363361', 'ZTzt1219089650@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18783363361'
);
UPDATE `user_account`
SET `nick_name` = '周婷', `organ_name` = '富牛小学', `password` = 'ZTzt1219089650@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18783363361';

-- 陈欣 / 富牛小学 / 13778832903
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈欣', '富牛小学', '13778832903', 'Chen0712@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13778832903'
);
UPDATE `user_account`
SET `nick_name` = '陈欣', `organ_name` = '富牛小学', `password` = 'Chen0712@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13778832903';

-- 韩秀兰 / 富牛小学 / 15182249409
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '韩秀兰', '富牛小学', '15182249409', 'Abcd1234@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15182249409'
);
UPDATE `user_account`
SET `nick_name` = '韩秀兰', `organ_name` = '富牛小学', `password` = 'Abcd1234@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15182249409';

-- 杨小兰 / 富牛小学 / 15328784913
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨小兰', '富牛小学', '15328784913', 'Abcd1234@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15328784913'
);
UPDATE `user_account`
SET `nick_name` = '杨小兰', `organ_name` = '富牛小学', `password` = 'Abcd1234@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15328784913';

-- 徐思源 / - / 13679644177
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '徐思源', NULL, '13679644177', 'Abcd1234@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13679644177'
);
UPDATE `user_account`
SET `nick_name` = '徐思源', `organ_name` = NULL, `password` = 'Abcd1234@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13679644177';

-- 徐艳萍 / - / 18380442322
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '徐艳萍', NULL, '18380442322', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18380442322'
);
UPDATE `user_account`
SET `nick_name` = '徐艳萍', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18380442322';

-- 曾艳 / - / 13618045535
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曾艳', NULL, '13618045535', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13618045535'
);
UPDATE `user_account`
SET `nick_name` = '曾艳', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13618045535';

-- 商鸥 / 东湖小学 / 18080395300
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '商鸥', '东湖小学', '18080395300', 'Aa@18080395300', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080395300'
);
UPDATE `user_account`
SET `nick_name` = '商鸥', `organ_name` = '东湖小学', `password` = 'Aa@18080395300', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080395300';

-- 朱华英 / - / 18382174077
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '朱华英', NULL, '18382174077', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18382174077'
);
UPDATE `user_account`
SET `nick_name` = '朱华英', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18382174077';

-- 张晓敏 / - / 13350705408
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张晓敏', NULL, '13350705408', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13350705408'
);
UPDATE `user_account`
SET `nick_name` = '张晓敏', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13350705408';

-- 胡春 / - / 15378348663
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡春', NULL, '15378348663', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15378348663'
);
UPDATE `user_account`
SET `nick_name` = '胡春', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15378348663';

-- 龚秀梅 / - / 13550500561
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '龚秀梅', NULL, '13550500561', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13550500561'
);
UPDATE `user_account`
SET `nick_name` = '龚秀梅', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13550500561';

-- 辛志明 / - / 13890314739
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '辛志明', NULL, '13890314739', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890314739'
);
UPDATE `user_account`
SET `nick_name` = '辛志明', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890314739';

-- 颜凤飞 / - / 17381757207
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '颜凤飞', NULL, '17381757207', '1995810Ff!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17381757207'
);
UPDATE `user_account`
SET `nick_name` = '颜凤飞', `organ_name` = NULL, `password` = '1995810Ff!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17381757207';

-- 陈另斌 / - / 13550519358
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈另斌', NULL, '13550519358', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13550519358'
);
UPDATE `user_account`
SET `nick_name` = '陈另斌', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13550519358';

-- 刘欣 / - / 15775960726
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘欣', NULL, '15775960726', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15775960726'
);
UPDATE `user_account`
SET `nick_name` = '刘欣', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15775960726';

-- 刘艳 / - / 18080674661
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘艳', NULL, '18080674661', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080674661'
);
UPDATE `user_account`
SET `nick_name` = '刘艳', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080674661';

-- 王丽华 / - / 15183330971
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王丽华', NULL, '15183330971', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15183330971'
);
UPDATE `user_account`
SET `nick_name` = '王丽华', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15183330971';

-- 鲍艮方 / - / 18381175360
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '鲍艮方', NULL, '18381175360', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381175360'
);
UPDATE `user_account`
SET `nick_name` = '鲍艮方', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381175360';

-- 罗远依 / - / 15983341377
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '罗远依', NULL, '15983341377', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15983341377'
);
UPDATE `user_account`
SET `nick_name` = '罗远依', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15983341377';

-- 汪雪琴 / - / 15184434368
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '汪雪琴', NULL, '15184434368', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15184434368'
);
UPDATE `user_account`
SET `nick_name` = '汪雪琴', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15184434368';

-- 张丽舒 / - / 13510517528
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张丽舒', NULL, '13510517528', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13510517528'
);
UPDATE `user_account`
SET `nick_name` = '张丽舒', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13510517528';

-- 乐淑婷 / - / 13547919803
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '乐淑婷', NULL, '13547919803', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13547919803'
);
UPDATE `user_account`
SET `nick_name` = '乐淑婷', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13547919803';

-- 陈怡芩 / - / 18683495167
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈怡芩', NULL, '18683495167', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18683495167'
);
UPDATE `user_account`
SET `nick_name` = '陈怡芩', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18683495167';

-- 左艳 / - / 13890240229
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '左艳', NULL, '13890240229', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890240229'
);
UPDATE `user_account`
SET `nick_name` = '左艳', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890240229';

-- 万秋利 / - / 18161488325
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '万秋利', NULL, '18161488325', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18161488325'
);
UPDATE `user_account`
SET `nick_name` = '万秋利', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18161488325';

-- 李青雪 / - / 13778880898
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李青雪', NULL, '13778880898', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13778880898'
);
UPDATE `user_account`
SET `nick_name` = '李青雪', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13778880898';

-- 杨敏 / - / 13678212435
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨敏', NULL, '13678212435', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13678212435'
);
UPDATE `user_account`
SET `nick_name` = '杨敏', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13678212435';

-- 蒲艳红 / - / 13350535011
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '蒲艳红', NULL, '13350535011', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13350535011'
);
UPDATE `user_account`
SET `nick_name` = '蒲艳红', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13350535011';

-- 张磊 / - / 13708163960
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张磊', NULL, '13708163960', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13708163960'
);
UPDATE `user_account`
SET `nick_name` = '张磊', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13708163960';

-- 杨镜榕 / - / 15700368576
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨镜榕', NULL, '15700368576', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15700368576'
);
UPDATE `user_account`
SET `nick_name` = '杨镜榕', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15700368576';

-- 杨皓月 / - / 18228194942
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨皓月', NULL, '18228194942', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18228194942'
);
UPDATE `user_account`
SET `nick_name` = '杨皓月', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18228194942';

-- 吴俊熹 / - / 13608184845
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴俊熹', NULL, '13608184845', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13608184845'
);
UPDATE `user_account`
SET `nick_name` = '吴俊熹', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13608184845';

-- 陈恬妮 / - / 13890679772
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈恬妮', NULL, '13890679772', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890679772'
);
UPDATE `user_account`
SET `nick_name` = '陈恬妮', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890679772';

-- 徐华 / - / 13350865368
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '徐华', NULL, '13350865368', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13350865368'
);
UPDATE `user_account`
SET `nick_name` = '徐华', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13350865368';

-- 彭露 / - / 13778887730
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '彭露', NULL, '13778887730', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13778887730'
);
UPDATE `user_account`
SET `nick_name` = '彭露', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13778887730';

-- 刘丽英 / - / 13980370361
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘丽英', NULL, '13980370361', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13980370361'
);
UPDATE `user_account`
SET `nick_name` = '刘丽英', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13980370361';

-- 韩晓莉 / - / 18383359880
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '韩晓莉', NULL, '18383359880', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18383359880'
);
UPDATE `user_account`
SET `nick_name` = '韩晓莉', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18383359880';

-- 张富美 / 安居区教育局 / 18228237529
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张富美', '安居区教育局', '18228237529', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18228237529'
);
UPDATE `user_account`
SET `nick_name` = '张富美', `organ_name` = '安居区教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18228237529';

-- 杨乐潇 / 安居区教育局 / 18283028464
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨乐潇', '安居区教育局', '18283028464', 'yyx@520123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18283028464'
);
UPDATE `user_account`
SET `nick_name` = '杨乐潇', `organ_name` = '安居区教育局', `password` = 'yyx@520123', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18283028464';

-- 谭弦 / 安居区教育局 / 18909065635
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '谭弦', '安居区教育局', '18909065635', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18909065635'
);
UPDATE `user_account`
SET `nick_name` = '谭弦', `organ_name` = '安居区教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18909065635';

-- 张丽萍 / 安居区教育局 / 15775359007
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张丽萍', '安居区教育局', '15775359007', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15775359007'
);
UPDATE `user_account`
SET `nick_name` = '张丽萍', `organ_name` = '安居区教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15775359007';

-- 李欢 / 安居区教育局 / 17723550543
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李欢', '安居区教育局', '17723550543', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17723550543'
);
UPDATE `user_account`
SET `nick_name` = '李欢', `organ_name` = '安居区教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17723550543';

-- 肖冬梅 / 安居区教育局 / 13795870458
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '肖冬梅', '安居区教育局', '13795870458', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13795870458'
);
UPDATE `user_account`
SET `nick_name` = '肖冬梅', `organ_name` = '安居区教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13795870458';

-- 唐俊荣 / 金甲小学 / 13518288330
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '唐俊荣', '金甲小学', '13518288330', 'tjr039299@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13518288330'
);
UPDATE `user_account`
SET `nick_name` = '唐俊荣', `organ_name` = '金甲小学', `password` = 'tjr039299@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13518288330';

-- 廖秀珍 / 大北街小学 / 15283778913
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '廖秀珍', '大北街小学', '15283778913', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15283778913'
);
UPDATE `user_account`
SET `nick_name` = '廖秀珍', `organ_name` = '大北街小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15283778913';

-- 冯建 / 遂宁市河东新区教育系统 / 19911862086
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '冯建', '遂宁市河东新区教育系统', '19911862086', '622622waa#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19911862086'
);
UPDATE `user_account`
SET `nick_name` = '冯建', `organ_name` = '遂宁市河东新区教育系统', `password` = '622622waa#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19911862086';

-- 邓蝶 / 遂宁经开区教育卫生行业党委 / 13320633360
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓蝶', '遂宁经开区教育卫生行业党委', '13320633360', 'deng147@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13320633360'
);
UPDATE `user_account`
SET `nick_name` = '邓蝶', `organ_name` = '遂宁经开区教育卫生行业党委', `password` = 'deng147@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13320633360';

-- 文艳红 / 苏辙小学 / 18628998777
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '文艳红', '苏辙小学', '18628998777', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18628998777'
);
UPDATE `user_account`
SET `nick_name` = '文艳红', `organ_name` = '苏辙小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18628998777';

-- 陈燕慧 / 苏辙小学 / 18228512993
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈燕慧', '苏辙小学', '18228512993', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18228512993'
);
UPDATE `user_account`
SET `nick_name` = '陈燕慧', `organ_name` = '苏辙小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18228512993';

-- 李彩玉 / 远景小学 / 18328193982
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李彩玉', '远景小学', '18328193982', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18328193982'
);
UPDATE `user_account`
SET `nick_name` = '李彩玉', `organ_name` = '远景小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18328193982';

-- 魏郑雪 / 齐通小学 / 15108448986
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '魏郑雪', '齐通小学', '15108448986', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15108448986'
);
UPDATE `user_account`
SET `nick_name` = '魏郑雪', `organ_name` = '齐通小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15108448986';

-- 徐雅婷 / 大北街小学 / 18180033317
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '徐雅婷', '大北街小学', '18180033317', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18180033317'
);
UPDATE `user_account`
SET `nick_name` = '徐雅婷', `organ_name` = '大北街小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18180033317';

-- 赵丽丽 / 齐通小学 / 18016198151
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赵丽丽', '齐通小学', '18016198151', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18016198151'
);
UPDATE `user_account`
SET `nick_name` = '赵丽丽', `organ_name` = '齐通小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18016198151';

-- 刘佳鑫 / 齐通小学 / 18783399953
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘佳鑫', '齐通小学', '18783399953', 'Liujiaxin@7', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18783399953'
);
UPDATE `user_account`
SET `nick_name` = '刘佳鑫', `organ_name` = '齐通小学', `password` = 'Liujiaxin@7', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18783399953';

-- 李丹丹 / 齐通小学 / 18011521369
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李丹丹', '齐通小学', '18011521369', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18011521369'
);
UPDATE `user_account`
SET `nick_name` = '李丹丹', `organ_name` = '齐通小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18011521369';

-- 杜苑嘉 / 苏南小学 / 18328423217
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杜苑嘉', '苏南小学', '18328423217', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18328423217'
);
UPDATE `user_account`
SET `nick_name` = '杜苑嘉', `organ_name` = '苏南小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18328423217';

-- 刘静 / 实验小学 / 17798250434
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘静', '实验小学', '17798250434', '1998919Lj@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17798250434'
);
UPDATE `user_account`
SET `nick_name` = '刘静', `organ_name` = '实验小学', `password` = '1998919Lj@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17798250434';

-- 邓冬梅 / 远景小学 / 18383367196
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓冬梅', '远景小学', '18383367196', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18383367196'
);
UPDATE `user_account`
SET `nick_name` = '邓冬梅', `organ_name` = '远景小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18383367196';

-- 曲慧芳 / 夹江县吴场镇中心小学校 / 18383324570
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曲慧芳', '夹江县吴场镇中心小学校', '18383324570', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18383324570'
);
UPDATE `user_account`
SET `nick_name` = '曲慧芳', `organ_name` = '夹江县吴场镇中心小学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18383324570';

-- 朱芳琼 / 大英县委组织部 / 17711410250
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '朱芳琼', '大英县委组织部', '17711410250', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17711410250'
);
UPDATE `user_account`
SET `nick_name` = '朱芳琼', `organ_name` = '大英县委组织部', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17711410250';

-- 方利 / 安居区教育局 / 19911899337
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '方利', '安居区教育局', '19911899337', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19911899337'
);
UPDATE `user_account`
SET `nick_name` = '方利', `organ_name` = '安居区教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19911899337';

-- 肖曼 / 遂宁市河东新区教育系统 / 18200547108
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '肖曼', '遂宁市河东新区教育系统', '18200547108', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18200547108'
);
UPDATE `user_account`
SET `nick_name` = '肖曼', `organ_name` = '遂宁市河东新区教育系统', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18200547108';

-- 杨舒晴 / 罗家小学 / 17780171194
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨舒晴', '罗家小学', '17780171194', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17780171194'
);
UPDATE `user_account`
SET `nick_name` = '杨舒晴', `organ_name` = '罗家小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17780171194';

-- 邹雪 / 市公安局 / 13699688282
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邹雪', '市公安局', '13699688282', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13699688282'
);
UPDATE `user_account`
SET `nick_name` = '邹雪', `organ_name` = '市公安局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13699688282';

-- 侯丽红 / 大北街小学 / 13518402622
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '侯丽红', '大北街小学', '13518402622', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13518402622'
);
UPDATE `user_account`
SET `nick_name` = '侯丽红', `organ_name` = '大北街小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13518402622';

-- 文涵 / 市公安局 / 15182930808
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '文涵', '市公安局', '15182930808', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15182930808'
);
UPDATE `user_account`
SET `nick_name` = '文涵', `organ_name` = '市公安局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15182930808';

-- 毛浩 / 市公安局 / 13508007179
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '毛浩', '市公安局', '13508007179', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13508007179'
);
UPDATE `user_account`
SET `nick_name` = '毛浩', `organ_name` = '市公安局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13508007179';

-- 李昆 / 市公安局 / 13890755577
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李昆', '市公安局', '13890755577', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890755577'
);
UPDATE `user_account`
SET `nick_name` = '李昆', `organ_name` = '市公安局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890755577';

-- 彭思 / 乐山市沙湾区葫芦镇中心小学校 / 18188333484
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '彭思', '乐山市沙湾区葫芦镇中心小学校', '18188333484', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18188333484'
);
UPDATE `user_account`
SET `nick_name` = '彭思', `organ_name` = '乐山市沙湾区葫芦镇中心小学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18188333484';

-- 吴冬梅 / 乐山市沙湾区葫芦镇中心小学校 / 13890622332
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴冬梅', '乐山市沙湾区葫芦镇中心小学校', '13890622332', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890622332'
);
UPDATE `user_account`
SET `nick_name` = '吴冬梅', `organ_name` = '乐山市沙湾区葫芦镇中心小学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890622332';

-- 陈坤英 / 乐山市沙湾区福禄镇初级中学 / 18080659385
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈坤英', '乐山市沙湾区福禄镇初级中学', '18080659385', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080659385'
);
UPDATE `user_account`
SET `nick_name` = '陈坤英', `organ_name` = '乐山市沙湾区福禄镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080659385';

-- 范晓文 / 夹江县第二中学校 / 18080602367
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '范晓文', '夹江县第二中学校', '18080602367', 'Abcd1234@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080602367'
);
UPDATE `user_account`
SET `nick_name` = '范晓文', `organ_name` = '夹江县第二中学校', `password` = 'Abcd1234@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080602367';

-- 陈朝辉 / 夹江县吴场镇初级中学 / 13981366603
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈朝辉', '夹江县吴场镇初级中学', '13981366603', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13981366603'
);
UPDATE `user_account`
SET `nick_name` = '陈朝辉', `organ_name` = '夹江县吴场镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13981366603';

-- 肖利芬 / 夹江县吴场镇初级中学 / 18080602366
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '肖利芬', '夹江县吴场镇初级中学', '18080602366', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080602366'
);
UPDATE `user_account`
SET `nick_name` = '肖利芬', `organ_name` = '夹江县吴场镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080602366';

-- 胡敬 / 夹江县吴场镇中心小学校 / 17360326775
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡敬', '夹江县吴场镇中心小学校', '17360326775', 'Hujing19990616@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17360326775'
);
UPDATE `user_account`
SET `nick_name` = '胡敬', `organ_name` = '夹江县吴场镇中心小学校', `password` = 'Hujing19990616@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17360326775';

-- 李嘉欣 / 夹江县吴场镇中心小学校 / 17360638636
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李嘉欣', '夹江县吴场镇中心小学校', '17360638636', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17360638636'
);
UPDATE `user_account`
SET `nick_name` = '李嘉欣', `organ_name` = '夹江县吴场镇中心小学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17360638636';

-- 曾素萍 / - / 13882548146
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曾素萍', NULL, '13882548146', 'SNzsp2849090@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13882548146'
);
UPDATE `user_account`
SET `nick_name` = '曾素萍', `organ_name` = NULL, `password` = 'SNzsp2849090@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13882548146';

-- 唐晶 / - / 18281957963
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '唐晶', NULL, '18281957963', 'Aa@18281957963', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18281957963'
);
UPDATE `user_account`
SET `nick_name` = '唐晶', `organ_name` = NULL, `password` = 'Aa@18281957963', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18281957963';

-- 邓颖 / 城西幼儿园 / 13551681309
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓颖', '城西幼儿园', '13551681309', 'Dy900821!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13551681309'
);
UPDATE `user_account`
SET `nick_name` = '邓颖', `organ_name` = '城西幼儿园', `password` = 'Dy900821!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13551681309';

-- 彭亚娣 / 四川省犍为第一中学 / 13540522958
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '彭亚娣', '四川省犍为第一中学', '13540522958', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540522958'
);
UPDATE `user_account`
SET `nick_name` = '彭亚娣', `organ_name` = '四川省犍为第一中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540522958';

-- 龚燕敏 / - / 19848537065
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '龚燕敏', NULL, '19848537065', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19848537065'
);
UPDATE `user_account`
SET `nick_name` = '龚燕敏', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19848537065';

-- 赵彩羊 / 广元中学 / 13795713134
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赵彩羊', '广元中学', '13795713134', 'wo3235812.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13795713134'
);
UPDATE `user_account`
SET `nick_name` = '赵彩羊', `organ_name` = '广元中学', `password` = 'wo3235812.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13795713134';

-- 黄庆 / 犍为县定文中心小学 / 13228179639
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '黄庆', '犍为县定文中心小学', '13228179639', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13228179639'
);
UPDATE `user_account`
SET `nick_name` = '黄庆', `organ_name` = '犍为县定文中心小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13228179639';

-- (无姓名) / 乐山市沙湾区葫芦镇中心小学校 / 13540549614
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '', '乐山市沙湾区葫芦镇中心小学校', '13540549614', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540549614'
);
UPDATE `user_account`
SET `nick_name` = '', `organ_name` = '乐山市沙湾区葫芦镇中心小学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540549614';

-- 袁媛 / 乐山市沙湾区葫芦镇中心小学校 / 18398608195
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '袁媛', '乐山市沙湾区葫芦镇中心小学校', '18398608195', 'yy930612.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18398608195'
);
UPDATE `user_account`
SET `nick_name` = '袁媛', `organ_name` = '乐山市沙湾区葫芦镇中心小学校', `password` = 'yy930612.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18398608195';

-- 邓勇军 / 安居区教育局 / 13882582935
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓勇军', '安居区教育局', '13882582935', 'DYJdyj@791205', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13882582935'
);
UPDATE `user_account`
SET `nick_name` = '邓勇军', `organ_name` = '安居区教育局', `password` = 'DYJdyj@791205', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13882582935';

-- 邹萌 / 四川省乐山市第五中学 / 13281115698
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邹萌', '四川省乐山市第五中学', '13281115698', 'zm2118921.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13281115698'
);
UPDATE `user_account`
SET `nick_name` = '邹萌', `organ_name` = '四川省乐山市第五中学', `password` = 'zm2118921.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13281115698';

-- 张婵 / 徐家小学 / 18381734945
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张婵', '徐家小学', '18381734945', 'yibo0805@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381734945'
);
UPDATE `user_account`
SET `nick_name` = '张婵', `organ_name` = '徐家小学', `password` = 'yibo0805@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381734945';

-- 李胜南 / - / 15196908212
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李胜南', NULL, '15196908212', 'Aa@15196908212', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15196908212'
);
UPDATE `user_account`
SET `nick_name` = '李胜南', `organ_name` = NULL, `password` = 'Aa@15196908212', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15196908212';

-- 刘玲 / 雁江分局 / 13708263661
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘玲', '雁江分局', '13708263661', 'L761216.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13708263661'
);
UPDATE `user_account`
SET `nick_name` = '刘玲', `organ_name` = '雁江分局', `password` = 'L761216.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13708263661';

-- 杨清 / 徐家小学 / 18508170379
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨清', '徐家小学', '18508170379', '@78xm31YXLdr4', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18508170379'
);
UPDATE `user_account`
SET `nick_name` = '杨清', `organ_name` = '徐家小学', `password` = '@78xm31YXLdr4', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18508170379';

-- 杨晓珑 / 徐家小学 / 18281751493
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨晓珑', '徐家小学', '18281751493', '@78xm31YXLdr4', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18281751493'
);
UPDATE `user_account`
SET `nick_name` = '杨晓珑', `organ_name` = '徐家小学', `password` = '@78xm31YXLdr4', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18281751493';

-- 高颖 / 徐家小学 / 13547547548
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '高颖', '徐家小学', '13547547548', '185151863Gy@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13547547548'
);
UPDATE `user_account`
SET `nick_name` = '高颖', `organ_name` = '徐家小学', `password` = '185151863Gy@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13547547548';

-- 彭建 / 犍为县岷东中心小学 / 13540553988
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '彭建', '犍为县岷东中心小学', '13540553988', 'mdxx4911092#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540553988'
);
UPDATE `user_account`
SET `nick_name` = '彭建', `organ_name` = '犍为县岷东中心小学', `password` = 'mdxx4911092#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540553988';

-- 兰阳 / 犍为县铁炉九年制学校 / 19140187989
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '兰阳', '犍为县铁炉九年制学校', '19140187989', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19140187989'
);
UPDATE `user_account`
SET `nick_name` = '兰阳', `organ_name` = '犍为县铁炉九年制学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19140187989';

-- 傅晶 / 犍为县铁炉九年制学校 / 17341726186
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '傅晶', '犍为县铁炉九年制学校', '17341726186', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17341726186'
);
UPDATE `user_account`
SET `nick_name` = '傅晶', `organ_name` = '犍为县铁炉九年制学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17341726186';

-- 蒋丹 / 乐山市沙湾小学 / 13408248964
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '蒋丹', '乐山市沙湾小学', '13408248964', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13408248964'
);
UPDATE `user_account`
SET `nick_name` = '蒋丹', `organ_name` = '乐山市沙湾小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13408248964';

-- 王莉萍 / - / 15775829319
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王莉萍', NULL, '15775829319', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15775829319'
);
UPDATE `user_account`
SET `nick_name` = '王莉萍', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15775829319';

-- 陈菊兰 / 乐山市五通桥区盐码头小学 / 15983368088
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈菊兰', '乐山市五通桥区盐码头小学', '15983368088', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15983368088'
);
UPDATE `user_account`
SET `nick_name` = '陈菊兰', `organ_name` = '乐山市五通桥区盐码头小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15983368088';

-- 税涛 / 犍为县铁炉九年制学校 / 13101374929
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '税涛', '犍为县铁炉九年制学校', '13101374929', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13101374929'
);
UPDATE `user_account`
SET `nick_name` = '税涛', `organ_name` = '犍为县铁炉九年制学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13101374929';

-- 于洋 / 遂宁经开区教育卫生行业党委 / 19331521778
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '于洋', '遂宁经开区教育卫生行业党委', '19331521778', '2025yysa0322@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19331521778'
);
UPDATE `user_account`
SET `nick_name` = '于洋', `organ_name` = '遂宁经开区教育卫生行业党委', `password` = '2025yysa0322@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19331521778';

-- 苟腊梅 / 马边彝族自治县建设镇光辉中心校 / 15283300745
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '苟腊梅', '马边彝族自治县建设镇光辉中心校', '15283300745', 'Abcd1234.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15283300745'
);
UPDATE `user_account`
SET `nick_name` = '苟腊梅', `organ_name` = '马边彝族自治县建设镇光辉中心校', `password` = 'Abcd1234.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15283300745';

-- 代冬琴 / 资阳市精神病医院 / 17713742821
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '代冬琴', '资阳市精神病医院', '17713742821', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17713742821'
);
UPDATE `user_account`
SET `nick_name` = '代冬琴', `organ_name` = '资阳市精神病医院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17713742821';

-- 严清 / 船山区教育局 / 18728563168
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '严清', '船山区教育局', '18728563168', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18728563168'
);
UPDATE `user_account`
SET `nick_name` = '严清', `organ_name` = '船山区教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18728563168';

-- 任梦佳 / 满福幼儿园 / 15310403301
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '任梦佳', '满福幼儿园', '15310403301', '24282361Rmj.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15310403301'
);
UPDATE `user_account`
SET `nick_name` = '任梦佳', `organ_name` = '满福幼儿园', `password` = '24282361Rmj.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15310403301';

-- 马晓清 / 徐家小学 / 17740272561
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '马晓清', '徐家小学', '17740272561', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17740272561'
);
UPDATE `user_account`
SET `nick_name` = '马晓清', `organ_name` = '徐家小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17740272561';

-- 何竹君 / 徐家小学 / 15390282852
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '何竹君', '徐家小学', '15390282852', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15390282852'
);
UPDATE `user_account`
SET `nick_name` = '何竹君', `organ_name` = '徐家小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15390282852';

-- 李蕊岑 / 乐山市徐家扁小学 / 18011676567
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李蕊岑', '乐山市徐家扁小学', '18011676567', 'Abcd1234!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18011676567'
);
UPDATE `user_account`
SET `nick_name` = '李蕊岑', `organ_name` = '乐山市徐家扁小学', `password` = 'Abcd1234!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18011676567';

-- 杨敏 / 徐家小学 / 15182903108
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨敏', '徐家小学', '15182903108', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15182903108'
);
UPDATE `user_account`
SET `nick_name` = '杨敏', `organ_name` = '徐家小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15182903108';

-- 明莉 / 徐家小学 / 18508171525
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '明莉', '徐家小学', '18508171525', 'ming.3115616', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18508171525'
);
UPDATE `user_account`
SET `nick_name` = '明莉', `organ_name` = '徐家小学', `password` = 'ming.3115616', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18508171525';

-- 吕立 / 乐山市市中区苏稽镇新桥幼儿园 / 13698397595
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吕立', '乐山市市中区苏稽镇新桥幼儿园', '13698397595', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13698397595'
);
UPDATE `user_account`
SET `nick_name` = '吕立', `organ_name` = '乐山市市中区苏稽镇新桥幼儿园', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13698397595';

-- 陈治安 / 夹江县吴场镇初级中学 / 13890688046
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈治安', '夹江县吴场镇初级中学', '13890688046', 'll147258@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890688046'
);
UPDATE `user_account`
SET `nick_name` = '陈治安', `organ_name` = '夹江县吴场镇初级中学', `password` = 'll147258@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890688046';

-- 廖子鑫 / 安岳县长河源小学 / 18328282873
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '廖子鑫', '安岳县长河源小学', '18328282873', 'Lzx18328282873!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18328282873'
);
UPDATE `user_account`
SET `nick_name` = '廖子鑫', `organ_name` = '安岳县长河源小学', `password` = 'Lzx18328282873!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18328282873';

-- 叶红英 / 乐山市沙湾区葫芦镇中心幼儿园 / 13006409725
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '叶红英', '乐山市沙湾区葫芦镇中心幼儿园', '13006409725', 'Jiangwei520#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13006409725'
);
UPDATE `user_account`
SET `nick_name` = '叶红英', `organ_name` = '乐山市沙湾区葫芦镇中心幼儿园', `password` = 'Jiangwei520#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13006409725';

-- 余嘉丽 / 乐山市市中区茅桥镇中心幼儿园 / 18781336833
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '余嘉丽', '乐山市市中区茅桥镇中心幼儿园', '18781336833', 'YJL931117@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18781336833'
);
UPDATE `user_account`
SET `nick_name` = '余嘉丽', `organ_name` = '乐山市市中区茅桥镇中心幼儿园', `password` = 'YJL931117@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18781336833';

-- 熊贝佳 / 船山区教育局 / 18728572917
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '熊贝佳', '船山区教育局', '18728572917', 'A99b88c2&4', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18728572917'
);
UPDATE `user_account`
SET `nick_name` = '熊贝佳', `organ_name` = '船山区教育局', `password` = 'A99b88c2&4', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18728572917';

-- 王路遥 / 苏祠街道社区卫生服务中心 / 18228557481
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王路遥', '苏祠街道社区卫生服务中心', '18228557481', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18228557481'
);
UPDATE `user_account`
SET `nick_name` = '王路遥', `organ_name` = '苏祠街道社区卫生服务中心', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18228557481';

-- 熊帆 / 安岳县九龙九年制学校 / 15196824858
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '熊帆', '安岳县九龙九年制学校', '15196824858', 'xf200911A@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15196824858'
);
UPDATE `user_account`
SET `nick_name` = '熊帆', `organ_name` = '安岳县九龙九年制学校', `password` = 'xf200911A@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15196824858';

-- 金铁梅 / 乐山市沙湾区牛石镇学校 / 18781902263
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '金铁梅', '乐山市沙湾区牛石镇学校', '18781902263', '@jtm183492', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18781902263'
);
UPDATE `user_account`
SET `nick_name` = '金铁梅', `organ_name` = '乐山市沙湾区牛石镇学校', `password` = '@jtm183492', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18781902263';

-- 薛理文 / 资阳市雁江区教育和体育局 / 15281785225
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '薛理文', '资阳市雁江区教育和体育局', '15281785225', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15281785225'
);
UPDATE `user_account`
SET `nick_name` = '薛理文', `organ_name` = '资阳市雁江区教育和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15281785225';

-- 李莎莎 / 广元市树人幼儿园 / 18283962126
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李莎莎', '广元市树人幼儿园', '18283962126', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18283962126'
);
UPDATE `user_account`
SET `nick_name` = '李莎莎', `organ_name` = '广元市树人幼儿园', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18283962126';

-- 曾晓红 / 乐山市机关幼儿园 / 15183360859
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曾晓红', '乐山市机关幼儿园', '15183360859', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15183360859'
);
UPDATE `user_account`
SET `nick_name` = '曾晓红', `organ_name` = '乐山市机关幼儿园', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15183360859';

-- 胡琳 / 徐家小学 / 15881714351
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡琳', '徐家小学', '15881714351', 'Zyp202303.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15881714351'
);
UPDATE `user_account`
SET `nick_name` = '胡琳', `organ_name` = '徐家小学', `password` = 'Zyp202303.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15881714351';

-- 杨文武 / 安居区教育局 / 13547431807
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨文武', '安居区教育局', '13547431807', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13547431807'
);
UPDATE `user_account`
SET `nick_name` = '杨文武', `organ_name` = '安居区教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13547431807';

-- 莫色什古 / 资阳市雁江区教育和体育局 / 15183493392
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '莫色什古', '资阳市雁江区教育和体育局', '15183493392', '144843883052mS.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15183493392'
);
UPDATE `user_account`
SET `nick_name` = '莫色什古', `organ_name` = '资阳市雁江区教育和体育局', `password` = '144843883052mS.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15183493392';

-- 徐雯雯 / 乐山市市中区剑峰镇初级中学 / 15283390091
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '徐雯雯', '乐山市市中区剑峰镇初级中学', '15283390091', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15283390091'
);
UPDATE `user_account`
SET `nick_name` = '徐雯雯', `organ_name` = '乐山市市中区剑峰镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15283390091';

-- 汪潇 / 资阳市雁江区教育和体育局 / 18328238268
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '汪潇', '资阳市雁江区教育和体育局', '18328238268', '123qweWX@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18328238268'
);
UPDATE `user_account`
SET `nick_name` = '汪潇', `organ_name` = '资阳市雁江区教育和体育局', `password` = '123qweWX@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18328238268';

-- 付丽蓉 / 安岳县高升初级中学 / 15351391711
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '付丽蓉', '安岳县高升初级中学', '15351391711', 'Flr18982937300!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15351391711'
);
UPDATE `user_account`
SET `nick_name` = '付丽蓉', `organ_name` = '安岳县高升初级中学', `password` = 'Flr18982937300!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15351391711';

-- 刘锦 / 峨边彝族自治县城区第二小学 / 17628410830
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘锦', '峨边彝族自治县城区第二小学', '17628410830', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17628410830'
);
UPDATE `user_account`
SET `nick_name` = '刘锦', `organ_name` = '峨边彝族自治县城区第二小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17628410830';

-- 朱燕 / 峨边彝族自治县城区第二小学 / 18142521691
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '朱燕', '峨边彝族自治县城区第二小学', '18142521691', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18142521691'
);
UPDATE `user_account`
SET `nick_name` = '朱燕', `organ_name` = '峨边彝族自治县城区第二小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18142521691';

-- 吴树英 / 峨边彝族自治县城区第二小学 / 13890640183
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴树英', '峨边彝族自治县城区第二小学', '13890640183', 'Wsy123823@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890640183'
);
UPDATE `user_account`
SET `nick_name` = '吴树英', `organ_name` = '峨边彝族自治县城区第二小学', `password` = 'Wsy123823@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890640183';

-- 唐正忠 / 峨边彝族自治县城区第二小学 / 17378921109
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '唐正忠', '峨边彝族自治县城区第二小学', '17378921109', '@tzz196661', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17378921109'
);
UPDATE `user_account`
SET `nick_name` = '唐正忠', `organ_name` = '峨边彝族自治县城区第二小学', `password` = '@tzz196661', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17378921109';

-- 张青 / 广元市利州区南鹰小学 / 15397643814
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张青', '广元市利州区南鹰小学', '15397643814', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15397643814'
);
UPDATE `user_account`
SET `nick_name` = '张青', `organ_name` = '广元市利州区南鹰小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15397643814';

-- 尹若铃 / 乐山市柏杨小学 / 15681335135
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '尹若铃', '乐山市柏杨小学', '15681335135', '@jasonzhang1220', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15681335135'
);
UPDATE `user_account`
SET `nick_name` = '尹若铃', `organ_name` = '乐山市柏杨小学', `password` = '@jasonzhang1220', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15681335135';

-- 赵娟 / 沐川县幸福小学 / 18728837289
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赵娟', '沐川县幸福小学', '18728837289', 'zhao201314@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18728837289'
);
UPDATE `user_account`
SET `nick_name` = '赵娟', `organ_name` = '沐川县幸福小学', `password` = 'zhao201314@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18728837289';

-- 王一汀 / 大英县委组织部 / 18919571749
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王一汀', '大英县委组织部', '18919571749', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18919571749'
);
UPDATE `user_account`
SET `nick_name` = '王一汀', `organ_name` = '大英县委组织部', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18919571749';

-- 范笑寒 / - / 18227896206
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '范笑寒', NULL, '18227896206', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18227896206'
);
UPDATE `user_account`
SET `nick_name` = '范笑寒', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18227896206';

-- 莫铭芝 / 沐川县箭板小学 / 15328610635
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '莫铭芝', '沐川县箭板小学', '15328610635', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15328610635'
);
UPDATE `user_account`
SET `nick_name` = '莫铭芝', `organ_name` = '沐川县箭板小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15328610635';

-- 吴孟雅 / 沐川县幸福小学 / 13540578818
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴孟雅', '沐川县幸福小学', '13540578818', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540578818'
);
UPDATE `user_account`
SET `nick_name` = '吴孟雅', `organ_name` = '沐川县幸福小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540578818';

-- 贾致力 / 峨边彝族自治县城区第二小学 / 15984382071
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '贾致力', '峨边彝族自治县城区第二小学', '15984382071', '15984382071@j', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15984382071'
);
UPDATE `user_account`
SET `nick_name` = '贾致力', `organ_name` = '峨边彝族自治县城区第二小学', `password` = '15984382071@j', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15984382071';

-- 胡平 / 沐川县武圣小学 / 13408338338
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡平', '沐川县武圣小学', '13408338338', 'Wsxx4696023!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13408338338'
);
UPDATE `user_account`
SET `nick_name` = '胡平', `organ_name` = '沐川县武圣小学', `password` = 'Wsxx4696023!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13408338338';

-- 李霞 / 沐川县武圣小学 / 18383313866
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李霞', '沐川县武圣小学', '18383313866', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18383313866'
);
UPDATE `user_account`
SET `nick_name` = '李霞', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18383313866';

-- 刘萍 / 沐川县武圣小学 / 17781222975
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘萍', '沐川县武圣小学', '17781222975', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17781222975'
);
UPDATE `user_account`
SET `nick_name` = '刘萍', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17781222975';

-- 朱苓 / 沐川县武圣小学 / 18980262570
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '朱苓', '沐川县武圣小学', '18980262570', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18980262570'
);
UPDATE `user_account`
SET `nick_name` = '朱苓', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18980262570';

-- 田蜜 / 沐川县武圣小学 / 18142526394
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '田蜜', '沐川县武圣小学', '18142526394', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18142526394'
);
UPDATE `user_account`
SET `nick_name` = '田蜜', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18142526394';

-- 吴秋月 / 沐川县武圣小学 / 17828245531
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴秋月', '沐川县武圣小学', '17828245531', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17828245531'
);
UPDATE `user_account`
SET `nick_name` = '吴秋月', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17828245531';

-- 向奇 / 沐川县武圣小学 / 18227582581
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '向奇', '沐川县武圣小学', '18227582581', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18227582581'
);
UPDATE `user_account`
SET `nick_name` = '向奇', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18227582581';

-- 廖慧敏 / 沐川县武圣小学 / 18381482823
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '廖慧敏', '沐川县武圣小学', '18381482823', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381482823'
);
UPDATE `user_account`
SET `nick_name` = '廖慧敏', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381482823';

-- 王春 / 沐川县武圣小学 / 15386510579
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王春', '沐川县武圣小学', '15386510579', 'wch98325@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15386510579'
);
UPDATE `user_account`
SET `nick_name` = '王春', `organ_name` = '沐川县武圣小学', `password` = 'wch98325@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15386510579';

-- 龙顶林 / 沐川县武圣小学 / 13990637563
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '龙顶林', '沐川县武圣小学', '13990637563', '13990637563@A', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13990637563'
);
UPDATE `user_account`
SET `nick_name` = '龙顶林', `organ_name` = '沐川县武圣小学', `password` = '13990637563@A', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13990637563';

-- 苟云宵 / 沐川县武圣小学 / 18224495396
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '苟云宵', '沐川县武圣小学', '18224495396', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18224495396'
);
UPDATE `user_account`
SET `nick_name` = '苟云宵', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18224495396';

-- 闫冬梅 / 沐川县武圣小学 / 18728196755
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '闫冬梅', '沐川县武圣小学', '18728196755', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18728196755'
);
UPDATE `user_account`
SET `nick_name` = '闫冬梅', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18728196755';

-- 辜凤琴 / 沐川县武圣小学 / 18728866054
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '辜凤琴', '沐川县武圣小学', '18728866054', '@Gfq13579', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18728866054'
);
UPDATE `user_account`
SET `nick_name` = '辜凤琴', `organ_name` = '沐川县武圣小学', `password` = '@Gfq13579', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18728866054';

-- 何娇 / 资阳市雁江区教育和体育局 / 15282231378
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '何娇', '资阳市雁江区教育和体育局', '15282231378', 'Yx710916$', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15282231378'
);
UPDATE `user_account`
SET `nick_name` = '何娇', `organ_name` = '资阳市雁江区教育和体育局', `password` = 'Yx710916$', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15282231378';

-- 胡悦 / 沐川县武圣小学 / 13108979560
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡悦', '沐川县武圣小学', '13108979560', '19970602hy.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13108979560'
);
UPDATE `user_account`
SET `nick_name` = '胡悦', `organ_name` = '沐川县武圣小学', `password` = '19970602hy.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13108979560';

-- 袁涛 / 沐川县武圣小学 / 18990682816
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '袁涛', '沐川县武圣小学', '18990682816', '@yt123888', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18990682816'
);
UPDATE `user_account`
SET `nick_name` = '袁涛', `organ_name` = '沐川县武圣小学', `password` = '@yt123888', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18990682816';

-- 底地阿雄 / 峨边彝族自治县城区第二小学 / 18384621927
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '底地阿雄', '峨边彝族自治县城区第二小学', '18384621927', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18384621927'
);
UPDATE `user_account`
SET `nick_name` = '底地阿雄', `organ_name` = '峨边彝族自治县城区第二小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18384621927';

-- 罗奇琦 / 沐川县幸福小学 / 18328019850
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '罗奇琦', '沐川县幸福小学', '18328019850', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18328019850'
);
UPDATE `user_account`
SET `nick_name` = '罗奇琦', `organ_name` = '沐川县幸福小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18328019850';

-- 肖遵英 / 安居区教育局 / 15108110712
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '肖遵英', '安居区教育局', '15108110712', '235235Ab@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15108110712'
);
UPDATE `user_account`
SET `nick_name` = '肖遵英', `organ_name` = '安居区教育局', `password` = '235235Ab@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15108110712';

-- 郑生利 / 安岳县高升初级中学 / 19881702201
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '郑生利', '安岳县高升初级中学', '19881702201', 'zl@123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19881702201'
);
UPDATE `user_account`
SET `nick_name` = '郑生利', `organ_name` = '安岳县高升初级中学', `password` = 'zl@123456', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19881702201';

-- 刘容 / 沐川县永福学校 / 13890630599
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘容', '沐川县永福学校', '13890630599', '12345YFxx!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890630599'
);
UPDATE `user_account`
SET `nick_name` = '刘容', `organ_name` = '沐川县永福学校', `password` = '12345YFxx!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890630599';

-- 李慧 / 沐川县永福学校 / 18283347277
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李慧', '沐川县永福学校', '18283347277', '12345YFxx!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18283347277'
);
UPDATE `user_account`
SET `nick_name` = '李慧', `organ_name` = '沐川县永福学校', `password` = '12345YFxx!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18283347277';

-- 陈静 / 沐川县永福学校 / 18398056465
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈静', '沐川县永福学校', '18398056465', '12345YFxx!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18398056465'
);
UPDATE `user_account`
SET `nick_name` = '陈静', `organ_name` = '沐川县永福学校', `password` = '12345YFxx!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18398056465';

-- 刘琪 / 乐山市柏杨小学 / 18728837186
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘琪', '乐山市柏杨小学', '18728837186', 'Gongzi2008@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18728837186'
);
UPDATE `user_account`
SET `nick_name` = '刘琪', `organ_name` = '乐山市柏杨小学', `password` = 'Gongzi2008@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18728837186';

-- 薛晓辉 / 乐山市实验中学 / 17835099305
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '薛晓辉', '乐山市实验中学', '17835099305', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17835099305'
);
UPDATE `user_account`
SET `nick_name` = '薛晓辉', `organ_name` = '乐山市实验中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17835099305';

-- 谭珏麒 / 乐山市沙湾区葫芦镇中心小学校 / 18683380745
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '谭珏麒', '乐山市沙湾区葫芦镇中心小学校', '18683380745', 'Tjq5203884..', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18683380745'
);
UPDATE `user_account`
SET `nick_name` = '谭珏麒', `organ_name` = '乐山市沙湾区葫芦镇中心小学校', `password` = 'Tjq5203884..', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18683380745';

-- 杨秋莲 / 仪陇县人民医院 / 13219405701
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨秋莲', '仪陇县人民医院', '13219405701', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13219405701'
);
UPDATE `user_account`
SET `nick_name` = '杨秋莲', `organ_name` = '仪陇县人民医院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13219405701';

-- 汪旭 / 仪陇县人民医院 / 18208785082
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '汪旭', '仪陇县人民医院', '18208785082', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18208785082'
);
UPDATE `user_account`
SET `nick_name` = '汪旭', `organ_name` = '仪陇县人民医院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18208785082';

-- 赵志刚 / 沐川县第二实验小学 / 13540929772
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赵志刚', '沐川县第二实验小学', '13540929772', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540929772'
);
UPDATE `user_account`
SET `nick_name` = '赵志刚', `organ_name` = '沐川县第二实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540929772';

-- 雷钰婷 / 马边彝族自治县第一初级中学 / 15182285459
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '雷钰婷', '马边彝族自治县第一初级中学', '15182285459', 'lyt@zhm134679852', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15182285459'
);
UPDATE `user_account`
SET `nick_name` = '雷钰婷', `organ_name` = '马边彝族自治县第一初级中学', `password` = 'lyt@zhm134679852', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15182285459';

-- 黄元君 / 乐山市市中区苏稽镇新桥小学 / 18283612098
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '黄元君', '乐山市市中区苏稽镇新桥小学', '18283612098', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18283612098'
);
UPDATE `user_account`
SET `nick_name` = '黄元君', `organ_name` = '乐山市市中区苏稽镇新桥小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18283612098';

-- 唐学会 / 沐川县永福学校 / 18384680676
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '唐学会', '沐川县永福学校', '18384680676', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18384680676'
);
UPDATE `user_account`
SET `nick_name` = '唐学会', `organ_name` = '沐川县永福学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18384680676';

-- 方亚芬 / 乐山市市中区杨湾小学 / 13981364346
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '方亚芬', '乐山市市中区杨湾小学', '13981364346', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13981364346'
);
UPDATE `user_account`
SET `nick_name` = '方亚芬', `organ_name` = '乐山市市中区杨湾小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13981364346';

-- 周彬玉 / - / 18040433828
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '周彬玉', NULL, '18040433828', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18040433828'
);
UPDATE `user_account`
SET `nick_name` = '周彬玉', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18040433828';

-- 石云婷 / 沐川县武圣小学 / 13378330306
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '石云婷', '沐川县武圣小学', '13378330306', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13378330306'
);
UPDATE `user_account`
SET `nick_name` = '石云婷', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13378330306';

-- 黄述彬 / 夹江县吴场镇初级中学 / 13388253657
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '黄述彬', '夹江县吴场镇初级中学', '13388253657', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13388253657'
);
UPDATE `user_account`
SET `nick_name` = '黄述彬', `organ_name` = '夹江县吴场镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13388253657';

-- 马卫华 / 夹江县吴场镇初级中学 / 15182286504
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '马卫华', '夹江县吴场镇初级中学', '15182286504', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15182286504'
);
UPDATE `user_account`
SET `nick_name` = '马卫华', `organ_name` = '夹江县吴场镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15182286504';

-- 眭龙生 / 沐川县永福学校 / 18080629130
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '眭龙生', '沐川县永福学校', '18080629130', 'SLS751241#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080629130'
);
UPDATE `user_account`
SET `nick_name` = '眭龙生', `organ_name` = '沐川县永福学校', `password` = 'SLS751241#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080629130';

-- 万春霞 / 沐川县武圣小学 / 15183373800
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '万春霞', '沐川县武圣小学', '15183373800', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15183373800'
);
UPDATE `user_account`
SET `nick_name` = '万春霞', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15183373800';

-- 夏旭萍 / 沐川县沐溪初级中学 / 13881330148
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '夏旭萍', '沐川县沐溪初级中学', '13881330148', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13881330148'
);
UPDATE `user_account`
SET `nick_name` = '夏旭萍', `organ_name` = '沐川县沐溪初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13881330148';

-- 陈珍羽 / 沐川县沐溪初级中学 / 15183398009
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈珍羽', '沐川县沐溪初级中学', '15183398009', 'Abcd@1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15183398009'
);
UPDATE `user_account`
SET `nick_name` = '陈珍羽', `organ_name` = '沐川县沐溪初级中学', `password` = 'Abcd@1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15183398009';

-- 万切永 / 沐川县沐溪初级中学 / 13036587963
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '万切永', '沐川县沐溪初级中学', '13036587963', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13036587963'
);
UPDATE `user_account`
SET `nick_name` = '万切永', `organ_name` = '沐川县沐溪初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13036587963';

-- 帅四光 / 夹江县吴场镇初级中学 / 18080602348
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '帅四光', '夹江县吴场镇初级中学', '18080602348', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080602348'
);
UPDATE `user_account`
SET `nick_name` = '帅四光', `organ_name` = '夹江县吴场镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080602348';

-- 邵娜 / 乐山市嘉州学校 / 18381395636
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邵娜', '乐山市嘉州学校', '18381395636', 'Sn901213.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381395636'
);
UPDATE `user_account`
SET `nick_name` = '邵娜', `organ_name` = '乐山市嘉州学校', `password` = 'Sn901213.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381395636';

-- 李希平 / 夹江县吴场镇初级中学 / 15298092965
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李希平', '夹江县吴场镇初级中学', '15298092965', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15298092965'
);
UPDATE `user_account`
SET `nick_name` = '李希平', `organ_name` = '夹江县吴场镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15298092965';

-- 万琴 / 乐山市嘉州学校 / 15892819175
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '万琴', '乐山市嘉州学校', '15892819175', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15892819175'
);
UPDATE `user_account`
SET `nick_name` = '万琴', `organ_name` = '乐山市嘉州学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15892819175';

-- 赵新月 / 乐山市实验中学 / 15198055535
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赵新月', '乐山市实验中学', '15198055535', 'xinyue@159', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15198055535'
);
UPDATE `user_account`
SET `nick_name` = '赵新月', `organ_name` = '乐山市实验中学', `password` = 'xinyue@159', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15198055535';

-- 陈阳光 / 南江县金银花产业发展中心 / 18382743725
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈阳光', '南江县金银花产业发展中心', '18382743725', '1232002314Chen@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18382743725'
);
UPDATE `user_account`
SET `nick_name` = '陈阳光', `organ_name` = '南江县金银花产业发展中心', `password` = '1232002314Chen@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18382743725';

-- 廖晓红 / 沐川县沐溪小学 / 13890661526
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '廖晓红', '沐川县沐溪小学', '13890661526', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890661526'
);
UPDATE `user_account`
SET `nick_name` = '廖晓红', `organ_name` = '沐川县沐溪小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890661526';

-- 牟明慧 / 四川省乐山沫若中学 / 13540906439
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '牟明慧', '四川省乐山沫若中学', '13540906439', 'moumh8687mmhMMJ@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540906439'
);
UPDATE `user_account`
SET `nick_name` = '牟明慧', `organ_name` = '四川省乐山沫若中学', `password` = 'moumh8687mmhMMJ@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540906439';

-- 郑诗嘉 / 四川省乐山沫若中学 / 18908134956
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '郑诗嘉', '四川省乐山沫若中学', '18908134956', 'zsj1016......', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18908134956'
);
UPDATE `user_account`
SET `nick_name` = '郑诗嘉', `organ_name` = '四川省乐山沫若中学', `password` = 'zsj1016......', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18908134956';

-- 刘晨霞 / 四川省乐山沫若中学 / 18981372707
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘晨霞', '四川省乐山沫若中学', '18981372707', 'mrzx@lcx123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18981372707'
);
UPDATE `user_account`
SET `nick_name` = '刘晨霞', `organ_name` = '四川省乐山沫若中学', `password` = 'mrzx@lcx123', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18981372707';

-- 何红兵 / 资阳市雁江区卫生健康局 / 15183757281
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '何红兵', '资阳市雁江区卫生健康局', '15183757281', 'hhb@861784140', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15183757281'
);
UPDATE `user_account`
SET `nick_name` = '何红兵', `organ_name` = '资阳市雁江区卫生健康局', `password` = 'hhb@861784140', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15183757281';

-- 王倩 / 沐川县实验小学 / 18183371268
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王倩', '沐川县实验小学', '18183371268', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18183371268'
);
UPDATE `user_account`
SET `nick_name` = '王倩', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18183371268';

-- 余晓芳 / 沐川县实验小学 / 13508149195
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '余晓芳', '沐川县实验小学', '13508149195', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13508149195'
);
UPDATE `user_account`
SET `nick_name` = '余晓芳', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13508149195';

-- 陈华 / 沐川县实验小学 / 18980262625
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈华', '沐川县实验小学', '18980262625', 'Hyh070601@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18980262625'
);
UPDATE `user_account`
SET `nick_name` = '陈华', `organ_name` = '沐川县实验小学', `password` = 'Hyh070601@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18980262625';

-- 李茂华 / 沐川县实验小学 / 13378332690
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李茂华', '沐川县实验小学', '13378332690', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13378332690'
);
UPDATE `user_account`
SET `nick_name` = '李茂华', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13378332690';

-- 夏家俊 / 沐川县教育局 / 13308279361
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '夏家俊', '沐川县教育局', '13308279361', 'xia199912.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13308279361'
);
UPDATE `user_account`
SET `nick_name` = '夏家俊', `organ_name` = '沐川县教育局', `password` = 'xia199912.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13308279361';

-- 陈昊通 / 沐川凯德绿色希望小学 / 13350736097
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈昊通', '沐川凯德绿色希望小学', '13350736097', 'LHj11335577.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13350736097'
);
UPDATE `user_account`
SET `nick_name` = '陈昊通', `organ_name` = '沐川凯德绿色希望小学', `password` = 'LHj11335577.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13350736097';

-- 王悦 / 沐川县实验小学 / 18980261726
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王悦', '沐川县实验小学', '18980261726', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18980261726'
);
UPDATE `user_account`
SET `nick_name` = '王悦', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18980261726';

-- 宋英 / 沐川县实验小学 / 13438732292
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '宋英', '沐川县实验小学', '13438732292', 'songying912823#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13438732292'
);
UPDATE `user_account`
SET `nick_name` = '宋英', `organ_name` = '沐川县实验小学', `password` = 'songying912823#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13438732292';

-- 李守琴 / 沐川县实验小学 / 13540926986
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李守琴', '沐川县实验小学', '13540926986', 'L13540926986l@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540926986'
);
UPDATE `user_account`
SET `nick_name` = '李守琴', `organ_name` = '沐川县实验小学', `password` = 'L13540926986l@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540926986';

-- 王一如 / - / 18781374981
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王一如', NULL, '18781374981', 'Wyr081998@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18781374981'
);
UPDATE `user_account`
SET `nick_name` = '王一如', `organ_name` = NULL, `password` = 'Wyr081998@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18781374981';

-- 叶玉平 / 沐川县实验小学 / 18183318997
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '叶玉平', '沐川县实验小学', '18183318997', 'yyp199901.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18183318997'
);
UPDATE `user_account`
SET `nick_name` = '叶玉平', `organ_name` = '沐川县实验小学', `password` = 'yyp199901.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18183318997';

-- 王艳 / 沐川县实验小学 / 15984360690
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王艳', '沐川县实验小学', '15984360690', 'wangyan910840@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15984360690'
);
UPDATE `user_account`
SET `nick_name` = '王艳', `organ_name` = '沐川县实验小学', `password` = 'wangyan910840@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15984360690';

-- 肖宣华 / 沐川县实验小学 / 18283391808
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '肖宣华', '沐川县实验小学', '18283391808', 'xxh750628!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18283391808'
);
UPDATE `user_account`
SET `nick_name` = '肖宣华', `organ_name` = '沐川县实验小学', `password` = 'xxh750628!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18283391808';

-- 马晓宇 / 沐川县实验小学 / 15883355828
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '马晓宇', '沐川县实验小学', '15883355828', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15883355828'
);
UPDATE `user_account`
SET `nick_name` = '马晓宇', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15883355828';

-- 兰英 / 沐川县实验小学 / 15608132197
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '兰英', '沐川县实验小学', '15608132197', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15608132197'
);
UPDATE `user_account`
SET `nick_name` = '兰英', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15608132197';

-- 龚世奇 / 清江镇 / 15215179316
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '龚世奇', '清江镇', '15215179316', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15215179316'
);
UPDATE `user_account`
SET `nick_name` = '龚世奇', `organ_name` = '清江镇', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15215179316';

-- 张晓慧 / 沐川县实验小学 / 18980262528
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张晓慧', '沐川县实验小学', '18980262528', 'GD1988818lh@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18980262528'
);
UPDATE `user_account`
SET `nick_name` = '张晓慧', `organ_name` = '沐川县实验小学', `password` = 'GD1988818lh@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18980262528';

-- 梁亚丽 / 乐山市沙湾区葫芦镇中心小学校 / 18784537092
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '梁亚丽', '乐山市沙湾区葫芦镇中心小学校', '18784537092', 'Pyw3559689@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18784537092'
);
UPDATE `user_account`
SET `nick_name` = '梁亚丽', `organ_name` = '乐山市沙湾区葫芦镇中心小学校', `password` = 'Pyw3559689@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18784537092';

-- 杨永成 / 资阳市雁江区教育和体育局 / 15520392579
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨永成', '资阳市雁江区教育和体育局', '15520392579', '673779Yyc.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15520392579'
);
UPDATE `user_account`
SET `nick_name` = '杨永成', `organ_name` = '资阳市雁江区教育和体育局', `password` = '673779Yyc.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15520392579';

-- 唐川 / - / 15282284356
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '唐川', NULL, '15282284356', '12345678Tc.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15282284356'
);
UPDATE `user_account`
SET `nick_name` = '唐川', `organ_name` = NULL, `password` = '12345678Tc.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15282284356';

-- 胡启强 / 夹江县马村初级中学 / 18080602365
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡启强', '夹江县马村初级中学', '18080602365', '18080602365@H', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080602365'
);
UPDATE `user_account`
SET `nick_name` = '胡启强', `organ_name` = '夹江县马村初级中学', `password` = '18080602365@H', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080602365';

-- 刘正容 / - / 13350752772
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘正容', NULL, '13350752772', 'Mslzr5566.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13350752772'
);
UPDATE `user_account`
SET `nick_name` = '刘正容', `organ_name` = NULL, `password` = 'Mslzr5566.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13350752772';

-- 张芳 / 南部县思源实验学校 / 18681798698
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张芳', '南部县思源实验学校', '18681798698', 'Zf197416!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18681798698'
);
UPDATE `user_account`
SET `nick_name` = '张芳', `organ_name` = '南部县思源实验学校', `password` = 'Zf197416!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18681798698';

-- 罗鸿杰 / 乐山市市中区童家学校 / 18728819437
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '罗鸿杰', '乐山市市中区童家学校', '18728819437', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18728819437'
);
UPDATE `user_account`
SET `nick_name` = '罗鸿杰', `organ_name` = '乐山市市中区童家学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18728819437';

-- 张小军 / 达川区 / 13882854693
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张小军', '达川区', '13882854693', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13882854693'
);
UPDATE `user_account`
SET `nick_name` = '张小军', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13882854693';

-- 李代秀 / 达川区 / 18780891910
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李代秀', '达川区', '18780891910', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18780891910'
);
UPDATE `user_account`
SET `nick_name` = '李代秀', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18780891910';

-- 蒋荭 / 达川区 / 13079012260
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '蒋荭', '达川区', '13079012260', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13079012260'
);
UPDATE `user_account`
SET `nick_name` = '蒋荭', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13079012260';

-- 唐兰 / 达川区 / 15882905625
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '唐兰', '达川区', '15882905625', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15882905625'
);
UPDATE `user_account`
SET `nick_name` = '唐兰', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15882905625';

-- 潘虹 / 达川区 / 13541801534
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '潘虹', '达川区', '13541801534', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13541801534'
);
UPDATE `user_account`
SET `nick_name` = '潘虹', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13541801534';

-- 王丹萍 / 达川区 / 18381839131
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王丹萍', '达川区', '18381839131', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381839131'
);
UPDATE `user_account`
SET `nick_name` = '王丹萍', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381839131';

-- 王和林 / 达川区 / 13982894499
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王和林', '达川区', '13982894499', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13982894499'
);
UPDATE `user_account`
SET `nick_name` = '王和林', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13982894499';

-- 李晓梅 / 徐家小学 / 13438760771
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李晓梅', '徐家小学', '13438760771', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13438760771'
);
UPDATE `user_account`
SET `nick_name` = '李晓梅', `organ_name` = '徐家小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13438760771';

-- 齐小清 / 达川区 / 15082864428
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '齐小清', '达川区', '15082864428', 'Dsczqxq864428#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15082864428'
);
UPDATE `user_account`
SET `nick_name` = '齐小清', `organ_name` = '达川区', `password` = 'Dsczqxq864428#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15082864428';

-- 唐嘉薪 / 达川区 / 18880953342
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '唐嘉薪', '达川区', '18880953342', '521103Tjx@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18880953342'
);
UPDATE `user_account`
SET `nick_name` = '唐嘉薪', `organ_name` = '达川区', `password` = '521103Tjx@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18880953342';

-- 吴怡 / 县教育和体育局 / 18783310001
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴怡', '县教育和体育局', '18783310001', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18783310001'
);
UPDATE `user_account`
SET `nick_name` = '吴怡', `organ_name` = '县教育和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18783310001';

-- 蒋宗周 / 达川区 / 13982889577
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '蒋宗周', '达川区', '13982889577', 'Dsczjzzh123@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13982889577'
);
UPDATE `user_account`
SET `nick_name` = '蒋宗周', `organ_name` = '达川区', `password` = 'Dsczjzzh123@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13982889577';

-- 何敏 / 乐山市沙湾区葫芦镇中心小学校 / 13419426304
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '何敏', '乐山市沙湾区葫芦镇中心小学校', '13419426304', '474916110hm@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13419426304'
);
UPDATE `user_account`
SET `nick_name` = '何敏', `organ_name` = '乐山市沙湾区葫芦镇中心小学校', `password` = '474916110hm@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13419426304';

-- 郑俊非 / 沐川县杨村乡卫生院 / 15983353913
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '郑俊非', '沐川县杨村乡卫生院', '15983353913', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15983353913'
);
UPDATE `user_account`
SET `nick_name` = '郑俊非', `organ_name` = '沐川县杨村乡卫生院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15983353913';

-- 赵俐 / 沐川县杨村乡卫生院 / 15281972880
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赵俐', '沐川县杨村乡卫生院', '15281972880', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15281972880'
);
UPDATE `user_account`
SET `nick_name` = '赵俐', `organ_name` = '沐川县杨村乡卫生院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15281972880';

-- 赵忠全 / - / 13518234217
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赵忠全', NULL, '13518234217', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13518234217'
);
UPDATE `user_account`
SET `nick_name` = '赵忠全', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13518234217';

-- 张君 / 沐川县杨村乡卫生院 / 13458921526
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张君', '沐川县杨村乡卫生院', '13458921526', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13458921526'
);
UPDATE `user_account`
SET `nick_name` = '张君', `organ_name` = '沐川县杨村乡卫生院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13458921526';

-- 刘国强 / 四川省汉王山监狱 / 18682598680
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘国强', '四川省汉王山监狱', '18682598680', '18682598680@A', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18682598680'
);
UPDATE `user_account`
SET `nick_name` = '刘国强', `organ_name` = '四川省汉王山监狱', `password` = '18682598680@A', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18682598680';

-- 邓佳佳 / 达川区 / 18282235439
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓佳佳', '达川区', '18282235439', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18282235439'
);
UPDATE `user_account`
SET `nick_name` = '邓佳佳', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18282235439';

-- 王继红 / 达川区 / 18781843640
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王继红', '达川区', '18781843640', 'Abcd1234%', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18781843640'
);
UPDATE `user_account`
SET `nick_name` = '王继红', `organ_name` = '达川区', `password` = 'Abcd1234%', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18781843640';

-- 廖书琴 / 达川区 / 15883720218
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '廖书琴', '达川区', '15883720218', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15883720218'
);
UPDATE `user_account`
SET `nick_name` = '廖书琴', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15883720218';

-- 张欢 / 达川区 / 15982781562
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张欢', '达川区', '15982781562', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15982781562'
);
UPDATE `user_account`
SET `nick_name` = '张欢', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15982781562';

-- 王金华 / 沐川县沐溪小学 / 15397662799
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王金华', '沐川县沐溪小学', '15397662799', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15397662799'
);
UPDATE `user_account`
SET `nick_name` = '王金华', `organ_name` = '沐川县沐溪小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15397662799';

-- 蒋玲丽 / 乐山市沙湾小学 / 15283333827
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '蒋玲丽', '乐山市沙湾小学', '15283333827', 'Zflgyh621615@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15283333827'
);
UPDATE `user_account`
SET `nick_name` = '蒋玲丽', `organ_name` = '乐山市沙湾小学', `password` = 'Zflgyh621615@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15283333827';

-- 鲁玲 / 达川区 / 13568190133
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '鲁玲', '达川区', '13568190133', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13568190133'
);
UPDATE `user_account`
SET `nick_name` = '鲁玲', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13568190133';

-- 张霞 / 达川区 / 13551424126
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张霞', '达川区', '13551424126', 'Z881007x@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13551424126'
);
UPDATE `user_account`
SET `nick_name` = '张霞', `organ_name` = '达川区', `password` = 'Z881007x@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13551424126';

-- 程启龙 / 大竹县 / 18223694809
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '程启龙', '大竹县', '18223694809', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18223694809'
);
UPDATE `user_account`
SET `nick_name` = '程启龙', `organ_name` = '大竹县', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18223694809';

-- 罗兰 / 达川区 / 18281805920
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '罗兰', '达川区', '18281805920', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18281805920'
);
UPDATE `user_account`
SET `nick_name` = '罗兰', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18281805920';

-- 梅晓红 / 夹江县吴场镇初级中学 / 13540901444
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '梅晓红', '夹江县吴场镇初级中学', '13540901444', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540901444'
);
UPDATE `user_account`
SET `nick_name` = '梅晓红', `organ_name` = '夹江县吴场镇初级中学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540901444';

-- 龚新颜 / 乐山市沙湾小学 / 13708135362
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '龚新颜', '乐山市沙湾小学', '13708135362', 'gxyzyl925@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13708135362'
);
UPDATE `user_account`
SET `nick_name` = '龚新颜', `organ_name` = '乐山市沙湾小学', `password` = 'gxyzyl925@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13708135362';

-- 许芹 / 乐山市沙湾小学 / 18113436418
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '许芹', '乐山市沙湾小学', '18113436418', 'Xwx100391@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18113436418'
);
UPDATE `user_account`
SET `nick_name` = '许芹', `organ_name` = '乐山市沙湾小学', `password` = 'Xwx100391@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18113436418';

-- 顾欢 / 夹江县吴场镇中心小学校 / 15884405530
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '顾欢', '夹江县吴场镇中心小学校', '15884405530', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15884405530'
);
UPDATE `user_account`
SET `nick_name` = '顾欢', `organ_name` = '夹江县吴场镇中心小学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15884405530';

-- 黄晓丽 / 乐山市市中区茅桥镇中心幼儿园 / 17828896966
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '黄晓丽', '乐山市市中区茅桥镇中心幼儿园', '17828896966', 'huang178#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17828896966'
);
UPDATE `user_account`
SET `nick_name` = '黄晓丽', `organ_name` = '乐山市市中区茅桥镇中心幼儿园', `password` = 'huang178#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17828896966';

-- 兰胜丰 / - / 13398255536
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '兰胜丰', NULL, '13398255536', 'Lsf123599!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13398255536'
);
UPDATE `user_account`
SET `nick_name` = '兰胜丰', `organ_name` = NULL, `password` = 'Lsf123599!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13398255536';

-- 王兴高 / 达川区 / 15881818676
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王兴高', '达川区', '15881818676', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15881818676'
);
UPDATE `user_account`
SET `nick_name` = '王兴高', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15881818676';

-- 蒲朝波 / 达川区 / 15182810266
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '蒲朝波', '达川区', '15182810266', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15182810266'
);
UPDATE `user_account`
SET `nick_name` = '蒲朝波', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15182810266';

-- 方英俊 / 达川区 / 15196852345
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '方英俊', '达川区', '15196852345', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15196852345'
);
UPDATE `user_account`
SET `nick_name` = '方英俊', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15196852345';

-- 李梦梅 / 沐川县武圣小学 / 15283396364
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李梦梅', '沐川县武圣小学', '15283396364', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15283396364'
);
UPDATE `user_account`
SET `nick_name` = '李梦梅', `organ_name` = '沐川县武圣小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15283396364';

-- 张慧 / - / 15883503521
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张慧', NULL, '15883503521', 'yixiu120@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15883503521'
);
UPDATE `user_account`
SET `nick_name` = '张慧', `organ_name` = NULL, `password` = 'yixiu120@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15883503521';

-- 吴伟 / 达川区 / 15775607111
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴伟', '达川区', '15775607111', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15775607111'
);
UPDATE `user_account`
SET `nick_name` = '吴伟', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15775607111';

-- 宋忠权 / 眉山市公安局 / 15983336018
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '宋忠权', '眉山市公安局', '15983336018', 'Szq123456@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15983336018'
);
UPDATE `user_account`
SET `nick_name` = '宋忠权', `organ_name` = '眉山市公安局', `password` = 'Szq123456@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15983336018';

-- 宋小兰 / 沐川县黄丹镇卫生院 / 13378330227
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '宋小兰', '沐川县黄丹镇卫生院', '13378330227', '@songxl133', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13378330227'
);
UPDATE `user_account`
SET `nick_name` = '宋小兰', `organ_name` = '沐川县黄丹镇卫生院', `password` = '@songxl133', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13378330227';

-- 陈芮戎 / 朝天区卫生健康局 / 15883931991
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈芮戎', '朝天区卫生健康局', '15883931991', 'Crr@123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15883931991'
);
UPDATE `user_account`
SET `nick_name` = '陈芮戎', `organ_name` = '朝天区卫生健康局', `password` = 'Crr@123456', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15883931991';

-- 许薇 / 四川省汉王山监狱 / 19380856120
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '许薇', '四川省汉王山监狱', '19380856120', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19380856120'
);
UPDATE `user_account`
SET `nick_name` = '许薇', `organ_name` = '四川省汉王山监狱', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19380856120';

-- 赖强 / 雁江分局 / 18982996668
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赖强', '雁江分局', '18982996668', '159842lq@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18982996668'
);
UPDATE `user_account`
SET `nick_name` = '赖强', `organ_name` = '雁江分局', `password` = '159842lq@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18982996668';

-- 向玉兰 / 朝天区卫生健康局 / 13547168529
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '向玉兰', '朝天区卫生健康局', '13547168529', 'Xyl123456@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13547168529'
);
UPDATE `user_account`
SET `nick_name` = '向玉兰', `organ_name` = '朝天区卫生健康局', `password` = 'Xyl123456@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13547168529';

-- 费群 / - / 13398255812
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '费群', NULL, '13398255812', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13398255812'
);
UPDATE `user_account`
SET `nick_name` = '费群', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13398255812';

-- 舒银春 / 朝天区卫生健康局 / 13568360236
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '舒银春', '朝天区卫生健康局', '13568360236', 'syc123456%', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13568360236'
);
UPDATE `user_account`
SET `nick_name` = '舒银春', `organ_name` = '朝天区卫生健康局', `password` = 'syc123456%', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13568360236';

-- 袁平文 / 沐川县实验小学 / 13378335883
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '袁平文', '沐川县实验小学', '13378335883', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13378335883'
);
UPDATE `user_account`
SET `nick_name` = '袁平文', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13378335883';

-- 李林 / 蓬溪县辖学校 / 18398856991
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李林', '蓬溪县辖学校', '18398856991', 'Aa@18398856991', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18398856991'
);
UPDATE `user_account`
SET `nick_name` = '李林', `organ_name` = '蓬溪县辖学校', `password` = 'Aa@18398856991', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18398856991';

-- 陈祥烨 / 蓬溪县辖学校 / 18483227261
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈祥烨', '蓬溪县辖学校', '18483227261', 'cxy*4613056qq', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18483227261'
);
UPDATE `user_account`
SET `nick_name` = '陈祥烨', `organ_name` = '蓬溪县辖学校', `password` = 'cxy*4613056qq', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18483227261';

-- 李高翔 / 雁江分局 / 18990352115
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李高翔', '雁江分局', '18990352115', 'lgx20000609.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18990352115'
);
UPDATE `user_account`
SET `nick_name` = '李高翔', `organ_name` = '雁江分局', `password` = 'lgx20000609.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18990352115';

-- 温和旭 / 射洪市各学校 / 13399821443
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '温和旭', '射洪市各学校', '13399821443', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13399821443'
);
UPDATE `user_account`
SET `nick_name` = '温和旭', `organ_name` = '射洪市各学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13399821443';

-- 谭越 / 四川省汉王山监狱 / 18190688787
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '谭越', '四川省汉王山监狱', '18190688787', '54tanyue520..', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18190688787'
);
UPDATE `user_account`
SET `nick_name` = '谭越', `organ_name` = '四川省汉王山监狱', `password` = '54tanyue520..', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18190688787';

-- 刘洁静 / 苏洵小学 / 15228508105
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘洁静', '苏洵小学', '15228508105', '199851Ljiejing@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15228508105'
);
UPDATE `user_account`
SET `nick_name` = '刘洁静', `organ_name` = '苏洵小学', `password` = '199851Ljiejing@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15228508105';

-- 帅港航 / 四川省乐山市第五中学 / 15184326781
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '帅港航', '四川省乐山市第五中学', '15184326781', 'Sgh199777!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15184326781'
);
UPDATE `user_account`
SET `nick_name` = '帅港航', `organ_name` = '四川省乐山市第五中学', `password` = 'Sgh199777!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15184326781';

-- 曲珍 / 建筑系党总支部 / 15983746589
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曲珍', '建筑系党总支部', '15983746589', '123456qwertY#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15983746589'
);
UPDATE `user_account`
SET `nick_name` = '曲珍', `organ_name` = '建筑系党总支部', `password` = '123456qwertY#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15983746589';

-- 章碧松 / 峨眉山市法院 / 18081395972
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '章碧松', '峨眉山市法院', '18081395972', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18081395972'
);
UPDATE `user_account`
SET `nick_name` = '章碧松', `organ_name` = '峨眉山市法院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18081395972';

-- 陈佳俊 / 剑阁县盐店镇人民政府 / 13419127097
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈佳俊', '剑阁县盐店镇人民政府', '13419127097', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13419127097'
);
UPDATE `user_account`
SET `nick_name` = '陈佳俊', `organ_name` = '剑阁县盐店镇人民政府', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13419127097';

-- 马蓉 / 朝天区卫生健康局 / 13881267855
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '马蓉', '朝天区卫生健康局', '13881267855', 'Mr123456@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13881267855'
);
UPDATE `user_account`
SET `nick_name` = '马蓉', `organ_name` = '朝天区卫生健康局', `password` = 'Mr123456@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13881267855';

-- 赵芬 / 朝天区卫生健康局 / 18942882662
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赵芬', '朝天区卫生健康局', '18942882662', 'Zf123456*', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18942882662'
);
UPDATE `user_account`
SET `nick_name` = '赵芬', `organ_name` = '朝天区卫生健康局', `password` = 'Zf123456*', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18942882662';

-- 汪燕 / 朝天区卫生健康局 / 18308365725
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '汪燕', '朝天区卫生健康局', '18308365725', 'wy123456.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18308365725'
);
UPDATE `user_account`
SET `nick_name` = '汪燕', `organ_name` = '朝天区卫生健康局', `password` = 'wy123456.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18308365725';

-- 魏超艳 / 达川区 / 18328439710
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '魏超艳', '达川区', '18328439710', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18328439710'
);
UPDATE `user_account`
SET `nick_name` = '魏超艳', `organ_name` = '达川区', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18328439710';

-- 姚沁伶 / 达川区 / 18381556990
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '姚沁伶', '达川区', '18381556990', '2linglingling!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381556990'
);
UPDATE `user_account`
SET `nick_name` = '姚沁伶', `organ_name` = '达川区', `password` = '2linglingling!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381556990';

-- 索郎卓玛 / 建筑系党总支部 / 17338906929
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '索郎卓玛', '建筑系党总支部', '17338906929', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17338906929'
);
UPDATE `user_account`
SET `nick_name` = '索郎卓玛', `organ_name` = '建筑系党总支部', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17338906929';

-- 黄伟 / 河清镇 / 13890127539
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '黄伟', '河清镇', '13890127539', 'Hw@123456', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890127539'
);
UPDATE `user_account`
SET `nick_name` = '黄伟', `organ_name` = '河清镇', `password` = 'Hw@123456', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890127539';

-- 向仕林 / 朝天区卫生健康局 / 15883532114
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '向仕林', '朝天区卫生健康局', '15883532114', 'xsl123456XSL@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15883532114'
);
UPDATE `user_account`
SET `nick_name` = '向仕林', `organ_name` = '朝天区卫生健康局', `password` = 'xsl123456XSL@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15883532114';

-- 刘静 / 绵阳市游仙区委组织部 / 18381673530
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘静', '绵阳市游仙区委组织部', '18381673530', 'LJ123456!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381673530'
);
UPDATE `user_account`
SET `nick_name` = '刘静', `organ_name` = '绵阳市游仙区委组织部', `password` = 'LJ123456!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381673530';

-- 陈园 / 四川省乐山市第五中学 / 18683339086
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈园', '四川省乐山市第五中学', '18683339086', 'Abcd1234@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18683339086'
);
UPDATE `user_account`
SET `nick_name` = '陈园', `organ_name` = '四川省乐山市第五中学', `password` = 'Abcd1234@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18683339086';

-- 王杨 / 犍为县铁炉九年制学校 / 13890616871
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王杨', '犍为县铁炉九年制学校', '13890616871', '@w12345678', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890616871'
);
UPDATE `user_account`
SET `nick_name` = '王杨', `organ_name` = '犍为县铁炉九年制学校', `password` = '@w12345678', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890616871';

-- 欧阳李奕 / 遂宁市教育局 / 18113455653
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '欧阳李奕', '遂宁市教育局', '18113455653', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18113455653'
);
UPDATE `user_account`
SET `nick_name` = '欧阳李奕', `organ_name` = '遂宁市教育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18113455653';

-- 黄钦骋 / 四川省汉王山监狱 / 15183167195
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '黄钦骋', '四川省汉王山监狱', '15183167195', 'hqclhqc1.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15183167195'
);
UPDATE `user_account`
SET `nick_name` = '黄钦骋', `organ_name` = '四川省汉王山监狱', `password` = 'hqclhqc1.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15183167195';

-- 刘忠秋 / 四川省汉王山监狱 / 18281046931
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘忠秋', '四川省汉王山监狱', '18281046931', '@L664146', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18281046931'
);
UPDATE `user_account`
SET `nick_name` = '刘忠秋', `organ_name` = '四川省汉王山监狱', `password` = '@L664146', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18281046931';

-- 邹欣芮 / 乐山市实验中学 / 18383386797
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邹欣芮', '乐山市实验中学', '18383386797', 'Zoelulu1992&', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18383386797'
);
UPDATE `user_account`
SET `nick_name` = '邹欣芮', `organ_name` = '乐山市实验中学', `password` = 'Zoelulu1992&', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18383386797';

-- 童琪 / 峨眉山市实验幼儿园 / 18683366503
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '童琪', '峨眉山市实验幼儿园', '18683366503', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18683366503'
);
UPDATE `user_account`
SET `nick_name` = '童琪', `organ_name` = '峨眉山市实验幼儿园', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18683366503';

-- 李琴 / 乐山市沙湾小学 / 15298017288
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李琴', '乐山市沙湾小学', '15298017288', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15298017288'
);
UPDATE `user_account`
SET `nick_name` = '李琴', `organ_name` = '乐山市沙湾小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15298017288';

-- 邓尚姣 / 大竹县 / 15760694133
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓尚姣', '大竹县', '15760694133', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15760694133'
);
UPDATE `user_account`
SET `nick_name` = '邓尚姣', `organ_name` = '大竹县', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15760694133';

-- 赖红艳 / 乐山市沙湾小学 / 13890680132
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '赖红艳', '乐山市沙湾小学', '13890680132', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890680132'
);
UPDATE `user_account`
SET `nick_name` = '赖红艳', `organ_name` = '乐山市沙湾小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890680132';

-- 明艳 / 高坪区教育科技和体育局 / 15298215566
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '明艳', '高坪区教育科技和体育局', '15298215566', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15298215566'
);
UPDATE `user_account`
SET `nick_name` = '明艳', `organ_name` = '高坪区教育科技和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15298215566';

-- 姜芙蓉 / 高坪区教育科技和体育局 / 18188432883
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '姜芙蓉', '高坪区教育科技和体育局', '18188432883', 'A@18188432883', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18188432883'
);
UPDATE `user_account`
SET `nick_name` = '姜芙蓉', `organ_name` = '高坪区教育科技和体育局', `password` = 'A@18188432883', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18188432883';

-- 杨冬梅 / 乐山市沙湾区福禄镇中心校 / 13890600869
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨冬梅', '乐山市沙湾区福禄镇中心校', '13890600869', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890600869'
);
UPDATE `user_account`
SET `nick_name` = '杨冬梅', `organ_name` = '乐山市沙湾区福禄镇中心校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890600869';

-- 何林芝 / - / 15298204132
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '何林芝', NULL, '15298204132', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15298204132'
);
UPDATE `user_account`
SET `nick_name` = '何林芝', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15298204132';

-- 谭禁军 / 乐山市沙湾小学 / 13698385972
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '谭禁军', '乐山市沙湾小学', '13698385972', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13698385972'
);
UPDATE `user_account`
SET `nick_name` = '谭禁军', `organ_name` = '乐山市沙湾小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13698385972';

-- 徐叶丹 / 乐山市沙湾小学 / 15183386707
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '徐叶丹', '乐山市沙湾小学', '15183386707', 'dandan19920713..', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15183386707'
);
UPDATE `user_account`
SET `nick_name` = '徐叶丹', `organ_name` = '乐山市沙湾小学', `password` = 'dandan19920713..', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15183386707';

-- 任文燕 / 宣汉县 / 15881862362
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '任文燕', '宣汉县', '15881862362', 'abc123456.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15881862362'
);
UPDATE `user_account`
SET `nick_name` = '任文燕', `organ_name` = '宣汉县', `password` = 'abc123456.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15881862362';

-- 袁华明 / 宣汉县 / 17711412849
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '袁华明', '宣汉县', '17711412849', 'abc136789.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17711412849'
);
UPDATE `user_account`
SET `nick_name` = '袁华明', `organ_name` = '宣汉县', `password` = 'abc136789.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17711412849';

-- 祝梵 / - / 18281719111
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '祝梵', NULL, '18281719111', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18281719111'
);
UPDATE `user_account`
SET `nick_name` = '祝梵', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18281719111';

-- 姚旭 / 高坪区教育科技和体育局 / 13990773060
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '姚旭', '高坪区教育科技和体育局', '13990773060', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13990773060'
);
UPDATE `user_account`
SET `nick_name` = '姚旭', `organ_name` = '高坪区教育科技和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13990773060';

-- 张玲 / 高坪区教育科技和体育局 / 13458250100
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张玲', '高坪区教育科技和体育局', '13458250100', 'A@13458250100', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13458250100'
);
UPDATE `user_account`
SET `nick_name` = '张玲', `organ_name` = '高坪区教育科技和体育局', `password` = 'A@13458250100', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13458250100';

-- 李佳桐 / 高坪区教育科技和体育局 / 18215870886
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李佳桐', '高坪区教育科技和体育局', '18215870886', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18215870886'
);
UPDATE `user_account`
SET `nick_name` = '李佳桐', `organ_name` = '高坪区教育科技和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18215870886';

-- 胡欢 / 高坪区教育科技和体育局 / 15390288248
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡欢', '高坪区教育科技和体育局', '15390288248', 'hh123456!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15390288248'
);
UPDATE `user_account`
SET `nick_name` = '胡欢', `organ_name` = '高坪区教育科技和体育局', `password` = 'hh123456!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15390288248';

-- 杜春华 / 高坪区教育科技和体育局 / 18784769269
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杜春华', '高坪区教育科技和体育局', '18784769269', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18784769269'
);
UPDATE `user_account`
SET `nick_name` = '杜春华', `organ_name` = '高坪区教育科技和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18784769269';

-- 刘莎莎 / 宣汉县 / 17738361390
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘莎莎', '宣汉县', '17738361390', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17738361390'
);
UPDATE `user_account`
SET `nick_name` = '刘莎莎', `organ_name` = '宣汉县', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17738361390';

-- 曹勇 / 乐山市沙湾小学 / 18981370353
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曹勇', '乐山市沙湾小学', '18981370353', 'Abcd1234.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18981370353'
);
UPDATE `user_account`
SET `nick_name` = '曹勇', `organ_name` = '乐山市沙湾小学', `password` = 'Abcd1234.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18981370353';

-- 王思轶 / 绵阳市盐亭县委组织部 / 19158865979
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王思轶', '绵阳市盐亭县委组织部', '19158865979', 'wsy1314.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19158865979'
);
UPDATE `user_account`
SET `nick_name` = '王思轶', `organ_name` = '绵阳市盐亭县委组织部', `password` = 'wsy1314.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19158865979';

-- 易雨超 / 乐山市沙湾小学 / 13541944499
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '易雨超', '乐山市沙湾小学', '13541944499', 'Yi885166.0', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13541944499'
);
UPDATE `user_account`
SET `nick_name` = '易雨超', `organ_name` = '乐山市沙湾小学', `password` = 'Yi885166.0', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13541944499';

-- 封卫兵 / 绵阳市梓潼生态环境局 / 15281638187
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '封卫兵', '绵阳市梓潼生态环境局', '15281638187', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15281638187'
);
UPDATE `user_account`
SET `nick_name` = '封卫兵', `organ_name` = '绵阳市梓潼生态环境局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15281638187';

-- 邓梅君 / 绵阳市梓潼生态环境局 / 17780191816
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓梅君', '绵阳市梓潼生态环境局', '17780191816', 'lhfdmj1989@lxy', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17780191816'
);
UPDATE `user_account`
SET `nick_name` = '邓梅君', `organ_name` = '绵阳市梓潼生态环境局', `password` = 'lhfdmj1989@lxy', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17780191816';

-- 王舰蓉 / 高坪区教育科技和体育局 / 15908379471
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王舰蓉', '高坪区教育科技和体育局', '15908379471', 'Wjr199785@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15908379471'
);
UPDATE `user_account`
SET `nick_name` = '王舰蓉', `organ_name` = '高坪区教育科技和体育局', `password` = 'Wjr199785@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15908379471';

-- 冯欢 / 高坪区教育科技和体育局 / 18010674923
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '冯欢', '高坪区教育科技和体育局', '18010674923', '54Fenghuan@123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18010674923'
);
UPDATE `user_account`
SET `nick_name` = '冯欢', `organ_name` = '高坪区教育科技和体育局', `password` = '54Fenghuan@123', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18010674923';

-- 郑敏 / 宣汉县 / 15182878991
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '郑敏', '宣汉县', '15182878991', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15182878991'
);
UPDATE `user_account`
SET `nick_name` = '郑敏', `organ_name` = '宣汉县', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15182878991';

-- 李伟 / - / 13696013669
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李伟', NULL, '13696013669', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13696013669'
);
UPDATE `user_account`
SET `nick_name` = '李伟', `organ_name` = NULL, `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13696013669';

-- 祝宛莹 / 徐家小学 / 17738798806
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '祝宛莹', '徐家小学', '17738798806', 'Zwy@1314520', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17738798806'
);
UPDATE `user_account`
SET `nick_name` = '祝宛莹', `organ_name` = '徐家小学', `password` = 'Zwy@1314520', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17738798806';

-- 罗正均 / 徐家小学 / 13980306104
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '罗正均', '徐家小学', '13980306104', 'Luo701026#', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13980306104'
);
UPDATE `user_account`
SET `nick_name` = '罗正均', `organ_name` = '徐家小学', `password` = 'Luo701026#', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13980306104';

-- 黄竞 / - / 18990839590
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '黄竞', NULL, '18990839590', 'QQssww%$123', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18990839590'
);
UPDATE `user_account`
SET `nick_name` = '黄竞', `organ_name` = NULL, `password` = 'QQssww%$123', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18990839590';

-- 何佳珊 / 高坪区教育科技和体育局 / 18681771103
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '何佳珊', '高坪区教育科技和体育局', '18681771103', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18681771103'
);
UPDATE `user_account`
SET `nick_name` = '何佳珊', `organ_name` = '高坪区教育科技和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18681771103';

-- 吴　丹 / 高坪区教育科技和体育局 / 17313876590
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴　丹', '高坪区教育科技和体育局', '17313876590', '18282047573oK@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17313876590'
);
UPDATE `user_account`
SET `nick_name` = '吴　丹', `organ_name` = '高坪区教育科技和体育局', `password` = '18282047573oK@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17313876590';

-- 秦永军 / - / 17383686301
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '秦永军', NULL, '17383686301', 'qyj12345678*', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17383686301'
);
UPDATE `user_account`
SET `nick_name` = '秦永军', `organ_name` = NULL, `password` = 'qyj12345678*', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17383686301';

-- 袁艺文 / 高坪区教育科技和体育局 / 13700973358
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '袁艺文', '高坪区教育科技和体育局', '13700973358', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13700973358'
);
UPDATE `user_account`
SET `nick_name` = '袁艺文', `organ_name` = '高坪区教育科技和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13700973358';

-- 陈俊良 / 高坪区教育科技和体育局 / 13890761899
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈俊良', '高坪区教育科技和体育局', '13890761899', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890761899'
);
UPDATE `user_account`
SET `nick_name` = '陈俊良', `organ_name` = '高坪区教育科技和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890761899';

-- 张凤 / 高坪区教育科技和体育局 / 13890875701
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张凤', '高坪区教育科技和体育局', '13890875701', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890875701'
);
UPDATE `user_account`
SET `nick_name` = '张凤', `organ_name` = '高坪区教育科技和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890875701';

-- 余思蒙 / 乐山市沙湾小学 / 13618180117
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '余思蒙', '乐山市沙湾小学', '13618180117', 'Yusm19931006@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13618180117'
);
UPDATE `user_account`
SET `nick_name` = '余思蒙', `organ_name` = '乐山市沙湾小学', `password` = 'Yusm19931006@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13618180117';

-- 陈泽英 / 威远县住房和城乡建设局 / 13882919060
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈泽英', '威远县住房和城乡建设局', '13882919060', 'Adc6758!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13882919060'
);
UPDATE `user_account`
SET `nick_name` = '陈泽英', `organ_name` = '威远县住房和城乡建设局', `password` = 'Adc6758!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13882919060';

-- 李鹏杰 / 马边彝族自治县公安局 / 18383374475
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李鹏杰', '马边彝族自治县公安局', '18383374475', 'w1213052613.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18383374475'
);
UPDATE `user_account`
SET `nick_name` = '李鹏杰', `organ_name` = '马边彝族自治县公安局', `password` = 'w1213052613.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18383374475';

-- 胡敏 / 沐川县教育局 / 17369141120
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡敏', '沐川县教育局', '17369141120', '1120@Humin', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17369141120'
);
UPDATE `user_account`
SET `nick_name` = '胡敏', `organ_name` = '沐川县教育局', `password` = '1120@Humin', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17369141120';

-- 刘茜 / 四川商务职业学院 / 13730666657
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘茜', '四川商务职业学院', '13730666657', 'lx1989516.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13730666657'
);
UPDATE `user_account`
SET `nick_name` = '刘茜', `organ_name` = '四川商务职业学院', `password` = 'lx1989516.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13730666657';

-- 陆晓莉 / 徐家小学 / 13458266271
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陆晓莉', '徐家小学', '13458266271', '8608653ab%', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13458266271'
);
UPDATE `user_account`
SET `nick_name` = '陆晓莉', `organ_name` = '徐家小学', `password` = '8608653ab%', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13458266271';

-- 敬启琴 / 峨眉山市第三小学校 / 18223788059
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '敬启琴', '峨眉山市第三小学校', '18223788059', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18223788059'
);
UPDATE `user_account`
SET `nick_name` = '敬启琴', `organ_name` = '峨眉山市第三小学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18223788059';

-- 王紫艺 / 峨眉山市第三小学校 / 13541935086
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王紫艺', '峨眉山市第三小学校', '13541935086', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13541935086'
);
UPDATE `user_account`
SET `nick_name` = '王紫艺', `organ_name` = '峨眉山市第三小学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13541935086';

-- 张露 / 夹江县财政局 / 18909032149
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '张露', '夹江县财政局', '18909032149', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18909032149'
);
UPDATE `user_account`
SET `nick_name` = '张露', `organ_name` = '夹江县财政局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18909032149';

-- 骆鑫 / 四川省夹江第一中学'高中部 / 15892202561
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '骆鑫', '四川省夹江第一中学''高中部', '15892202561', 'Daxin119110@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15892202561'
);
UPDATE `user_account`
SET `nick_name` = '骆鑫', `organ_name` = '四川省夹江第一中学''高中部', `password` = 'Daxin119110@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15892202561';

-- 先珈敏 / 乐山市中医医院 / 15298019626
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '先珈敏', '乐山市中医医院', '15298019626', 'xjm123456.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15298019626'
);
UPDATE `user_account`
SET `nick_name` = '先珈敏', `organ_name` = '乐山市中医医院', `password` = 'xjm123456.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15298019626';

-- 李荣娟 / 高坪区教育科技和体育局 / 13198189661
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李荣娟', '高坪区教育科技和体育局', '13198189661', 'Aa@13198189661', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13198189661'
);
UPDATE `user_account`
SET `nick_name` = '李荣娟', `organ_name` = '高坪区教育科技和体育局', `password` = 'Aa@13198189661', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13198189661';

-- 曾琳 / 沐川县杨村乡卫生院 / 15281952673
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曾琳', '沐川县杨村乡卫生院', '15281952673', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15281952673'
);
UPDATE `user_account`
SET `nick_name` = '曾琳', `organ_name` = '沐川县杨村乡卫生院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15281952673';

-- 尤钟玲 / - / 18282501759
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '尤钟玲', NULL, '18282501759', 'Aa@18282501759', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18282501759'
);
UPDATE `user_account`
SET `nick_name` = '尤钟玲', `organ_name` = NULL, `password` = 'Aa@18282501759', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18282501759';

-- 刘菊芳 / 朝天区卫生健康局 / 15184455730
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘菊芳', '朝天区卫生健康局', '15184455730', 'Aa@15184455730', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15184455730'
);
UPDATE `user_account`
SET `nick_name` = '刘菊芳', `organ_name` = '朝天区卫生健康局', `password` = 'Aa@15184455730', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15184455730';

-- 李明静 / 宣汉县 / 18117922828
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李明静', '宣汉县', '18117922828', 'Lmj.628088', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18117922828'
);
UPDATE `user_account`
SET `nick_name` = '李明静', `organ_name` = '宣汉县', `password` = 'Lmj.628088', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18117922828';

-- 殷兴均 / 宣汉县 / 18981471648
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '殷兴均', '宣汉县', '18981471648', 'Aa@18981471648', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18981471648'
);
UPDATE `user_account`
SET `nick_name` = '殷兴均', `organ_name` = '宣汉县', `password` = 'Aa@18981471648', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18981471648';

-- 杨溢 / 宣汉县 / 18200383698
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨溢', '宣汉县', '18200383698', '123456789yy.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18200383698'
);
UPDATE `user_account`
SET `nick_name` = '杨溢', `organ_name` = '宣汉县', `password` = '123456789yy.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18200383698';

-- 姚刚 / 宣汉县 / 15982999694
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '姚刚', '宣汉县', '15982999694', 'yg941120...', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15982999694'
);
UPDATE `user_account`
SET `nick_name` = '姚刚', `organ_name` = '宣汉县', `password` = 'yg941120...', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15982999694';

-- 丁慧君 / 宣汉县 / 18381986575
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '丁慧君', '宣汉县', '18381986575', 'Dhj13579@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381986575'
);
UPDATE `user_account`
SET `nick_name` = '丁慧君', `organ_name` = '宣汉县', `password` = 'Dhj13579@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381986575';

-- 吴春霞 / 宣汉县 / 13778352833
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴春霞', '宣汉县', '13778352833', 'Aa@13778352833', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13778352833'
);
UPDATE `user_account`
SET `nick_name` = '吴春霞', `organ_name` = '宣汉县', `password` = 'Aa@13778352833', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13778352833';

-- 冯云霞 / 宣汉县 / 18381848437
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '冯云霞', '宣汉县', '18381848437', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18381848437'
);
UPDATE `user_account`
SET `nick_name` = '冯云霞', `organ_name` = '宣汉县', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18381848437';

-- 伍梦秋 / 沐川县实验小学 / 18080622610
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '伍梦秋', '沐川县实验小学', '18080622610', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080622610'
);
UPDATE `user_account`
SET `nick_name` = '伍梦秋', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080622610';

-- 邓英芝 / 徐家小学 / 13990808968
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓英芝', '徐家小学', '13990808968', 'Hg198433@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13990808968'
);
UPDATE `user_account`
SET `nick_name` = '邓英芝', `organ_name` = '徐家小学', `password` = 'Hg198433@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13990808968';

-- 杨贞燕 / 宣汉县 / 15082424089
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨贞燕', '宣汉县', '15082424089', 'Aa@15082424089', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15082424089'
);
UPDATE `user_account`
SET `nick_name` = '杨贞燕', `organ_name` = '宣汉县', `password` = 'Aa@15082424089', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15082424089';

-- 吴珊 / 沐川县实验小学 / 18990667486
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴珊', '沐川县实验小学', '18990667486', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18990667486'
);
UPDATE `user_account`
SET `nick_name` = '吴珊', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18990667486';

-- 李梅 / 宣汉县 / 13518247169
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李梅', '宣汉县', '13518247169', 'Aa@13518247169', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13518247169'
);
UPDATE `user_account`
SET `nick_name` = '李梅', `organ_name` = '宣汉县', `password` = 'Aa@13518247169', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13518247169';

-- 陈佳 / 宣汉县 / 15808197745
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈佳', '宣汉县', '15808197745', 'Jjlovess9999@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15808197745'
);
UPDATE `user_account`
SET `nick_name` = '陈佳', `organ_name` = '宣汉县', `password` = 'Jjlovess9999@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15808197745';

-- 石渝山 / 宣汉县 / 17828293309
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '石渝山', '宣汉县', '17828293309', 'Aa@17828293309', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17828293309'
);
UPDATE `user_account`
SET `nick_name` = '石渝山', `organ_name` = '宣汉县', `password` = 'Aa@17828293309', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17828293309';

-- 钟文胜 / 乐山市沙湾区福禄镇初级中学 / 18080659391
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '钟文胜', '乐山市沙湾区福禄镇初级中学', '18080659391', 'Zws024680!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18080659391'
);
UPDATE `user_account`
SET `nick_name` = '钟文胜', `organ_name` = '乐山市沙湾区福禄镇初级中学', `password` = 'Zws024680!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18080659391';

-- 肖雪花 / 沐川县实验小学 / 17738890070
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '肖雪花', '沐川县实验小学', '17738890070', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17738890070'
);
UPDATE `user_account`
SET `nick_name` = '肖雪花', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17738890070';

-- 梁秋萍 / 乐山市五通桥区盐码头小学 / 18090356131
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '梁秋萍', '乐山市五通桥区盐码头小学', '18090356131', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18090356131'
);
UPDATE `user_account`
SET `nick_name` = '梁秋萍', `organ_name` = '乐山市五通桥区盐码头小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18090356131';

-- 李旭志 / 乐山市五通桥区盐码头小学 / 13308132851
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李旭志', '乐山市五通桥区盐码头小学', '13308132851', 'Aa@13308132851', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13308132851'
);
UPDATE `user_account`
SET `nick_name` = '李旭志', `organ_name` = '乐山市五通桥区盐码头小学', `password` = 'Aa@13308132851', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13308132851';

-- 潘军 / 乐山市五通桥区盐码头小学 / 13540908772
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '潘军', '乐山市五通桥区盐码头小学', '13540908772', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540908772'
);
UPDATE `user_account`
SET `nick_name` = '潘军', `organ_name` = '乐山市五通桥区盐码头小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540908772';

-- 成丽 / 乐山市五通桥区盐码头小学 / 17766086782
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '成丽', '乐山市五通桥区盐码头小学', '17766086782', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '17766086782'
);
UPDATE `user_account`
SET `nick_name` = '成丽', `organ_name` = '乐山市五通桥区盐码头小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '17766086782';

-- 李旭梅 / 乐山市五通桥区牛华镇二码头小学 / 13540545615
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李旭梅', '乐山市五通桥区牛华镇二码头小学', '13540545615', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540545615'
);
UPDATE `user_account`
SET `nick_name` = '李旭梅', `organ_name` = '乐山市五通桥区牛华镇二码头小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540545615';

-- 肖岚 / 乐山市五通桥区盐码头小学 / 15883381415
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '肖岚', '乐山市五通桥区盐码头小学', '15883381415', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15883381415'
);
UPDATE `user_account`
SET `nick_name` = '肖岚', `organ_name` = '乐山市五通桥区盐码头小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15883381415';

-- 韩丰超 / 四川省汉王山监狱 / 18008112957
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '韩丰超', '四川省汉王山监狱', '18008112957', 'Aa@18008112957', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18008112957'
);
UPDATE `user_account`
SET `nick_name` = '韩丰超', `organ_name` = '四川省汉王山监狱', `password` = 'Aa@18008112957', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18008112957';

-- 毛静云 / 乐山市沙湾小学 / 13981308316
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '毛静云', '乐山市沙湾小学', '13981308316', 'Aa@13981308316', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13981308316'
);
UPDATE `user_account`
SET `nick_name` = '毛静云', `organ_name` = '乐山市沙湾小学', `password` = 'Aa@13981308316', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13981308316';

-- 孙丽容 / 乐山市沙湾小学 / 13700937318
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '孙丽容', '乐山市沙湾小学', '13700937318', 'slr123456@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13700937318'
);
UPDATE `user_account`
SET `nick_name` = '孙丽容', `organ_name` = '乐山市沙湾小学', `password` = 'slr123456@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13700937318';

-- 徐育刚 / 乐山市沙湾小学 / 15884363588
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '徐育刚', '乐山市沙湾小学', '15884363588', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15884363588'
);
UPDATE `user_account`
SET `nick_name` = '徐育刚', `organ_name` = '乐山市沙湾小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15884363588';

-- 曾梦雪 / 乐山市实验小学 / 18284323673
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曾梦雪', '乐山市实验小学', '18284323673', 'ZMX19940807zmx.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18284323673'
);
UPDATE `user_account`
SET `nick_name` = '曾梦雪', `organ_name` = '乐山市实验小学', `password` = 'ZMX19940807zmx.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18284323673';

-- 周函燕 / 宣汉县 / 15082892704
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '周函燕', '宣汉县', '15082892704', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15082892704'
);
UPDATE `user_account`
SET `nick_name` = '周函燕', `organ_name` = '宣汉县', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15082892704';

-- 甘家惠 / 市教育和体育局 / 13541500216
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '甘家惠', '市教育和体育局', '13541500216', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13541500216'
);
UPDATE `user_account`
SET `nick_name` = '甘家惠', `organ_name` = '市教育和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13541500216';

-- 姚蕾 / 市教育和体育局 / 18783906863
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '姚蕾', '市教育和体育局', '18783906863', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18783906863'
);
UPDATE `user_account`
SET `nick_name` = '姚蕾', `organ_name` = '市教育和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18783906863';

-- 倪晓凡 / 市教育和体育局 / 13980201080
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '倪晓凡', '市教育和体育局', '13980201080', 'Aa@13980201080', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13980201080'
);
UPDATE `user_account`
SET `nick_name` = '倪晓凡', `organ_name` = '市教育和体育局', `password` = 'Aa@13980201080', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13980201080';

-- 王燕 / 市教育和体育局 / 13698306637
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王燕', '市教育和体育局', '13698306637', 'Fantingshan2004@', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13698306637'
);
UPDATE `user_account`
SET `nick_name` = '王燕', `organ_name` = '市教育和体育局', `password` = 'Fantingshan2004@', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13698306637';

-- 周定伟 / 四川省汉王山监狱 / 18682598090
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '周定伟', '四川省汉王山监狱', '18682598090', 'Aa@18682598090', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18682598090'
);
UPDATE `user_account`
SET `nick_name` = '周定伟', `organ_name` = '四川省汉王山监狱', `password` = 'Aa@18682598090', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18682598090';

-- 余春秀 / 乐山市沙湾小学 / 13881396628
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '余春秀', '乐山市沙湾小学', '13881396628', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13881396628'
);
UPDATE `user_account`
SET `nick_name` = '余春秀', `organ_name` = '乐山市沙湾小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13881396628';

-- 程厚东 / 四川省汉王山监狱 / 19160059113
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '程厚东', '四川省汉王山监狱', '19160059113', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19160059113'
);
UPDATE `user_account`
SET `nick_name` = '程厚东', `organ_name` = '四川省汉王山监狱', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19160059113';

-- 邹凌鹰 / 市教育和体育局 / 13568058885
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邹凌鹰', '市教育和体育局', '13568058885', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13568058885'
);
UPDATE `user_account`
SET `nick_name` = '邹凌鹰', `organ_name` = '市教育和体育局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13568058885';

-- 叶晓兰 / 市教育和体育局 / 13568029486
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '叶晓兰', '市教育和体育局', '13568029486', 'Aa@13568029486', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13568029486'
);
UPDATE `user_account`
SET `nick_name` = '叶晓兰', `organ_name` = '市教育和体育局', `password` = 'Aa@13568029486', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13568029486';

-- 戚书丹 / 乐山市实验小学 / 18784565048
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '戚书丹', '乐山市实验小学', '18784565048', '1466914135Wsx!', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18784565048'
);
UPDATE `user_account`
SET `nick_name` = '戚书丹', `organ_name` = '乐山市实验小学', `password` = '1466914135Wsx!', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18784565048';

-- 杨燕 / 乐山市城南学校 / 13540552281
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '杨燕', '乐山市城南学校', '13540552281', '652888yy$', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13540552281'
);
UPDATE `user_account`
SET `nick_name` = '杨燕', `organ_name` = '乐山市城南学校', `password` = '652888yy$', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13540552281';

-- 陈颖静 / 广元市利州区万达实验学校 / 15228142819
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈颖静', '广元市利州区万达实验学校', '15228142819', 'Aa@15228142819', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15228142819'
);
UPDATE `user_account`
SET `nick_name` = '陈颖静', `organ_name` = '广元市利州区万达实验学校', `password` = 'Aa@15228142819', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15228142819';

-- 罗琴 / 广元市利州区万达实验学校 / 13350038621
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '罗琴', '广元市利州区万达实验学校', '13350038621', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13350038621'
);
UPDATE `user_account`
SET `nick_name` = '罗琴', `organ_name` = '广元市利州区万达实验学校', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13350038621';

-- 李文君 / 广元市利州区万达实验学校 / 18181018375
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李文君', '广元市利州区万达实验学校', '18181018375', 'Aa@18181018375', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18181018375'
);
UPDATE `user_account`
SET `nick_name` = '李文君', `organ_name` = '广元市利州区万达实验学校', `password` = 'Aa@18181018375', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18181018375';

-- 潘慧 / 沐川县第二实验小学 / 18781362449
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '潘慧', '沐川县第二实验小学', '18781362449', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18781362449'
);
UPDATE `user_account`
SET `nick_name` = '潘慧', `organ_name` = '沐川县第二实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18781362449';

-- 肖汉 / 县公安局 / 13890363319
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '肖汉', '县公安局', '13890363319', 'Xiaohan100200.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13890363319'
);
UPDATE `user_account`
SET `nick_name` = '肖汉', `organ_name` = '县公安局', `password` = 'Xiaohan100200.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13890363319';

-- 江云川 / 安岳县人民医院 / 15884225859
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '江云川', '安岳县人民医院', '15884225859', 'jyc789086123.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15884225859'
);
UPDATE `user_account`
SET `nick_name` = '江云川', `organ_name` = '安岳县人民医院', `password` = 'jyc789086123.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15884225859';

-- 吴泽君 / 安岳县人民医院 / 13688278504
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '吴泽君', '安岳县人民医院', '13688278504', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13688278504'
);
UPDATE `user_account`
SET `nick_name` = '吴泽君', `organ_name` = '安岳县人民医院', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13688278504';

-- 胡安婷 / 安岳县人民医院 / 18228482236
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '胡安婷', '安岳县人民医院', '18228482236', 'Aa@18228482236', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18228482236'
);
UPDATE `user_account`
SET `nick_name` = '胡安婷', `organ_name` = '安岳县人民医院', `password` = 'Aa@18228482236', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18228482236';

-- 廖晓波 / 富牛小学 / 13982801769
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '廖晓波', '富牛小学', '13982801769', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13982801769'
);
UPDATE `user_account`
SET `nick_name` = '廖晓波', `organ_name` = '富牛小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13982801769';

-- 唐光强 / 富牛小学 / 13990355642
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '唐光强', '富牛小学', '13990355642', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13990355642'
);
UPDATE `user_account`
SET `nick_name` = '唐光强', `organ_name` = '富牛小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13990355642';

-- 李丹 / 富牛小学 / 13558551739
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '李丹', '富牛小学', '13558551739', 'Aa@13558551739', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13558551739'
);
UPDATE `user_account`
SET `nick_name` = '李丹', `organ_name` = '富牛小学', `password` = 'Aa@13558551739', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13558551739';

-- 任忠秀 / 富牛小学 / 13795509554
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '任忠秀', '富牛小学', '13795509554', 'Aa@13795509554', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13795509554'
);
UPDATE `user_account`
SET `nick_name` = '任忠秀', `organ_name` = '富牛小学', `password` = 'Aa@13795509554', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13795509554';

-- 王国洪 / 齐通初中 / 13419076678
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王国洪', '齐通初中', '13419076678', 'Aa@13419076678', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '13419076678'
);
UPDATE `user_account`
SET `nick_name` = '王国洪', `organ_name` = '齐通初中', `password` = 'Aa@13419076678', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '13419076678';

-- 王泽孝 / 富牛小学 / 15298143978
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '王泽孝', '富牛小学', '15298143978', 'Aa@15298143978', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15298143978'
);
UPDATE `user_account`
SET `nick_name` = '王泽孝', `organ_name` = '富牛小学', `password` = 'Aa@15298143978', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15298143978';

-- 陈菊红 / 富牛小学 / 18980369616
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '陈菊红', '富牛小学', '18980369616', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18980369616'
);
UPDATE `user_account`
SET `nick_name` = '陈菊红', `organ_name` = '富牛小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18980369616';

-- 樊万强 / 沐川县公安局 / 18728873898
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '樊万强', '沐川县公安局', '18728873898', 'fwq.041142', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18728873898'
);
UPDATE `user_account`
SET `nick_name` = '樊万强', `organ_name` = '沐川县公安局', `password` = 'fwq.041142', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18728873898';

-- 曾荣安 / 沐川县实验小学 / 18328812156
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '曾荣安', '沐川县实验小学', '18328812156', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18328812156'
);
UPDATE `user_account`
SET `nick_name` = '曾荣安', `organ_name` = '沐川县实验小学', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18328812156';

-- 邓茜月 / 城西幼儿园 / 15775871666
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '邓茜月', '城西幼儿园', '15775871666', 'Aa@15775871666', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15775871666'
);
UPDATE `user_account`
SET `nick_name` = '邓茜月', `organ_name` = '城西幼儿园', `password` = 'Aa@15775871666', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15775871666';

-- 滕曦 / 城西幼儿园 / 18284170027
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '滕曦', '城西幼儿园', '18284170027', 'Aa@18284170027', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '18284170027'
);
UPDATE `user_account`
SET `nick_name` = '滕曦', `organ_name` = '城西幼儿园', `password` = 'Aa@18284170027', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '18284170027';

-- 刘城 / 沐川县公安局 / 15298000095
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '刘城', '沐川县公安局', '15298000095', 'liu198431cheng.', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '15298000095'
);
UPDATE `user_account`
SET `nick_name` = '刘城', `organ_name` = '沐川县公安局', `password` = 'liu198431cheng.', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '15298000095';

-- 郭健 / 沐川县公安局 / 19981566509
INSERT INTO `user_account` (`website_code`, `nick_name`, `organ_name`, `username`, `password`, `create_time`, `update_time`)
SELECT 'SCGB', '郭健', '沐川县公安局', '19981566509', 'Abcd1234', NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (
  SELECT 1 FROM `user_account` WHERE `website_code` = 'SCGB' AND `username` = '19981566509'
);
UPDATE `user_account`
SET `nick_name` = '郭健', `organ_name` = '沐川县公安局', `password` = 'Abcd1234', `update_time` = NOW()
WHERE `website_code` = 'SCGB' AND `username` = '19981566509';

-- 共 405 个账号（同 username 按最后一条去重；跳过缺账号/密码 0 行）
