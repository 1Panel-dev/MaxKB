# MaxKB Database and Deployment Rules

## Database Design and Management

### PostgreSQL with pgvector
- Use PostgreSQL as the primary database
- Enable pgvector extension for vector operations
- Implement proper indexing strategies for vector searches
- Use connection pooling for performance optimization
- Example configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        'NAME': 'maxkb',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        }
    }
}
```

### Database Schema Design
- Use UUID fields for primary keys where appropriate
- Implement proper foreign key relationships
- Add database constraints for data integrity
- Use Django migrations for schema changes
- Example model:
```python
class Knowledge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'knowledge'
        indexes = [
            models.Index(fields=['workspace', 'created_time']),
        ]
```

### Vector Database Operations
- Store document embeddings in pgvector format
- Implement efficient similarity search queries
- Use proper vector indexing (HNSW, IVFFlat)
- Handle vector dimension consistency
- Example vector operations:
```python
class DocumentVector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    vector = VectorField(dimensions=1536)  # OpenAI embedding dimension
    content = models.TextField()
    
    class Meta:
        indexes = [
            HnswIndex(
                name='document_vector_hnsw_idx',
                fields=['vector'],
                m=16,
                ef_construction=64,
            ),
        ]
```

### Database Performance Optimization
- Use select_related() and prefetch_related() for query optimization
- Implement database query monitoring and analysis
- Use database indexes for frequently queried fields
- Implement proper pagination for large datasets
- Monitor and optimize slow queries

## Redis Configuration

### Caching Strategy
- Use Redis for session storage and caching
- Implement cache invalidation strategies
- Cache frequently accessed data (user sessions, model configs)
- Use Redis for Celery message broker
- Example Redis configuration:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,
            }
        }
    }
}
```

### Celery Configuration
- Use Redis as Celery broker and result backend
- Configure Celery workers for async tasks
- Implement task monitoring and error handling
- Use Celery Beat for scheduled tasks
- Example Celery setup:
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
```

## Docker Containerization

### Multi-stage Docker Builds
- Use multi-stage builds for optimization
- Separate build and runtime environments
- Minimize image size and security vulnerabilities
- Example Dockerfile structure:
```dockerfile
# Build stage
FROM node:18-alpine AS frontend-builder
WORKDIR /app/ui
COPY ui/package*.json ./
RUN npm ci --only=production
COPY ui/ ./
RUN npm run build

# Runtime stage
FROM python:3.11-slim
WORKDIR /opt/maxkb
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=frontend-builder /app/ui/dist ./ui/dist
COPY . .
EXPOSE 8080
CMD ["gunicorn", "maxkb.wsgi:application"]
```

### Docker Compose Configuration
- Use Docker Compose for local development
- Define services for all components (app, db, redis)
- Implement proper networking and volumes
- Support environment-specific configurations
- Example docker-compose.yml:
```yaml
version: '3.8'
services:
  maxkb:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: maxkb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

## Environment Configuration

### Configuration Management
- Use environment variables for configuration
- Support multiple deployment environments (dev, staging, prod)
- Implement configuration validation
- Use secure secret management
- Example configuration:
```python
class Config(dict):
    defaults = {
        "DB_HOST": "127.0.0.1",
        "DB_PORT": 5432,
        "DB_USER": "postgres",
        "DB_PASSWORD": "password",
        "REDIS_HOST": "127.0.0.1",
        "REDIS_PORT": 6379,
        "DEBUG": False,
    }
    
    def load_from_env(self):
        for key in self.defaults:
            value = os.environ.get(key, self.defaults[key])
            self[key] = self._convert_type(value)
```

### Security Configuration
- Use secure random secret keys
- Implement proper CORS settings
- Configure HTTPS in production
- Set up proper authentication and authorization
- Use environment-specific security settings

## Deployment Strategies

### Production Deployment
- Use Gunicorn as WSGI server
- Configure Nginx as reverse proxy
- Implement proper logging and monitoring
- Set up health checks and readiness probes
- Example Gunicorn configuration:
```python
# gunicorn.conf.py
bind = "0.0.0.0:8080"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
```

### Scaling Considerations
- Design for horizontal scaling
- Use load balancers for multiple instances
- Implement database read replicas
- Use CDN for static assets
- Monitor resource usage and performance

### Backup and Recovery
- Implement automated database backups
- Test backup restoration procedures
- Use versioned backup storage
- Implement disaster recovery plans
- Monitor backup integrity and completeness

## Monitoring and Logging

### Application Monitoring
- Implement comprehensive logging
- Use structured logging formats
- Monitor application performance metrics
- Set up alerting for critical issues
- Example logging configuration:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/maxkb/application.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Database Monitoring
- Monitor database performance and connections
- Track query execution times
- Monitor vector search performance
- Set up database health checks
- Implement query optimization alerts

### Infrastructure Monitoring
- Monitor server resources (CPU, memory, disk)
- Track network performance and latency
- Monitor container health and resource usage
- Implement automated scaling triggers
- Set up comprehensive alerting systems
