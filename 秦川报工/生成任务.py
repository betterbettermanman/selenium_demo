"""根据当天 git 提交生成任务信息、报工说明、commitId 和提交记录截图。不创建、不排产、不报工。"""

import json
import os

import 新增任务_排产_报工 as task_flow
from 直接报工 import create_driver, log

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    day = task_flow.target_day()
    grouped = task_flow.collect_commits(day)
    log.info("开始整理任务说明")
    task = task_flow.build_task(grouped, day)
    if not task:
        log.info("%s 没有提交记录，不生成任务信息", day.isoformat())
        return
    log.info("开始整理报工说明")
    work_description = task_flow.build_work_description(grouped, task["name"])
    commit_id = task_flow.commit_ids(grouped)
    output_dir = os.path.join(HERE, "output", day.isoformat())
    os.makedirs(output_dir, exist_ok=True)
    driver = create_driver()
    try:
        screenshot = task_flow.render_commit_screenshot(driver, grouped, day, output_dir)
    finally:
        driver.quit()
    payload = {
        "date": day.isoformat(),
        "任务信息": {
            "任务名称": task["name"],
            "岗位": task["position"],
            "涉及端": task["scope"],
            "任务描述": task["description"],
        },
        "报工信息": work_description,
        "commitId": commit_id,
        "提交信息截图": screenshot,
    }
    if not (task.get("description") or "").strip():
        raise RuntimeError("没有按模板生成任务描述")
    output_path = os.path.join(output_dir, "任务信息.json")
    text_path = os.path.join(output_dir, "任务信息.txt")
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")
    with open(text_path, "w", encoding="utf-8") as text_file:
        text_file.write(render_text(payload))
    info = payload["任务信息"]
    log.info("任务名称：%s", info["任务名称"])
    log.info("岗位：%s", info["岗位"])
    log.info("任务描述：\n%s", info["任务描述"])
    log.info("报工信息：\n%s", payload["报工信息"])
    log.info("提交ID：%s", payload["commitId"])
    log.info("提交截图：%s", payload["提交信息截图"])
    log.info("已写入 %s", output_path)
    log.info("已写入 %s", text_path)


def render_text(payload):
    info = payload["任务信息"]
    return (
        f"日期：{payload['date']}\n\n"
        "任务信息\n"
        f"任务名称：{info['任务名称']}\n"
        f"岗位：{info['岗位']}\n"
        f"涉及端：{info['涉及端']}\n"
        f"任务描述：\n{info['任务描述']}\n\n"
        "报工信息\n"
        f"{payload['报工信息']}\n\n"
        f"commitId：{payload['commitId']}\n\n"
        f"提交信息截图：{payload['提交信息截图']}\n"
    )


if __name__ == "__main__":
    main()
