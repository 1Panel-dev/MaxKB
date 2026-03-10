# AI-RAG Docker 外挂配置指南

本文档详细说明如何将 AI-RAG 项目打包成 Docker 镜像时，将数据库和存储进行外挂配置，以实现数据持久化和灵活部署。

## 1. 现有 Docker 配置分析

### 1.1 基础镜像信息

- 基础镜像：`ghcr.io/1panel-dev/maxkb-base:python3.11-pg17.6`
- 包含 PostgreSQL 17.6 和 Redis
- 暴露端口：8080
- 卷挂载：`/opt/maxkb`

### 1.2 默认配置

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| MAXKB_DB_HOST | 127.0.0.1 | 数据库主机地址 |
| MAXKB_DB_PORT | 5432 | 数据库端口 |
| MAXKB_DB_NAME | maxkb | 数据库名称 |
| MAXKB_DB_USER | ${POSTGRES_USER} | 数据库用户名 |
| MAXKB_DB_PASSWORD | ${POSTGRES_PASSWORD} | 数据库密码 |
| MAXKB_REDIS_HOST | 127.0.0.1 | Redis 主机地址 |
| MAXKB_REDIS_PORT | 6379 | Redis 端口 |
| MAXKB_EMBEDDING_MODEL_PATH | /opt/maxkb-app/model/embedding | 嵌入模型路径 |
| MAXKB_EMBEDDING_MODEL_NAME | /opt/maxkb-app/model/embedding/shibing624_text2vec-base-chinese | 嵌入模型名称 |

### 1.3 镜像打包

1. docker build -f installer/Dockerfile -t maxkb:latest 

## 2. 数据库外挂配置

### 2.1 使用外部 PostgreSQL 数据库

#### 步骤 1: 准备外部数据库

1. 安装并启动 PostgreSQL 数据库（建议版本 14+）
2. 创建数据库和用户：

```sql
CREATE DATABASE maxkb;
CREATE USER maxkb_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE maxkb TO maxkb_user;
```

#### 步骤 2: 配置 Docker 容器

使用 `docker run` 命令时，通过环境变量指定外部数据库配置：
##### 2.1：简单目录挂载
```
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /path/to/maxkb:/opt/maxkb \
  -v /path/to/postgres/data:/var/lib/postgresql/data \
  -v /path/to/redis/data:/data \
  your_maxkb_image:tag
```
##### 2.2：外部数据库挂载
```bash
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /path/to/maxkb:/opt/maxkb \
  -e MAXKB_DB_HOST=your_database_host \
  -e MAXKB_DB_PORT=5432 \
  -e MAXKB_DB_NAME=maxkb \
  -e MAXKB_DB_USER=maxkb_user \
  -e MAXKB_DB_PASSWORD=your_strong_password \
  your_maxkb_image:tag
```

### 2.2 使用外部 Redis

#### 步骤 1: 准备外部 Redis

1. 安装并启动 Redis 服务
2. 配置 Redis 密码（可选）

#### 步骤 2: 配置 Docker 容器

```bash
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /path/to/maxkb:/opt/maxkb \
  -e MAXKB_REDIS_HOST=your_redis_host \
  -e MAXKB_REDIS_PORT=6379 \
  -e MAXKB_REDIS_PASSWORD=your_redis_password \
  your_maxkb_image:tag
```

## 3. 存储外挂配置

### 3.1 基础存储挂载

MaxKB 默认会在 `/opt/maxkb` 目录下创建以下子目录：
- `logs`: 日志文件
- `local`: 本地存储
- `python-packages`: Python 包

#### 挂载方式

```bash
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /path/to/maxkb:/opt/maxkb \
  your_maxkb_image:tag
```

### 3.2 模型文件外挂

#### 步骤 1: 准备模型目录

```bash
mkdir -p /path/to/maxkb/model/embedding
```

#### 步骤 2: 下载模型文件

将嵌入模型文件下载到准备好的目录中，例如：
- `shibing624_text2vec-base-chinese`

#### 步骤 3: 配置 Docker 容器

```bash
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /path/to/maxkb:/opt/maxkb \
  -v /path/to/maxkb/model:/opt/maxkb-app/model \
  -e MAXKB_EMBEDDING_MODEL_PATH=/opt/maxkb-app/model/embedding \
  -e MAXKB_EMBEDDING_MODEL_NAME=/opt/maxkb-app/model/embedding/shibing624_text2vec-base-chinese \
  your_maxkb_image:tag
```

### 3.3 静态文件外挂

如果需要自定义静态文件，可以挂载 `ui/dist` 目录：

```bash
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /path/to/maxkb:/opt/maxkb \
  -v /path/to/ui/dist:/opt/maxkb-app/ui/dist \
  your_maxkb_image:tag
```

## 4. 完整的 Docker Compose 配置

### 4.1 使用外部数据库

