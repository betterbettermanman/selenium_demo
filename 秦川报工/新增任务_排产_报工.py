"""根据 296 仓库指定日期的提交，调用大模型按开发任务模板生成任务并新增。"""

import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timedelta
from html import escape

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from 直接报工 import (
    ASSIGNEE,
    ENV_PATH,
    USERNAME,
    _env_value,
    load_env,
    _modal_ready,
    _saved as work_hour_saved,
    click_work_hour,
    create_driver,
    log,
    login,
    select_assignee_and_search,
)

from model_client import generate_text

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(HERE, "template")
DEFAULT_TEMPLATE = "开发任务填报-父任务模版.md"
TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, DEFAULT_TEMPLATE)
TASK_TEMPLATES = {
    "开发任务填报-父任务模版.md": {
        "kind": "父任务",
        "title": "父任务名称",
        "required_fields": ("需求背景", "技术性描述"),
    },
    "开发任务填报-子任务模版.md": {
        "kind": "子任务",
        "title": "任务名称",
        "required_fields": ("任务名称", "涉及端"),
    },
    "非开发工作场景与交付要求填报说明.md": {
        "kind": "非开发任务",
        "title": "任务名称",
        "required_fields": (
            "工作类别",
            "工作场景",
            "工作内容及边界",
            "交付内容",
            "交付方式",
            "交付要求",
            "评估标准（基线工时）",
        ),
    },
}

TASK_LIST_URL = "https://scic.cdqckj.com:65036/businessFlow/taskManagement/taskList"
TASK_SCHEDULING_URL = "https://scic.cdqckj.com:65036/businessFlow/taskManagement/taskScheduling"
TASK_EXECUTE_URL = "https://scic.cdqckj.com:65036/businessFlow/taskManagement/taskExecute"
TASK_CATEGORY = "development"
DEFAULT_WORK_DESCRIPTION_MAX_LENGTH = 60
POSITION_BY_SCOPE = {
    "前端": "前端工程师",
    "后端": "Java开发工程师",
    "全栈": "Java开发工程师",
}


def target_day():
    configured_day = (load_env(ENV_PATH).get("TASK_DATE") or "").strip()
    if configured_day:
        return datetime.strptime(configured_day, "%Y-%m-%d").date()
    return datetime.now().date()


def repo_root():
    return _env_value(load_env(ENV_PATH), "REPO_ROOT")


def find_repos(root):
    if not os.path.isdir(root):
        raise RuntimeError("Git 仓库目录不存在：%s，请检查 .env 中的 REPO_ROOT" % root)
    repos = []
    for dirpath, dirnames, _filenames in os.walk(root):
        if ".git" in dirnames:
            repos.append(dirpath)
        dirnames[:] = [name for name in dirnames if name not in {".git", "node_modules", "target", "dist"}]
    return repos


def side_of(repo):
    name = os.path.basename(repo).lower()
    if "frontend" in name or name.endswith("-web") or name.endswith("-ui"):
        return "前端"
    return "后端"


