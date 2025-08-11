# MaxKB Development Rules

This directory contains comprehensive development rules and guidelines for the MaxKB project. These rules are designed to help developers understand the project structure, coding standards, and best practices when working with the MaxKB codebase.

## Rules Overview

### 1. maxkb-development.md
**Purpose**: Main development guidelines and project overview
**Scope**: Overall project architecture, technology stack, and general development practices
**Key Topics**:
- Project overview and core features
- Technology stack (Django, Vue.js, LangChain, PostgreSQL)
- Code organization and app structure
- Development guidelines and security practices
- Testing and performance optimization
- Documentation standards

### 2. api-development.md
**Purpose**: Backend API development standards
**Scope**: Django REST Framework patterns, API design, and backend development
**Key Topics**:
- RESTful API design principles
- URL structure and HTTP methods
- Authentication and authorization patterns
- Serializer patterns and validation
- Error handling and custom exceptions
- Database operations and query optimization
- Pagination and file upload handling
- Testing and security best practices

### 3. frontend-development.md
**Purpose**: Frontend development standards using Vue.js 3
**Scope**: Vue.js components, TypeScript integration, and UI development
**Key Topics**:
- Vue 3 Composition API patterns
- TypeScript integration and type definitions
- Element Plus UI framework usage
- State management with Pinia
- API integration and HTTP client setup
- Component development and reusability
- Styling with SCSS and responsive design
- Performance optimization and error handling

### 4. ai-integration.md
**Purpose**: AI/LLM integration patterns and practices
**Scope**: LangChain integration, RAG implementation, and AI workflow management
**Key Topics**:
- LangChain integration patterns
- Model provider architecture
- RAG (Retrieval-Augmented Generation) implementation
- Workflow engine integration with LangGraph
- Multi-modal AI support (text, image, audio, video)
- MCP (Model Context Protocol) integration
- Streaming and real-time processing
- AI security and monitoring

### 5. database-deployment.md
**Purpose**: Database design and deployment practices
**Scope**: PostgreSQL configuration, Redis setup, Docker containerization, and production deployment
**Key Topics**:
- PostgreSQL with pgvector configuration
- Database schema design and optimization
- Vector database operations
- Redis caching and Celery configuration
- Docker containerization strategies
- Environment configuration management
- Production deployment and scaling
- Monitoring and logging practices

## How to Use These Rules

### For New Developers
1. Start with `maxkb-development.md` to understand the overall project structure
2. Review `api-development.md` if working on backend features
3. Study `frontend-development.md` for frontend development tasks
4. Consult `ai-integration.md` when working with AI/LLM features
5. Reference `database-deployment.md` for database and deployment tasks

### For Specific Development Tasks

#### Backend API Development
- Primary: `api-development.md`
- Secondary: `maxkb-development.md`, `database-deployment.md`

#### Frontend Development
- Primary: `frontend-development.md`
- Secondary: `maxkb-development.md`, `api-development.md`

#### AI/LLM Features
- Primary: `ai-integration.md`
- Secondary: `maxkb-development.md`, `api-development.md`

#### Database Operations
- Primary: `database-deployment.md`
- Secondary: `maxkb-development.md`, `api-development.md`

#### Deployment and DevOps
- Primary: `database-deployment.md`
- Secondary: `maxkb-development.md`

## Key Principles Across All Rules

### Code Quality
- Follow established coding standards and conventions
- Implement comprehensive error handling
- Write maintainable and readable code
- Use proper typing (Python type hints, TypeScript)
- Follow security best practices

### Architecture Patterns
- Use established design patterns consistently
- Implement proper separation of concerns
- Follow DRY (Don't Repeat Yourself) principles
- Use dependency injection where appropriate
- Maintain clean architecture boundaries

### Testing and Quality Assurance
- Write comprehensive unit and integration tests
- Implement proper test coverage
- Use automated testing in CI/CD pipelines
- Perform code reviews and quality checks
- Monitor application performance and errors

### Documentation
- Maintain up-to-date documentation
- Write clear API documentation
- Include code examples and usage patterns
- Document configuration and deployment procedures
- Provide troubleshooting guides

## Technology Stack Summary

### Backend
- **Framework**: Django 5.2.4 with Django REST Framework
- **Database**: PostgreSQL with pgvector extension
- **Caching**: Redis for caching and message queuing
- **Task Queue**: Celery for asynchronous processing
- **AI/ML**: LangChain for LLM integration and workflows

### Frontend
- **Framework**: Vue.js 3.5+ with TypeScript
- **UI Library**: Element Plus 2.10+
- **State Management**: Pinia
- **Build Tool**: Vite
- **Styling**: SCSS with responsive design

### AI/ML Integration
- **LLM Framework**: LangChain and LangGraph
- **Vector Database**: PostgreSQL with pgvector
- **Embedding Models**: sentence-transformers, OpenAI embeddings
- **Model Providers**: OpenAI, Claude, DeepSeek, Qwen, local models
- **Workflow Engine**: LangGraph for AI workflow orchestration

### Deployment
- **Containerization**: Docker and Docker Compose
- **Web Server**: Gunicorn with Nginx reverse proxy
- **Environment Management**: Environment variables and configuration files
- **Monitoring**: Comprehensive logging and monitoring setup

## Contributing to Rules

When updating or adding new rules:
1. Follow the established format and structure
2. Include practical examples and code snippets
3. Ensure consistency with existing rules
4. Update this README when adding new rule files
5. Review changes with the development team

## Questions and Support

For questions about these rules or clarifications on specific practices:
1. Check the relevant rule file for detailed information
2. Consult the project documentation and README files
3. Reach out to the development team for guidance
4. Contribute improvements and updates to the rules as needed
