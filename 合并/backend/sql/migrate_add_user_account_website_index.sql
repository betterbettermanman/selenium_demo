USE `task_manager`;

-- 用户账号列表 JOIN 查询加速
ALTER TABLE `user_account`
  ADD INDEX `idx_user_account_website_code` (`website_code`);