def read_commits(repo, day):
    since = day.strftime("%Y-%m-%d 00:00:00")
    until = (day + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    output = subprocess.check_output(
        [
            "git",
            "-C",
            repo,
            "log",
            "--no-merges",
            f"--since={since}",
            f"--until={until}",
            "--pretty=format:---%H%x09%ci%x09%s",
            "--name-only",
        ],
        encoding="utf-8",
        errors="replace",
    )
    commits = []
    current = None
    for line in output.splitlines():
        if line.startswith("---"):
            if current:
                commits.append(current)
            digest, committed_at, subject = line[3:].split("\t", 2)
            current = {
                "hash": digest,
                "time": committed_at.strip(),
                "subject": subject.strip(),
                "files": [],
            }
            continue
        if current and line.strip():
            current["files"].append(line.strip())
    if current:
        commits.append(current)
    return commits


def collect_commits(day):
    grouped = {"前端": [], "后端": []}
    for repo in find_repos(repo_root()):
        side = side_of(repo)
        commits = read_commits(repo, day)
        repo_name = os.path.basename(repo)
        log.info("%s %s %s提交 %s 条", side, repo_name,day, len(commits))
        for commit in commits:
            commit["repo"] = repo_name
            commit["side"] = side
        grouped[side].extend(commits)
    return grouped


def format_commits(grouped):
    lines = []
    for side in ("前端", "后端"):
        commits = grouped[side]
        if not commits:
            continue
        lines.append(f"【{side}】")
        for commit in commits:
            lines.append(f"- {commit['subject']}")
            if commit["files"]:
                lines.append("  改动文件：" + "、".join(commit["files"][:12]))
    return "\n".join(lines)


def selected_template():
    filename = (load_env(ENV_PATH).get("TASK_TEMPLATE") or "").strip() or DEFAULT_TEMPLATE
    if filename not in TASK_TEMPLATES:
        supported = "、".join(TASK_TEMPLATES)
        raise RuntimeError(f"不支持的模板：{filename}，可选值：{supported}")
    return filename


def load_template():
    filename = selected_template()
    with open(os.path.join(TEMPLATE_DIR, filename), encoding="utf-8") as template_file:
        text = template_file.read().strip()
    marker = "填写示例"
    if marker in text:
        body, example = text.split(marker, 1)
        return body.strip(), example.strip(), filename
    return text, "", filename


def validate_non_development_fields(raw, required_fields):
    values = {}
    for field in required_fields:
        matches = re.findall(rf"(?m)^{re.escape(field)}[ \t]*[：:][ \t]*(.*)$", raw)
        if len(matches) != 1 or not matches[0].strip():
            raise RuntimeError(f"非开发任务字段「{field}」必须恰好出现一次且内容不能为空")
        values[field] = matches[0].strip()
    if values["交付方式"] not in {"任务描述中写明即可", "需要额外附件", "两者结合"}:
        raise RuntimeError("非开发任务字段「交付方式」的值不符合模板要求")


def parse_task_text(text, template_filename=DEFAULT_TEMPLATE):
    config = TASK_TEMPLATES[template_filename]
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0].strip()
    raw = raw.split("填写示例", 1)[0].strip()
    if config["kind"] == "非开发任务":
        validate_non_development_fields(raw, config["required_fields"])
    elif not all(field in raw for field in config["required_fields"]):
        raise RuntimeError(f"大模型没有按{config['kind']}模板返回任务：{text}")
    lines = raw.splitlines()
    task_name = ""
    title_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("1.") or "需求背景" in stripped:
            break
        matched = re.match(r"^(?:【)?(?:父任务名称|任务名称)(?:】)?\s*[：:]\s*(.*)$", stripped)
        if matched and matched.group(1).strip():
            task_name = matched.group(1).strip("【】 ")
        else:
            task_name = stripped.strip("【】：: ")
        title_index = index
        break
    if not task_name:
        raise RuntimeError(f"大模型没有按模板返回任务：{text}")
    title = config["title"]
    if title_index is None:
        lines.insert(0, f"【{title}】：{task_name}")
    else:
        lines[title_index] = f"【{title}】：{task_name}"
    normalized = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("【") and stripped.endswith("】") and stripped.count("【") == 1:
            normalized.append(stripped[1:-1])
        else:
            normalized.append(line)
    description = "\n".join(normalized).strip()
    if config["kind"] == "非开发任务":
        description = re.sub(
            r"(?m)^评估标准（基线工时）[ \t]*[：:].*$",
            "评估标准（基线工时）：待确认",
            description,
        )
    return task_name, description


def load_model_config():
    values = load_env(ENV_PATH)
    return {
        "provider": (values.get("MODEL_PROVIDER") or "qoder").strip(),
        "model": (values.get("MODEL") or "").strip(),
        "baseUrl": (values.get("MODEL_BASE_URL") or "").strip(),
        "apiKey": (values.get("MODEL_API_KEY") or "").strip(),
    }


def call_llm(system, user):
    return generate_text(system, user, load_model_config())


def build_task(grouped, day):
    if not any(grouped.values()):
        return None
    template, example, template_filename = load_template()
    config = TASK_TEMPLATES[template_filename]
    sides = [side for side in ("前端", "后端") if grouped[side]]
    scope = "全栈" if len(sides) == 2 else sides[0]
    system = (
        f"你是研发任务编辑。根据 git 提交整理一条{config['kind']}。"
        "只依据提交里真实做过的事来写，不要编造未出现的功能。"
        "用完整、通顺的中文，不要照抄提交说明和文件路径。"
        "只输出任务名称和模板正文，不要 Markdown，不要输出填写示例。"
    )
    instructions = (
        "栏目标题保持不变，把【】里的提示换成具体内容，不要保留提示原话。\n"
        f"第一行必须是「【{config['title']}】：具体名称」，名称在 30 个字以内，不要放进方括号。\n"
    )
    if template_filename == "开发任务填报-父任务模版.md":
        instructions += (
            "子任务拆解按实际改动写，每条以「前端」「后端」或「全栈」开头；没有改动的端不要写。\n"
            "关键改动点和方案要点里，提交里看不出来的项直接省略，不要写「无」。\n"
        )
    elif template_filename == "开发任务填报-子任务模版.md":
        instructions += (
            "涉及端按实际改动填写，按模块或分类组织具体工作。\n"
            "前端、后端分别写实际改动；只有存在外部系统对接时才写联调。\n"
            "提交里看不出来的模块和不做范围直接省略。\n"
        )
    else:
        instructions += (
            "只整理提交中真实体现的分析、数据处理、配置、部署、排查或支持工作，"
            "不要把功能开发改写成非开发工作。\n"
            "任务名称后逐行输出七个字段：工作类别、工作场景、工作内容及边界、交付内容、"
            "交付方式、交付要求、评估标准（基线工时）。\n"
            "交付方式只能选「任务描述中写明即可」「需要额外附件」「两者结合」。"
            "Git 提交没有可靠工时依据，基线工时统一写「待确认」，不要编造数值。\n"
        )
    user = (
        f"日期：{day.isoformat()}\n"
        f"当天改动端：{scope}\n"
        f"提交记录：\n{format_commits(grouped)}\n\n"
        f"请按最新模板写一条{config['kind']}。\n{instructions}"
        "不要输出「填写示例」以及示例里的内容。\n\n"
        f"模板：\n{template}\n\n"
        f"写法参考（不要照抄，不要出现在输出里）：\n{example}"
    )
    try:
        task_name, description = parse_task_text(call_llm(system, user), template_filename)
    except RuntimeError:
        required_fields = "、".join(config["required_fields"])
        task_name, description = parse_task_text(call_llm(
            system,
            user + f"\n\n请重新输出。第一行必须是「【{config['title']}】：具体名称」，并保留字段：{required_fields}。",
        ), template_filename)
    if scope not in POSITION_BY_SCOPE:
        sides = [side for side in ("前端", "后端") if grouped[side]]
        scope = "全栈" if len(sides) == 2 else sides[0]
    if not task_name or not description:
        raise RuntimeError("大模型返回缺少任务名称或描述")
    if len(task_name) > 40:
        task_name = task_name[:40]
    return {
        "name": task_name,
        "scope": scope,
        "position": POSITION_BY_SCOPE[scope],
        "description": description,
    }


