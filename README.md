# 目录级文档

> 目的：本仓库为交付给客户的精简存档版本。本文档以“文件夹”为最小说明粒度，描述每个目录的用途、主要内容与对外行为。

- 仓库：`wanhua_deploy`（branch: `master`）
- 生成日期：2026-01-28

## 1. 根目录（`/`）

用于承载整体工程（前端 + 后端 + 通用工具）的顶层入口。

### 1.1 `README.md`

项目总览说明（偏向 RDKit 化学数据处理工具与能力介绍）。

### 1.2 `pyproject.toml`

根级 Python 包配置（精简）：
- 包名：`rdkit-py`
- Python：`>=3.10`
- 依赖（示例）：`bs4`、`lxml`、`seaborn`、`squarify`、`xlsxwriter`

> 说明：根级依赖更像是“通用数据处理/可视化工具集”侧的依赖；服务端运行依赖以 `backend/requirements.txt` 为准。

### 1.3 `uv.lock`

使用 `uv` 管理依赖时的锁文件，用于复现一致的 Python 依赖版本。

### 1.4 其他：`.gitignore` / `.python-version` / `.venv/` / `.vscode/`

- `.python-version`：项目 Python 版本提示（通常给 pyenv/asdf 等工具使用）。
- `.venv/`：本地虚拟环境目录（通常不建议提交，但该仓库为存档精简版，可能保留）。
- `.vscode/`：VS Code 配置（调试、格式化、任务等）。

## 2. 后端服务（`backend/`）

FastAPI 后端服务工程，用于：
- 文件上传与数据校验（CSV / SDF）
- 训练/推理任务的提交、查询、停止、删除
- 模型列表查询
- 用户注册/登录/鉴权（JWT）
- 连接 MongoDB（用户、token 黑名单、任务信息等）

### 2.1 `backend/README.md`

后端使用说明（包含历史部署信息/端口/服务器目录等）。

### 2.2 `backend/requirements.txt`

后端运行依赖（关键项）：
- `fastapi[all]`
- `rdkit==2023.9.6`
- `motor==3.4.0`（MongoDB 异步驱动）
- `pyjwt` / `cryptography` / `passlib` / `bcrypt`（鉴权 & 密码）
- `pandas` / `numpy` / `scikit-learn` / `seaborn`
- `httpx` / `aiofiles`
- `bohrium-open-sdk`（可能用于对接外部计算平台/认证）

### 2.3 `backend/pyproject.toml`

后端代码质量/格式化等工具配置（当前仅看到 `ruff` 配置）。

### 2.4 `backend/Dockerfile`、`backend/run.sh`

后端容器化与启动脚本：
- 用于构建/运行后端服务镜像（具体流程以文件内容为准）。

### 2.5 业务代码（`backend/app/`）

后端 FastAPI 应用主体。

#### 2.5.1 `backend/app/main.py`

应用入口：
- 读取 `.env`（`dotenv`）环境变量
- 初始化日志配置（`log_config.json`）
- 启动时建立 MongoDB 连接与索引
- 注册路由：`/user`、`/file`、`/task`、`/model`
- 启用 CORS（全放开：`*`）

#### 2.5.2 `backend/app/db/`

数据库连接与索引管理：
- `utils.py`：使用 `motor` 建立 MongoDB 连接；创建用户唯一索引、token 黑名单 TTL 索引等。

#### 2.5.3 `backend/app/user/`

用户与鉴权模块：
- `user_router.py`：注册、登录、发 token、登出、改密、获取当前用户信息等接口。
- `utils.py` / `bohrium_auth.py`：JWT 校验、cookie 校验、与外部认证（若接入）等。

#### 2.5.4 `backend/app/file/`

文件处理模块：
- `file_router.py`：
  - `/file/upload`：上传原始 CSV/SDF 到 `raw_files`
  - `/file/check`：校验并写入 `valid_files`，返回错误行、猜测任务类型等
  - `/file/upload_infer_file`、`/file/check_infer_file`：推理文件上传与校验
  - `/file/download_template`：下载模板 CSV
- `utils.py`：保存文件、解析数据、校验 SMILES/列名、任务类型推断等工具函数。

> 注意：代码里存在硬编码目录（如 `/vepfs/fs_users/.../files`），交付落地时通常需要通过环境变量/配置文件替换。

#### 2.5.5 `backend/app/task/`

任务系统模块：
- `task_router.py`：
  - `/task/new_train`：提交训练任务
  - `/task/new_infer`：提交推理任务（依赖训练任务状态 FINISHED）
  - `/task/list`：任务列表
  - `/task/get_by_run_id`：任务详情
  - `/task/log`：读取训练/推理日志
  - `/task/stop`、`/task/remove`：停止/删除任务
  - `/task/acquire_task`：worker 拉取任务（配合 token 验证）
- `task_manager.py`：任务对象、状态流转、与 DB 的交互（commit/stop/rm/deliver 等）。
- `deliver_token_utils.py`：worker token 解密校验逻辑。
- `config_default.yaml`：默认任务配置模板。
- `utils.py`：任务入参/出参数据结构（如 `InFit`、`InInfer`、`RES`、`TaskType` 等）。

