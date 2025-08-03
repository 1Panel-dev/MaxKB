# MaxKB v2.0 分离部署完整指南

## 概述

MaxKB v2.0 支持分离部署模式，将系统拆分为4个独立的组件：

1. **Redis 缓存服务** - 会话存储和缓存
2. **PostgreSQL+pgvector 数据库** - 主数据存储和向量检索
3. **MaxKB 后台应用** - 核心业务逻辑和 API 服务
4. **前端页面** - 用户界面和管理后台

## 部署架构图

```
┌─────────────────┐    ┌─────────────────┐
│   前端 Nginx    │    │   后台应用      │
│   (80/443)      │◄──►│   (8080)        │
└─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐
│   Redis         │◄──►│  PostgreSQL     │
│   (6379)        │    │  +pgvector      │
└─────────────────┘    │  (5432)         │
                       └─────────────────┘
```

## 准备工作

### 1. 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+/CentOS 7+)
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 20GB，推荐 100GB+
- **CPU**: 最低 2 核，推荐 4 核+
- **Docker**: 版本 20.10+
- **Docker Compose**: 版本 2.0+ (可选)

### 2. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
```

### 3. 创建数据目录

```bash
sudo mkdir -p /opt/maxkb-data/{redis,postgres,maxkb-logs,maxkb-local,maxkb-models}
sudo chown -R $USER:$USER /opt/maxkb-data
```

## 构建镜像

### 1. 下载源码

```bash
git clone https://github.com/1panel-dev/MaxKB.git
cd MaxKB
git checkout v2.0
```

### 2. 构建所有镜像

```bash
# 设置私有仓库地址
export REGISTRY="harbor.company.com/maxkb"

# 构建并推送所有镜像
chmod +x installer/build-images.sh
./installer/build-images.sh --registry $REGISTRY --push all
```

### 3. 单独构建特定组件

```bash
# 仅构建后台应用
./installer/build-images.sh --registry $REGISTRY --push backend

# 仅构建前端页面
./installer/build-images.sh --registry $REGISTRY --push frontend

# 仅构建向量模型
./installer/build-images.sh --registry $REGISTRY --push models
```

## 部署方式

### 方式一：使用部署脚本 (推荐)

#### 1. 下载部署脚本

```bash
curl -O https://raw.githubusercontent.com/1panel-dev/MaxKB/v2.0/installer/deploy-separated.sh
chmod +x deploy-separated.sh
```

#### 2. 完整部署

```bash
# 部署所有组件
./deploy-separated.sh --registry harbor.company.com/maxkb all

# 自定义配置部署
./deploy-separated.sh \
  --registry harbor.company.com/maxkb \
  --data-dir /data/maxkb \
  --backend-port 8080 \
  --frontend-port 80 \
  all
```

#### 3. 选择性部署

```bash
# 仅部署基础服务
./deploy-separated.sh redis postgres

# 仅部署应用服务
./deploy-separated.sh --registry harbor.company.com/maxkb backend frontend

# 连接外部数据库
./deploy-separated.sh \
  --registry harbor.company.com/maxkb \
  --db-host external-postgres.company.com \
  --db-port 5432 \
  --redis-host external-redis.company.com \
  --redis-port 6379 \
  backend frontend
```

### 方式二：使用 Docker Compose

#### 1. 创建配置文件

```bash
# 复制配置模板
cp installer/env.example .env

# 编辑配置文件
vi .env
```

#### 2. 启动服务

```bash
# 启动所有服务
docker-compose -f installer/docker-compose.yml up -d

# 查看服务状态
docker-compose -f installer/docker-compose.yml ps

# 查看日志
docker-compose -f installer/docker-compose.yml logs -f
```

### 方式三：手动部署

#### 1. 创建网络

```bash
docker network create maxkb-network
```

#### 2. 部署 Redis

```bash
docker run -d \
  --name maxkb-redis \
  --network maxkb-network \
  -p 6379:6379 \
  -v /opt/maxkb-data/redis:/data \
  -e REDIS_PASSWORD="your-redis-password" \
  --restart unless-stopped \
  redis:7-alpine \
  redis-server --requirepass "your-redis-password" --appendonly yes
```

#### 3. 部署 PostgreSQL

```bash
# 创建初始化脚本
cat > /opt/maxkb-data/postgres/init.sql << EOF
CREATE DATABASE maxkb;
\c maxkb;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
EOF

# 启动容器
docker run -d \
  --name maxkb-postgres \
  --network maxkb-network \
  -p 5432:5432 \
  -v /opt/maxkb-data/postgres:/var/lib/postgresql/data \
  -v /opt/maxkb-data/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_USER=maxkb \
  -e POSTGRES_PASSWORD="your-db-password" \
  --restart unless-stopped \
  pgvector/pgvector:pg17
