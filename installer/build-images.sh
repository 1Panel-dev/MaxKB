#!/bin/bash

# MaxKB v2.0 镜像构建脚本
# 支持本地测试和私有仓库部署

set -e

# 快速开始信息
show_quick_start() {
    echo "==============================================="
    echo "  MaxKB v2.0 本地开发测试快速开始"
    echo "==============================================="
    echo ""
    echo "常用命令："
    echo "  $0 --local all                     # 构建所有镜像（本地测试）"
    echo "  $0 --local --china --optimized all # 中国网络优化构建（推荐）"
    echo "  $0 --local --test backend          # 构建后端并启动测试容器"
    echo "  $0 --status                        # 查看本地镜像和容器状态"
    echo "  $0 --clean                         # 清理所有本地镜像"
    echo ""
    echo "如需帮助，请运行: $0 --help"
    echo "==============================================="
}

# 默认配置
DEFAULT_REGISTRY="localhost"
DEFAULT_TAG="dev"
DEFAULT_PLATFORM="linux/amd64"
DEFAULT_LOCAL_MODE="false"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帮助信息
print_help() {
    echo "MaxKB v2.0 镜像构建脚本 - 支持本地测试和私有部署"
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
    echo "  --local             本地测试模式 (无需指定 registry)"
    echo "  --registry <url>    私有镜像仓库地址 (本地模式下可选)"
    echo "  --tag <tag>         镜像标签 (默认: dev)"
    echo "  --platform <arch>   目标平台 (默认: linux/amd64)"
    echo "  --push              构建后推送到仓库"
    echo "  --no-cache          不使用缓存构建"
    echo "  --optimized         使用优化版 Dockerfile（减少镜像大小）"
    echo "  --test              构建后启动容器进行测试"
    echo "  --clean             清理本地 MaxKB 相关镜像"
    echo "  --status            查看本地镜像和容器状态"
    echo "  --china             中国网络优化模式 (使用国内镜像源)"
    echo "  --help              显示此帮助信息"
    echo ""
    echo "本地测试示例:"
    echo "  $0 --local all                           # 本地构建所有镜像"
    echo "  $0 --local --china --optimized all       # 中国网络优化构建（推荐）"
    echo "  $0 --local --test backend                # 构建后端并启动测试容器"
    echo "  $0 --local --no-cache --optimized all    # 优化构建不使用缓存"
    echo "  $0 --clean                               # 清理本地镜像"
    echo ""
    echo "私有仓库示例:"
    echo "  $0 --registry harbor.company.com/maxkb --push all"
    echo "  $0 --registry myregistry.com --tag v2.0.1 backend frontend"
    echo "  $0 --registry localhost:5000 --no-cache models"
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
    
    # 执行构建
    if ! docker build $build_args \
        -f "$dockerfile" \
        -t "$image_name" \
        .; then
        handle_build_error "backend" $?
    fi
    
    if [ "$PUSH" = "true" ]; then
        log_info "推送镜像: $image_name"
        if ! docker push "$image_name"; then
            log_error "推送镜像失败"
            exit 1
        fi
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
    if [ -n "$REGISTRY" ] && [ "$REGISTRY" != "docker.io" ] && [ "$REGISTRY" != "localhost" ] && [ "$LOCAL_MODE" != "true" ]; then
        log_info "登录私有镜像仓库: $REGISTRY"
        echo "请输入仓库用户名和密码"
        docker login "$REGISTRY"
    fi
}

