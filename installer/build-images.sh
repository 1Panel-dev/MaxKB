#!/bin/bash

# MaxKB v2.0 镜像构建脚本
# 用于构建并推送镜像到私有仓库

set -e

# 默认配置
DEFAULT_REGISTRY=""
DEFAULT_TAG="v2.0"
DEFAULT_PLATFORM="linux/amd64"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帮助信息
print_help() {
    echo "MaxKB v2.0 镜像构建脚本"
    echo ""
    echo "用法: $0 [选项] <组件>"
    echo ""
    echo "组件:"
    echo "  backend     构建后台应用镜像"
    echo "  frontend    构建前端页面镜像"
    echo "  models      构建向量模型镜像"
    echo "  all         构建所有镜像"
    echo ""
    echo "选项:"
    echo "  --registry <url>    私有镜像仓库地址 (必需)"
    echo "  --tag <tag>         镜像标签 (默认: v2.0)"
    echo "  --platform <arch>   目标平台 (默认: linux/amd64)"
    echo "  --push              构建后推送到仓库"
    echo "  --no-cache          不使用缓存构建"
    echo "  --optimized         使用优化版 Dockerfile（减少镜像大小）"
    echo "  --help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --registry harbor.company.com/maxkb --push all"
    echo "  $0 --registry myregistry.com --tag v2.0.1 backend frontend"
    echo "  $0 --registry localhost:5000 --no-cache models"
    echo "  $0 --registry myregistry.com --optimized --push backend  # 使用优化版构建后端"
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

# 检查必要文件
check_files() {
    local files=(
        "installer/Dockerfile-backend"
        "installer/Dockerfile-frontend" 
        "installer/Dockerfile-models"
        "ui/package.json"
        "pyproject.toml"
    )
    
    # 如果使用优化版，也检查优化版 Dockerfile
    if [ "$OPTIMIZED" = "true" ]; then
        files+=("installer/Dockerfile-backend-optimized")
    fi
    
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "缺少必要文件: $file"
            exit 1
        fi
    done
    
    log_info "文件检查通过"
}

# 构建后台镜像
build_backend() {
    local image_name="$REGISTRY/maxkb/backend:$TAG"
    log_info "构建后台应用镜像: $image_name"
    
    local build_args="--platform $PLATFORM"
    if [ "$NO_CACHE" = "true" ]; then
        build_args="$build_args --no-cache"
    fi
    
    # 选择 Dockerfile
    local dockerfile="installer/Dockerfile-backend"
    if [ "$OPTIMIZED" = "true" ]; then
        dockerfile="installer/Dockerfile-backend-optimized"
        log_info "使用优化版 Dockerfile，预计可减少 30-50% 镜像大小"
    fi
    
    docker build $build_args \
        -f "$dockerfile" \
        -t "$image_name" \
        .
    
    if [ "$PUSH" = "true" ]; then
        log_info "推送镜像: $image_name"
        docker push "$image_name"
    fi
    
    log_info "后台应用镜像构建完成"
}

# 构建前端镜像
build_frontend() {
    local image_name="$REGISTRY/maxkb/frontend:$TAG"
    log_info "构建前端页面镜像: $image_name"
    
    local build_args="--platform $PLATFORM"
    if [ "$NO_CACHE" = "true" ]; then
        build_args="$build_args --no-cache"
    fi
    
    docker build $build_args \
        -f installer/Dockerfile-frontend \
        -t "$image_name" \
        .
    
    if [ "$PUSH" = "true" ]; then
        log_info "推送镜像: $image_name"
        docker push "$image_name"
    fi
    
    log_info "前端页面镜像构建完成"
}

# 构建向量模型镜像
build_models() {
    local image_name="$REGISTRY/maxkb/models:$TAG"
    log_info "构建向量模型镜像: $image_name"
    
    local build_args="--platform $PLATFORM"
    if [ "$NO_CACHE" = "true" ]; then
        build_args="$build_args --no-cache"
    fi
    
    docker build $build_args \
        -f installer/Dockerfile-models \
        -t "$image_name" \
        .
    
    if [ "$PUSH" = "true" ]; then
        log_info "推送镜像: $image_name"
        docker push "$image_name"
    fi
    
    log_info "向量模型镜像构建完成"
}

# 登录私有仓库
docker_login() {
    if [ -n "$REGISTRY" ] && [ "$REGISTRY" != "docker.io" ]; then
        log_info "登录私有镜像仓库: $REGISTRY"
        echo "请输入仓库用户名和密码"
        docker login "$REGISTRY"
    fi
}

# 显示构建摘要
show_summary() {
    echo ""
    log_info "=== 构建摘要 ==="
    echo "仓库地址: $REGISTRY"
    echo "镜像标签: $TAG"
    echo "目标平台: $PLATFORM"
    echo "推送状态: $([ "$PUSH" = "true" ] && echo "已推送" || echo "仅本地构建")"
    
    echo ""
    log_info "=== 镜像列表 ==="
    
    for component in "${COMPONENTS[@]}"; do
        case $component in
            backend)
                echo "后台应用: $REGISTRY/maxkb/backend:$TAG"
                ;;
            frontend)
                echo "前端页面: $REGISTRY/maxkb/frontend:$TAG"
                ;;
            models)
                echo "向量模型: $REGISTRY/maxkb/models:$TAG"
                ;;
            all)
                echo "后台应用: $REGISTRY/maxkb/backend:$TAG"
                echo "前端页面: $REGISTRY/maxkb/frontend:$TAG"
                echo "向量模型: $REGISTRY/maxkb/models:$TAG"
                break
                ;;
        esac
    done
    
    echo ""
    log_info "构建完成！"
}

