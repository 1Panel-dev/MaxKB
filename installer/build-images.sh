#!/bin/bash

# MaxKB v2.0 后端镜像构建脚本
# 支持本地构建和私有仓库推送

# 本地构建
#./build-images.sh local

# 构建并推送到私有仓库
#./build-images.sh push

# 指定标签推送
#./build-images.sh push --tag v2.0.1

# 不使用缓存本地构建
#./build-images.sh local --no-cache

# 查看帮助
#./build-images.sh --help

set -e

# 默认配置
DEFAULT_REGISTRY="docker.zhouke.tech/gs_kh"
DEFAULT_TAG="dev"
DEFAULT_PLATFORM="linux/amd64"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帮助信息
print_help() {
    echo "MaxKB v2.0 后端镜像构建脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "构建模式:"
    echo "  local       本地构建后端镜像"
    echo "  push        构建镜像并推送到私有仓库"
    echo ""
    echo "选项:"
    echo "  --tag <tag>         镜像标签 (默认: dev)"
    echo "  --platform <arch>   目标平台 (默认: linux/amd64)"
    echo "  --no-cache          不使用缓存构建"
    echo "  --help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 local                    # 本地构建后端镜像"
    echo "  $0 push                     # 构建并推送到私有仓库"
    echo "  $0 push --tag v2.0.1        # 指定标签推送"
    echo "  $0 local --no-cache         # 不使用缓存本地构建"
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
        "installer/Dockerfile-backend-optimized"
        "pyproject.toml"
    )

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
    local image_name="$REGISTRY/backend:$TAG"
    log_info "构建后台应用镜像: $image_name"

    local build_args="--platform $PLATFORM"
    if [ "$NO_CACHE" = "true" ]; then
        build_args="$build_args --no-cache"
    fi

    # 使用优化版 Dockerfile
    local dockerfile="installer/Dockerfile-backend-optimized"
    log_info "使用优化版 Dockerfile"

    # 执行构建
    if ! docker build $build_args \
        -f "$dockerfile" \
        -t "$image_name" \
        .; then
        log_error "后台镜像构建失败"
        exit 1
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

# 登录私有仓库
docker_login() {
    if [ "$PUSH" = "true" ]; then
        log_info "登录私有镜像仓库: $REGISTRY"
        echo "请输入仓库用户名和密码"
        docker login "$REGISTRY"
    fi
}

# 显示构建摘要
show_summary() {
    echo ""
    log_info "=== 构建摘要 ==="
    echo "镜像地址: $REGISTRY/backend:$TAG"
    echo "目标平台: $PLATFORM"
    echo "推送状态: $([ "$PUSH" = "true" ] && echo "已推送" || echo "仅本地构建")"

    if [ "$PUSH" = "false" ]; then
        echo ""
        log_info "=== 本地测试命令 ==="
        echo "查看镜像: docker images | grep backend"
        echo "启动容器: docker run -d --name maxkb-backend -p 8080:8080 $REGISTRY/backend:$TAG"
    fi

    echo ""
    log_info "构建完成！"
}

# 主函数
main() {
    # 默认值
    REGISTRY="$DEFAULT_REGISTRY"
    TAG="$DEFAULT_TAG"
    PLATFORM="$DEFAULT_PLATFORM"
    PUSH="false"
    NO_CACHE="false"

    # 如果没有参数，显示帮助信息
    if [ $# -eq 0 ]; then
        print_help
        exit 0
    fi

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            local)
                PUSH="false"
                REGISTRY="maxkb"
                shift
                ;;
            push)
                PUSH="true"
                shift
                ;;
            --tag)
                TAG="$2"
                shift 2
                ;;
            --platform)
                PLATFORM="$2"
                shift 2
                ;;
            --no-cache)
                NO_CACHE="true"
                shift
                ;;
            --help)
                print_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                print_help
                exit 1
                ;;
        esac
    done

    # 检查环境和文件
    check_docker
    check_files

    # 登录仓库 (仅在推送模式时)
    if [ "$PUSH" = "true" ]; then
        docker_login
    fi

    # 构建后端镜像
    build_backend

    # 显示摘要
    show_summary
}

# 执行主函数
main "$@"