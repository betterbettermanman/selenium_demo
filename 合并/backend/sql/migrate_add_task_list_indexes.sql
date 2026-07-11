USE `task_manager`;

ALTER TABLE `website`
  ADD INDEX `idx_website_code` (`code`);

ALTER TABLE `course`
  ADD INDEX `idx_course_website_class` (`website_code`, `class_id`);

ALTER TABLE `task`
  ADD INDEX `idx_task_website_code` (`website_code`),
  ADD INDEX `idx_task_status_id` (`status`, `id`);
