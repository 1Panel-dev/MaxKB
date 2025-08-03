# MaxKB v2.0 分离部署工具

本目录包含 MaxKB v2.0 分离部署的所有必要文件和脚本。

## 📁 文件说明

| 文件名 | 说明 |
|--------|------|
| `deploy-separated.sh` | 🚀 主部署脚本，支持选择性部署 4 个组件 |
| `build-images.sh` | 🔨 镜像构建脚本，构建并推送到私有仓库 |
| `Dockerfile-backend` | 🐳 后台应用 Dockerfile |
| `Dockerfile-frontend` | 🐳 前端页面 Dockerfile |
| `Dockerfile-models` | 🐳 向量模型 Dockerfile |
| `docker-compose.yml` | 📋 Docker Compose 配置文件 |
| `env.example` | ⚙️ 环境变量配置模板 |
| `DEPLOYMENT_GUIDE.md` | 📖 详细部署指南 |

## 🚀 快速开始

### 1. 构建镜像

```bash
# 设置私有仓库地址
export REGISTRY="harbor.company.com/maxkb"

# 构建并推送所有镜像
./build-images.sh --registry $REGISTRY --push all
```

### 2. 部署应用

```bash
# 部署所有组件
./deploy-separated.sh --registry $REGISTRY all

# 或选择性部署
./deploy-separated.sh --registry $REGISTRY backend frontend
```

## 📋 组件说明

### 🔴 Redis 缓存服务
- **端口**: 6379
- **用途**: 会话存储、缓存
- **数据持久化**: `/opt/maxkb-data/redis`

### 🟢 PostgreSQL+pgvector 数据库
- **端口**: 5432
- **用途**: 主数据存储、向量检索
- **扩展**: pgvector, age
- **数据持久化**: `/opt/maxkb-data/postgres`

### 🔵 MaxKB 后台应用
- **端口**: 8080
- **用途**: 核心业务逻辑、API 服务
- **依赖**: PostgreSQL, Redis
- **数据持久化**: `/opt/maxkb-data/maxkb-{logs,local,models}`

### 🟡 前端页面
- **端口**: 80
- **用途**: 用户界面、管理后台
- **依赖**: 后台应用
- **特性**: Nginx 反向代理、静态资源服务

## 🔧 配置选项

### 基础配置
```bash
--registry <url>        # 私有镜像仓库地址
--network <name>        # Docker 网络名称
--data-dir <path>       # 数据持久化目录
```

### 数据库配置
```bash
--db-host <host>        # 数据库主机地址
--db-port <port>        # 数据库端口
--db-user <user>        # 数据库用户名
--db-password <pass>    # 数据库密码
```

### Redis 配置
```bash
--redis-host <host>     # Redis 主机地址
--redis-port <port>     # Redis 端口
--redis-password <pass> # Redis 密码
```

### 应用端口配置
```bash
--backend-port <port>   # 后台应用端口
--frontend-port <port>  # 前端页面端口
```

## 📊 部署场景

### 🏢 企业内网部署
```bash
# 完整部署到内网
./deploy-separated.sh \
  --registry harbor.internal.com/maxkb \
  --data-dir /data/maxkb \
  all
```

### ☁️ 云服务部署
```bash
# 使用云数据库
./deploy-separated.sh \
  --registry registry.cloud.com/maxkb \
  --db-host rds.cloud.com \
  --redis-host redis.cloud.com \
  backend frontend
```

### 🔧 开发测试环境
```bash
# 本地开发部署
docker-compose -f docker-compose.yml up -d
```

### 🎯 生产高可用部署
```bash
# 多实例部署
for i in {1..3}; do
  ./deploy-separated.sh \
    --registry prod.registry.com/maxkb \
    --backend-port $((8080+i)) \
    --db-host postgres-cluster.prod.com \
    --redis-host redis-cluster.prod.com \
    backend
done
```

## 🛠️ 维护命令

### 查看状态
```bash
docker ps --filter "name=maxkb"
```

### 查看日志
```bash
docker logs -f maxkb-backend
docker logs -f maxkb-frontend
```

### 重启服务
```bash
docker restart maxkb-backend
docker restart maxkb-frontend
```

### 更新镜像
```bash
# 拉取新镜像
docker pull $REGISTRY/maxkb/backend:v2.1

# 重新部署
./deploy-separated.sh --registry $REGISTRY backend
```

## 🔍 故障排除

### 连接问题
```bash
# 测试数据库连接
docker exec maxkb-backend ping maxkb-postgres

# 测试 Redis 连接
docker exec maxkb-backend ping maxkb-redis
```

### 权限问题
```bash
# 修复数据目录权限
sudo chown -R $USER:$USER /opt/maxkb-data
```

### 网络问题
```bash
# 检查 Docker 网络
docker network inspect maxkb-network

# 重新创建网络
docker network rm maxkb-network
docker network create maxkb-network
```

## 📈 性能优化

### 数据库优化
- 调整 PostgreSQL 配置参数
- 使用 SSD 存储
- 配置连接池

### Redis 优化
- 设置合适的内存限制
- 配置持久化策略
- 使用 Redis 集群

### 应用优化
- 调整工作进程数
- 配置负载均衡
- 启用 HTTP/2

## 🔒 安全建议

1. **网络隔离**: 使用私有网络，限制外部访问
2. **强密码**: 数据库和 Redis 使用复杂密码
3. **HTTPS**: 配置 SSL 证书，启用 HTTPS
4. **防火墙**: 配置防火墙规则，只开放必要端口
5. **更新**: 定期更新镜像和依赖
6. **备份**: 配置自动备份策略

## ❓ 获取帮助

```bash
# 查看部署脚本帮助
./deploy-separated.sh --help

# 查看构建脚本帮助
./build-images.sh --help
```

如需更详细的信息，请查看 `DEPLOYMENT_GUIDE.md`。

---

*MaxKB v2.0 - 让 AI 知识库部署更简单* 🚀