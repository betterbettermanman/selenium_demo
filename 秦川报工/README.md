# 秦川报工

根据 Git 提交生成开发任务和工时说明，并通过 Selenium 完成秦川系统的任务新增、排产、报工及提交截图上传。本目录已内置 ChromeDriver 管理模块，不依赖原工作区的 `合并` 目录，可整体复制到其他 Windows 环境使用。

## 脚本用途

| 文件 | 用途 | 是否会修改秦川系统数据 |
| --- | --- | --- |
| `直接报工.py` | 给已有且符合条件的任务填写当天工时 | 会，真实保存工时 |
| `新增任务_排产_报工.py` | 根据指定日期（默认当天）的提交生成父任务，然后新增、排产、报工并上传提交截图 | 会，真实新增和保存 |
| `生成任务.py` | 只生成任务信息、报工说明、commitId 和提交截图 | 不会，但会调用大模型并打开浏览器生成截图 |
| `model_client.py` | 大模型调用封装 | 被其他脚本引用，不单独运行 |
| `chromedriver_manager.py` | Chrome 版本检测、ChromeDriver 下载和缓存 | 被其他脚本引用，不单独运行 |
| `template\` | 开发任务模板和非开发工作填报说明 | 不会 |
| `test\test_报工.py` | 自动化回归测试 | 不会 |

## 环境要求

- Windows 10/11，推荐使用 Python 3.10；
- Google Chrome；
- Git，并确保 `git` 在 `PATH` 中；
- 能访问秦川系统；
- 使用默认模型时，需要安装并登录 `qodercli`；也可以配置 OpenAI 或 Anthropic 兼容接口；
- 首次运行且没有可用 ChromeDriver 缓存时，需要联网下载驱动。

## 安装

在本目录打开 PowerShell：

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

然后编辑 `.env`，至少填写以下配置：

```dotenv
USERNAME=秦川账号
PASSWORD=秦川密码
ASSIGNEE=系统里的指派人姓名
PROJECT=系统顶部项目列表里的完整项目名称
TASK_DATE=
TASK_TEMPLATE=开发任务填报-父任务模版.md
REPO_ROOT=Git仓库扫描根目录
```

`REPO_ROOT` 可以包含多个 Git 仓库，脚本会递归扫描，并自动跳过 `.git`、`node_modules`、`target`、`dist` 等目录。例如：

```dotenv
REPO_ROOT=F:\workspace\qc\296
```

迁移到其他电脑时，只需把该路径改为目标电脑上的实际仓库路径。`.env` 含有账号等敏感信息，不要提交或转发真实配置。

`TASK_DATE` 用于指定任务日期，格式为 `YYYY-MM-DD`，例如 `TASK_DATE=2026-11-03`。`生成任务.py` 和 `新增任务_排产_报工.py` 都会读取该配置，Git 提交查询、任务查找、排产、报工及提交截图使用同一天；留空时使用运行当天。

`TASK_TEMPLATE` 用于选择任务模板，填写 `template` 目录中的文件名，留空时使用父任务模板。支持以下三个值：

- `开发任务填报-父任务模版.md`：生成包含需求背景和技术性描述的父任务；
- `开发任务填报-子任务模版.md`：生成按模块分类、包含前后端及外部联调内容的子任务；
- `非开发工作场景与交付要求填报说明.md`：生成一条包含工作类别、工作场景、工作内容及边界、交付内容、交付方式、交付要求和基线工时的非开发任务；Git 提交没有可靠工时依据，基线工时统一填写“待确认”。

## 模型配置

默认配置为：

```dotenv
MODEL_PROVIDER=qoder
MODEL=
```

此时会调用本机已登录的 `qodercli`。如需指定模型，可填写 `MODEL`。

使用 OpenAI 兼容接口时：

```dotenv
MODEL_PROVIDER=openai
MODEL=模型名称
MODEL_BASE_URL=https://api.example.com/v1
MODEL_API_KEY=接口密钥
```

使用 Anthropic 兼容接口时，将 `MODEL_PROVIDER` 改为 `anthropic`，并填写相同的三个模型字段。也可以通过系统环境变量 `QINCHUAN_MODEL_API_KEY` 提供接口密钥。

## 运行

### 只预览配置日期的 Git 提交

```powershell
.\.venv\Scripts\python.exe 新增任务_排产_报工.py --prepare
```

该命令只输出提交信息 JSON，不打开浏览器、不调用大模型，也不修改秦川系统数据。

### 直接给已有任务报工

```powershell
.\.venv\Scripts\python.exe 直接报工.py
```

### 新增任务、排产并完成报工

```powershell
.\.venv\Scripts\python.exe 新增任务_排产_报工.py
```

如需使用已经写好的任务内容：

```powershell
.\.venv\Scripts\python.exe 新增任务_排产_报工.py --task-file task.json
```

任务文件示例：

```json
{
  "name": "订单统计功能开发",
  "description": "【父任务名称】：订单统计功能开发\n1. 需求背景\n补充订单统计能力。\n2. 技术性描述\n实现查询、汇总和展示。",
  "workDescription": "1.完成订单统计接口和页面开发"
}
```

`workDescription` 可以省略；最终报工内容会统一限制为不超过 60 个字符。

### 只生成任务资料

```powershell
.\.venv\Scripts\python.exe 生成任务.py
```

生成结果写入 `output\日期\`，包括 `任务信息.json`、`任务信息.txt` 和提交记录截图。

## ChromeDriver

脚本默认根据本机 Chrome 版本自动下载匹配的 ChromeDriver，缓存到本目录：

```text
driver_cache\chromedriver\
```

如需使用已有驱动，可设置系统环境变量 `CHROMEDRIVER_PATH` 为 `chromedriver.exe` 的完整路径。该变量是系统环境变量，不是 `.env` 配置项。

## 测试

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s test -p "test_*.py" -v
```

测试使用模拟对象，不会登录或修改秦川系统数据。

## 迁移检查清单

1. 整体复制本目录，包括 `model_client.py`、`chromedriver_manager.py` 和 `template` 目录；
2. 在目标环境重新创建 `.venv` 并安装 `requirements.txt`；
3. 根据 `.env.example` 创建并填写 `.env`，尤其是新的 `REPO_ROOT`；
4. 安装 Chrome、Git，并准备可用的模型服务；
5. 先运行 `--prepare` 和测试脚本，再执行会真实新增或报工的命令。
