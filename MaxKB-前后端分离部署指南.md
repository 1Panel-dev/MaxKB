# MaxKB v2.0 前后端分离部署指南

## 概述

本指南详细说明如何将MaxKB项目部署为前后端分离架构：
- **前端**: 部署在Nginx上，提供静态文件服务
- **后端**: 运行在Docker容器中，提供API服务和部分静态资源

## 部署架构

```
┌─────────────────────────────────────┐
│              Nginx                  │
│         (前端 + 反向代理)            │
│              :80                    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│           Docker 后端               │
│      (API + 后端静态资源)           │
│             :8080                   │
└─────────────────────────────────────┘
```

### 资源分布策略

| 资源类型 | 位置 | 访问路径 | 说明 |
|---------|------|----------|------|
| 前端页面 | Nginx | `/`, `/admin/*` | 前端应用主体 |
| 主题图片 | 后端 | `/static/theme/*` | 系统主题背景 |
| 工具图标 | 后端 | `/static/tool/*` | 系统内置图标 |
| API文档 | 后端 | `/doc/*`, `/schema/*` | Swagger UI |
| 业务API | 后端 | `/admin/api/*`, `/chat/api/*` | RESTful API |
| 文件服务 | 后端 | `/oss/*` | 用户上传文件 |

## 部署步骤

### 第一步：构建后端Docker镜像

```bash
# 克隆项目（如果还没有）
git clone https://github.com/1Panel-dev/MaxKB.git
cd MaxKB
git checkout v2.0

# 构建后端镜像
./installer/build-images.sh --registry your-registry.com/maxkb --tag v2.0 backend

# 推送到仓库（可选）
./installer/build-images.sh --registry your-registry.com/maxkb --tag v2.0 --push backend
```

### 第二步：配置前端构建环境

#### 2.1 创建生产环境配置

```bash
# 创建生产环境配置文件
cat > ui/env/.env.production << EOF
VITE_APP_NAME=admin
VITE_BASE_PATH=/
VITE_APP_PORT=80
VITE_APP_TITLE=MaxKB
VITE_ENTRY="admin.html"
EOF
```

#### 2.2 构建前端

```bash
cd ui
# 安装依赖（如果还没有）
npm install --legacy-peer-deps

# 构建生产版本
npm run build

# 验证构建结果
ls -la dist/admin/
```

### 第三步：配置Nginx

#### 3.1 创建Nginx配置文件

```bash
sudo nano /etc/nginx/sites-available/maxkb
```

