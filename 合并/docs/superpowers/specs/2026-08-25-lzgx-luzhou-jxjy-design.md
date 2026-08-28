# 泸州公需课（LZGX）自动登录与课程学习设计

日期：2026-08-25  
状态：已确认（待实现）

## 背景

任务管理系统已支持广元（GYGX）、眉山（MSGX）、内江（NJGX）、乐山（LSGX）等公需课执行器。需新增 **泸州职业技术学院专业技术人员继续教育网**（`https://jxjy.lzy.edu.cn/`），支持自动登录与按课程自动播放。

站点为传统 jQuery + 服务端渲染：首页表单登录（身份证 + 密码 + 图形验证码），登录 Cookie `lzrspx_front`；课程列表在 `/reg/userStudy?courseId=`，播放在新窗口 `/reg/userStudy/videoStudy/{userStudyId}`，每 10 秒 POST `/reg/userStudy/record` 记学时。

## 目标（本期）

1. 新增网站类型：编码 `LZGX`，名称「泸州公需课」。
2. 自动登录：身份证号 + 密码 + 图形验证码（ddddocr）。
3. 按任务 `class_id`（课程 ID / `courseId`）打开学习列表，自动播放未完成视频。
4. 本课所有小节进度均为 100%（「已完成」）后标记任务完成。

## 非目标

- 在线考试 / 答题 / 证书
- 短信验证码登录（`enable_sms_code=0`）
- 纯 API 刷学时（不绕过页面播放）
- 依赖 `task.courses` JSON 课表（仅用 `class_id`）
- 改动前端 UI

## 方案选择

采用独立 `LzgxTaskRunner`（继承 `SeleniumTaskRunner`），通过 **同浏览器窗口句柄切换** 完成列表页 ↔ 播放页循环（对齐 GYGX），不另起 WebDriver、不直达无关 URL 重建会话。

## 架构

| 层 | 改动 |
|---|---|
| 数据 | 网站表新增：`LZGX` / 泸州公需课 / `https://jxjy.lzy.edu.cn/` / `enable_sms_code=0` |
| 执行器 | 新建 `backend/services/runners/lzgx_runner.py`，`@register_runner('LZGX')` |
| 注册 | `backend/services/runners/__init__.py` 导入该类 |
| 种子 | `backend/sql/seed_lzgx_website.sql` |
| 前端 | 无改动 |

## 任务字段约定

| 字段 | 用途 |
|---|---|
| `website_code` | `LZGX` |
| `class_id` | 课程 ID（`courseId`），例如 `8ad2e7349e38942c019e96ec953a0040`；**不含**完整 URL |
| `username` / `password` | 身份证号 / 登录密码 |
| 完成条件 | 学习列表中所有小节进度文本含 `100%` 或「已完成」→ `status=2` |

缺少非空 `class_id` 时任务启动即失败。

学习页 URL 由常量拼装：

`https://jxjy.lzy.edu.cn/reg/userStudy?courseId={class_id}`

## 登录与会话

### 登录步骤

1. 打开 `https://jxjy.lzy.edu.cn/`。
2. 若存在 layer「温馨提示」等弹层，关闭（`.layui-layer-close` / `.layui-layer-ico`）。
3. 等待 `#username`、`#password`、`#captcha` 可交互；填入账号密码。
4. 对 `#imgcode`（`/web/loginImage`）截图，用 `_recognize_captcha_screenshot` / ddddocr 识别后填入 `#captcha`。
5. 点击 `.btn_dl`（`onclick=login()` → POST `/login`）。
6. 成功：跳转 `/reg/index`（或带 `?tab=1`）；失败：layer 提示，刷新验证码后重试。

### 登录态判定

满足任一即可：

- 当前 URL 含 `/reg/`，且页面存在「注销登录」链接（`/logout`）
- Cookie 存在 `lzrspx_front` **且** 能打开 `/reg/index` 并看到学员姓名区域

未登录则 `_auto_login`，`_ensure_logged_in` 上限约 5 轮。

### 会话硬约束