# 创建部署文档
create_deploy_guide() {
    cat > "maxkb-deploy-guide.md" << EOF
# MaxKB v2.0 私有部署指南

## 镜像信息

- 仓库地址: \`$REGISTRY\`
- 镜像标签: \`$TAG\`
- 构建时间: \`$(date '+%Y-%m-%d %H:%M:%S')\`
- 目标平台: \`$PLATFORM\`

## 镜像列表

\`\`\`
$REGISTRY/maxkb/backend:$TAG     # 后台应用
$REGISTRY/maxkb/frontend:$TAG    # 前端页面
$REGISTRY/maxkb/models:$TAG      # 向量模型
\`\`\`

## 快速部署

### 1. 下载部署脚本

\`\`\`bash
curl -O https://raw.githubusercontent.com/1panel-dev/MaxKB/v2.0/installer/deploy-separated.sh
chmod +x deploy-separated.sh
\`\`\`

### 2. 部署所有组件

\`\`\`bash
./deploy-separated.sh --registry $REGISTRY all
\`\`\`

### 3. 选择性部署

\`\`\`bash
# 仅部署数据库和缓存
./deploy-separated.sh redis postgres

# 仅部署应用
./deploy-separated.sh --registry $REGISTRY backend frontend
\`\`\`

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MAXKB_DB_HOST | 数据库主机 | maxkb-postgres |
| MAXKB_DB_PORT | 数据库端口 | 5432 |
| MAXKB_DB_USER | 数据库用户 | maxkb |
| MAXKB_DB_PASSWORD | 数据库密码 | 自动生成 |
| MAXKB_REDIS_HOST | Redis 主机 | maxkb-redis |
| MAXKB_REDIS_PORT | Redis 端口 | 6379 |
| MAXKB_REDIS_PASSWORD | Redis 密码 | 自动生成 |

### 数据持久化

默认数据目录: \`/opt/maxkb-data\`

\`\`\`
/opt/maxkb-data/
├── redis/              # Redis 数据
├── postgres/           # PostgreSQL 数据
├── maxkb-logs/         # 应用日志
├── maxkb-local/        # 本地文件存储
└── maxkb-models/       # 向量模型文件
\`\`\`

## 访问地址

- 前端页面: http://localhost
- 管理后台: http://localhost/admin
- API 文档: http://localhost:8080/api/docs

## 故障排除

### 查看容器状态

\`\`\`bash
docker ps --filter "name=maxkb"
\`\`\`

### 查看日志

\`\`\`bash
docker logs maxkb-backend
docker logs maxkb-frontend
\`\`\`

### 重启服务

\`\`\`bash
docker restart maxkb-backend
docker restart maxkb-frontend
\`\`\`

## 更新升级

### 1. 拉取新镜像

\`\`\`bash
docker pull $REGISTRY/maxkb/backend:$TAG
docker pull $REGISTRY/maxkb/frontend:$TAG
\`\`\`

### 2. 重新部署

\`\`\`bash
./deploy-separated.sh --registry $REGISTRY backend frontend
\`\`\`

---

*生成时间: $(date '+%Y-%m-%d %H:%M:%S')*
EOF
    
    log_info "部署指南已生成: maxkb-deploy-guide.md"
}

# 主函数
main() {
    # 默认值
    REGISTRY="$DEFAULT_REGISTRY"
    TAG="$DEFAULT_TAG"
    PLATFORM="$DEFAULT_PLATFORM"
    PUSH="false"
    NO_CACHE="false"
    OPTIMIZED="false"
    
    # 解析命令行参数
    COMPONENTS=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --tag)
                TAG="$2"
                shift 2
                ;;
            --platform)
                PLATFORM="$2"
                shift 2
                ;;
            --push)
                PUSH="true"
                shift
                ;;
            --no-cache)
                NO_CACHE="true"
                shift
                ;;
            --optimized)
                OPTIMIZED="true"
                shift
                ;;
            --help)
                print_help
                exit 0
                ;;
            backend|frontend|models|all)
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
    
    # 检查必需参数
    if [ -z "$REGISTRY" ]; then
        log_error "请指定私有镜像仓库地址 (--registry)"
        print_help
        exit 1
    fi
    
    if [ ${#COMPONENTS[@]} -eq 0 ]; then
        log_error "请指定要构建的组件"
        print_help
        exit 1
    fi
    
    # 检查环境和文件
    check_docker
    check_files
    
    # 登录仓库
    if [ "$PUSH" = "true" ]; then
        docker_login
    fi
    
    # 构建镜像
    for component in "${COMPONENTS[@]}"; do
        case $component in
            backend)
                build_backend
                ;;
            frontend)
                build_frontend
                ;;
            models)
                build_models
                ;;
            all)
                build_backend
                build_frontend
                build_models
                ;;
        esac
    done
    
    # 生成部署指南
    create_deploy_guide
    
    # 显示摘要
    show_summary
}

# 执行主函数
main "$@"