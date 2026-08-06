# 四川智慧中小学平台（SCZH）设计

日期：2026-08-05  
状态：已确认（待实现）

## 背景

任务管理系统已支持国家中小学智慧教育平台（`ZXZH`，`basic.smartedu.cn`）等执行器。需新增 **四川智慧中小学平台**（`basic.sc.smartedu.cn`），参考独立脚本 `selenium_demo/四川智慧教育平台2`。

该站点与 ZXZH 不同：登录走四川 ThirdPortal 账号密码页（无腾讯滑块），课程在教师研修详情页按小节播放，进度通过 `chapterProcess` 接口查询。

## 目标（本期）

1. 新增网站类型：编码 `SCZH`，名称「四川智慧中小学平台」。
2. 自动登录：账号 + 密码（ThirdPortal 登录 URL）。
3. 按任务 `class_id`（课程详情页 URL）自动扫描未学小节并播放视频。
4. 通过 `chapterProcess` 接口轮询小节进度，学完后切换下一节；全部「已学习」后任务完成。

## 非目标

- 考试 / AI 答题（源脚本虽有代码，本期不移植）
- 依赖 `task.courses` JSON 课表配置（采用方案 A：仅 `class_id`）
- 短信验证码登录（`enable_sms_code=0`）
- 改动前端 UI（沿用现有网站/任务管理）
- 与 ZXZH 共用同一 runner（站点差异大，独立实现）

## 方案选择

采用独立 `SczhTaskRunner`（继承 `SeleniumTaskRunner`），与现有站点执行器模式一致。逻辑移植自 `四川智慧教育平台2/main.py` 的登录与播课主路径，并纳入合并项目的任务状态、浏览器隔离、停止信号等基础设施。

## 架构

| 层 | 改动 |
|---|---|
| 数据 | 网站表新增：`SCZH` / 四川智慧中小学平台 / `https://basic.sc.smartedu.cn/` / `enable_sms_code=0`（SQL 种子或 UI 录入） |
| 执行器 | 新建 `backend/services/runners/sczh_runner.py`，`@register_runner('SCZH')` |
| 注册 | `backend/services/runners/__init__.py` 导入该类 |
| 种子 | `backend/sql/seed_sczh_website.sql` |
| 前端 | 无改动 |

## 任务字段约定

| 字段 | 用途 |
|---|---|
| `website_code` | `SCZH` |
| `class_id` | 课程详情页完整 URL，须含 `courseId`，例如 `https://basic.sc.smartedu.cn/hd/teacherTraining/coursedatail?courseId=xxxx` |
| `username` / `password` | 平台账号密码 |
| `courses` | 配置总目标：`{"sum": 16}`（创建任务时写入 task.courses） |
| 完成条件 | 页面已学列表数 >= sum 才 `status=2`；当前课学完但未达 sum 只结束本次执行 |

缺少合法 `class_id`（非 http 开头）时任务启动即失败。

## 登录与会话

### 登录 URL

固定 ThirdPortal 入口（与源脚本一致）：

`https://basic.sc.smartedu.cn/ThirdPortalService/user/otherlogin!login.ac?appkey=...&pkey=...&params=...`

（实现时将完整 URL 定义为模块常量。）

### 登录步骤

1. 打开登录 URL。
2. 等待 `#loginName`、`#password` 可交互，填入账号密码。
3. 点击 `.submit-btn`。
4. 若 5 秒内出现含「取消」文本的 `a` 链接，则点击关闭弹层。
5. 检测 Cookie `Teaching_Autonomic_Learning_Token`；存在则视为已登录，并写入请求头 `x-token` 供进度接口使用。

### 登录态判定

- 主信号：Cookie `Teaching_Autonomic_Learning_Token`
- 未登录则调用 `_auto_login`，在 `_ensure_logged_in` 轮次上限内重试

## 播课与进度

### 打开课程

1. `driver.get(task.class_id)`。
2. 查找 `.course-list-cell`。
3. 对每个 cell：若子元素 `.status` 文本为「已学习」则跳过；否则点击该 cell。
4. 等待 `#video` 可点击，执行 `arguments[0].play()`。
5. 从当前 URL 解析 `subsectionId` 作为当前小节 ID。

### chapterId 解析（方案 B）

进度接口需要 `chapterId`（与 `courseId` / `subsectionId` 不同）。解析顺序：

1. 从当前页 URL / hash 查询参数取 `chapterId`
2. 从页面 DOM、内嵌脚本或已加载接口响应中匹配
3. 仍取不到则记日志并短暂等待后重试；连续失败则回到课程页重开未学小节

### 进度轮询

- 请求：`GET https://basic.sc.smartedu.cn/hd/teacherTraining/api/studyCourseUser/chapterProcess?chapterId={chapterId}`
- Header：携带 Cookie / `x-token`（`Teaching_Autonomic_Learning_Token`）
- 在 `returnData.studySubsectionUsers` 中匹配当前 `subsectionId`
- `schedule >= 100`：回课程页打开下一未学小节
- 未完成：随机间隔约 150–300 秒再查
- 同一睡眠间隔连续过多次无进展：重新检测登录并重开课程页

### 完成条件

课程页所有 `.course-list-cell` 均为「已学习」（或不存在可点的未学项）→ `is_complete=True`，同步任务状态为完成（`status=2`）。

## 错误处理

| 场景 | 处理 |
|---|---|
| 登录失败 / Cookie 丢失 | 重新登录；超过轮次则任务失败 |
| 页面 / ChromeDriver 超时 | 基类 `_driver_get` 有限次重试 |
| 进度接口失败 | 记日志，短暂等待重试；疑似掉登录则先确保登录 |
| 找不到 `#video` 或小节列表 | 回课程页重试；连续失败则任务失败 |
| 用户手动停止 | 响应 `_stopped`，关闭浏览器 |

### 收尾

与现有 Selenium runner 一致：`finally` 中 `_finalize_run` 关闭浏览器并清理状态。

## 验收标准

1. 执行种子 SQL 或 UI 可新增网站「四川智慧中小学平台 / SCZH」。
2. 创建任务并填写 `class_id`（课程详情 URL）+ 账号密码后，可自动登录。
3. 能自动点击未学小节并播放；接口进度满后切换下一节。
4. 全部小节「已学习」后任务标记完成。

## 参考

- 源脚本：`selenium_demo/四川智慧教育平台2/main.py`（`auto_login` / `open_home` / `check_course_success`）
- 合并基类：`backend/services/runners/selenium_runner.py`
- 相近站点：`zxzh_runner.py`（国家站，仅作任务字段与注册模式参考）