def work_description_max_length():
    configured = (
        load_env(ENV_PATH).get("WORK_DESCRIPTION_MAX_LENGTH") or ""
    ).strip()
    if not configured:
        return DEFAULT_WORK_DESCRIPTION_MAX_LENGTH
    try:
        max_length = int(configured)
    except ValueError:
        raise RuntimeError("WORK_DESCRIPTION_MAX_LENGTH 必须是正整数") from None
    if max_length <= 0:
        raise RuntimeError("WORK_DESCRIPTION_MAX_LENGTH 必须是正整数")
    return max_length


def limit_work_description(text):
    description = (text or "").strip()
    max_length = work_description_max_length()
    if len(description) <= max_length:
        return description
    lines = [line.strip() for line in description.splitlines() if line.strip()]
    kept = []
    for line in lines:
        candidate = "\n".join(kept + [line])
        if len(candidate) > max_length:
            break
        kept.append(line)
    if not kept:
        raise RuntimeError(
            "报工说明第一条完整内容超过 WORK_DESCRIPTION_MAX_LENGTH，"
            "请调大字数限制或缩短内容"
        )
    return "\n".join(kept)


def numbered_description(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and all(re.match(r"^\d+[.、]", line) for line in lines):
        return "\n".join(lines)
    return ""


def build_work_description(grouped, task_name):
    """把当天全部提交整理成工时说明。同一件事合并，不同的事分行编号。"""
    max_length = work_description_max_length()
    subjects = []
    seen = set()
    for side in ("前端", "后端"):
        for commit in grouped.get(side) or []:
            subject = (commit.get("subject") or "").strip()
            if subject and subject not in seen:
                seen.add(subject)
                subjects.append(subject)
    if not subjects:
        return limit_work_description(f"1.{task_name}")
    system = (
        "你是工时报工编辑。把当天的 git 提交整理成可直接填写的工时说明。"
        "只写提交里真实做过的事，不要编造功能，不要写文件路径和提交哈希。"
        f"同一件事的多次提交合并成一条，不同的事分开写，{max_length} 字内优先保留主要改动。"
        "一条提交里的文件不要再单独写成另一条。条目数量不要超过提交条数。"
        "每条单独一行，从 1 连续编号，格式为「1.具体做了什么」。"
        "每条必须是语义完整的短句，不得截断词语或句子。"
        f"包含编号、标点和换行在内，全部内容不能超过 {max_length} 个字符。"
        "不要 Markdown，不要空行，不要额外解释。"
    )
    user = f"任务名称：{task_name}\n提交记录：\n{format_commits(grouped)}"
    try:
        description = numbered_description(call_llm(system, user))
        if description:
            if len(description) <= max_length:
                return description
            retry_user = (
                f"{user}\n上次生成的报工说明超过 {max_length} 个字符。"
                "请压缩改写为语义完整的短句，保留主要改动，不要从句中截断。"
                f"上次内容：\n{description}"
            )
            rewritten = numbered_description(call_llm(system, retry_user))
            if rewritten:
                return limit_work_description(rewritten)
            log.warning("工时说明压缩改写未按编号返回，保留原结果的完整条目")
            return limit_work_description(description)
        log.warning("工时说明没有按编号返回，改用提交说明")
    except RuntimeError as error:
        log.warning("工时说明生成失败，改用提交说明：%s", error)
    return limit_work_description("\n".join(f"{index}.{subject}" for index, subject in enumerate(subjects, 1)))


def commit_rows(grouped):
    rows = []
    for side in ("前端", "后端"):
        for commit in grouped.get(side) or []:
            if commit.get("hash"):
                rows.append(commit)
    return rows


def commit_ids(grouped):
    ids = []
    for commit in commit_rows(grouped):
        digest = commit["hash"].strip()
        if digest not in ids:
            ids.append(digest)
    return ",".join(ids)


def render_commit_screenshot(driver, grouped, day, output_dir=None):
    rows = commit_rows(grouped)
    if not rows:
        return ""
    blocks = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<style>",
        "body{margin:0;background:#f6f8fa;font-family:'Microsoft YaHei',Consolas,monospace;color:#24292f;}",
        ".page{width:960px;padding:28px 32px 36px;}",
        "h1{margin:0 0 6px;font-size:22px;}",
        ".meta{margin:0 0 22px;color:#57606a;font-size:14px;}",
        "h2{margin:18px 0 8px;font-size:16px;}",
        ".commit{background:#fff;border:1px solid #d0d7de;border-radius:6px;padding:10px 14px;margin:0 0 8px;}",
        ".hash{font-family:Consolas,monospace;color:#0969da;}",
        ".time{color:#57606a;margin-left:10px;}",
        ".subject{margin-top:4px;}",
        "</style></head><body><div class='page'>",
        f"<h1>{escape(day.isoformat())} 提交记录</h1>",
        f"<p class='meta'>共 {len(rows)} 条</p>",
    ]
    current_repo = None
    for commit in rows:
        repo = commit.get("repo") or commit.get("side") or ""
        if repo != current_repo:
            blocks.append(f"<h2>{escape(repo)}</h2>")
            current_repo = repo
        blocks.append(
            "<div class='commit'>"
            f"<div><span class='hash'>{escape(commit['hash'])}</span>"
            f"<span class='time'>{escape(commit.get('time') or '')}</span></div>"
            f"<div class='subject'>{escape(commit.get('subject') or '')}</div>"
            "</div>"
        )
    blocks.append("</div></body></html>")
    html_path = os.path.join(tempfile.gettempdir(), f"qinchuan-commits-{day.isoformat()}.html")
    folder = output_dir or os.path.dirname(os.path.abspath(__file__))
    os.makedirs(folder, exist_ok=True)
    png_path = os.path.join(folder, f"commits-{day.isoformat()}.png")
    with open(html_path, "w", encoding="utf-8") as html_file:
        html_file.write("".join(blocks))
    current_handle = driver.current_window_handle
    driver.execute_script("window.open('about:blank', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    try:
        driver.get(html_path if html_path.startswith("file:") else "file:///" + html_path.replace("\\", "/"))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page")))
        height = driver.execute_script("return Math.ceil(document.body.scrollHeight)")
        driver.set_window_size(1040, max(int(height) + 80, 500))
        page = driver.find_element(By.CSS_SELECTOR, ".page")
        with open(png_path, "wb") as image_file:
            image_file.write(page.screenshot_as_png)
    finally:
        driver.close()
        driver.switch_to.window(current_handle)
        driver.maximize_window()
    return png_path


def to_html(text):
    blocks = []
    for line in text.splitlines():
        blocks.append(f"<p>{escape(line) if line.strip() else '<br>'}</p>")
    return "".join(blocks)


def wait_project(driver):
    WebDriverWait(driver, 40).until(
        lambda d: d.execute_script(
            """
            for (let i = 0; i < localStorage.length; i++) {
              const key = localStorage.key(i) || '';
              if (key.endsWith('_kfgl_currentProject') && localStorage.getItem(key)) return true;
            }
            return false;
            """
        )
    )


def task_exists(driver, task_name):
    return driver.execute_async_script(
        """
        const done = arguments[1];
        const taskName = arguments[0];
        const token = readToken();
        const projectId = readProjectId();
        const params = new URLSearchParams({
          taskName,
          pageNo: '1',
          pageSize: '20',
          queryTaskList: 'true',
          statusList: '1,2,3,4',
          _t: Date.now()
        });
        fetch('/dms/bizProcess/task/taskList?' + params.toString(), {
          headers: {'X-Access-Token': token, 'project-id': projectId, 'tenant-id': '0'}
        }).then(response => response.json()).then(json => {
          const records = (json.result && json.result.records) || [];
          done(records.some(item => item.taskName === taskName));
        }).catch(() => done(false));
        function readToken() {
          const raw = localStorage.getItem('pro__Access-Token') || '';
          try { return JSON.parse(raw).value || raw; } catch (e) { return raw; }
        }
        function readProjectId() {
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i) || '';
            if (key.endsWith('_kfgl_currentProject') && localStorage.getItem(key)) {
              return localStorage.getItem(key);
            }
          }
          return '';
        }
        """,
        task_name,
    )


def open_add_dialog(driver):
    wait = WebDriverWait(driver, 20)
    button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'新增')]")))
    button.click()
    wait.until(
        lambda d: d.execute_script(
            """
            const pop = findPop();
            return !!(pop && pop.positionOptions && pop.positionOptions.length);
            function findPop() {
              const seen = new Set();
              for (const el of document.querySelectorAll('*')) {
                let current = el.__vue__;
                while (current && !seen.has(current)) {
                  seen.add(current);
                  const file = (current.$options && current.$options.__file) || '';
                  if (file.includes('addTaskPop.vue')) return current;
                  current = current.$parent;
                }
              }
              return null;
            }
            """
        )
    )