# 查看本地状态
show_local_status() {
    log_info "=== MaxKB 本地状态检查 ==="
    echo ""
    
    # 检查 MaxKB 相关镜像
    log_info "镜像列表:"
    local images=$(docker images --filter "reference=*/maxkb/*" --filter "reference=maxkb/*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null)
    if [ -n "$images" ]; then
        echo "$images"
    else
        echo "未找到 MaxKB 相关镜像"
    fi
    
    echo ""
    
    # 检查 MaxKB 相关容器
    log_info "容器列表:"
    local containers=$(docker ps -a --filter "name=maxkb" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null)
    if [ -n "$containers" ]; then
        echo "$containers"
    else
        echo "未找到 MaxKB 相关容器"
    fi
    
    echo ""
    
    # 检查正在运行的服务
    log_info "运行中的服务:"
    local running=$(docker ps --filter "name=maxkb" --format "{{.Names}}: {{.Status}}" 2>/dev/null)
    if [ -n "$running" ]; then
        echo "$running"
        
        echo ""
        log_info "服务访问地址:"
        if docker ps --filter "name=maxkb-backend" --format "{{.Names}}" | grep -q maxkb-backend; then
            echo "后端服务: http://localhost:8080"
        fi
        if docker ps --filter "name=maxkb-frontend" --format "{{.Names}}" | grep -q maxkb-frontend; then
            echo "前端服务: http://localhost"
        fi
        if docker ps --filter "name=maxkb-models" --format "{{.Names}}" | grep -q maxkb-models; then
            echo "模型服务: http://localhost:6333"
        fi
    else
        echo "没有正在运行的 MaxKB 服务"
        
        echo ""
        log_info "快速启动命令:"
        echo "$0 --local --test all    # 构建并启动所有服务"
    fi
    
    echo ""
}

# 网络故障排除
network_troubleshooting() {
    log_error "构建过程中遇到网络问题！"
    echo ""
    log_info "=== 网络故障排除建议 ==="
    echo ""
    
    log_info "1. 检查网络连接:"
    echo "   - 确保可以访问互联网"
    echo "   - 检查防火墙和代理设置"
    
    echo ""
    log_info "2. 使用中国网络优化模式:"
    echo "   $0 --local --china --optimized all"
    
    echo ""
    log_info "3. 手动配置 Docker 代理 (如果使用代理):"
    echo "   # 创建或编辑 Docker daemon 配置"
    echo "   sudo mkdir -p /etc/systemd/system/docker.service.d"
    echo "   sudo cat > /etc/systemd/system/docker.service.d/http-proxy.conf << EOF"
    echo "   [Service]"
    echo "   Environment=\"HTTP_PROXY=http://proxy.example.com:8080\""
    echo "   Environment=\"HTTPS_PROXY=http://proxy.example.com:8080\""
    echo "   EOF"
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl restart docker"
    
    echo ""
    log_info "4. 测试网络连接:"
    echo "   ping -c 4 mirrors.aliyun.com"
    echo "   curl -I https://mirrors.aliyun.com/pypi/simple/"
    
    echo ""
    log_info "5. Poetry 相关问题:"
    echo "   # 清理 Poetry 缓存"
    echo "   poetry cache clear pypi --all"
    echo "   poetry cache clear poetry --all"
    
    echo ""
    log_info "6. 如果问题持续，尝试:"
    echo "   - 使用 --no-cache 重新构建"
    echo "   - 检查 DNS 设置"
    echo "   - 降级到 Poetry 1.8.0 版本"
    echo "   - 联系网络管理员"
    
    echo ""
}

# Poetry 故障排除
poetry_troubleshooting() {
    log_error "构建过程中遇到 Poetry 问题！"
    echo ""
    log_info "=== Poetry 故障排除建议 ==="
    echo ""
    
    log_info "1. Poetry 版本兼容性问题:"
    echo "   当前使用: Poetry 2.0.0"
    echo "   如果遇到命令参数错误，可能需要调整语法"
    
    echo ""
    log_info "2. 源配置问题:"
    echo "   检查是否有重复的源配置"
    echo "   使用: poetry source show"
    
    echo ""
    log_info "3. 网络和缓存问题:"
    echo "   # 清理 Poetry 缓存"
    echo "   poetry cache clear pypi --all"
    echo "   poetry cache clear poetry --all"
    echo "   # 重新生成锁定文件"
    echo "   rm -f poetry.lock && poetry lock"
    
    echo ""
    log_info "4. 快速解决方案:"
    echo "   $0 --local --china --no-cache --optimized backend"
    
    echo ""
}

# 构建错误处理
handle_build_error() {
    local component="$1"
    local exit_code="$2"
    
    log_error "${component} 镜像构建失败 (退出码: $exit_code)"
    
    # 获取最后一个容器的日志
    local last_logs=$(docker logs $(docker ps -lq) 2>&1 || echo "无法获取容器日志")
    
    # 检查是否是特定类型的错误
    if echo "$last_logs" | grep -qi "poetry.*timeout\|poetry.*option.*does not exist\|poetry.*source.*already exists"; then
        poetry_troubleshooting
    elif echo "$last_logs" | grep -qi "timeout\|connection\|network\|ssl\|certificate"; then
        network_troubleshooting
    else
        echo ""
        log_info "=== 故障排除建议 ==="
        echo "1. 查看详细错误信息"
        echo "2. 检查 Dockerfile 语法"
        echo "3. 确保所有依赖文件存在"
        echo "4. 尝试使用 --no-cache 重新构建"
        echo ""
        log_info "最近的构建日志:"
        echo "$last_logs" | tail -10
    fi
    
    exit $exit_code
}

# 清理本地镜像
clean_images() {
    log_info "清理本地 MaxKB 相关镜像..."
    
    # 停止并删除 MaxKB 相关容器
    local containers=$(docker ps -a --filter "name=maxkb" --format "{{.Names}}" 2>/dev/null || true)
    if [ -n "$containers" ]; then
        log_info "停止并删除相关容器..."
        echo "$containers" | xargs docker rm -f 2>/dev/null || true
    fi
    
    # 删除 MaxKB 相关镜像
    local images=$(docker images --filter "reference=*/maxkb/*" --filter "reference=maxkb/*" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || true)
    if [ -n "$images" ]; then
        log_info "删除相关镜像..."
        echo "$images" | xargs docker rmi -f 2>/dev/null || true
    fi
    
    # 清理悬空镜像
    docker image prune -f 2>/dev/null || true
    
    log_info "清理完成！"
}

# 启动测试容器
start_test_container() {
    local component="$1"
    local image_name
    
    case $component in
        backend)
            image_name="$REGISTRY/maxkb/backend:$TAG"
            log_info "启动后端测试容器..."
            docker run -d --name maxkb-backend-test \
                -p 8080:8080 \
                -e DEBUG=true \
                -e DJANGO_SETTINGS_MODULE=maxkb.settings.dev \
                "$image_name"
            log_info "后端服务已启动: http://localhost:8080"
            ;;
        frontend)
            image_name="$REGISTRY/maxkb/frontend:$TAG"
            log_info "启动前端测试容器..."
            docker run -d --name maxkb-frontend-test \
                -p 80:80 \
                "$image_name"
            log_info "前端服务已启动: http://localhost"
            ;;
        models)
            image_name="$REGISTRY/maxkb/models:$TAG"
            log_info "启动模型服务测试容器..."
            docker run -d --name maxkb-models-test \
                -p 6333:6333 \
                "$image_name"
            log_info "模型服务已启动: http://localhost:6333"
            ;;
    esac
    
    # 等待容器启动
    sleep 3
    
    # 检查容器状态
    if docker ps --filter "name=maxkb-${component}-test" --format "{{.Names}}" | grep -q maxkb; then
        log_info "${component} 测试容器启动成功"
        echo "查看日志: docker logs maxkb-${component}-test"
        echo "停止容器: docker stop maxkb-${component}-test"
    else
        log_error "${component} 测试容器启动失败"
        docker logs "maxkb-${component}-test" 2>/dev/null || true
    fi
}

