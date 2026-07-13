# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MaxKB (Max Knowledge Brain) is an open-source enterprise-grade agent platform built on RAG, agentic workflows, and MCP tool-use. Backend is Python 3.11 / Django 5.2 / LangChain; frontend is Vue 3 / Vite. Data layer is PostgreSQL + pgvector and Redis; Celery for async work. GPL-3.0.

## Development Commands

The backend is driven by a single entrypoint `main.py` (not `manage.py` directly). It sets `apps/` on `sys.path` and configures Django settings, so module imports are `from application...`, `from common...` — not `from apps.application...`.

```bash
# Dev: runs collectstatic + migrate, then ONE service. You usually run all three in separate terminals.
python main.py dev            # web      (Django runserver on 0.0.0.0:8080)
python main.py dev celery     # celery worker (queues: celery, model)
python main.py dev local_model # embedding/local model server on 127.0.0.1:11636

# Production-style start (spawns gunicorn + celery_default + local_model as watched daemons)
python main.py start all -d
python main.py start web -w 3      # gunicorn + local_model
python main.py start task          # celery_default + celery_model
python main.py stop all            # stop daemons
python main.py status              # daemon status

# Database / static
python main.py upgrade_db          # run migrations (has PG-crash-recovery retry logic)
python main.py collect_static      # collect static files (serves ui/dist)
python apps/manage.py makemigrations <app>
python apps/manage.py migrate

# i18n — .po files live in apps/locales/{en_US,zh_CN,zh_Hant}/LC_MESSAGES/
python apps/manage.py makemessages -l zh_Hant  # extract strings
python apps/manage.py compilemessages            # compile .po -> .mo (required at build time)
```

Frontend (`ui/`):
```bash
cd ui
npm install
npm run dev          # admin SPA (Vite dev server, proxies /admin/api & /chat/api -> :8080)
npm run chat         # chat embed SPA
npm run build        # build admin dist
npm run build-chat   # build chat dist
npm run lint         # eslint --fix
npm run type-check   # vue-tsc
```

Python linting: `ruff` (line-length 120, config in `pyproject.toml`). No test runner is configured; per-app `tests.py` files are empty stubs.

Dependencies are managed with `uv` (`uv.lock`, `pyproject.toml`). Python is pinned to `~=3.11.0`.

## Architecture

### Settings: one project, two runtimes

`apps/maxkb/settings/` is split by the `SERVER_NAME` env var (set by `main.py` based on the service):
- `base/web.py` — full Django app (DB, cache, REST framework, all `INSTALLED_APPS`, templates, i18n). Default for `web`.
- `base/model.py` — minimal settings for the local-embedding model server. Selected when `SERVER_NAME=local_model`.
- `settings/__init__.py` imports `web` or `model` accordingly. This is why a missing/wrong `SERVER_NAME` silently loads the wrong app set.

All runtime config comes from the `CONFIG` singleton (`apps/maxkb/const.py` + `conf.py`). `MAXKB_CONFIG_TYPE=ENV` reads `MAXKB_*` env vars (the `.env` file uses this); otherwise it loads YAML from `/opt/maxkb/conf`. `CONFIG.get_db_setting()` / `get_cache_setting()` build the DB and Redis configs (with optional Redis Sentinel support).

### URL layout

Two API surfaces, configured via `CONFIG.get_admin_path()` (default `/admin`) and `get_chat_path()` (default `/chat`):
- `/admin/api/*` — management API (users, tools, models_provider, folders, knowledge, system_manage, application, trigger, oss, homepage). Backed by DRF + drf-spectacular (Swagger at `/admin/api-doc`).
- `/chat/api/*` — runtime chat API (chat views + MCP endpoint at `chat/views/mcp.py`).

The Vue admin SPA and chat SPA are served as Django static files from `ui/dist` (`STATICFILES_DIRS`).

### Model provider abstraction (`apps/models_provider/`)