#### 2.5.6 `backend/app/model/`

模型相关接口：
- `model_router.py`：`/model/available_models` 查询指定用户可用模型列表。
- `chart/`：模型/任务可视化统计相关接口与实现（具体以该目录内容为准）。
- `utils.py` / `utils_reference.py`：模型枚举、结构定义、参考实现等。

#### 2.5.7 `backend/app/log_config.json`

日志配置（Python logging dictConfig）。

### 2.6 Worker/密集计算服务（`backend/docker/`）

用于在容器或独立环境中运行“任务执行端（worker）”，通常与后端通过 HTTP 接口交互。

- `run.sh` / `run_image.sh`：启动脚本（拉镜像/运行容器等）。
- `service/`：worker 服务代码（FastAPI）。

#### 2.6.1 `backend/docker/service/main.py`

worker 服务入口：
- 暴露 `/state` 查询 worker 状态
- 暴露 `/stop_current_task` 终止指定任务（通过 pid 管理）
- 生命周期钩子里 `on_create/on_destroy` 初始化与清理

### 2.7 测试与样例数据（`backend/test/`）

用于后端/任务流程的样例数据与 Notebook：
- `data.csv` / `data.sdf` / `train_regression_group.sdf`：样例数据
- `config_default.yaml`：测试配置
- `test.ipynb`：测试 notebook（仅用于研发/演示，客户存档可保留或删除）

## 3. 前端工程（`frontend/`）

Vue3 + Vite + TypeScript 的前端工程（Uni-QSAR UI）：
- 文件上传、任务创建、任务列表/详情展示
- 模型列表/可视化
- 分子结构编辑与展示（集成 RDKit js、Ketcher、3Dmol 等）

### 3.1 `frontend/README.md`

前端说明（指出 ketcher 版本与来源）。

### 3.2 `frontend/package.json`

前端依赖与脚本：
- 开发：`vite`
- 构建：`build-dev` / `build-prod`
- 类型检查：`vue-tsc`
- 代码规范：`eslint`、`prettier`

关键依赖（节选）：
- `vue`、`vue-router`、`pinia`
- `element-plus`（UI）
- `echarts`（图表）
- `@rdkit/rdkit`（RDKit wasm/js）
- `molstar`、`3Dmol`（结构展示相关）
- `dexie`（IndexedDB）

### 3.3 `frontend/public/`

静态资源：
- `RDKit_minimal.js/.wasm`、`3Dmol-min.js`
- `ketcher-standalone/`：结构编辑器静态站点资源
- 图片/模板等

### 3.4 `frontend/src/`

前端源代码：
- `App.vue` / `main.ts`：应用入口
- `router/`：路由
- `stores/`：Pinia 状态
- `service/`：API 请求封装（对接后端）
- `views/`：页面
- `components/`：组件库（含分子编辑/可视化等）
- `utils/` / `types/` / `constants/`：通用工具、类型与常量
- `locale/`：多语言

### 3.5 `frontend/Dockerfile`、`frontend/default.conf`

前端容器化与 Nginx 配置（用于部署静态页面）。

## 4. 通用工具与数据处理（`utils/`）

该目录更偏 “RDKit + 数据处理工具集/脚本”，与 `backend/` 的服务逻辑相对独立。

### 4.1 `utils/struct/`

数据结构定义（Pydantic 模型等）：
- `base.py`：分子数据基础结构/扩展结构（以 SMILES、CAS、odor label 等为核心字段）。

### 4.2 `utils/utils/`

通用工具函数：
- `base.py`：基础工具（如 SMILES 校验、数据处理等）
- `draw.py`：可视化绘图（条形图、treemap 等）
- `robot.py`：数据抓取/自动化（如 PubChem / goodscents 获取信息等）
- `run.log`：运行日志样例

### 4.3 `utils/database/`

数据/Notebook：
- `data/`：数据文件目录（例如样例/缓存/中间产物，具体以目录内容为准）
- `test.ipynb`：数据处理/分析 notebook

## 5. 交付与落地注意事项（面向客户/运维）

### 5.1 路径与配置

当前后端代码中存在多处硬编码路径（例如 `/vepfs/fs_users/...`），客户环境落地时一般需要：
- 改为环境变量（如 `FILES_DIR`、`MODELS_DIR`、`MLRUNS_DIR` 等）
- 或统一写入配置文件（YAML/JSON）并在启动时加载

### 5.2 服务拆分

从目录结构看，系统包含：
- Web 后端（`backend/app`）：提供 API、鉴权、任务管理、MongoDB 存储
- Worker 服务（`backend/docker/service`）：执行任务、管理进程 PID、可被后端调度
- Web 前端（`frontend`）：用户交互
- 工具库（`utils`）：离线/脚本/分析工具

### 5.3 最小运行形态（概念说明）

典型需要组件：
- MongoDB
- 后端 FastAPI
- 前端静态站点（Nginx 或 Vite build 产物）
- （可选）worker 执行端

> 本文档不包含一键启动步骤，因为不同客户环境（路径、端口、鉴权、MongoDB 地址、模型存储）需要定制化；如需我可以补充一份“客户环境部署清单/变量表”。