def fill_and_save(driver, task):
    html = to_html(task["description"])
    filled = driver.execute_script(
        """
        const task = arguments[0];
        const html = arguments[1];
        const pop = findPop();
        const position = (pop.positionOptions || []).find(item => (item.name_dictText || item.name) === task.position);
        if (!position) {
          return {ok: false, message: '没有找到岗位：' + task.position};
        }
        pop.$set(pop.formData, 'taskName', task.name);
        pop.$set(pop.formData, 'taskType', String(position.id));
        pop.$set(pop.formData, 'taskCategory', task.category);
        pop.$set(pop.formData, 'description', html);
        if (window.tinymce && window.tinymce.activeEditor) {
          window.tinymce.activeEditor.setContent(html);
        }
        return {ok: true, position: position.name_dictText || position.name};
        function findPop() {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && current.$options.__file) || '';
              if (file.includes('addTaskPop.vue')) return current;
              current = current.$parent;
            }
          }
          return null;
        }
        """,
        {
            "name": task["name"],
            "position": task["position"],
            "category": TASK_CATEGORY,
        },
        html,
    )
    if not filled["ok"]:
        raise RuntimeError(filled["message"])
    log.info("填写任务：%s，岗位 %s", task["name"], filled["position"])
    driver.find_element(
        By.XPATH,
        "//div[contains(@class,'ant-modal') and not(contains(@class,'ant-modal-confirm'))]//button[contains(.,'确') and contains(.,'定')]",
    ).click()
    WebDriverWait(driver, 20).until(lambda d: _saved(d))
    later = driver.find_elements(By.XPATH, "//button[contains(.,'稍后创建')]")
    if later:
        later[0].click()
        log.info("已跳过创建子任务")
    log.info("任务已新增：%s", task["name"])