`IModelProvider` (abstract) -> per-vendor impl in `impl/<vendor>_model_provider/` (OpenAI, Anthropic, Gemini, Qwen, DeepSeek, Ollama, vLLM, Wenxin, Zhipu, Volcengine, AWS Bedrock, Tencent, Kimi, MiniMax, Xinference, local, etc.). Each provider registers `ModelInfo` (model type + credential + model class) into `ModelInfoManage`. Model types are `LLM`, `EMBEDDING`, `STT`, `TTS`, `IMAGE` (vision), `TTI` (image gen), `RERANKER`, `TTV`, `ITV` (`ModelTypeConst`). To add a model, register `ModelInfo` with a `MaxKBBaseModel` subclass and a `BaseModelCredential`. The local_model service serves the bundled sentence-transformers embedding model.

### Application & chat (`apps/application/`, `apps/chat/`)

An "application" is a configurable agent. Two execution engines coexist:
- `chat_pipeline/` — older linear step pipeline (`PipelineManage` builder, steps in `step/`).
- `flow/` — the workflow engine. A graph of `step_node/*` nodes (start, ai_chat, search_knowledge, search_document, reranker, condition, tool, mcp, loop/*, variable_*, form, document_split/extract, knowledge_write, speech/text/image/video nodes, etc.). `workflow_manage.py` runs nodes concurrently on a `ThreadPoolExecutor`, streams output, and merges node details. Default workflows are seeded from `default_workflow*.json`. Specialized managers: `tool_workflow_manage`, `knowledge_workflow_manage`, `loop_workflow_manage` (and their `_loop_` variants).

Streaming chat responses go through `BaseToResponse` (`apps/common/handle/base_to_response.py`) with three impls: `system_to_response` (MaxKB SSE protocol), `openai_to_response` (OpenAI-compatible), `loop_to_response`. SSE frames are `data: <json>\n\n`.

### RAG / knowledge (`apps/knowledge/`)

Documents are split into paragraphs; paragraphs are embedded and stored via `vector/pg_vector.py` (pgvector). Search hits the vector store then optionally a reranker model. Celery tasks under `knowledge/task/` handle document parsing/embedding.

### Async & scheduling (`apps/ops/`)

Celery app `ops.celery` (name `MaxKB`) with two queues: `celery` (general) and `model` (model/long tasks). Broker + result backend is Redis (sentinel-aware). Tasks use a custom `hmac_signed_serializer`. `@celery_app.task` decorated functions are autodiscovered from every `INSTALLED_APPS`. `django-apscheduler` and `django-celery-beat` provide scheduled jobs. `celery-once` provides single-execution locking.

### MCP (`apps/chat/views/mcp.py`)

MaxKB applications can be exposed as MCP tools: a JSON-RPC endpoint (`initialize`, `tools/list`, `tools/call`) routed through `chat.mcp.tools.MCPToolHandler`. MaxKB also *consumes* external MCP servers via `mcp_node` in the workflow and `langchain-mcp-adapters`.

### Frontend (`ui/`)

Two SPAs built from the same repo: admin (`npm run build`) and chat embed (`npm run build-chat`), both into `ui/dist`. Workflow canvas uses LogicFlow; markdown editor is md-editor-v3. Vite proxies `/admin/api` and `/chat/api` to `127.0.0.1:8080` in dev. Env files are in `ui/env/`.

### Sandbox

`installer/sandbox.c` is compiled to `sandbox.so` (loaded via ctypes) to run untrusted Python from tools/nodes in a restricted namespace. Banned keywords/hosts come from `MAXKB_SANDBOX_PYTHON_BANNED_KEYWORDS` / `MAXKB_SANDBOX_PYTHON_BANNED_HOSTS`. Pre-installed packages for sandbox execution live under the path in `MAXKB_SANDBOX_PYTHON_PACKAGE_PATHS`.

## Coding Conventions

- Python line length: **120** (`.editorconfig`, `pyproject.toml`, Copilot rules).
- **Minimize diffs.** Do not reformat entire files, reflow lines, or rename unless required. Make the smallest possible change and preserve existing structure/formatting. (`.github/copilot-instructions.md`)
- Match the existing module header style (most files begin with a `# coding=utf-8` block-style docstring with `@project/@Author/@file/@date/@desc`).
- UI code follows the existing Vue 3 Composition API + `<script setup>` + Element Plus patterns; lint with `npm run lint` before finishing.
