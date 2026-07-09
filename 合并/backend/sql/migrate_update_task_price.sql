-- 价格改为整数、默认空
USE `task_manager`;

ALTER TABLE `task`
  MODIFY COLUMN `price` int DEFAULT NULL COMMENT '价格';

UPDATE `task` SET `price` = NULL WHERE `price` = 0;