# 显示构建摘要
show_summary() {
    echo ""
    log_info "=== 构建摘要 ==="
    echo "运行模式: $([ "$LOCAL_MODE" = "true" ] && echo "本地测试" || echo "私有仓库")"
    echo "镜像前缀: $REGISTRY"
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
    
    # 本地模式的额外信息
    if [ "$LOCAL_MODE" = "true" ]; then
        echo ""
        log_info "=== 本地测试命令 ==="
        echo "查看镜像: docker images | grep maxkb"
        echo "清理镜像: $0 --clean"
        
        if [ "$TEST_MODE" = "true" ]; then
            echo ""
            log_info "=== 测试容器信息 ==="
            echo "查看容器: docker ps --filter 'name=maxkb'"
            echo "查看日志: docker logs <容器名>"
            echo "停止容器: docker stop <容器名>"
        else
            echo ""
            log_info "=== 启动测试容器 ==="
            for component in "${COMPONENTS[@]}"; do
                case $component in
                    backend)
                        echo "启动后端: docker run -d --name maxkb-backend-test -p 8080:8080 $REGISTRY/maxkb/backend:$TAG"
                        ;;
                    frontend)
                        echo "启动前端: docker run -d --name maxkb-frontend-test -p 80:80 $REGISTRY/maxkb/frontend:$TAG"
                        ;;
                    models)
                        echo "启动模型: docker run -d --name maxkb-models-test -p 6333:6333 $REGISTRY/maxkb/models:$TAG"
                        ;;
                    all)
                        echo "启动后端: docker run -d --name maxkb-backend-test -p 8080:8080 $REGISTRY/maxkb/backend:$TAG"
                        echo "启动前端: docker run -d --name maxkb-frontend-test -p 80:80 $REGISTRY/maxkb/frontend:$TAG"
                        echo "启动模型: docker run -d --name maxkb-models-test -p 6333:6333 $REGISTRY/maxkb/models:$TAG"
                        break
                        ;;
                esac
            done
        fi
    fi
    
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
    LOCAL_MODE="$DEFAULT_LOCAL_MODE"
    TEST_MODE="false"
    CLEAN_MODE="false"
    CHINA_MODE="false"
    
    # 如果没有参数，显示快速开始信息
    if [ $# -eq 0 ]; then
        show_quick_start
        exit 0
    fi
    
    # 解析命令行参数
    COMPONENTS=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --local)
                LOCAL_MODE="true"
                # 本地模式下设置默认仓库前缀
                if [ "$REGISTRY" = "$DEFAULT_REGISTRY" ]; then
                    REGISTRY="maxkb"
                fi
                shift
                ;;
            --registry)
                REGISTRY="$2"
                LOCAL_MODE="false"  # 明确指定仓库时关闭本地模式
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
            --test)
                TEST_MODE="true"
                shift
                ;;
            --clean)
                CLEAN_MODE="true"
                shift
                ;;
            --status)
                show_local_status
                exit 0
                ;;
            --china)
                CHINA_MODE="true"
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
    
    # 处理清理模式
    if [ "$CLEAN_MODE" = "true" ]; then
        clean_images
        exit 0
    fi
    
    # 检查必需参数
    if [ "$LOCAL_MODE" = "false" ] && [ -z "$REGISTRY" ]; then
        log_error "请指定私有镜像仓库地址 (--registry) 或使用本地模式 (--local)"
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
    
    # 本地模式提示信息
    if [ "$LOCAL_MODE" = "true" ]; then
        log_info "=== 本地测试模式 ==="
        log_info "镜像前缀: $REGISTRY"
        log_info "镜像标签: $TAG"
        
        # 检测是否在中国网络环境
        if [ "$CHINA_MODE" = "false" ]; then
            # 简单检测中国网络环境
            if ping -c 1 -W 2 mirrors.aliyun.com &>/dev/null; then
                log_warn "检测到可能的中国网络环境，建议使用 --china 参数优化构建速度"
                echo "   优化命令: $0 --local --china --optimized all"
            fi
        else
            log_info "中国网络优化: 已启用"
        fi
        
        if [ "$TEST_MODE" = "true" ]; then
            log_info "构建完成后将启动测试容器"
        fi
        echo ""
    fi
    
    # 登录仓库 (仅在推送且非本地模式时)
    if [ "$PUSH" = "true" ] && [ "$LOCAL_MODE" = "false" ]; then
        docker_login
    fi
    
    # 构建镜像
    for component in "${COMPONENTS[@]}"; do
        case $component in
            backend)
                build_backend
                if [ "$TEST_MODE" = "true" ]; then
                    start_test_container "backend"
                fi
                ;;
            frontend)
                build_frontend
                if [ "$TEST_MODE" = "true" ]; then
                    start_test_container "frontend"
                fi
                ;;
            models)
                build_models
                if [ "$TEST_MODE" = "true" ]; then
                    start_test_container "models"
                fi
                ;;
            all)
                build_backend
                build_frontend
                build_models
                if [ "$TEST_MODE" = "true" ]; then
                    log_info "启动所有测试容器..."
                    start_test_container "backend"
                    start_test_container "frontend"
                    start_test_container "models"
                fi
                ;;
        esac
    done
    
    # 仅在非本地模式时生成部署指南
    if [ "$LOCAL_MODE" = "false" ]; then
        create_deploy_guide
    fi
    
    # 显示摘要
    show_summary
}

# 执行主函数
main "$@"