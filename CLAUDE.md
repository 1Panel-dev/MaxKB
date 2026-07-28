# MaxKB-v3

MaxKB (Max Knowledge Brain) is an open-source platform for building enterprise AI agents with RAG pipelines, agentic workflows, and MCP tool-use capabilities.

## Tech Stack

**Backend:** Python 3.13, Django 6.0, Django REST Framework, LangChain 1.3, LangGraph 1.2, Celery 5.6, uv (package manager)

**Frontend:** Vue 3.5, TypeScript, Vite 8, Element Plus, Pinia, Vue Router

**Infrastructure:** PostgreSQL 17.10 + pgvector, Redis 7

## Project Structure

```
apps/                    # Django backend
  application/           # AI agents & applications
  knowledge/             # Knowledge base & document management
  chat/                  # Chat functionality & MCP integration
  models_provider/       # LLM provider integrations (OpenAI, Anthropic, etc.)
  common/                # Shared utilities, auth, caching, chunking
  maxkb/                 # Django settings, URL routing, config
  ops/                   # Celery task queue configuration
  users/                 # User management
  tools/                 # Tool/function management
ui/                      # Vue.js frontend
  src/
    api/                 # API client services
    views/               # Page views
    components/          # Vue components
    workflow/            # Workflow UI
installer/               # Docker build scripts and startup scripts
main.py                  # Application entry point
```

## Development Setup

### Backend

```bash
# Install dependencies (requires Python 3.13)
python -m uv pip install -r pyproject.toml

# Run database migrations
cd apps && python manage.py migrate

# Start dev server
python main.py dev
# or: cd apps && python manage.py runserver 0.0.0.0:8080
```

### Frontend

```bash
cd ui
npm install
npm run dev        # dev server with hot reload
npm run build      # production build
npm run type-check # TypeScript check
npm run lint       # ESLint
npm run format     # Prettier
```

### Service Management

```bash
python main.py start all -d       # start all services (web + celery)
python main.py start web -d       # web only
python main.py start task -d      # celery worker
python main.py start local_model -d  # local model service
```

### Docker

```bash
docker build -f installer/Dockerfile -t maxkb:latest .
```

## Configuration

Key environment variables (see `.env`):

| Variable                                                | Description            |
| ------------------------------------------------------- | ---------------------- |
| `MAXKB_DB_HOST` / `MAXKB_DB_PORT`                       | PostgreSQL connection  |
| `MAXKB_DB_NAME` / `MAXKB_DB_USER` / `MAXKB_DB_PASSWORD` | PostgreSQL credentials |
| `MAXKB_REDIS_HOST` / `MAXKB_REDIS_PORT`                 | Redis connection       |

Settings files:

- `apps/maxkb/conf.py` — main config manager (reads env vars)
- `apps/maxkb/settings/base/web.py` — Django settings
- `apps/maxkb/settings/lib.py` — Celery/Redis settings

## Testing

```bash
cd apps && python manage.py test
```

## Code Style

- Python: Ruff linter, line length 120 (`pyproject.toml`)
- TypeScript/Vue: ESLint + Prettier (`ui/`)
- Migrations in `apps/*/migrations/`

## Key Concepts

- **Knowledge Base**: Documents are chunked, embedded, and stored in PostgreSQL with pgvector for semantic search.
- **Applications/Agents**: Built on top of knowledge bases; support workflow-based and RAG-based configurations.
- **Models Provider**: Abstraction layer in `apps/models_provider/` supporting 10+ LLM providers via LangChain.
- **MCP**: Model Context Protocol tools integrated via `langchain-mcp-adapters` in `apps/chat/mcp/`.
- **Task Queue**: Heavy document processing runs async via Celery workers.

## Internationalization

Translations in `apps/locales/` (zh_CN, en_US, zh_Hant) and `ui/src/locales/`.