#### 3.2 Nginx配置内容

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名
    
    # 安全设置
    server_tokens off;
    client_max_body_size 100M;
    
    # ===== 前端静态文件 =====
    location / {
        root /var/www/maxkb;
        try_files $uri $uri/ /index.html;
        index index.html;
        
        # 前端静态文件缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # ===== API代理到后端 =====
    location /admin/api/ {
        proxy_pass http://your-backend-host:8080;  # 替换为后端地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /chat/api/ {
        proxy_pass http://your-backend-host:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # ===== 文档和Schema =====
    location /doc/ {
        proxy_pass http://your-backend-host:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /schema/ {
        proxy_pass http://your-backend-host:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # ===== 后端静态资源 =====
    location /static/ {
        proxy_pass http://your-backend-host:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # ===== 文件服务 =====
    location /oss/ {
        proxy_pass http://your-backend-host:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 100M;
    }
    
    # ===== WebSocket支持（如果需要）=====
    location /ws/ {
        proxy_pass http://your-backend-host:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # ===== 性能优化 =====
    # 开启gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

#### 3.3 启用Nginx配置

```bash
# 测试配置文件语法
sudo nginx -t

# 启用配置
sudo ln -s /etc/nginx/sites-available/maxkb /etc/nginx/sites-enabled/

# 重载配置
sudo systemctl reload nginx
```

### 第四步：部署前端文件

```bash
# 创建前端文件目录
sudo mkdir -p /var/www/maxkb

# 复制构建文件
sudo cp -r ui/dist/admin/* /var/www/maxkb/

# 设置权限
sudo chown -R www-data:www-data /var/www/maxkb
sudo chmod -R 755 /var/www/maxkb

# 验证文件
ls -la /var/www/maxkb
```

### 第五步：启动后端服务

#### 5.1 准备数据库和Redis

```bash
# 启动PostgreSQL（使用项目提供的脚本或自行安装）
# 启动Redis

# 或者使用Docker Compose启动基础服务
docker-compose -f installer/docker-compose.yml up -d maxkb-postgres maxkb-redis
```

#### 5.2 启动后端容器

```bash
# 创建数据目录
sudo mkdir -p /opt/maxkb/{logs,local}
sudo chown -R 1000:1000 /opt/maxkb

# 运行后端容器
docker run -d \
  --name maxkb-backend \
  --restart unless-stopped \
  -p 8080:8080 \
  -e MAXKB_CONFIG_TYPE=ENV \
  -e MAXKB_DB_HOST=your-db-host \
  -e MAXKB_DB_PORT=5432 \
  -e MAXKB_DB_USER=maxkb \
  -e MAXKB_DB_PASSWORD=your-db-password \
  -e MAXKB_DB_NAME=maxkb \
  -e MAXKB_REDIS_HOST=your-redis-host \
  -e MAXKB_REDIS_PORT=6379 \
  -e MAXKB_REDIS_PASSWORD=your-redis-password \
  -e MAXKB_REDIS_DB=0 \
  -e MAXKB_LOG_LEVEL=INFO \
  -v /opt/maxkb/logs:/opt/maxkb/logs \
  -v /opt/maxkb/local:/opt/maxkb/local \
  your-registry.com/maxkb/backend:v2.0
```

### 第六步：健康检查

```bash
# 检查前端
curl -I http://your-domain.com/

# 检查后端API
curl -I http://your-domain.com/admin/api/

# 检查静态资源
curl -I http://your-domain.com/static/theme/default.jpg

# 检查API文档
curl -I http://your-domain.com/doc/

# 查看容器状态
docker ps --filter "name=maxkb"

# 查看容器日志
docker logs maxkb-backend
```

## 自动化部署脚本

### 完整部署脚本

创建 `deploy-separated.sh`:

```bash
#!/bin/bash
# MaxKB前后端分离部署脚本

set -e

# 配置变量
REGISTRY="your-registry.com/maxkb"
TAG="v2.0"
DOMAIN="your-domain.com"
BACKEND_HOST="127.0.0.1"
DB_HOST="127.0.0.1"
DB_PASSWORD="your-secure-password"
REDIS_HOST="127.0.0.1"
REDIS_PASSWORD="your-secure-password"

echo "=== MaxKB前后端分离部署 ==="

# 1. 构建后端镜像
echo "1. 构建后端镜像..."
./installer/build-images.sh --registry $REGISTRY --tag $TAG backend

# 2. 构建前端
echo "2. 构建前端..."
cd ui
npm run build
cd ..

# 3. 部署前端到Nginx
echo "3. 部署前端..."
sudo cp -r ui/dist/admin/* /var/www/maxkb/
sudo chown -R www-data:www-data /var/www/maxkb

# 4. 更新后端容器
echo "4. 更新后端容器..."
docker stop maxkb-backend 2>/dev/null || true
docker rm maxkb-backend 2>/dev/null || true

docker run -d \
  --name maxkb-backend \
  --restart unless-stopped \
  -p 8080:8080 \
  -e MAXKB_CONFIG_TYPE=ENV \
  -e MAXKB_DB_HOST=$DB_HOST \
  -e MAXKB_DB_PASSWORD=$DB_PASSWORD \
  -e MAXKB_REDIS_HOST=$REDIS_HOST \
  -e MAXKB_REDIS_PASSWORD=$REDIS_PASSWORD \
  -v /opt/maxkb/logs:/opt/maxkb/logs \
  -v /opt/maxkb/local:/opt/maxkb/local \
  $REGISTRY/backend:$TAG

# 5. 重载Nginx
echo "5. 重载Nginx..."
sudo nginx -t && sudo systemctl reload nginx

# 6. 健康检查
echo "6. 健康检查..."
sleep 10

if curl -f -s http://localhost/ > /dev/null; then
    echo "✅ 前端部署成功"
else
    echo "❌ 前端部署失败"
fi

if curl -f -s http://localhost/admin/api/ > /dev/null; then
    echo "✅ 后端API正常"
else
    echo "❌ 后端API异常"
fi

echo "=== 部署完成 ==="
echo "前端地址: http://$DOMAIN/"
echo "管理后台: http://$DOMAIN/admin/"
echo "API文档: http://$DOMAIN/doc/"
```

### 使用方法

```bash
# 赋予执行权限
chmod +x deploy-separated.sh

# 执行部署
./deploy-separated.sh
```

## 故障排除

### 常见问题

#### 1. 前端页面空白
```bash
# 检查前端文件是否正确部署
ls -la /var/www/maxkb/
# 检查nginx配置
sudo nginx -t
# 查看nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

#### 2. API请求失败
```bash
# 检查后端容器状态
docker ps --filter "name=maxkb-backend"
# 查看后端日志
docker logs maxkb-backend
# 检查代理配置
curl -v http://localhost/admin/api/
```

#### 3. 静态资源404
```bash
# 检查后端静态文件收集
docker exec maxkb-backend ls -la /opt/maxkb/apps/static/
# 检查nginx代理配置
curl -I http://localhost/static/theme/default.jpg
```

#### 4. 数据库连接失败
```bash
# 检查数据库服务
docker logs maxkb-postgres
# 检查环境变量
docker exec maxkb-backend env | grep MAXKB_DB
```

### 日志查看

```bash
# Nginx访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 后端应用日志
docker logs -f maxkb-backend

# 系统日志
sudo journalctl -u nginx -f
```

## 维护升级

### 更新前端

```bash
# 1. 重新构建前端
cd ui && npm run build && cd ..

# 2. 更新前端文件
sudo cp -r ui/dist/admin/* /var/www/maxkb/

# 3. 清理浏览器缓存（可选）
```

### 更新后端

```bash
# 1. 构建新镜像
./installer/build-images.sh --registry $REGISTRY --tag $NEW_TAG backend

# 2. 停止旧容器
docker stop maxkb-backend

# 3. 启动新容器
docker run -d --name maxkb-backend-new $REGISTRY/backend:$NEW_TAG

# 4. 测试无误后移除旧容器
docker rm maxkb-backend
docker rename maxkb-backend-new maxkb-backend
```

### 备份恢复

```bash
# 备份前端文件
sudo tar -czf maxkb-frontend-$(date +%Y%m%d).tar.gz -C /var/www maxkb

# 备份数据库
docker exec maxkb-postgres pg_dump -U maxkb maxkb > maxkb-db-$(date +%Y%m%d).sql

# 备份用户文件
sudo tar -czf maxkb-data-$(date +%Y%m%d).tar.gz /opt/maxkb/local
```

## 性能优化建议

### 1. CDN加速
- 将前端静态资源部署到CDN
- 配置合适的缓存策略

### 2. 负载均衡
- 使用多个后端实例
- 配置Nginx upstream

### 3. 数据库优化
- 配置连接池
- 定期维护和优化查询

### 4. 缓存策略
- Redis集群
- 应用层缓存

## 安全建议

### 1. HTTPS配置
```nginx
# SSL证书配置
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... 其他配置
}
```

### 2. 防火墙设置
```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8080/tcp  # 不直接暴露后端端口
```

### 3. 访问控制
```nginx
# IP白名单（可选）
location /admin/ {
    allow 192.168.1.0/24;
    deny all;
    # ... 其他配置
}
```

---

*文档版本: v2.0*  
*更新时间: 2025-08-05*  
*适用于: MaxKB v2.0*