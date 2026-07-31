# 任务列表「打开浏览器」设计

日期：2026-07-31

## 目标

任务管理操作列增加「打开浏览器」：用任务专属 Chrome 用户目录、有头模式打开关联网站 URL，不启动学习流程。

## 行为

- `POST /api/tasks/<id>/open-browser`
- user-data-dir：`browser_data/{website.code}/{task.id}/{username}`（与执行器一致）
- 强制有头；重复点击复用已有窗口并 `get(url)`
- 任务 `is_running` 时拒绝打开，避免与执行器抢同一目录
- 无网站 / 无有效 URL 时返回明确错误

## 前端

- PC / 手机任务列表操作区增加按钮，loading 防重复
- 不改启动 / 关闭语义
