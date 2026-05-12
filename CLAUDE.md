# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

MaxKB (Max Knowledge Brain) is an enterprise agent platform combining a RAG pipeline, an agentic workflow engine, and MCP tool-use. The repo is a single deployable that ships a Django/DRF backend and a Vue 3 SPA frontend built into Django's `staticfiles`.

- **Backend**: Python 3.11, Django 5.2, DRF, LangChain/LangGraph, Celery + django-celery-beat + django-apscheduler, PostgreSQL (with pgvector), Redis. Dependency manager is **uv** (see `pyproject.toml`, `tool.uv` sections — torch is pinned to CPU index on Linux/Win and the default index on macOS).
- **Frontend**: Vue 3 + Vite + Element Plus + Pinia, in `ui/`. Two entry HTMLs: `admin.html` (full console) and `chat.html` (embed/widget). The `build` script type-checks and bundles both; `build-chat` builds only the chat entry (`--mode chat`).
- **Packaging**: `installer/` contains the Dockerfile(s) and the layered start scripts (`start-all.sh` → orchestrates `start-postgres.sh`, `start-redis.sh`, `start-maxkb.sh`). The published image is `1panel/maxkb`.

## Common commands

Backend (run from repo root; `uv sync` first to install deps):

```bash
# Dev server (Django runserver on 0.0.0.0:8080) — also runs collectstatic + migrate first
python main.py dev web

# Dev: Celery worker (named "celery") or the local model service
python main.py dev celery
python main.py dev local_model

# Production-style: start everything (web + task workers)
python main.py start all            # add -d for daemon, -w N for worker count, -f to force
python main.py start web
python main.py start task

# DB / static only
python main.py upgrade_db
python main.py collect_static

# Standard Django/DRF tooling (manage.py lives in apps/, not repo root)
python apps/manage.py <command>
python apps/manage.py test <app_label>           # e.g. application, knowledge, chat
python apps/manage.py test application.tests     # single module/class/method
```

`main.py` is the canonical entrypoint; it inserts `apps/` onto `sys.path`, sets `DJANGO_SETTINGS_MODULE=maxkb.settings`, and dispatches to custom management commands in `apps/common/management/commands/` (`start`, `stop`, `restart`, `status`, `celery`). Don't bypass it for `start`/`stop` — those commands manage daemonization and worker pools.

Frontend (run from `ui/`):

```bash
npm install
npm run dev           # admin app (vite default mode)
npm run chat          # chat embed (vite --mode chat)
npm run build         # type-check + build admin
npm run build-chat    # type-check + build chat embed
npm run lint          # eslint --fix
npm run format        # prettier write src/
npm run type-check    # vue-tsc --build, no emit
```

Lint (Python uses ruff, configured in `pyproject.toml` — `line-length = 120`):

```bash
uv run ruff check .
uv run ruff format .
```

Docker quickstart (what users actually run):

```bash
docker run -d --name=maxkb --restart=always -p 8080:8080 -v ~/.maxkb:/opt/maxkb 1panel/maxkb
```

## Architecture

### Process model & settings split

`apps/maxkb/` is the Django project. Settings and URL routing branch on `SERVER_NAME` (set in `main.py` from the requested service):

