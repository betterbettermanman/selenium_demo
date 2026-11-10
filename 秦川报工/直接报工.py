"""秦川开发管理系统：登录、按指派人筛选、填写并保存当日工时。"""

import base64
import logging
import os
import time
from datetime import datetime

import ddddocr
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chromedriver_manager import get_chromedriver_path

HERE = os.path.dirname(os.path.abspath(__file__))
LOGIN_URL = "https://scic.cdqckj.com:65036/businessFlow/taskManagement/taskExecute"
ENV_PATH = os.path.join(HERE, ".env")
DRIVER_CACHE_DIR = os.path.join(HERE, "driver_cache", "chromedriver")


def load_env(path):
    if not os.path.isfile(path):
        raise RuntimeError("没有找到配置文件：%s" % path)
    values = {}
    with open(path, encoding="utf-8") as env_file:
        for raw in env_file:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            values[key.strip()] = value
    return values


def _env_value(values, key):
    value = (values.get(key) or "").strip()
    if not value:
        raise RuntimeError("配置文件缺少 %s：%s" % (key, ENV_PATH))
    return value


_ENV = load_env(ENV_PATH)
USERNAME = _env_value(_ENV, "USERNAME")
PASSWORD = _env_value(_ENV, "PASSWORD")
ASSIGNEE = _env_value(_ENV, "ASSIGNEE")


def configure_account(username=None, password=None, assignee=None):
    global USERNAME, PASSWORD, ASSIGNEE
    if username:
        USERNAME = username
    if password:
        PASSWORD = password
    if assignee:
        ASSIGNEE = assignee

# 执行时段。页面会按此时段扣午休后算出耗时，并按上一条剩余工时算出剩余。
WORK_START = "08:30:00"
WORK_END = "17:30:00"
# 为空时使用「1.任务名称」。
WORK_DESCRIPTION = ""
# 只给最近仍在填报、且今天还没报过的那一条任务报工。
REPORT_LATEST_ONLY = True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("qinchuan")
ocr = ddddocr.DdddOcr(show_ad=False)


def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    os.environ.setdefault("CHROMEDRIVER_CACHE_DIR", DRIVER_CACHE_DIR)
    log.info("正在准备 ChromeDriver")
    chromedriver_path = get_chromedriver_path()
    log.info("ChromeDriver 就绪：%s", chromedriver_path)
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    driver.set_script_timeout(60)
    return driver


def set_input(driver, element, value):
    driver.execute_script(
        """
        const el = arguments[0];
        const value = arguments[1];
        const proto = el.tagName === 'TEXTAREA'
            ? HTMLTextAreaElement.prototype
            : HTMLInputElement.prototype;
        Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        """,
        element,
        value,
    )


def login(driver):
    wait = WebDriverWait(driver, 20)
    driver.get(LOGIN_URL)
    for attempt in range(1, 9):
        user = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入帐户名']"))
        )
        password = driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入密码']")
        captcha_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入验证码']")
        image = driver.find_element(By.CSS_SELECTOR, ".ant-input-group-addon img")
        src = image.get_attribute("src") or ""
        if "," not in src:
            raise RuntimeError("验证码图片还没加载出来")
        code = ocr.classification(base64.b64decode(src.split(",", 1)[1]))
        code = "".join(ch for ch in code if ch.isalnum())
        log.info("第 %s 次登录，验证码识别为 %s", attempt, code)
        set_input(driver, user, USERNAME)
        set_input(driver, password, PASSWORD)
        set_input(driver, captcha_input, code)
        driver.find_element(By.XPATH, "//button[contains(., '登录系统')]").click()
        if _leave_login(driver, 8):
            log.info("登录成功")
            select_project(driver)
            return
        message = _message_text(driver)
        log.warning("登录未成功：%s", message or "验证码可能不正确，刷新后重试")
        try:
            image.click()
        except Exception:
            driver.refresh()
        time.sleep(0.8)
    raise RuntimeError("多次尝试后仍未登录成功")


