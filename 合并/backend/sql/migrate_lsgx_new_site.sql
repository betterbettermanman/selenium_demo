-- 乐山公需（LSGX）站点从 ls1018.com.cn 迁到 lssjjw.63ym.cn
-- 课程 class_id 与任务 class_id 必须一起改，任务列表按二者关联课程。

UPDATE website
SET url = 'http://lssjjw.63ym.cn/',
    update_time = NOW()
WHERE code = 'LSGX';

UPDATE course
SET class_id = 'http://lssjjw.63ym.cn/coursedetail.aspx?id=118',
    update_time = NOW()
WHERE website_code = 'LSGX'
  AND class_id = 'https://www.ls1018.com.cn/course/118.html';

UPDATE task
SET class_id = 'http://lssjjw.63ym.cn/coursedetail.aspx?id=118',
    update_time = NOW()
WHERE website_code = 'LSGX'
  AND class_id = 'https://www.ls1018.com.cn/course/118.html';
