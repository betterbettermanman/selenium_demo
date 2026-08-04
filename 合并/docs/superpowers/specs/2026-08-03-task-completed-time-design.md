# 任务完成时间设计

## 背景

任务列表仅有 `create_time` / `update_time`。`update_time` 在任意编辑时刷新，不能作为完成时间。

## 决策

- 新增字段 `task.completed_time`（DateTime，可空）
- 当 `status` 被设为 `'2'`（完成）时写入当前时间（再次完成则覆盖）
- 当 `status` 回退为 `'1'`（未完成/停止/异常）时**保留**原完成时间，不清空

## 实现要点

1. SQL：`migrate_add_task_completed_time.sql` + 更新 `init.sql`
2. 模型 `Task.completed_time` + `to_dict`
3. `update_task_fields`：若本次 `status=='2'` 且未显式传 `completed_time`，自动设 `datetime.now()`
4. 导出 Excel 增加「完成时间」列
5. 前端桌面/移动任务列表展示；空值显示 `-`

## 非目标

- 不回溯历史已完成任务的完成时间（存量保持 NULL）
- 不做按完成时间筛选/排序（可后续加）