```

#### 4. 部署后台应用

```bash
docker run -d \
  --name maxkb-backend \
  --network maxkb-network \
  -p 8080:8080 \
  -v /opt/maxkb-data/maxkb-logs:/opt/maxkb/logs \
  -v /opt/maxkb-data/maxkb-local:/opt/maxkb/local \
  -v /opt/maxkb-data/maxkb-models:/opt/maxkb-app/model \
  -e MAXKB_CONFIG_TYPE=ENV \
  -e MAXKB_DB_HOST=maxkb-postgres \
  -e MAXKB_DB_USER=maxkb \
  -e MAXKB_DB_PASSWORD="your-db-password" \
  -e MAXKB_REDIS_HOST=maxkb-redis \
  -e MAXKB_REDIS_PASSWORD="your-redis-password" \
  --restart unless-stopped \
  harbor.company.com/maxkb/backend:v2.0
```

#### 5. 部署前端页面

```bash
docker run -d \
  --name maxkb-frontend \
  --network maxkb-network \
  -p 80:80 \
  -e BACKEND_HOST=maxkb-backend \
  -e BACKEND_PORT=8080 \
  --restart unless-stopped \
  harbor.company.com/maxkb/frontend:v2.0
```

## 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| MAXKB_CONFIG_TYPE | 配置类型 | ENV | 是 |
| MAXKB_DB_HOST | 数据库主机 | maxkb-postgres | 是 |
| MAXKB_DB_PORT | 数据库端口 | 5432 | 是 |
| MAXKB_DB_USER | 数据库用户 | maxkb | 是 |
| MAXKB_DB_PASSWORD | 数据库密码 | - | 是 |
| MAXKB_DB_NAME | 数据库名称 | maxkb | 是 |
| MAXKB_REDIS_HOST | Redis 主机 | maxkb-redis | 是 |
| MAXKB_REDIS_PORT | Redis 端口 | 6379 | 是 |
| MAXKB_REDIS_PASSWORD | Redis 密码 | - | 是 |
| MAXKB_REDIS_DB | Redis 数据库 | 0 | 否 |
| MAXKB_LOG_LEVEL | 日志级别 | INFO | 否 |
| MAXKB_LANGUAGE_CODE | 语言代码 | zh-CN | 否 |
| MAXKB_TIME_ZONE | 时区 | Asia/Shanghai | 否 |

### 数据持久化

```
/opt/maxkb-data/
├── redis/              # Redis 数据文件
├── postgres/           # PostgreSQL 数据文件
├── maxkb-logs/         # 应用日志文件
├── maxkb-local/        # 用户上传文件
├── maxkb-models/       # 向量模型文件
└── maxkb-config.env    # 部署配置备份
```

### 网络配置

- **内部网络**: maxkb-network (172.20.0.0/16)
- **容器通信**: 通过容器名进行内部通信
- **外部访问**: 通过端口映射提供外部访问

## 高级配置

### 使用外部数据库

如果您已有 PostgreSQL 和 Redis 服务，可以配置应用连接外部服务：

```bash
./deploy-separated.sh \
  --registry harbor.company.com/maxkb \
  --db-host external-postgres.company.com \
  --db-port 5432 \
  --db-user maxkb \
  --db-password "external-db-password" \
  --redis-host external-redis.company.com \
  --redis-port 6379 \
  --redis-password "external-redis-password" \
  backend frontend
