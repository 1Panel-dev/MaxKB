#!/bin/bash

# MaxKB v2.0 分离部署脚本
# 支持选择性部署：Redis、PostgreSQL+pgvector、MaxKB后台、前端页面

set -e

# 默认配置
DEFAULT_REGISTRY=""
DEFAULT_NETWORK="maxkb-network"
DEFAULT_DATA_DIR="/opt/maxkb-data"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帮助信息
print_help() {
    echo "MaxKB v2.0 分离部署脚本"
    echo ""
    echo "用法: $0 [选项] <组件>"
    echo ""
    echo "组件:"
    echo "  redis       部署 Redis 缓存服务"
    echo "  postgres    部署 PostgreSQL+pgvector 数据库"
    echo "  backend     部署 MaxKB 后台应用"
    echo "  frontend    部署前端页面"
    echo "  all         部署所有组件"
    echo ""
    echo "选项:"
    echo "  --registry <url>        私有镜像仓库地址 (默认: Docker Hub)"
    echo "  --network <name>        Docker 网络名称 (默认: maxkb-network)"
    echo "  --data-dir <path>       数据持久化目录 (默认: /opt/maxkb-data)"
    echo "  --db-host <host>        数据库主机地址 (默认: maxkb-postgres)"
    echo "  --db-port <port>        数据库端口 (默认: 5432)"
    echo "  --db-user <user>        数据库用户名 (默认: maxkb)"
    echo "  --db-password <pass>    数据库密码 (默认: 随机生成)"
    echo "  --redis-host <host>     Redis 主机地址 (默认: maxkb-redis)"
    echo "  --redis-port <port>     Redis 端口 (默认: 6379)"
    echo "  --redis-password <pass> Redis 密码 (默认: 随机生成)"
    echo "  --backend-port <port>   后台应用端口 (默认: 8080)"
    echo "  --frontend-port <port>  前端页面端口 (默认: 80)"
    echo "  --help                  显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --registry harbor.company.com redis postgres"
    echo "  $0 --data-dir /data/maxkb backend"
    echo "  $0 all"
}

# 生成随机密码
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-16
}

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查 Docker 环境
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker 服务未启动，请启动 Docker 服务"
        exit 1
    fi
    
    log_info "Docker 环境检查通过"
}

# 创建 Docker 网络
create_network() {
    if ! docker network inspect "$NETWORK" &> /dev/null; then
        log_info "创建 Docker 网络: $NETWORK"
        docker network create "$NETWORK"
    else
        log_info "Docker 网络 $NETWORK 已存在"
    fi
}

# 创建数据目录
create_data_dirs() {
    log_info "创建数据持久化目录"
    mkdir -p "$DATA_DIR"/{redis,postgres,maxkb-logs,maxkb-local,maxkb-models}
    chmod 755 "$DATA_DIR"
    log_info "数据目录创建完成: $DATA_DIR"
}

# 部署 Redis
deploy_redis() {
    log_info "部署 Redis 服务..."
    
    local image="redis:7-alpine"
    if [ -n "$REGISTRY" ]; then
        image="$REGISTRY/redis:7-alpine"
    fi
    
    # 停止并删除现有容器
    docker stop maxkb-redis 2>/dev/null || true
    docker rm maxkb-redis 2>/dev/null || true
    
    # 启动 Redis 容器
    docker run -d \
        --name maxkb-redis \
        --network "$NETWORK" \
        -p "$REDIS_PORT:6379" \
        -v "$DATA_DIR/redis:/data" \
        -e REDIS_PASSWORD="$REDIS_PASSWORD" \
        --restart unless-stopped \
        "$image" \
        redis-server --requirepass "$REDIS_PASSWORD" --appendonly yes
    
    log_info "Redis 部署完成"
    log_info "  - 容器名称: maxkb-redis"
    log_info "  - 端口映射: $REDIS_PORT:6379"
    log_info "  - 密码: $REDIS_PASSWORD"
    log_info "  - 数据目录: $DATA_DIR/redis"
}