def select_project(driver):
    project_name = _env_value(load_env(ENV_PATH), "PROJECT")
    switched = False
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            result = driver.execute_script(
                """
                const targetName = (arguments[0] || '').trim();
                const project = findProject();
                const list = (project && project.projectList) || [];
                if (!list.length) return {pending: true};
                const match = list.find(item => (item.projectName || '').trim() === targetName);
                if (!match) return {missing: true};
                const key = project.$store.getters.username + '_kfgl_currentProject';
                const current = localStorage.getItem(key) || '';
                if (current === String(match.id)) return {same: true, name: match.projectName};
                project.selectProject(String(match.id));
                return {switched: true, name: match.projectName};
                function findProject() {
                  const seen = new Set();
                  for (const el of document.querySelectorAll('*')) {
                    let current = el.__vue__;
                    while (current && !seen.has(current)) {
                      seen.add(current);
                      const file = (current.$options && current.$options.__file) || '';
                      if (file.includes('GlobalProject.vue')) return current;
                      current = current.$parent;
                    }
                  }
                  return null;
                }
                """,
                project_name,
            )
        except Exception:
            switched = True
            break
        if not result or result.get("pending"):
            time.sleep(0.4)
            continue
        if result.get("missing"):
            raise RuntimeError("没有找到项目「%s」，请按顶部项目列表中的名称填写" % project_name)
        if result.get("same"):
            log.info("当前项目已是「%s」", project_name)
            return
        switched = True
        break
    else:
        raise RuntimeError("项目列表还没加载出来")
    if switched:
        WebDriverWait(driver, 30).until(lambda d: _project_selected(d, project_name))
        log.info("已切换项目：%s", project_name)


def _project_selected(driver, project_name):
    if "/user/login" in (driver.current_url or ""):
        return False
    try:
        current = driver.execute_script(
            """
            const el = document.querySelector('.selectedProject .ant-select-selection-selected-value');
            return el ? el.innerText.trim() : '';
            """
        )
    except Exception:
        return False
    return current == project_name


def _leave_login(driver, seconds):
    end = time.time() + seconds
    while time.time() < end:
        if "/user/login" not in driver.current_url:
            return True
        time.sleep(0.3)
    return False


def _message_text(driver):
    texts = driver.execute_script(
        """
        return [...document.querySelectorAll('.ant-message-notice-content')]
            .map(el => el.innerText.trim())
            .filter(Boolean);
        """
    )
    return "；".join(texts)


def _assignee_form_item(driver):
    return driver.find_elements(
        By.XPATH,
        "//div[contains(@class,'ant-form-item')][.//label[contains(.,'指派给')]]",
    )


def _expand_search_form(driver):
    WebDriverWait(driver, 40).until(lambda d: "taskExecute" in d.current_url)
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table, .ant-form"))
    )
    for _ in range(3):
        items = [item for item in _assignee_form_item(driver) if item.is_displayed()]
        if items:
            return
        expanders = driver.find_elements(By.XPATH, "//button[contains(.,'展开')]")
        if not expanders:
            time.sleep(0.5)
            continue
        expanders[0].click()
        time.sleep(0.4)
    if not any(item.is_displayed() for item in _assignee_form_item(driver)):
        raise RuntimeError("查询条件里没有找到「指派给」，请先展开查询区")