def _saved(driver):
    message = driver.execute_script(
        """
        return [...document.querySelectorAll('.ant-message-notice-content')]
          .map(el => el.innerText.trim())
          .filter(Boolean)
          .join('；');
        """
    )
    if message and any(word in message for word in ("失败", "请输入", "请选择")):
        raise RuntimeError(message)
    if message and "成功" in message:
        return True
    return bool(driver.find_elements(By.XPATH, "//div[contains(@class,'ant-modal-confirm')]"))


def create_tasks(driver, tasks):
    driver.get(TASK_LIST_URL)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button[contains(.,'新增')]")))
    wait_project(driver)
    for task in tasks:
        if task_exists(driver, task["name"]):
            log.info("任务已存在，跳过：%s", task["name"])
            continue
        open_add_dialog(driver)
        fill_and_save(driver, task)


def find_task_record(driver, task_name):
    return driver.execute_async_script(
        """
        const done = arguments[1];
        const taskName = arguments[0];
        const params = new URLSearchParams({
          taskName,
          pageNo: '1',
          pageSize: '20',
          queryTaskList: 'true',
          column: 'createTime',
          order: 'desc',
          _t: Date.now()
        });
        fetch('/dms/bizProcess/task/taskList?' + params.toString(), {
          headers: {'X-Access-Token': readToken(), 'project-id': readProjectId(), 'tenant-id': '0'}
        }).then(response => response.json()).then(json => {
          const records = (json.result && json.result.records) || [];
          done(records.find(item => item.taskName === taskName) || null);
        }).catch(error => done({error: String(error)}));
        function readToken() {
          const raw = localStorage.getItem('pro__Access-Token') || '';
          try { return JSON.parse(raw).value || raw; } catch (e) { return raw; }
        }
        function readProjectId() {
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i) || '';
            if (key.endsWith('_kfgl_currentProject') && localStorage.getItem(key)) return localStorage.getItem(key);
          }
          return '';
        }
        """,
        task_name,
    )