- 登录后不另起浏览器配置目录、不随意 `driver.get` 到无关外链以重建会话。
- **课程列表页**始终保留为一个 window handle（`list_window`）。
- 播放由站点 `videoStudy(id)` 新开 `target=videoStudy` → `switch_to.window` 到播放页；播完切回列表页并关闭播放页。
- 禁止为播放主动 `window.open` 空白页或另起 WebDriver。

## 选课与播放循环

### 进入课程

1. 登录成功后（可顺带关掉学员中心「网站通告」弹层）。
2. `driver.get` 学习列表 URL（见上）。
3. 校验页面含「课程名称」或课件表格；若被重定向到登录页则重新登录。
4. 记录当前窗口为 `list_window`。

### 列表解析

表格行结构（在线学习页）：

| 课件标题 | … | 学习进度 | 在线学习 |
|---|---|---|---|
| … | … | `100.0%（已完成）` / `0.0%（未学习）` | `<a onclick="videoStudy('…')">学习</a>` |

- **已完成**：进度单元格文本含 `100%` 或「已完成」
- **未完成**：其余行；点击该行「学习」链接（执行站点 `videoStudy`）

课程头信息「必修 x/y 学时」仅作日志，**不作为**本期完成条件。

### 播放循环

1. 在列表中找第一节未完成课件，点击「学习」。
2. 等待新窗口出现（URL 含 `/reg/userStudy/videoStudy/`），切换到 `play_window`。
3. 等待 `#video` 可播放；必要时 `video.play()`；站点 `canplaythrough` 后会自行 `play` 并每 10 秒 `sendMsg`。
4. 监控线程（或主循环短轮询）：
   - 若出现「继续学习」类 layer 确认（暂停 / 超时观看），点击「继续学习」并确保 `video.play()`
   - 检测 `video.ended` 或进度相关文案；也可定时切回列表刷新判断该节是否已达 100%
5. 判定本节完成：切回 `list_window`，刷新列表（`driver.refresh` 或重新 `get` 列表 URL），对应行已为 100% / 已完成；关闭 `play_window`。
6. 找下一节未完成，重复 1–5。
7. 无未完成项 → `is_complete=True`，`status=2`，结束。

### 播放页注意点（实现时遵守）

- 站点禁止拖动进度条（拖动不计学时）；自动化 **不要** seek 进度。
- 窗口失焦会 `pause`；执行器应尽量保持播放窗焦点，或自动处理「继续学习」弹窗。
- 单日有效学时上限等长文案告警：记日志；若站点停止计时（`state=0`），结束当前播放并回列表评估是否继续其他节 / 结束本次执行。

## 错误处理

| 场景 | 处理 |
|---|---|
| 登录失败 / 验证码错误 | 刷新 `#imgcode` 重试，上限约 5 次；仍失败则任务失败 |
| `class_id` 为空或课程页无法打开 | 错误日志，任务失败 |
| 新播放窗口未出现 | 超时后重试点击；仍失败则任务失败 |
| 监控中掉登录 | 停止循环，任务失败/进行中，关浏览器 |
| 用户手动停止 | 现有 `request_stop`，关浏览器 |

### 收尾

- 正常全部完成：`status=2`，关浏览器。
- 异常：沿用 `SeleniumTaskRunner` 收尾，`status=1` 或保持进行中，关浏览器。

## 关键文件

- `backend/services/runners/lzgx_runner.py`（新建）
- `backend/services/runners/__init__.py`（注册导入）
- `backend/sql/seed_lzgx_website.sql`（新建）

## 验证

1. 启动后 `_runner_registry` 含 `LZGX`。
2. 有真实账号时冒烟：登录 → `class_id` 进列表 → 播一节未完成课 → 回列表见进度上升 → 全部完成后 `status=2`。

## 决议摘要

- 范围：自动登录 + 自动播课；本课小节全 100% 即完成；不做考试。
- 选课：`class_id` = `courseId`（非 URL）。
- 窗口模型：保留列表页 + 站点新开播放页，句柄切换。
- 编码：`LZGX`；名称：泸州公需课。