def _wait_assignee_options(driver):
    _expand_search_form(driver)
    loaded = driver.execute_async_script(
        """
        const done = arguments[0];
        let settled = false;
        const finish = (value) => {
          if (settled) return;
          settled = true;
          clearInterval(timer);
          done(value);
        };
        const timer = setInterval(async () => {
          const projectId = readProjectId();
          if (!projectId) return;
          try {
            const response = await fetch('/dms/bizProcess/common/queryProjectPerson?_t=' + Date.now(), {
              headers: {
                'X-Access-Token': readToken(),
                'project-id': projectId,
                'tenant-id': '0'
              }
            });
            const json = await response.json();
            const people = (json && json.success && json.result) || [];
            if (!people.length) return;
            const page = findVue(file => file.includes('taskExecute/index.vue') || file === 'businessFlow-taskManagement-taskExecute');
            if (page && page.searchConfig) {
              const config = page.searchConfig.find(item => item.field === 'assignId');
              if (config && config.attrs) page.$set(config.attrs, 'options', people);
            }
            const select = findVue(file => file.includes('JSelectAssignedPerson'));
            if (select) {
              select.selectOptions = people;
              if (select.$forceUpdate) select.$forceUpdate();
            }
            const count = (select && select.selectOptions && select.selectOptions.length) || 0;
            if (count > 0) finish({count, projectId});
          } catch (error) {}
        }, 400);
        setTimeout(() => finish({count: 0, projectId: readProjectId()}), 30000);
        function readProjectId() {
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i) || '';
            if (key.endsWith('_kfgl_currentProject')) {
              const value = localStorage.getItem(key);
              if (value) return value;
            }
          }
          return '';
        }
        function readToken() {
          const raw = localStorage.getItem('pro__Access-Token') || '';
          try { return JSON.parse(raw).value || raw; } catch (e) { return raw; }
        }
        function findVue(match) {
          const seen = new Set();
          for (const el of document.querySelectorAll('*')) {
            let current = el.__vue__;
            while (current && !seen.has(current)) {
              seen.add(current);
              const file = (current.$options && (current.$options.__file || current.$options.name)) || '';
              if (match(file)) return current;
              current = current.$parent;
            }
          }
          return null;
        }
        """
    )
    option_count = loaded.get("count") if isinstance(loaded, dict) else 0
    if not option_count:
        project_id = loaded.get("projectId") if isinstance(loaded, dict) else ""
        if not project_id:
            raise RuntimeError("当前项目还没选好，指派给人员加载失败")
        raise RuntimeError("指派给下拉没有加载出人员")
    log.info("指派给人员已加载，共 %s 人", option_count)


def select_assignee_and_search(driver):
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-table")))
    _wait_assignee_options(driver)
    form_item = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'ant-form-item') and .//label[contains(.,'指派给')]]")
        )
    )
    form_item.find_element(By.CSS_SELECTOR, ".ant-select").click()
    search = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-select-open .ant-select-search__field"))
    )
    search.clear()
    search.send_keys(ASSIGNEE)
    option = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[contains(@class,'ant-select-dropdown')]//li[contains(@class,'ant-select-dropdown-menu-item') and normalize-space()='%s']" % ASSIGNEE,
            )
        )
    )
    option.click()
    driver.find_element(By.XPATH, "//button[contains(normalize-space(.), '查') and contains(normalize-space(.), '询')]").click()
    wait.until(lambda d: _assignee_applied(d))
    log.info("已按指派给「%s」查询", ASSIGNEE)


def _assignee_applied(driver):
    return driver.execute_script(
        """
        const page = findTaskPage();
        if (!page || !page.queryParam || !page.queryParam.assignId) return false;
        const rows = page.dataSource || [];
        if (!rows.length) return page.loading === false;
        return rows.every(row => (row.assignId_dictText || '') === arguments[0]);
        function findTaskPage() {
          const table = document.querySelector('.ant-table');
          let node = table;
          for (let i = 0; i < 30 && node; i++) {
            const vue = node.__vue__;
            if (vue && vue.$options && vue.$options.name === 'RouteView') {
              return (vue.$children || []).find(child => child.$options && child.$options.name === 'businessFlow-taskManagement-taskExecute');
            }
            node = node.parentElement;
          }
          return null;
        }
        """,
        ASSIGNEE,
    )


