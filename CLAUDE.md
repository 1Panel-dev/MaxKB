# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MaxKB is an enterprise-grade AI assistant platform that integrates RAG (Retrieval-Augmented Generation) pipelines, workflow engines, and MCP tool-use capabilities. The project uses Django for the backend and Vue.js for the frontend.

**Tech Stack:**
- Backend: Python/Django 5.2.6 with Django REST Framework
- Frontend: Vue.js 3 + TypeScript + Vite
- Database: PostgreSQL with pgvector for vector storage
- AI Framework: LangChain with support for multiple LLM providers
- Task Processing: Celery for background tasks

## Development Commands

### Frontend (ui/ directory)
```bash
# Development server
npm run dev

# Chat interface development
npm run chat

# Build for production
npm run build

# Build chat interface
npm run build-chat

# Type checking
npm run type-check

# Linting and formatting
npm run lint
npm run format
```

### Backend (apps/ directory)
```bash
# Development server (from apps/ directory)
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### Package Management
Uses `uv` with `pyproject.toml` for Python dependencies. Install with:
```bash
uv sync
```

## Architecture Overview

### Django Application Structure
- **apps/maxkb/** - Core configuration and settings
- **apps/chat/** - Conversation and dialogue functionality
- **apps/knowledge/** - Knowledge base and RAG pipeline management
- **apps/application/** - Application and agent management
- **apps/models_provider/** - LLM provider integrations (OpenAI, Claude, etc.)
- **apps/users/** - User management and authentication
- **apps/system_manage/** - System administration
- **apps/common/** - Shared utilities and base classes
- **apps/tools/** - Tool integrations and MCP support
- **apps/folders/** - File and folder organization
- **apps/oss/** - Object storage service integration

### Frontend Structure
- Vue 3 with Composition API
- TypeScript throughout
- Element Plus UI framework
- Pinia for state management
- Vue Router for navigation
- Vite for build tooling

### Key Integrations
- Multiple LLM providers (OpenAI, Anthropic, DeepSeek, Qwen, etc.)
- Vector databases via pgvector
- MCP (Model Context Protocol) for tool integration
- LangChain for AI workflow orchestration
- LogicFlow for workflow visualization

## Coding Standards

### Python/Django Code
- Use snake_case for functions and variables
- Use PascalCase for class names
- Use UPPER_SNAKE_CASE for constants
- Add Chinese comments for complex business logic
- Keep views simple, extract complex logic to service layers
- Use Django ORM for database operations
- Follow DRF patterns for API development

### Frontend Code
- Use PascalCase for component file names
- Use camelCase for function and variable names
- Use TypeScript types throughout, avoid `any`
- Add Chinese comments for complex UI interactions
- Use existing Element Plus components
- Centralize API calls, avoid direct requests in components
- Follow project's ESLint and Prettier configurations

### General Principles
- Keep logic simple and maintainable
- Use existing Django/Vue patterns and utilities
- Minimize scope of changes
- Add Chinese comments for business logic explanation
- Be direct and concise - avoid creating unnecessary documentation files

## Environment Notes
- Development environment: Windows
- Use PowerShell syntax for command examples
- Project includes comprehensive Cursor rules for code style and patterns