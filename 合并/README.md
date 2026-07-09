# 任务管理系统

基于 Vue 3 + Ant Design Vue + Flask + MySQL 的全栈任务管理系统。

## 功能模块

- **网站管理** - 网站列表的增删改查
- **课程管理** - 课程列表的增删改查（支持 JSON 课表）
- **任务管理** - 任务列表的增删改查（支持状态筛选、JSON 字段）

## 项目结构

```
├── backend/          # Flask 后端
│   ├── app.py        # 应用入口
│   ├── config.py     # 配置
│   ├── models/       # 数据模型
│   ├── routes/       # API 路由
│   ├── sql/          # 数据库初始化脚本
│   └── requirements.txt
├── frontend/         # Vue 3 前端
│   ├── src/
│   │   ├── api/      # API 请求封装
│   │   ├── views/    # 页面组件
│   │   └── router/   # 路由配置
│   └── package.json
└── README.md
```

## 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 5.7+ / 8.0+

## 快速开始

### 1. 初始化数据库

```bash
mysql -u root -p < backend/sql/init.sql
```

### 2. 配置后端

```bash
cd backend
cp .env.example .env
# 编辑 .env 修改数据库连接信息
pip install -r requirements.txt
python app.py
```

后端端口：
- 开发模式 `http://localhost:6002`（`dev.bat` / `python app.py` + `FLASK_DEBUG=1`）
- 打包生产 `http://localhost:6001`（`start.bat`）

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`

## 一键脚本（Windows）

项目根目录提供三个批处理文件，双击即可运行：

| 脚本 | 说明 |
|------|------|
| `dev.bat` | 开发模式：新开窗口启动后端(6002) + 前端 Vite(5173) |
| `build.bat` | 打包：构建前端并复制到 `backend/static` |
| `start.bat` | 生产模式：启动后端，同时托管前端页面（需先执行 build.bat） |

生产环境访问地址：`http://localhost:6001`

对应 PowerShell 脚本位于 `scripts/` 目录（`build.ps1` / `start.ps1` / `dev.ps1`）。

## API 接口

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 网站 | GET | `/api/websites` | 列表（支持分页、关键词搜索） |
| 网站 | POST | `/api/websites` | 新增 |
| 网站 | PUT | `/api/websites/:id` | 更新 |
| 网站 | DELETE | `/api/websites/:id` | 删除 |
| 课程 | GET | `/api/courses` | 列表 |
| 课程 | POST | `/api/courses` | 新增 |
| 课程 | PUT | `/api/courses/:id` | 更新 |
| 课程 | DELETE | `/api/courses/:id` | 删除 |
| 任务 | GET | `/api/tasks` | 列表（支持状态筛选） |
| 任务 | POST | `/api/tasks` | 新增 |
| 任务 | PUT | `/api/tasks/:id` | 更新 |
| 任务 | DELETE | `/api/tasks/:id` | 删除 |

## 数据库配置

在 `backend/.env` 中配置（推荐方式，**密码含 `@` 等特殊字符无需转义**）：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=abc@123#456
DB_NAME=task_manager
```

程序会自动对用户名和密码做 URL 编码后再拼接连接串。

若仍使用完整 `DATABASE_URL`，密码中的特殊字符需手动编码，例如 `@` → `%40`：

```
DATABASE_URL=mysql+pymysql://root:abc%40123@localhost:3306/task_manager?charset=utf8mb4
```