def choose_task(driver):
    today = datetime.now().strftime("%Y-%m-%d")
    driver.execute_script(
        """
        const table = mainTable();
        [...table.querySelectorAll('.ant-table-row-expand-icon.ant-table-row-collapsed')].forEach(icon => icon.click());
        function mainTable() {
          return [...document.querySelectorAll('.ant-table')].find(el => !el.closest('.ant-modal'));
        }
        """
    )
    time.sleep(0.8)
    tasks = driver.execute_async_script(
        """
        const today = arguments[0];
        const done = arguments[arguments.length - 1];
        (async () => {
          const rows = workHourRows();
          const tokenRaw = localStorage.getItem('pro__Access-Token') || '';
          let token = tokenRaw;
          try { token = JSON.parse(tokenRaw).value || tokenRaw; } catch (e) {}
          const result = [];
          for (const row of rows) {
            const response = await fetch('/dms/taskWorkHour/list?taskId=' + row.id + '&_t=' + Date.now(), {
              headers: {'X-Access-Token': token}
            });
            const json = await response.json();
            const logs = (json && json.result) || [];
            const last = logs.length ? logs[logs.length - 1] : null;
            result.push({
              id: row.id,
              name: row.name,
              lastStart: last ? last.executeStartTime : '',
              lastRemain: last ? Number(last.remainingTime) : null,
              reportedToday: logs.some(item => String(item.executeStartTime || '').slice(0, 10) === today)
            });
          }
          done(result);
        })().catch(error => done({error: String(error)}));
        function workHourRows() {
          const table = [...document.querySelectorAll('.ant-table')].find(el => !el.closest('.ant-modal'));
          const leftRows = [...table.querySelectorAll('.ant-table-fixed-left tbody tr.ant-table-row')];
          const fixedRows = [...table.querySelectorAll('.ant-table-fixed-right tbody tr.ant-table-row')];
          const rows = [];
          fixedRows.forEach((row, index) => {
            const link = [...row.querySelectorAll('a')].find(el => el.innerText.trim() === '工时');
            if (!link || !leftRows[index]) return;
            const cells = [...leftRows[index].children].map(cell => cell.innerText.trim());
            const name = (cells[1] || '').replace(/^子任务\\s*-\\s*/, '').trim();
            rows.push({id: cells[0], name});
          });
          return rows;
        }
        """,
        today,
    )
    if isinstance(tasks, dict) and tasks.get("error"):
        raise RuntimeError(tasks["error"])
    candidates = []
    for task in tasks or []:
        log.info(
            "任务 %s %s 最近报工=%s 剩余=%s 今天已报=%s",
            task["id"],
            task["name"],
            task["lastStart"] or "无",
            task["lastRemain"],
            task["reportedToday"],
        )
        if task["lastRemain"] is not None and task["lastRemain"] <= 0:
            continue
        candidates.append(task)
    if not candidates:
        return None
    candidates.sort(key=lambda item: item["lastStart"] or "", reverse=True)
    if REPORT_LATEST_ONLY:
        latest = candidates[0]
        if latest["reportedToday"]:
            log.info("最近仍在填报的任务 %s 今天已经报过", latest["id"])
            return None
        return [latest]
    return [task for task in candidates if not task["reportedToday"]]


def report_task(driver, task):
    today = datetime.now().strftime("%Y-%m-%d")
    description = WORK_DESCRIPTION.strip() or f"1.{task['name']}"
    start = f"{today} {WORK_START}"
    end = f"{today} {WORK_END}"
    click_work_hour(driver, task["id"])
    WebDriverWait(driver, 20).until(lambda d: _modal_ready(d))
    filled = driver.execute_script(
        """
        const modal = findModal();
        const log = modal.model.newLogs[0];
        modal.$set(log, 'description', arguments[0]);
        modal.handleMultipleChange([arguments[1], arguments[2]], log, 0);
        return {duration: log.durationTime, remaining: log.remainingTime, description: log.description};
        function findModal() {
          const page = findTaskPage();
          return page.$refs.workingHoursModal;
        }
        function findTaskPage() {
          const table = document.querySelector('.ant-table');
          let node = table;
          for (let i = 0; i < 30 && node; i++) {
            const vue = node.__vue__;
            if (vue && vue.$options && vue.$options.name === 'RouteView') {
              return (vue.$children || []).find(child => child.$options && child.$options.name === 'businessFlow-taskManagement-taskExecute');
            }
            node = node.parentElement;
          }
          return null;
        }
        """,
        description,
        start,
        end,
    )
    log.info(
        "填写工时：%s ~ %s，耗时 %s，剩余 %s，内容 %s",
        start,
        end,
        filled["duration"],
        filled["remaining"],
        filled["description"],
    )
    if filled["duration"] is None or filled["remaining"] is None:
        raise RuntimeError("耗时或剩余工时没有算出来，已停止保存")
    driver.find_element(By.XPATH, "//div[contains(@class,'ant-modal')]//button[contains(normalize-space(.), '保') and contains(normalize-space(.), '存')]").click()
    WebDriverWait(driver, 20).until(lambda d: _saved(d, task["id"], today))
    log.info("任务 %s 报工已保存", task["id"])
    close = driver.find_elements(By.XPATH, "//div[contains(@class,'ant-modal')]//button[contains(normalize-space(.), '关') and contains(normalize-space(.), '闭')]")
    if close:
        close[-1].click()


