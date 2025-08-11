# MaxKB Development Rules

## Project Overview
MaxKB is an enterprise-grade AI agent platform that provides RAG (Retrieval-Augmented Generation) capabilities, workflow orchestration, and multi-modal AI interactions. The platform supports knowledge base management, application development, and seamless integration with various LLM providers.

## Technology Stack & Architecture

### Backend Framework
- Use Django 5.2.4 as the primary web framework
- Follow Django REST Framework patterns for API development
- Use PostgreSQL with pgvector for vector database operations
- Implement Celery for asynchronous task processing
- Use Redis for caching and message queuing

### Frontend Framework
- Use Vue.js 3.5+ with TypeScript for frontend development
- Use Element Plus 2.10+ as the primary UI component library
- Use Pinia for state management
- Use Vite as the build tool
- Follow Vue 3 Composition API patterns

### AI/ML Integration
- Use LangChain for LLM integration and workflow orchestration
- Support multiple model providers (OpenAI, Claude, DeepSeek, Qwen, etc.)
- Use sentence-transformers for text embedding
- Implement RAG patterns for knowledge retrieval

## Code Organization & Structure

### Django Apps Structure
- `users`: User management and authentication
- `knowledge`: Knowledge base and document management
- `application`: AI application and workflow management
- `chat`: Chat functionality and conversation handling
- `models_provider`: LLM provider integration
- `tools`: Tool management and MCP integration
- `system_manage`: System administration
- `oss`: Object storage service
- `common`: Shared utilities and base classes

### API Design Patterns
- Follow RESTful API conventions
- Use workspace-based URL patterns: `/workspace/{workspace_id}/resource`
- Implement proper authentication and permission checks
- Use serializers for data validation and transformation
- Return consistent response formats using `common.result`

## Development Guidelines

### Python Code Style
- Follow PEP 8 coding standards
- Use type hints for function parameters and return values
- Implement proper error handling with custom exceptions
- Use Django's translation framework for internationalization
- Write comprehensive docstrings for classes and methods

### Frontend Code Style
- Use TypeScript for all new frontend code
- Follow Vue.js style guide and best practices
- Use composition API over options API
- Implement proper error handling and loading states
- Use Element Plus components consistently

### Database Design
- Use Django ORM for database operations
- Implement proper foreign key relationships
- Use UUID fields for primary keys where appropriate
- Add proper database indexes for performance
- Use migrations for all schema changes

### Security Practices
- Implement proper authentication and authorization
- Use Django's built-in security features
- Validate all user inputs
- Implement rate limiting for API endpoints
- Use HTTPS in production environments

## Specific Implementation Patterns

### Knowledge Base Management
- Support multiple document formats (PDF, DOCX, TXT, etc.)
- Implement document chunking and vectorization
- Use embedding models for semantic search
- Support web crawling for online documents
- Implement document versioning and updates

### Application Workflow
- Use workflow engine for complex AI processes
- Support various node types (AI chat, search, condition, etc.)
- Implement proper workflow validation
- Support workflow versioning and rollback
- Use LangGraph for workflow orchestration

### Model Provider Integration
- Implement abstract base classes for model providers
- Support both local and cloud-based models
- Handle model credentials securely
- Implement proper error handling for model failures
- Support streaming responses for chat interactions

### Chat System
- Implement real-time chat functionality
- Support conversation history and context
- Handle multi-modal inputs (text, image, audio)
- Implement proper message formatting and rendering
- Support chat export and analysis

## Testing Guidelines
- Write unit tests for all business logic
- Use Django's test framework for backend testing
- Implement integration tests for API endpoints
- Use Vue Test Utils for frontend component testing
- Maintain test coverage above 80%

## Performance Optimization
- Use database query optimization techniques
- Implement proper caching strategies
- Use async/await for I/O operations
- Optimize vector search operations
- Monitor and profile application performance

## Deployment & Operations
- Use Docker for containerization
- Support both single-node and distributed deployments
- Implement proper logging and monitoring
- Use environment variables for configuration
- Support database migrations and backups

## Documentation Standards
- Write clear API documentation using drf-spectacular
- Maintain up-to-date README files
- Document configuration options and environment variables
- Provide deployment guides and troubleshooting tips
- Include code examples in documentation