- `SERVER_NAME=web` (default) → loads `settings/base/web.py`, `urls/web.py`. Full app: REST API, RAG, workflow engine, chat, Celery integration.
- `SERVER_NAME=local_model` → loads `settings/base/model.py`, `urls/model.py`. A separate, much smaller Django process that hosts local embedding/rerank/STT/TTS models (so the heavy ML deps don't have to live in every web worker). Bind host/port come from `LOCAL_MODEL_HOST`/`LOCAL_MODEL_PORT`.

`settings/__init__.py` composes `base + logging + auth + lib + mem`. `lib.py` builds the Celery broker URL (with Redis Sentinel support via `MAXKB_REDIS_SENTINEL_SENTINELS`). Config is read by `apps/maxkb/conf.py:ConfigManager` from env vars and `/opt/maxkb/conf` (overridable via `MAXKB_CONFIG`); key env vars are `MAXKB_DB_*`, `MAXKB_REDIS_*`, `MAXKB_CORE_WORKER`.

The `installer/start-all.sh` is what runs inside the official image: it conditionally launches embedded Postgres/Redis (only when their host is `127.0.0.1`) and then `start-maxkb.sh` runs init-shell hooks from `MAXKB_INIT_SHELL_DIR` before calling `python main.py start`. Note the v1→v2 guard: presence of `PG_VERSION` in legacy paths aborts startup.

### Django apps (under `apps/`)

Each is a self-contained DRF app with the same shape: `api/` (serializers + permissions + view inputs), `views/` (DRF views and routers), `models/`, `serializers/`, `migrations/`, plus optional `sql/`, `template/`, `task/`.

- **`application`** — Agents/applications themselves. Two big engines live here:
  - `chat_pipeline/` — the request-time chat orchestration pipeline (`pipeline_manage.py` + `step/`). This is the simpler "RAG chat" path.
  - `flow/` — the agentic workflow engine. `workflow_manage.py` (plus `knowledge_workflow_manage.py`, `tool_workflow_manage.py`, `*_loop_workflow_manage.py`) executes graphs built from `step_node/` node types (`ai_chat_step_node`, `condition_node`, `intent_node`, `loop_node`/`loop_start_node`/`loop_break_node`/`loop_continue_node`, `mcp_node`, `parameter_extraction_node`, `search_knowledge_node`, `tool_lib_node`, multimodal `image_*`/`speech_*`/`text_to_*` nodes, etc.). Default workflows are JSON: `default_workflow{,_en,_zh,_zh_Hant}.json`. `i_step_node.py` is the node contract; new node types subclass it and register a folder under `step_node/`.
  - `long_term_memory/` — agent-level memory beyond a single chat.
- **`chat`** — Runtime chat sessions, message persistence, MCP client integration (`mcp/`), and chat-page templates (`template/`).
- **`knowledge`** — Knowledge bases, documents, paragraphs, and the vector layer (`vector/`). Background indexing in `task/`.
- **`models_provider`** — LLM/embedding/rerank/STT/TTS provider abstraction. `base_model_provider.py` is the interface; the langchain-* deps (`openai`, `anthropic`, `deepseek`, `google-genai`, `community`, `huggingface`, `ollama`, `aws`, plus `qianfan`, `zhipuai`, `volcengine`, `dashscope`, `cohere`, `tencentcloud`, `xinference-client`) plug in here.
- **`tools`** — Function/tool library exposed to workflows and MCP.
- **`users`**, **`system_manage`**, **`folders`**, **`oss`**, **`trigger`** — auth/RBAC, platform settings, folder/tree organization (uses `django-mptt`), object storage, and scheduled/event triggers (built on `django-celery-beat` and `django-apscheduler`).
- **`local_model`** — Server-side model-serving views (only mounted when `SERVER_NAME=local_model`).
- **`common`** — Cross-cutting infrastructure used by every app. Notable subpackages: `auth/`, `cache/`, `chunk/` (text splitting), `db/`, `encoder/`, `event/`, `exception/`, `field/`, `handle/` (document parsers), `init/` (bootstrapping), `job/`, `lock/`, `log/`, `management/commands/` (the `start`/`stop`/`celery` commands), `middleware/`, `mixins/`, `result/` (standard API response envelope).

### Frontend (`ui/`)

`vite.config.ts` switches entry/output between admin and chat modes. Logic-flow editor for workflows uses `@logicflow/core` + `@logicflow/extension`. Markdown rendering uses `md-editor-v3` + `marked` + `highlight.js` + `katex` + `mermaid`. Audio recording (for STT nodes) via `recorder-core`. PDFs via `pdfjs-dist`. State is Pinia, routing is `vue-router`, i18n is `vue-i18n` with locale files under `src/` (also note backend locales at `apps/locales/`).

### Adding a workflow node

A new workflow step is a directory under `apps/application/flow/step_node/<name>_node/` implementing `i_step_node.INode` (look at `ai_chat_step_node` or `condition_node` as templates). The frontend counterpart lives under `ui/src/` in the workflow editor — both sides share the same node `type` string, and the node's JSON schema drives the editor form.

## Conventions worth knowing

- All Python code uses `ruff` with 120-char lines — run `uv run ruff format` before committing.
- `main.py` rewrites `HF_HOME` to `/opt/maxkb-app/model/base` and `TMPDIR` to `/opt/maxkb-app/tmp`. Local dev outside Docker generally needs those directories to exist and be writable, or those env vars set before launch.
- `collectstatic` is invoked on every `start`/`dev` — the built Vue assets from `ui/dist` are expected on disk; the Docker build does this for you, but for local dev run `npm run build` (or `npm run dev` and proxy) before hitting the Django server if you need the bundled UI.
- The `migrate` step in `main.py:perform_db_migrate` retries up to 10×5s while Postgres is in crash-recovery startup — useful to remember when debugging container boot loops.
- Celery task serializer is `hmac_signed_serializer` (custom); broker URL is built from the same Redis env vars as the Django cache and supports Sentinel.
- License is GPLv3. Contributions are expected to be small, incremental PRs (see `CONTRIBUTING.md`).