def schedule_task(driver, task_name, day):
    driver.get(TASK_SCHEDULING_URL)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table")))
    wait_project(driver)
    record = find_task_record(driver, task_name)
    if isinstance(record, dict) and record.get("error"):
        raise RuntimeError(record["error"])
    if not record:
        raise RuntimeError(f"排产列表没有找到任务：{task_name}")
    if str(record.get("schedulingStatus")) == "1":
        log.info("任务已排产，跳过：%s", task_name)
        return record
    start = f"{day.isoformat()} 08:30:00"
    end = f"{(day + timedelta(days=4)).isoformat()} 17:30:00"
    scheduled = driver.execute_async_script(
        """
        const taskName = arguments[0];
        const plan = arguments[1];
        const assignee = arguments[2];
        const done = arguments[arguments.length - 1];
        let settled = false;
        const finish = (value) => {
          if (settled) return;
          settled = true;
          done(value);
        };
        const started = Date.now();
        const timer = setInterval(async () => {
          const page = findByFile('taskScheduling/index.vue');
          if (!page && Date.now() - started < 20000) return;
          if (!page) {
            clearInterval(timer);
            finish({ok: false, message: '排产页没有打开'});
            return;
          }
          if (page.queryParam && page.queryParam.taskName !== taskName) {
            page.$set(page.queryParam, 'taskName', taskName);
            page.searchQuery();
            return;
          }
          if (page.loading && Date.now() - started < 20000) return;
          const record = (page.dataSource || []).find(row => row.taskName === taskName);
          if (!record && Date.now() - started < 20000) return;
          clearInterval(timer);
          if (!record) {
            finish({ok: false, message: '排产页没有这一行'});
            return;
          }
          const people = await loadPeople();
          const person = people.find(item => (item.personId_dictText || item.realname || '') === assignee);
          if (!person) {
            finish({ok: false, message: '项目人员里没有' + assignee});
            return;
          }
          page.toScheduling(record);
          const waitPop = setInterval(() => {
            const pop = findByFile('taskSchedulingPop.vue');
            if (!pop && Date.now() - started < 25000) return;
            clearInterval(waitPop);
            if (!pop) { finish({ok: false, message: '排产弹窗没有打开'}); return; }
            const assignId = person.personId || person.id;
            pop.$set(pop.formData, 'assignId', assignId);
            pop.$set(pop.formData, 'taskPriority', '1');
            pop.$set(pop.formData, 'estimatedTime', 40);
            pop.$set(pop.formData, 'estimatedStartTime', plan.start);
            pop.$set(pop.formData, 'estimatedEndTime', plan.end);
            pop.$set(pop.formData, 'estimatedDate', [pop.moment(plan.start), pop.moment(plan.end)]);
            pop.$set(pop.subTaskForm, 'taskSubList', []);
            pop.handleOk();
            const waitSaved = setInterval(() => {
              const message = readMessage();
              const explains = [...document.querySelectorAll('.ant-form-explain')].map(el => el.innerText.trim()).filter(Boolean);
              if (explains.length) {
                clearInterval(waitSaved);
                finish({ok: false, message: explains.join('；')});
                return;
              }
              if (message && (message.includes('失败') || message.includes('请'))) {
                clearInterval(waitSaved);
                finish({ok: false, message});
                return;
              }
              if (message && message.includes('成功')) {
                clearInterval(waitSaved);
                finish({ok: true, message, id: record.id});
              }
            }, 300);
            setTimeout(() => {
              clearInterval(waitSaved);
              finish({ok: false, message: readMessage() || '排产没有返回结果'});
            }, 20000);
          }, 300);
        }, 400);
        function loadPeople() {
          return fetch('/dms/bizProcess/common/queryProjectPerson?_t=' + Date.now(), {
            headers: {'X-Access-Token': readToken(), 'project-id': readProjectId(), 'tenant-id': '0'}
          }).then(response => response.json()).then(json => (json && json.result) || []);
        }
        function readMessage() {
          return [...document.querySelectorAll('.ant-message-notice-content')].map(el => el.innerText.trim()).filter(Boolean).join('；');
        }
        function readToken() {
          const raw = localStorage.getItem('pro__Access-Token') || '';
          try { return JSON.parse(raw).value || raw; } catch (e) { return raw; }
        }
        function readProjectId() {
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i) || '';
            if (key.endsWith('_kfgl_currentProject') && localStorage.getItem(key)) return localStorage.getItem(key);
          }
          return '';
        }
        function findByFile(part) {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && current.$options.__file) || '';
              if (file.includes(part)) return current;
              current = current.$parent;
            }
          }
          return null;
        }
        """,
        task_name,
        {"start": start, "end": end},
        ASSIGNEE,
    )
    if not scheduled or not scheduled.get("ok"):
        raise RuntimeError((scheduled or {}).get("message") or "排产失败")
    log.info("任务已排产：%s，%s ~ %s，指派 %s", task_name, start, end, ASSIGNEE)
    return record