def click_work_hour(driver, task_id):
    clicked = driver.execute_script(
        """
        const taskId = String(arguments[0]);
        const table = [...document.querySelectorAll('.ant-table')].find(el => !el.closest('.ant-modal'));
        const leftRows = [...table.querySelectorAll('.ant-table-fixed-left tbody tr.ant-table-row')];
        const fixedRows = [...table.querySelectorAll('.ant-table-fixed-right tbody tr.ant-table-row')];
        const index = leftRows.findIndex(row => (row.innerText.trim().split(/\\s+/)[0] || '') === taskId);
        if (index < 0 || !fixedRows[index]) return false;
        const link = [...fixedRows[index].querySelectorAll('a')].find(el => el.innerText.trim() === '工时');
        if (!link) return false;
        link.click();
        return true;
        """,
        task_id,
    )
    if not clicked:
        raise RuntimeError(f"任务 {task_id} 这一行没有可点击的「工时」")


def _modal_ready(driver):
    return driver.execute_script(
        """
        const page = findTaskPage();
        const modal = page && page.$refs && page.$refs.workingHoursModal;
        return !!(modal && modal.visible && modal.loading === false && modal.model && modal.model.newLogs && modal.model.newLogs.length);
        function findTaskPage() {
          const table = document.querySelector('.ant-table');
          let node = table;
          for (let i = 0; i < 30 && node; i++) {
            const vue = node.__vue__;
            if (vue && vue.$options && vue.$options.name === 'RouteView') {
              return (vue.$children || []).find(child => child.$options && child.$options.name === 'businessFlow-taskManagement-taskExecute');
            }
            node = node.parentElement;
          }
          return null;
        }
        """
    )


def _saved(driver, task_id, today):
    message = _message_text(driver)
    if message and ("失败" in message or "不能" in message or "请" in message):
        raise RuntimeError(message)
    return driver.execute_script(
        """
        const modal = findModal();
        const logs = (modal && modal.model && modal.model.submittedLogs) || [];
        return logs.some(item => String(item.executeStartTime || (item.date && item.date[0]) || '').slice(0, 10) === arguments[1]);
        function findModal() {
          const page = findTaskPage();
          return page && page.$refs && page.$refs.workingHoursModal;
        }
        function findTaskPage() {
          const table = document.querySelector('.ant-table');
          let node = table;
          for (let i = 0; i < 30 && node; i++) {
            const vue = node.__vue__;
            if (vue && vue.$options && vue.$options.name === 'RouteView') {
              return (vue.$children || []).find(child => child.$options && child.$options.name === 'businessFlow-taskManagement-taskExecute');
            }
            node = node.parentElement;
          }
          return null;
        }
        """,
        task_id,
        today,
    )


def main():
    driver = create_driver()
    try:
        login(driver)
        select_assignee_and_search(driver)
        tasks = choose_task(driver)
        if not tasks:
            log.info("没有需要报工的任务：今天已经报过，或剩余工时为 0")
            return
        for task in tasks:
            report_task(driver, task)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
