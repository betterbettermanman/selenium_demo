# 广元公需课（GYGX）自动登录与播放设计

日期：2026-07-23  
状态：已确认（待实现）

## 背景

任务管理系统已支持乐山（LSGX）、眉山（MSGX）、内江（NJGX）、四川干部（SCGB）等网站执行器。需新增 **广元公需课**（广元市继续教育网），支持自动登录与自动播放。

站点：`https://www.gysjxjy.com:90/`  
技术栈观察：Vue + Element UI SPA；登录态主要依赖浏览器会话缓存（sessionStorage），与内江/乐山「直达播放 URL」模式不兼容。

## 目标

1. 新增网站类型：编码 `GYGX`，名称「广元公需课」。
2. 自动登录（账号 + 密码 + 图形验证码）。
3. 按 `class_id` 进入「我的课程」中的目标课，自动播放未完成视频。
4. 本课视频全部播完后标记任务完成；不做考试、不启用短信登录。

## 非目标

- 自动考试 / 答题
- 短信验证码登录（`enable_sms_code=0`）
- 纯 API 刷进度
- 对齐内江/乐山的 `driver.get` 直达播放页方案

## 方案选择

采用独立 `GygxTaskRunner`（继承 `SeleniumTaskRunner`），通过 **同浏览器窗口句柄切换** 完成列表页 ↔ 播放页循环，避免重建会话。

## 架构

| 层 | 改动 |
|---|---|
| 数据 | 网站表新增：`GYGX` / 广元公需课 / `https://www.gysjxjy.com:90/` / `enable_sms_code=0`（UI 录入或 SQL 种子均可） |
| 执行器 | 新建 `backend/services/runners/gygx_runner.py`，`@register_runner('GYGX')` |
| 注册 | `backend/services/runners/__init__.py` 导入该类 |
| 前端 | 无改动；沿用现有网站/任务管理 |

任务以 `class_id` 精确匹配目标课程。

## 登录与会话

### 登录步骤

1. 打开 `https://www.gysjxjy.com:90/`（或 `/Index`）。
2. 若存在「特别提醒」弹窗，点击 `.sure-btn` 关闭。
3. 「学员培训登录」下点击「登录」（`.my.cursor`）展开表单。
4. 确保「账号登录」Tab 激活（非「验证码登录」）。
5. 填写账号、密码；对图形验证码截图并用 ddddocr 识别（复用 `_recognize_captcha_screenshot`）。
6. 点击 `.login-btn` 提交；失败则重试（约 5 次）。

### 登录态判定

实现时探测 sessionStorage / cookie 中的登录字段，或页面出现「个人中心」等已登录入口。

### 会话硬约束

- 登录后不另起浏览器配置目录、不随意 `driver.get` 到无关外链以重建会话。
- **课程列表页**始终保留为一个 window handle（`list_window`）。
- 播放由站点自行新开页 → `switch_to.window` 到播放页；播完切回列表页并关闭播放页。
- 禁止为播放主动 `window.open` 空白页或另起 WebDriver。

## 选课与播放循环

### 进入课程

1. 首页 → 个人中心 → 我的课程。
2. 用任务 `class_id` 在列表中精确匹配并进入。
3. 记录当前窗口为 `list_window`。

### 播放循环

1. 在列表中找进度未满（≠100%）的第一节，点击播放。
2. 等待新窗口出现，切换到 `play_window`。
3. 启动监控线程：检测播放进度与播放状态（暂停则尝试继续）。
4. 进度达到 100% 后：切回 `list_window`，关闭 `play_window`。
5. 在列表页点击「查询」刷新进度。
6. 找下一节未完成视频，重复 1–5。
7. 无未完成项 → `status=2`，结束。

### 匹配规则

- 仅使用 `class_id` 精确匹配。
- 找不到对应课程 → 任务失败并写错误日志。

## 错误处理

| 场景 | 处理 |
|---|---|
| 登录失败 / 验证码错误 | 刷新验证码重试，上限约 5 次；仍失败则 `status=1` 并抛错 |
| 找不到 `class_id` 对应课程 | 错误日志，任务失败 |
| 新播放窗口未出现 | 超时后重试点击；仍失败则失败 |
| 监控中页面异常 / 掉登录 | 停止循环，任务置失败/进行中，关闭浏览器 |
| 用户手动停止 | 现有 `request_stop`，关闭浏览器 |

### 收尾

- 正常播完：`status=2`，关浏览器。
- 异常：必要时 rollback session，`status=1`，关浏览器。

## 关键文件

- `backend/services/runners/gygx_runner.py`（新建）
- `backend/services/runners/__init__.py`（注册导入）
- 可选：`backend/sql/` 种子或迁移说明；或依赖网站管理 UI 手工新增

## 验证

1. 启动后 `_runner_registry` 含 `GYGX`。
2. 有真实账号时冒烟：登录 → 按 `class_id` 进课 → 播一节 → 回列表点「查询」刷新进度。

## 决议摘要

- 范围：自动登录 + 自动播放；视频播完即完成，不做考试。
- 选课：`class_id`。
- 窗口模型：保留列表页 + 站点新开播放页，句柄切换，禁止对齐内江/乐山直达 URL。
- 编码：`GYGX`。