def report_created_task(driver, task_name, work_description, commit_id, grouped, day):
    driver.get(TASK_EXECUTE_URL)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table")))
    driver.execute_script(
        """
        const page = findByFile('taskExecute/index.vue');
        if (page) page.$set(page.queryParam, 'taskName', arguments[0]);
        function findByFile(part) {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && current.$options.__file) || '';
              if (file.includes(part)) return current;
              current = current.$parent;
            }
          }
          return null;
        }
        """,
        task_name,
    )
    select_assignee_and_search(driver)
    WebDriverWait(driver, 20).until(lambda d: _task_row_ready(d, task_name))
    task = driver.execute_script(
        """
        const taskName = arguments[0];
        const page = findByFile('taskExecute/index.vue');
        const rows = [];
        walk(page && page.dataSource);
        const matched = rows.filter(row => row.taskName === taskName || row.taskName === '子任务 - ' + taskName);
        const child = matched.find(row => row.parentTaskId && String(row.parentTaskId) !== '0');
        return child || matched[0] || null;
        function walk(list) {
          (list || []).forEach(row => {
            rows.push(row);
            walk(row.children);
          });
        }
        function findByFile(part) {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && current.$options.__file) || '';
              if (file.includes(part)) return current;
              current = current.$parent;
            }
          }
          return null;
        }
        """,
        task_name,
    )
    if not task:
        raise RuntimeError(f"任务执行里没有找到已排产任务：{task_name}")
    today = day.isoformat()
    reported = driver.execute_async_script(
        """
        const taskId = arguments[0];
        const today = arguments[1];
        const done = arguments[arguments.length - 1];
        fetch('/dms/taskWorkHour/list?taskId=' + taskId + '&_t=' + Date.now(), {
          headers: {'X-Access-Token': readToken()}
        }).then(response => response.json()).then(json => {
          const logs = (json && json.result) || [];
          done(logs.some(item => String(item.executeStartTime || '').slice(0, 10) === today));
        }).catch(() => done(false));
        function readToken() {
          const raw = localStorage.getItem('pro__Access-Token') || '';
          try { return JSON.parse(raw).value || raw; } catch (e) { return raw; }
        }
        """,
        task["id"],
        today,
    )
    if reported:
        log.info("任务 %s 今天已经报过工时", task["id"])
        return
    if not commit_id:
        raise RuntimeError("当天没有提交记录，无法填写提交ID")
    target = {"id": task["id"], "name": task.get("taskName") or task_name}
    screenshot = render_commit_screenshot(driver, grouped, day)
    click_work_hour(driver, target["id"])
    WebDriverWait(driver, 20).until(lambda d: _modal_ready(d))
    start = f"{today} 08:30:00"
    end = f"{today} 17:30:00"
    description = (work_description or "").strip() or f"1.{task_name}"
    filled = driver.execute_script(
        """
        const modal = findModal();
        const log = modal.model.newLogs[0];
        modal.$set(log, 'description', arguments[0]);
        modal.handleMultipleChange([arguments[1], arguments[2]], log, 0);
        modal.$set(log, 'remainingTime', 0);
        modal.handleRemainingTimeChange(0);
        modal.$set(log, 'commitId', arguments[3]);
        return {
          duration: log.durationTime,
          remaining: log.remainingTime,
          description: log.description,
          commitId: log.commitId,
          isStorage: log.isStorage,
          finalOutputFlag: log.finalOutputFlag,
          documentVersion: log.documentVersion
        };
        function findModal() {
          const page = findByFile('taskExecute/index.vue');
          return page.$refs.workingHoursModal;
        }
        function findByFile(part) {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && current.$options.__file) || '';
              if (file.includes(part)) return current;
              current = current.$parent;
            }
          }
          return null;
        }
        """,
        description,
        start,
        end,
        commit_id,
    )
    upload_output(driver, screenshot)
    log.info(
        "填写工时：%s ~ %s，耗时 %s，剩余 %s，提交ID %s，产出物 %s",
        start,
        end,
        filled["duration"],
        filled["remaining"],
        filled["commitId"],
        os.path.basename(screenshot),
    )
    log.info("报工内容：\n%s", filled["description"])
    if filled["duration"] is None or float(filled["remaining"]) != 0:
        raise RuntimeError("耗时没有算出来，或剩余没有改成 0，已停止保存")
    driver.find_element(
        By.XPATH,
        "//div[contains(@class,'ant-modal')]//button[contains(normalize-space(.), '保') and contains(normalize-space(.), '存')]",
    ).click()
    WebDriverWait(driver, 20).until(lambda d: _hour_saved(d, target["id"], today))
    log.info("任务 %s 报工已保存", target["id"])


def upload_output(driver, image_path):
    if not image_path or not os.path.isfile(image_path):
        raise RuntimeError("提交记录截图没有生成")
    file_input = driver.execute_script(
        """
        const modal = findModal();
        const target = modal.model.newLogs[0];
        const seen = new Set();
        let matched = null;
        (function walk(vm) {
          if (!vm || seen.has(vm) || matched) return;
          seen.add(vm);
          const file = (vm.$options && vm.$options.__file) || '';
          if (file.includes('ClipboardUpload.vue') && vm.value === target.fileList) matched = vm;
          (vm.$children || []).forEach(walk);
        })(modal);
        return (matched || {}).$el && matched.$el.querySelector('input[type=file]');
        function findModal() {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && current.$options.__file) || '';
              if (file.includes('taskExecute/index.vue')) return current.$refs.workingHoursModal;
              current = current.$parent;
            }
          }
          return null;
        }
        """
    )
    if file_input is None:
        raise RuntimeError("工时弹窗没有找到产出物上传框")
    file_input.send_keys(os.path.abspath(image_path))
    WebDriverWait(driver, 30).until(_output_uploaded)


def _output_uploaded(driver):
    state = driver.execute_script(
        """
        const modal = findModal();
        const file = ((modal.model.newLogs[0] || {}).fileList || [])[0];
        if (!file) return {done: false};
        if (file.status === 'error') {
          const response = file.response || {};
          return {done: false, error: response.message || file.msg || '产出物上传失败'};
        }
        if (file.status !== 'done') return {done: false};
        const response = file.response || {};
        if (response.success === false || response.code === 500) {
          return {done: false, error: response.message || '产出物上传失败'};
        }
        return {done: true, name: file.name || ''};
        function findModal() {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && current.$options.__file) || '';
              if (file.includes('taskExecute/index.vue')) return current.$refs.workingHoursModal;
              current = current.$parent;
            }
          }
          return null;
        }
        """
    )
    if state.get("error"):
        raise RuntimeError(state["error"])
    return bool(state.get("done"))


def _hour_saved(driver, task_id, today):
    message = driver.execute_script(
        """
        return [...document.querySelectorAll('.ant-message-notice-content')]
          .map(el => el.innerText.trim())
          .filter(Boolean)
          .join('；');
        """
    )
    if message and any(word in message for word in ("失败", "不能", "请", "冲突")):
        raise RuntimeError(message)
    return work_hour_saved(driver, task_id, today)


def _task_row_ready(driver, task_name):
    return driver.execute_script(
        """
        const page = findByFile('taskExecute/index.vue');
        if (!page || page.loading) return false;
        const rows = [];
        walk(page.dataSource);
        return rows.some(row => row.taskName === arguments[0] || row.taskName === '子任务 - ' + arguments[0]);
        function walk(list) {
          (list || []).forEach(row => { rows.push(row); walk(row.children); });
        }
        function findByFile(part) {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && current.$options.__file) || '';
              if (file.includes(part)) return current;
              current = current.$parent;
            }
          }
          return null;
        }
        """,
        task_name,
    )


