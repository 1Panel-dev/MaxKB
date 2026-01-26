# MokeKB

基于大模型与 RAG 的知识库问答系统，包含完整的知识库构建、向量检索、对话编排与模型接入能力。后端采用 Django + DRF，前端采用 Vue 3（Vite），默认使用 PostgreSQL + pgvector 作为向量存储，并通过 Celery 处理异步任务。

## 功能概览

- 文档上传与在线内容采集，自动切分与向量化入库
- RAG 检索增强生成，降低幻觉并提升命中率
- 模型中立：内置多家模型提供方接入（本地/云端）
- 工作流与函数库编排，支持复杂对话/工具调用
- 管理端 Web UI，支持多语言

## 架构概览

- Web 前端：`ui/`，Vue 3 + Vite，构建产物由后端静态服务承载
- API 后端：`apps/`，Django + DRF（`drf_spectacular` 生成 API 文档）
- 异步任务：`apps/ops/celery` + 各业务 app 的 `task/`
- 数据存储：PostgreSQL + pgvector（向量检索）+ Redis 缓存

典型流程（简化）：

1. 用户在前端发起问答请求
2. `chat` 接口接收请求并转交 `application`
3. `application` 运行对话流水线（`chat_pipeline/`）与工作流（`flow/`）
4. `knowledge` 完成检索与向量匹配
5. `models_provider` 选择并调用大模型生成答案
6. 返回答案与引用内容给前端

## 目录结构

```
.
├── apps/                   # Django 后端
│   ├── application/         # 对话编排、工作流、chat pipeline
│   ├── chat/                # 对话接口与会话模型
│   ├── knowledge/           # 知识库、向量检索与文档处理
│   ├── models_provider/     # 模型接入与供应商适配
│   ├── local_model/         # 本地模型服务入口
│   ├── tools/               # 工具与函数库
│   ├── users/               # 用户与权限
│   ├── folders/             # 目录与组织结构
│   ├── oss/                 # 对象存储与文件管理
│   ├── system_manage/       # 系统配置与运维管理
│   ├── common/              # 公共组件：缓存/中间件/工具等
│   ├── ops/                 # Celery 与运维任务
│   └── maxkb/               # Django 项目配置与路由
├── ui/                     # Vue 3 前端
├── installer/              # Docker 与安装脚本
├── main.py                 # 服务控制入口
├── config_example.yml      # 配置示例
└── pyproject.toml          # Python 依赖与版本
```

## 运行与配置

- 配置参考 `config_example.yml`（数据库、Redis、路径、语言等）
- 后端入口在 `main.py`，支持 `start/dev/upgrade_db/collect_static`
- Docker 镜像与安装脚本位于 `installer/`
- 前端构建与开发脚本在 `ui/`

## 后端详解

### 配置与启动

- 入口：`main.py`，启动前会执行 `collectstatic` 和 `migrate`
- 配置加载：`apps/maxkb/conf.py`，优先读取 `config.yml`，也可用 `MAXKB_` 前缀环境变量
- 运行模式：通过 `SERVER_NAME` 切换 `web`/`local_model` 两套 settings 与路由

### URL 路由与页面

- Django 根路由在 `apps/maxkb/urls/`
- `web` 模式：区分管理后台与对话端路径（默认 `/admin` 与 `/chat`），并挂载各业务 app 的 API
- `local_model` 模式：仅暴露 `local_model` 相关接口
- API 文档由 `drf_spectacular` 提供

### 核心业务模块

- `application`：对话编排核心，包含 `chat_pipeline/` 与 `flow/` 两套编排机制
- `knowledge`：知识库与向量检索，负责文档入库、切分、向量化与检索
- `models_provider`：多模型适配层，统一模型调用与配置管理
- `chat`：对话接口与会话记录管理
- `tools`：函数库/工具调用能力，为工作流提供可调用能力
- `oss`：对象存储与文件管理
- `system_manage`：系统配置与运维相关能力

### 异步任务

- Celery 配置在 `apps/ops/celery`
- 各业务 app 的 `task/` 目录提供异步任务（如文档处理、向量化等）

## 技术栈

- 前端：Vue 3 + Vite
- 后端：Python 3.11 + Django + DRF
- LLM：LangChain 生态
- 存储：PostgreSQL + pgvector
- 任务队列：Celery

## License

GPL-3.0，详见 `LICENSE`。