```

### SSL/HTTPS 配置

#### 1. 使用 Nginx 反向代理

```nginx
server {
    listen 443 ssl http2;
    server_name maxkb.company.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2. 使用 Traefik

```yaml
version: '3.8'
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=admin@company.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    
  maxkb-frontend:
    image: harbor.company.com/maxkb/frontend:v2.0
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.maxkb.rule=Host(`maxkb.company.com`)"
      - "traefik.http.routers.maxkb.entrypoints=websecure"
      - "traefik.http.routers.maxkb.tls.certresolver=myresolver"
```

### 集群部署

#### 1. 多实例部署

```bash
# 部署多个后台实例
for i in {1..3}; do
  docker run -d \
    --name maxkb-backend-$i \
    --network maxkb-network \
    -e MAXKB_CONFIG_TYPE=ENV \
    -e MAXKB_DB_HOST=maxkb-postgres \
    -e MAXKB_REDIS_HOST=maxkb-redis \
    harbor.company.com/maxkb/backend:v2.0
done

# 配置负载均衡器
docker run -d \
  --name maxkb-loadbalancer \
  --network maxkb-network \
  -p 8080:80 \
  nginx:alpine
```

#### 2. Redis 集群配置

```bash
# Redis 哨兵模式
export MAXKB_REDIS_SENTINEL_SENTINELS="sentinel1:26379,sentinel2:26379,sentinel3:26379"
export MAXKB_REDIS_SENTINEL_MASTER="mymaster"
```

## 监控和维护

### 健康检查

```bash
# 检查容器状态
docker ps --filter "name=maxkb"

# 检查服务健康状态
curl -f http://localhost:8080/api/health
curl -f http://localhost/

# 检查数据库连接
docker exec maxkb-postgres pg_isready -U maxkb -d maxkb

# 检查 Redis 连接
docker exec maxkb-redis redis-cli -a "your-redis-password" ping
```

### 日志管理

```bash
# 查看应用日志
docker logs maxkb-backend
docker logs maxkb-frontend

# 实时跟踪日志
docker logs -f maxkb-backend

# 查看持久化日志
tail -f /opt/maxkb-data/maxkb-logs/maxkb.log
```

### 备份和恢复

#### 数据库备份

```bash
# 备份数据库
docker exec maxkb-postgres pg_dump -U maxkb maxkb > maxkb_backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker exec -i maxkb-postgres psql -U maxkb maxkb < maxkb_backup.sql
```

#### Redis 备份

```bash
# 备份 Redis
docker exec maxkb-redis redis-cli -a "your-redis-password" BGSAVE
docker cp maxkb-redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d_%H%M%S).rdb
```

#### 文件备份

```bash
# 备份用户文件
tar -czf maxkb_files_backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/maxkb-data/maxkb-local/
```

### 更新升级

#### 1. 更新镜像

```bash
# 拉取新版本镜像
docker pull harbor.company.com/maxkb/backend:v2.1
docker pull harbor.company.com/maxkb/frontend:v2.1

# 更新后台应用
docker stop maxkb-backend
docker rm maxkb-backend
./deploy-separated.sh --registry harbor.company.com/maxkb backend

# 更新前端页面
docker stop maxkb-frontend
docker rm maxkb-frontend
./deploy-separated.sh --registry harbor.company.com/maxkb frontend
```

#### 2. 数据库迁移

```bash
# 执行数据库迁移
docker exec maxkb-backend python main.py upgrade_db
```

## 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器日志
docker logs maxkb-backend

# 检查环境变量
docker exec maxkb-backend env | grep MAXKB

# 检查网络连接
docker exec maxkb-backend ping maxkb-postgres
docker exec maxkb-backend ping maxkb-redis
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
docker exec maxkb-postgres pg_isready

# 测试数据库连接
docker exec maxkb-postgres psql -U maxkb -d maxkb -c "SELECT version();"

# 检查防火墙设置
sudo iptables -L
sudo ufw status
```

#### 3. Redis 连接失败

```bash
# 检查 Redis 状态
docker exec maxkb-redis redis-cli ping

# 测试密码认证
docker exec maxkb-redis redis-cli -a "your-redis-password" ping

# 检查 Redis 配置
docker exec maxkb-redis cat /etc/redis/redis.conf
```

#### 4. 文件上传失败

```bash
# 检查存储目录权限
ls -la /opt/maxkb-data/maxkb-local/

# 检查磁盘空间
df -h /opt/maxkb-data/

# 修复权限
sudo chown -R 1000:1000 /opt/maxkb-data/maxkb-local/
```

### 性能优化

#### 1. 数据库优化

```sql
-- 在 PostgreSQL 中执行
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

#### 2. Redis 优化

```bash
# 调整 Redis 配置
docker exec maxkb-redis redis-cli config set maxmemory 1gb
docker exec maxkb-redis redis-cli config set maxmemory-policy allkeys-lru
```

#### 3. 应用优化

```bash
# 调整工作进程数
docker run -d \
  --name maxkb-backend \
  -e CORE_WORKER=4 \
  harbor.company.com/maxkb/backend:v2.0
```

## 安全建议

### 1. 网络安全

- 使用防火墙限制端口访问
- 配置内部网络隔离
- 启用 HTTPS/SSL 加密

### 2. 认证安全

- 使用强密码
- 定期更换密码
- 启用双因素认证

### 3. 数据安全

- 定期备份数据
- 加密敏感数据
- 限制数据库访问权限

### 4. 容器安全

- 使用非 root 用户运行容器
- 定期更新镜像
- 扫描镜像漏洞

## 联系支持

如果在部署过程中遇到问题，请通过以下方式获取支持：

- **GitHub Issues**: https://github.com/1panel-dev/MaxKB/issues
- **官方文档**: https://maxkb.cn/
- **社区论坛**: https://bbs.fit2cloud.com/

---

*文档版本: v2.0*  
*更新时间: $(date '+%Y-%m-%d')*