# 部署 PostgreSQL
deploy_postgres() {
    log_info "部署 PostgreSQL+pgvector 服务..."
    
    local image="pgvector/pgvector:pg17"
    if [ -n "$REGISTRY" ]; then
        image="$REGISTRY/pgvector/pgvector:pg17"
    fi
    
    # 停止并删除现有容器
    docker stop maxkb-postgres 2>/dev/null || true
    docker rm maxkb-postgres 2>/dev/null || true
    
    # 创建初始化脚本
    cat > "$DATA_DIR/postgres/init.sql" << EOF
CREATE DATABASE maxkb;
\c maxkb;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
EOF
    
    # 启动 PostgreSQL 容器
    docker run -d \
        --name maxkb-postgres \
        --network "$NETWORK" \
        -p "$DB_PORT:5432" \
        -v "$DATA_DIR/postgres:/var/lib/postgresql/data" \
        -v "$DATA_DIR/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql" \
        -e POSTGRES_DB=postgres \
        -e POSTGRES_USER="$DB_USER" \
        -e POSTGRES_PASSWORD="$DB_PASSWORD" \
        -e POSTGRES_MAX_CONNECTIONS=1000 \
        --restart unless-stopped \
        "$image"
    
    log_info "PostgreSQL 部署完成"
    log_info "  - 容器名称: maxkb-postgres"
    log_info "  - 端口映射: $DB_PORT:5432"
    log_info "  - 用户名: $DB_USER"
    log_info "  - 密码: $DB_PASSWORD"
    log_info "  - 数据库: maxkb"
    log_info "  - 数据目录: $DATA_DIR/postgres"
}

# 部署后台应用
deploy_backend() {
    log_info "部署 MaxKB 后台应用..."
    
    local image="maxkb/backend:v2.0"
    if [ -n "$REGISTRY" ]; then
        image="$REGISTRY/maxkb/backend:v2.0"
    fi
    
    # 停止并删除现有容器
    docker stop maxkb-backend 2>/dev/null || true
    docker rm maxkb-backend 2>/dev/null || true
    
    # 启动后台应用容器
    docker run -d \
        --name maxkb-backend \
        --network "$NETWORK" \
        -p "$BACKEND_PORT:8080" \
        -v "$DATA_DIR/maxkb-logs:/opt/maxkb/logs" \
        -v "$DATA_DIR/maxkb-local:/opt/maxkb/local" \
        -v "$DATA_DIR/maxkb-models:/opt/maxkb-app/model" \
        -e MAXKB_CONFIG_TYPE=ENV \
        -e MAXKB_DB_NAME=maxkb \
        -e MAXKB_DB_HOST="$DB_HOST" \
        -e MAXKB_DB_PORT="$DB_PORT" \
        -e MAXKB_DB_USER="$DB_USER" \
        -e MAXKB_DB_PASSWORD="$DB_PASSWORD" \
        -e MAXKB_REDIS_HOST="$REDIS_HOST" \
        -e MAXKB_REDIS_PORT="$REDIS_PORT" \
        -e MAXKB_REDIS_PASSWORD="$REDIS_PASSWORD" \
        -e MAXKB_REDIS_DB=0 \
        -e MAXKB_LOG_LEVEL=INFO \
        --restart unless-stopped \
        "$image"
    
    log_info "MaxKB 后台应用部署完成"
    log_info "  - 容器名称: maxkb-backend"
    log_info "  - 端口映射: $BACKEND_PORT:8080"
    log_info "  - 数据库连接: $DB_HOST:$DB_PORT"
    log_info "  - Redis 连接: $REDIS_HOST:$REDIS_PORT"
}