```yaml
version: '3.8'

services:
  maxkb:
    image: your_maxkb_image:tag
    container_name: maxkb
    ports:
      - "8080:8080"
    volumes:
      - /path/to/maxkb:/opt/maxkb
      - /path/to/maxkb/model:/opt/maxkb-app/model
    environment:
      - MAXKB_DB_HOST=postgres
      - MAXKB_DB_PORT=5432
      - MAXKB_DB_NAME=maxkb
      - MAXKB_DB_USER=maxkb_user
      - MAXKB_DB_PASSWORD=your_strong_password
      - MAXKB_REDIS_HOST=redis
      - MAXKB_REDIS_PORT=6379
      - MAXKB_REDIS_PASSWORD=your_redis_password
      - MAXKB_EMBEDDING_MODEL_PATH=/opt/maxkb-app/model/embedding
      - MAXKB_EMBEDDING_MODEL_NAME=/opt/maxkb-app/model/embedding/shibing624_text2vec-base-chinese
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14-alpine
    container_name: postgres
    ports:
      - "5432:5432"
    volumes:
      - /path/to/postgres/data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=maxkb
      - POSTGRES_USER=maxkb_user
      - POSTGRES_PASSWORD=your_strong_password

  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - /path/to/redis/data:/data
    command: redis-server --requirepass your_redis_password
```

### 4.2 使用内置数据库（仅挂载存储）

```yaml
version: '3.8'

services:
  maxkb:
    image: your_maxkb_image:tag
    container_name: maxkb
    ports:
      - "8080:8080"
    volumes:
      - /path/to/maxkb:/opt/maxkb
      - /path/to/maxkb/model:/opt/maxkb-app/model
      - /path/to/postgres/data:/var/lib/postgresql/data
      - /path/to/redis/data:/data
    environment:
      - MAXKB_EMBEDDING_MODEL_PATH=/opt/maxkb-app/model/embedding
      - MAXKB_EMBEDDING_MODEL_NAME=/opt/maxkb-app/model/embedding/shibing624_text2vec-base-chinese
```

## 5. 数据迁移和备份

### 5.1 数据库备份

#### 使用外部数据库

直接备份外部 PostgreSQL 数据库：

```bash
pg_dump -h your_database_host -U maxkb_user -d maxkb > maxkb_backup.sql
```

#### 使用内置数据库

```bash
docker exec -t maxkb pg_dump -U postgres -d maxkb > maxkb_backup.sql
```

### 5.2 数据库恢复

#### 使用外部数据库

```bash
psql -h your_database_host -U maxkb_user -d maxkb < maxkb_backup.sql
```

#### 使用内置数据库

```bash
cat maxkb_backup.sql | docker exec -i maxkb psql -U postgres -d maxkb
```

### 5.3 存储备份

备份挂载的存储目录：

```bash
rsync -av /path/to/maxkb /path/to/backup/maxkb
```

## 6. 注意事项

1. **权限设置**：确保挂载目录的权限正确，容器内进程需要有读写权限
2. **路径一致性**：确保环境变量中指定的路径与挂载路径一致
3. **首次启动**：首次启动时，系统会自动执行数据库迁移，创建所需的表结构
4. **模型文件**：确保模型文件的完整性和正确性，避免模型加载失败
5. **版本兼容性**：不同版本的 MaxKB 可能有不同的数据库结构，升级时需要注意
6. **性能优化**：对于生产环境，建议使用外部数据库和 Redis，以获得更好的性能
7. **网络配置**：如果使用外部数据库，确保网络连接畅通，防火墙规则允许访问
8. **备份策略**：定期备份数据库和存储目录，以防数据丢失

## 7. 故障排查

### 7.1 数据库连接失败

- 检查数据库服务是否运行
- 检查网络连接是否畅通
- 检查数据库用户名和密码是否正确
- 检查数据库是否存在

### 7.2 存储挂载问题

- 检查挂载目录权限
- 检查目录是否存在
- 检查文件系统权限

### 7.3 模型加载失败

- 检查模型文件是否完整
- 检查模型路径配置是否正确
- 检查模型文件权限

## 8. 最佳实践

1. **生产环境**：使用外部数据库和 Redis，实现更好的性能和可靠性
2. **开发环境**：可以使用内置数据库，方便快速启动和测试
3. **数据持久化**：始终挂载 `/opt/maxkb` 目录，确保数据不会丢失
4. **定期备份**：建立定期备份机制，确保数据安全
5. **监控**：监控数据库和存储使用情况，及时发现问题
6. **版本管理**：使用 Docker 标签管理不同版本的镜像，方便回滚
7. **配置管理**：使用环境变量或配置文件管理配置，避免硬编码

## 9. 示例部署命令

### 9.1 基本部署（使用内置数据库）

```bash
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /data/maxkb:/opt/maxkb \
  your_maxkb_image:tag
```

### 9.2 完整部署（使用外部数据库）

```bash
docker run -d \
  --name maxkb \
  -p 8080:8080 \
  -v /data/maxkb:/opt/maxkb \
  -v /data/maxkb/model:/opt/maxkb-app/model \
  -e MAXKB_DB_HOST=192.168.1.100 \
  -e MAXKB_DB_PORT=5432 \
  -e MAXKB_DB_NAME=maxkb \
  -e MAXKB_DB_USER=maxkb_user \
  -e MAXKB_DB_PASSWORD=your_strong_password \
  -e MAXKB_REDIS_HOST=192.168.1.100 \
  -e MAXKB_REDIS_PORT=6379 \
  -e MAXKB_REDIS_PASSWORD=your_redis_password \
  your_maxkb_image:tag
```

通过以上配置，您可以灵活地将 MaxKB 部署在 Docker 容器中，并实现数据库和存储的外挂，确保数据持久化和系统可靠性。