def is_supported_task_description(description):
    return any(
        all(field in description for field in config["required_fields"])
        for config in TASK_TEMPLATES.values()
    )


def find_today_task(driver, day):
    """当天已经由本脚本创建过的父任务。按创建人和受支持模板正文识别，不看任务名称。"""
    driver.get(TASK_LIST_URL)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//button[contains(.,'新增')]")))
    wait_project(driver)
    records = driver.execute_async_script(
        """
        const done = arguments[1];
        const params = new URLSearchParams({
          pageNo: '1',
          pageSize: '50',
          queryTaskList: 'true',
          column: 'createTime',
          order: 'desc',
          createTime_begin: arguments[0].begin,
          createTime_end: arguments[0].end,
          _t: Date.now()
        });
        fetch('/dms/bizProcess/task/taskList?' + params.toString(), {
          headers: {'X-Access-Token': readToken(), 'project-id': readProjectId(), 'tenant-id': '0'}
        }).then(response => response.json()).then(json => {
          const records = (json.result && json.result.records) || [];
          done(records.map(item => ({
            id: item.id,
            taskName: item.taskName,
            createTime: item.createTime,
            createBy: item.createBy,
            parentTaskId: item.parentTaskId,
            schedulingStatus: item.schedulingStatus,
            description: item.description || ''
          })));
        }).catch(error => done({error: String(error)}));
        function readToken() {
          const raw = localStorage.getItem('pro__Access-Token') || '';
          try { return JSON.parse(raw).value || raw; } catch (e) { return raw; }
        }
        function readProjectId() {
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i) || '';
            if (key.endsWith('_kfgl_currentProject') && localStorage.getItem(key)) return localStorage.getItem(key);
          }
          return '';
        }
        """,
        {
            "begin": f"{day.isoformat()} 00:00:00",
            "end": f"{(day + timedelta(days=1)).isoformat()} 00:00:00",
        },
    )
    if isinstance(records, dict) and records.get("error"):
        raise RuntimeError(records["error"])
    day_text = day.isoformat()
    matched = []
    for item in records or []:
        if not str(item.get("createTime") or "").startswith(day_text):
            continue
        if item.get("createBy") != USERNAME:
            continue
        parent = item.get("parentTaskId")
        if parent not in (None, "", 0, "0"):
            continue
        description = str(item.get("description") or "")
        if not is_supported_task_description(description):
            continue
        matched.append(item)
    if not matched:
        return None
    matched.sort(key=lambda item: item.get("createTime") or "", reverse=True)
    return matched[0]


def task_from_preset(preset, grouped):
    name = (preset.get("name") or "").strip()
    description = (preset.get("description") or "").strip()
    if not name or not description:
        raise RuntimeError("任务文件需要 name 和 description")
    sides = [side for side in ("前端", "后端") if grouped.get(side)]
    scope = "全栈" if len(sides) == 2 else (sides[0] if sides else "后端")
    if len(name) > 40:
        name = name[:40]
    return {
        "name": name,
        "scope": scope,
        "position": POSITION_BY_SCOPE[scope],
        "description": description,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="只输出指定日期的提交，不打开浏览器")
    parser.add_argument("--task-file", help="使用已经写好的任务名称、描述和报工说明")
    args = parser.parse_args(argv)
    day = target_day()
    grouped = collect_commits(day)
    if args.prepare:
        rows = commit_rows(grouped)
        print(json.dumps({
            "date": day.isoformat(),
            "commitIds": commit_ids(grouped),
            "commits": [
                {
                    "repo": item.get("repo"),
                    "side": item.get("side"),
                    "hash": item.get("hash"),
                    "time": item.get("time"),
                    "subject": item.get("subject"),
                    "files": (item.get("files") or [])[:12],
                }
                for item in rows
            ],
        }, ensure_ascii=False, indent=2))
        return
    preset = None
    if args.task_file:
        with open(args.task_file, encoding="utf-8") as task_file:
            preset = json.load(task_file)
    driver = create_driver()
    try:
        login(driver)
        existing = find_today_task(driver, day)
        if existing:
            task_name = existing["taskName"]
            log.info("当天任务已存在，不再创建：%s（%s）", task_name, existing["id"])
        else:
            task = task_from_preset(preset, grouped) if preset else build_task(grouped, day)
            if not task:
                log.info("%s 没有提交记录，不新增任务", day.isoformat())
                return
            log.info("准备新增：%s", task["name"])
            log.info("\n%s", task["description"])
            create_tasks(driver, [task])
            task_name = task["name"]
        if preset and (preset.get("workDescription") or "").strip():
            description = preset["workDescription"].strip()
        else:
            description = build_work_description(grouped, task_name)
        description = limit_work_description(description)
        commit_id = commit_ids(grouped)
        log.info("报工内容：\n%s", description)
        log.info("提交ID：%s", commit_id)
        schedule_task(driver, task_name, day)
        report_created_task(driver, task_name, description, commit_id, grouped, day)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