# 部署前端页面
deploy_frontend() {
    log_info "部署前端页面..."
    
    local image="maxkb/frontend:v2.0"
    if [ -n "$REGISTRY" ]; then
        image="$REGISTRY/maxkb/frontend:v2.0"
    fi
    
    # 停止并删除现有容器
    docker stop maxkb-frontend 2>/dev/null || true
    docker rm maxkb-frontend 2>/dev/null || true
    
    # 创建 Nginx 配置
    mkdir -p "$DATA_DIR/nginx"
    cat > "$DATA_DIR/nginx/nginx.conf" << EOF
server {
    listen 80;
    server_name localhost;
    
    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    # API 代理到后台
    location /api/ {
        proxy_pass http://maxkb-backend:8080/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 管理后台代理
    location /admin/ {
        proxy_pass http://maxkb-backend:8080/admin/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 聊天接口代理
    location /chat/ {
        proxy_pass http://maxkb-backend:8080/chat/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
    
    # 启动前端容器
    docker run -d \
        --name maxkb-frontend \
        --network "$NETWORK" \
        -p "$FRONTEND_PORT:80" \
        -v "$DATA_DIR/nginx/nginx.conf:/etc/nginx/conf.d/default.conf" \
        --restart unless-stopped \
        "$image"
    
    log_info "前端页面部署完成"
    log_info "  - 容器名称: maxkb-frontend"
    log_info "  - 端口映射: $FRONTEND_PORT:80"
    log_info "  - 后台代理: maxkb-backend:8080"
}

# 等待服务就绪
wait_for_service() {
    local service=$1
    local host=$2
    local port=$3
    local timeout=${4:-60}
    
    log_info "等待 $service 服务就绪..."
    
    for i in $(seq 1 $timeout); do
        if docker run --rm --network "$NETWORK" alpine/curl -s "http://$host:$port" &>/dev/null; then
            log_info "$service 服务已就绪"
            return 0
        fi
        sleep 1
    done
    
    log_error "$service 服务启动超时"
    return 1
}

# 显示部署状态
show_status() {
    echo ""
    log_info "=== MaxKB 部署状态 ==="
    
    containers=("maxkb-redis" "maxkb-postgres" "maxkb-backend" "maxkb-frontend")
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container"; then
            status=$(docker ps --format "{{.Status}}" --filter "name=$container")
            echo -e "${GREEN}✓${NC} $container: $status"
        else
            echo -e "${RED}✗${NC} $container: 未运行"
        fi
    done
    
    echo ""
    log_info "=== 访问地址 ==="
    echo "前端页面: http://localhost:$FRONTEND_PORT"
    echo "管理后台: http://localhost:$FRONTEND_PORT/admin"
    echo "API 文档: http://localhost:$BACKEND_PORT/api/docs"
    
    echo ""
    log_info "=== 连接信息 ==="
    echo "数据库: $DB_HOST:$DB_PORT (用户: $DB_USER)"
    echo "Redis: $REDIS_HOST:$REDIS_PORT"
    echo "数据目录: $DATA_DIR"
}

# 保存配置信息
save_config() {
    cat > "$DATA_DIR/maxkb-config.env" << EOF
# MaxKB 部署配置
REGISTRY=$REGISTRY
NETWORK=$NETWORK
DATA_DIR=$DATA_DIR

# 数据库配置
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Redis 配置
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT
REDIS_PASSWORD=$REDIS_PASSWORD

# 应用端口配置
BACKEND_PORT=$BACKEND_PORT
FRONTEND_PORT=$FRONTEND_PORT

# 部署时间
DEPLOY_TIME=$(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    log_info "配置信息已保存到: $DATA_DIR/maxkb-config.env"
}

# 主函数
main() {
    # 默认值
    REGISTRY="$DEFAULT_REGISTRY"
    NETWORK="$DEFAULT_NETWORK"
    DATA_DIR="$DEFAULT_DATA_DIR"
    
    # 数据库配置
    DB_HOST="maxkb-postgres"
    DB_PORT="5432"
    DB_USER="maxkb"
    DB_PASSWORD=$(generate_password)
    
    # Redis 配置
    REDIS_HOST="maxkb-redis"
    REDIS_PORT="6379"
    REDIS_PASSWORD=$(generate_password)
    
    # 应用端口
    BACKEND_PORT="8080"
    FRONTEND_PORT="80"
    
    # 解析命令行参数
    COMPONENTS=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --network)
                NETWORK="$2"
                shift 2
                ;;
            --data-dir)
                DATA_DIR="$2"
                shift 2
                ;;
            --db-host)
                DB_HOST="$2"
                shift 2
                ;;
            --db-port)
                DB_PORT="$2"
                shift 2
                ;;
            --db-user)
                DB_USER="$2"
                shift 2
                ;;
            --db-password)
                DB_PASSWORD="$2"
                shift 2
                ;;
            --redis-host)
                REDIS_HOST="$2"
                shift 2
                ;;
            --redis-port)
                REDIS_PORT="$2"
                shift 2
                ;;
            --redis-password)
                REDIS_PASSWORD="$2"
                shift 2
                ;;
            --backend-port)
                BACKEND_PORT="$2"
                shift 2
                ;;
            --frontend-port)
                FRONTEND_PORT="$2"
                shift 2
                ;;
            --help)
                print_help
                exit 0
                ;;
            redis|postgres|backend|frontend|all)
                COMPONENTS+=("$1")
                shift
                ;;
            *)
                log_error "未知参数: $1"
                print_help
                exit 1
                ;;
        esac
    done
    
    # 检查是否指定了组件
    if [ ${#COMPONENTS[@]} -eq 0 ]; then
        log_error "请指定要部署的组件"
        print_help
        exit 1
    fi
    
    # 检查环境
    check_docker
    
    # 创建网络和目录
    create_network
    create_data_dirs
    
    # 部署组件
    for component in "${COMPONENTS[@]}"; do
        case $component in
            redis)
                deploy_redis
                ;;
            postgres)
                deploy_postgres
                ;;
            backend)
                deploy_backend
                ;;
            frontend)
                deploy_frontend
                ;;
            all)
                deploy_redis
                deploy_postgres
                sleep 10  # 等待数据库启动
                deploy_backend
                sleep 5   # 等待后台启动
                deploy_frontend
                ;;
        esac
    done
    
    # 保存配置
    save_config
    
    # 显示状态
    show_status
    
    log_info "MaxKB 分离部署完成！"
}

# 执行主函数
main "$@"