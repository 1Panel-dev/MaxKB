#!/bin/bash

# MaxKB v2.0 交互式部署脚本
# 按组件分别配置参数

set -e

# 默认配置
DEFAULT_REGISTRY=""
DEFAULT_NETWORK="gs-network"
DEFAULT_DATA_DIR="/opt/maxkb-data"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

log_step() {
    echo -e "${CYAN}[步骤]${NC} $1"
}

# 生成随机密码
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-16
}

# 输入提示函数
read_input() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        echo -e "${YELLOW}$prompt${NC} [默认: ${BLUE}$default${NC}]: "
    else
        echo -e "${YELLOW}$prompt${NC}: "
    fi
    
    read -r input
    if [ -z "$input" ] && [ -n "$default" ]; then
        input="$default"
    fi
    
    eval "$var_name='$input'"
}

# 密码输入函数（可选择生成随机密码）
read_password() {
    local prompt="$1"
    local var_name="$2"
    local random_pass=$(generate_password)
    
    echo -e "${YELLOW}$prompt${NC}"
    echo -e "  1) 使用随机生成的密码: ${BLUE}$random_pass${NC}"
    echo -e "  2) 手动输入密码"
    echo -e "请选择 [1-2，默认1]: "
    
    read -r choice
    case $choice in
        2)
            echo -e "${YELLOW}请输入密码${NC}: "
            read -r password
            eval "$var_name='$password'"
            ;;
        *)
            eval "$var_name='$random_pass'"
            echo -e "使用随机密码: ${BLUE}$random_pass${NC}"
            ;;
    esac
}

# 外部服务密码输入函数（只能手动输入）
read_external_password() {
    local prompt="$1"
    local var_name="$2"
    
    echo -e "${YELLOW}$prompt${NC}: "
    read -r password
    
    # 验证密码不为空
    while [ -z "$password" ]; do
        echo -e "${RED}密码不能为空，请重新输入${NC}"
        echo -e "${YELLOW}$prompt${NC}: "
        read -r password
    done
    
    eval "$var_name='$password'"
}



# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${CYAN}=================================${NC}"
    echo -e "${CYAN}   GS-KH v2.0 交互式部署向导   ${NC}"
    echo -e "${CYAN}=================================${NC}"
    echo ""
}

# 选择要部署的组件
select_components() {
    log_step "选择要部署的组件"
    echo ""

    # 如果使用现有配置，显示当前组件并询问是否修改
    if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$DEPLOYED_COMPONENTS" ]; then
        echo "当前已部署组件: $DEPLOYED_COMPONENTS"
        echo ""
        echo -e "${YELLOW}是否修改组件选择？${NC}"
        echo "  1) 保持当前组件选择"
        echo "  2) 重新选择组件"
        echo -e "请选择 [1-2，默认1]: "

        read -r modify_components
        case $modify_components in
            2)
                # 重新选择组件
                ;;
            *)
                # 使用现有组件配置
                IFS=' ' read -ra SELECTED_COMPONENTS <<< "$DEPLOYED_COMPONENTS"
                log_info "使用现有组件配置: ${SELECTED_COMPONENTS[*]}"
                echo ""
                return
                ;;
        esac
    fi

    echo "可选组件："
    echo "  1) Redis 缓存服务"
    echo "  2) PostgreSQL+pgvector 数据库"
    echo "  3) GS_KH 后台应用"
    echo ""

    while true; do
        echo -e "${YELLOW}请选择要部署的组件 (用空格分隔多个选项，如: 1 2 3)${NC}: "
        read -r selection

        SELECTED_COMPONENTS=()
        for choice in $selection; do
            case $choice in
                1)
                    SELECTED_COMPONENTS+=("redis")
                    ;;
                2)
                    SELECTED_COMPONENTS+=("postgres")
                    ;;
                3)
                    SELECTED_COMPONENTS+=("backend")
                    ;;
                *)
                    log_error "无效选择: $choice"
                    continue 2
                    ;;
            esac
        done

        if [ ${#SELECTED_COMPONENTS[@]} -gt 0 ]; then
            break
        else
            log_error "请至少选择一个组件"
        fi
    done

    echo ""
    log_info "已选择组件: ${SELECTED_COMPONENTS[*]}"
    echo ""
}

# 配置通用参数
configure_general() {
    log_step "配置通用参数"
    echo ""

    # 使用现有配置作为默认值
    local default_registry="${REGISTRY:-$DEFAULT_REGISTRY}"
    local default_network="${NETWORK:-$DEFAULT_NETWORK}"
    local default_data_dir="${DATA_DIR:-$DEFAULT_DATA_DIR}"

    read_input "私有镜像仓库地址" "$default_registry" "REGISTRY"
    
    # 如果配置了私有仓库，询问是否需要登录认证
    if [ -n "$REGISTRY" ] && [ "$REGISTRY" != "docker.io" ]; then
        echo ""

        # 检查是否有现有的认证配置
        if [ "$USE_EXISTING_CONFIG" = "true" ] && [ "$NEED_DOCKER_LOGIN" = "true" ] && [ -n "$DOCKER_USERNAME" ]; then
            echo -e "${YELLOW}检测到现有Docker认证配置 (用户名: $DOCKER_USERNAME)${NC}"
            echo "  1) 使用现有认证配置"
            echo "  2) 重新配置认证信息"
            echo "  3) 无需认证（公开仓库或已登录）"
            echo -e "请选择 [1-3，默认1]: "

            read -r auth_choice
            case $auth_choice in
                2)
                    echo ""
                    echo -e "${YELLOW}请输入新的 Docker 仓库认证信息:${NC}"
                    read_input "用户名" "$DOCKER_USERNAME" "DOCKER_USERNAME"
                    read_external_password "密码" "DOCKER_PASSWORD"
                    NEED_DOCKER_LOGIN="true"
                    ;;
                3)
                    NEED_DOCKER_LOGIN="false"
                    ;;
                *)
                    log_info "使用现有认证配置"
                    # 需要重新输入密码（安全考虑）
                    read_external_password "请重新输入密码" "DOCKER_PASSWORD"
                    NEED_DOCKER_LOGIN="true"
                    ;;
            esac
        else
            echo -e "${YELLOW}检测到私有镜像仓库，是否需要登录认证？${NC}"
            echo "  1) 需要登录认证"
            echo "  2) 无需认证（公开仓库或已登录）"
            echo -e "请选择 [1-2，默认2]: "

            read -r auth_choice
            case $auth_choice in
                1)
                    echo ""
                    echo -e "${YELLOW}请输入 Docker 仓库认证信息:${NC}"
                    read_input "用户名" "${DOCKER_USERNAME:-}" "DOCKER_USERNAME"
                    read_external_password "密码" "DOCKER_PASSWORD"
                    NEED_DOCKER_LOGIN="true"
                    ;;
                *)
                    NEED_DOCKER_LOGIN="false"
                    ;;
            esac
        fi
    else
        NEED_DOCKER_LOGIN="false"
    fi

    echo ""
    read_input "Docker 网络名称" "$default_network" "NETWORK"
    read_input "数据持久化目录" "$default_data_dir" "DATA_DIR"
    
    echo ""
}

# 配置 Redis 参数
configure_redis() {
    log_step "配置 Redis 参数"
    echo ""

    # 使用现有配置作为默认值
    local default_redis_container="${REDIS_CONTAINER:-gs-redis}"
    local default_redis_port="${REDIS_PORT:-6379}"

    read_input "Redis 容器名称" "$default_redis_container" "REDIS_CONTAINER"
    read_input "Redis 端口" "$default_redis_port" "REDIS_PORT"

    # 如果有现有密码，询问是否使用
    if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$REDIS_PASSWORD" ]; then
        echo -e "${YELLOW}检测到现有Redis密码，是否使用现有密码？${NC}"
        echo "  1) 使用现有密码"
        echo "  2) 重新设置密码"
        echo -e "请选择 [1-2，默认1]: "

        read -r password_choice
        case $password_choice in
            2)
                read_password "Redis 密码" "REDIS_PASSWORD"
                ;;
            *)
                log_info "使用现有Redis密码"
                ;;
        esac
    else
        read_password "Redis 密码" "REDIS_PASSWORD"
    fi
    
    # Redis 在网络内的主机名就是容器名
    REDIS_HOST="$REDIS_CONTAINER"
    
    echo ""
    log_info "Redis 配置完成"
    echo "  - 容器名: $REDIS_CONTAINER"
    echo "  - 端口: $REDIS_PORT"
    echo "  - 内部主机名: $REDIS_HOST"
    echo ""
}

# 配置 PostgreSQL 参数
configure_postgres() {
    log_step "配置 PostgreSQL 参数"
    echo ""

    # 使用现有配置作为默认值
    local default_db_container="${DB_CONTAINER:-gs-postgres}"
    local default_db_port="${DB_PORT:-5432}"
    local default_db_name="${DB_NAME:-gskh}"
    local default_db_user="${DB_USER:-maxkb}"

    read_input "PostgreSQL 容器名称" "$default_db_container" "DB_CONTAINER"
    read_input "PostgreSQL 端口" "$default_db_port" "DB_PORT"
    read_input "数据库名称" "$default_db_name" "DB_NAME"
    read_input "数据库用户名" "$default_db_user" "DB_USER"

    # 如果有现有密码，询问是否使用
    if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$DB_PASSWORD" ]; then
        echo -e "${YELLOW}检测到现有数据库密码，是否使用现有密码？${NC}"
        echo "  1) 使用现有密码"
        echo "  2) 重新设置密码"
        echo -e "请选择 [1-2，默认1]: "

        read -r password_choice
        case $password_choice in
            2)
                read_password "数据库密码" "DB_PASSWORD"
                ;;
            *)
                log_info "使用现有数据库密码"
                ;;
        esac
    else
        read_password "数据库密码" "DB_PASSWORD"
    fi
    
    # PostgreSQL 在网络内的主机名就是容器名
    DB_HOST="$DB_CONTAINER"
    
    echo ""
    log_info "PostgreSQL 配置完成"
    echo "  - 容器名: $DB_CONTAINER"
    echo "  - 端口: $DB_PORT"
    echo "  - 数据库: $DB_NAME"
    echo "  - 用户名: $DB_USER"
    echo "  - 内部主机名: $DB_HOST"
    echo ""
}

# 配置后台应用的镜像
configure_backend_image() {
    echo -e "${CYAN}=== 配置后台应用镜像 ===${NC}"

    # 设置默认镜像仓库地址
    local default_registry="docker.zhouke.tech/gs_kh"

    # 如果有现有配置，解析当前镜像信息
    if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$BACKEND_IMAGE" ]; then
        echo "当前后台镜像: $BACKEND_IMAGE"
        echo ""

        # 解析当前镜像的tag
        local current_tag=$(echo "$BACKEND_IMAGE" | sed 's/.*://')
        local current_registry_and_repo=$(echo "$BACKEND_IMAGE" | sed 's/:.*$//')

        echo -e "${YELLOW}镜像配置选项:${NC}"
        echo "  1) 仅更新镜像标签 (推荐用于版本更新)"
        echo "  2) 使用当前镜像配置"
        echo "  3) 重新配置完整镜像地址"
        echo -e "请选择 [1-3，默认1]: "

        read -r image_choice
        case $image_choice in
            2)
                log_info "使用当前镜像: $BACKEND_IMAGE"
                echo ""
                return
                ;;
            3)
                # 重新配置完整镜像
                echo -e "${YELLOW}请输入完整的镜像地址${NC} [默认: ${BLUE}$default_registry/backend:dev${NC}]: "
                read -r full_image_input
                if [ -z "$full_image_input" ]; then
                    BACKEND_IMAGE="$default_registry/backend:dev"
                else
                    BACKEND_IMAGE="$full_image_input"
                fi
                ;;
            *)
                # 仅更新标签
                echo -e "${YELLOW}请输入新的镜像标签${NC} [当前: ${BLUE}$current_tag${NC}]: "
                read -r tag_input
                if [ -z "$tag_input" ]; then
                    tag_input="$current_tag"
                fi
                BACKEND_IMAGE="$current_registry_and_repo:$tag_input"
                ;;
        esac
    else
        # 全新配置
        echo -e "${YELLOW}请输入镜像标签${NC} [默认: ${BLUE}dev${NC}]: "
        read -r tag_input
        if [ -z "$tag_input" ]; then
            tag_input="dev"
        fi

        # 构建完整的镜像地址
        BACKEND_IMAGE="$default_registry/backend:$tag_input"
    fi

    log_info "使用后台镜像: $BACKEND_IMAGE"
    echo ""
}

# 配置后台应用参数
configure_backend() {
    log_step "配置 GS-KH 后台应用参数"
    echo ""
    
    # 配置后台镜像
    configure_backend_image
    
    # 配置数据库连接
    configure_backend_database
    
    # 配置Redis连接
    configure_backend_redis
    
    # 使用现有配置作为默认值
    local default_backend_port="${BACKEND_PORT:-8080}"
    local default_log_level="${LOG_LEVEL:-INFO}"

    read_input "后台应用端口" "$default_backend_port" "BACKEND_PORT"
    read_input "日志级别" "$default_log_level" "LOG_LEVEL"
    
    echo ""
    log_info "后台应用配置完成"
    echo "  - 镜像: $BACKEND_IMAGE"
    echo "  - 端口: $BACKEND_PORT"
    echo "  - 数据库连接: $DB_HOST:$DB_PORT/$DB_NAME"
    echo "  - Redis 连接: $REDIS_HOST:$REDIS_PORT"
    echo ""
}

# 配置后台应用的数据库连接
configure_backend_database() {
    echo -e "${CYAN}=== 配置数据库连接 ===${NC}"

    # 如果有现有配置，显示当前设置
    if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$USE_EXTERNAL_DB" ]; then
        if [ "$USE_EXTERNAL_DB" = "true" ]; then
            echo "当前配置: 使用外部数据库 ($DB_HOST:$DB_PORT/$DB_NAME)"
        else
            echo "当前配置: 使用内部数据库"
        fi
        echo ""
        echo -e "${YELLOW}是否修改数据库连接配置？${NC}"
        echo "  1) 保持当前配置"
        echo "  2) 重新配置数据库连接"
        echo -e "请选择 [1-2，默认1]: "

        read -r modify_db
        case $modify_db in
            2)
                # 重新配置
                ;;
            *)
                log_info "保持当前数据库连接配置"
                echo ""
                return
                ;;
        esac
    fi

    if [[ " ${SELECTED_COMPONENTS[*]} " =~ " postgres " ]]; then
        echo "检测到已选择部署 PostgreSQL 组件"
        echo -e "${YELLOW}请选择数据库连接方式:${NC}"
        echo "  1) 使用内部 PostgreSQL (推荐)"
        echo "  2) 使用外部数据库"
        echo -e "请选择 [1-2，默认1]: "

        read -r db_choice
        case $db_choice in
            2)
                echo -e "${YELLOW}请配置外部数据库连接:${NC}"
                echo -e "${CYAN}💡 提示: 后台应用使用host网络，建议使用 127.0.0.1${NC}"

                # 使用现有配置作为默认值
                local default_db_host="${DB_HOST:-127.0.0.1}"
                local default_db_port="${DB_PORT:-5433}"
                local default_db_name="${DB_NAME:-gskh}"
                local default_db_user="${DB_USER:-gskh}"

                read_input "数据库主机地址" "$default_db_host" "DB_HOST"
                read_input "数据库端口" "$default_db_port" "DB_PORT"
                read_input "数据库名称" "$default_db_name" "DB_NAME"
                read_input "数据库用户名" "$default_db_user" "DB_USER"

                # 处理密码
                if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$DB_PASSWORD" ]; then
                    echo -e "${YELLOW}是否使用现有数据库密码？${NC}"
                    echo "  1) 使用现有密码"
                    echo "  2) 重新输入密码"
                    echo -e "请选择 [1-2，默认1]: "

                    read -r password_choice
                    case $password_choice in
                        2)
                            read_external_password "数据库密码" "DB_PASSWORD"
                            ;;
                        *)
                            log_info "使用现有数据库密码"
                            ;;
                    esac
                else
                    read_external_password "数据库密码" "DB_PASSWORD"
                fi

                # 标记不部署内部PostgreSQL
                USE_EXTERNAL_DB="true"
                ;;
            *)
                echo -e "${GREEN}使用内部 PostgreSQL 连接${NC}"
                # 使用内部配置的值（已在 configure_postgres 中设置）
                USE_EXTERNAL_DB="false"
                ;;
        esac
    else
        echo -e "${YELLOW}未部署 PostgreSQL，请配置外部数据库连接:${NC}"
        echo -e "${CYAN}💡 提示: 后台应用使用host网络，建议使用 127.0.0.1${NC}"

        # 使用现有配置作为默认值
        local default_db_host="${DB_HOST:-127.0.0.1}"
        local default_db_port="${DB_PORT:-5432}"
        local default_db_name="${DB_NAME:-gskh}"
        local default_db_user="${DB_USER:-gskh}"

        read_input "数据库主机地址" "$default_db_host" "DB_HOST"
        read_input "数据库端口" "$default_db_port" "DB_PORT"
        read_input "数据库名称" "$default_db_name" "DB_NAME"
        read_input "数据库用户名" "$default_db_user" "DB_USER"

        # 处理密码
        if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$DB_PASSWORD" ]; then
            echo -e "${YELLOW}是否使用现有数据库密码？${NC}"
            echo "  1) 使用现有密码"
            echo "  2) 重新输入密码"
            echo -e "请选择 [1-2，默认1]: "

            read -r password_choice
            case $password_choice in
                2)
                    read_external_password "数据库密码" "DB_PASSWORD"
                    ;;
                *)
                    log_info "使用现有数据库密码"
                    ;;
            esac
        else
            read_external_password "数据库密码" "DB_PASSWORD"
        fi

        # 标记不部署内部PostgreSQL
        USE_EXTERNAL_DB="true"
    fi
    echo ""
}

# 配置后台应用的Redis连接
configure_backend_redis() {
    echo -e "${CYAN}=== 配置 Redis 连接 ===${NC}"

    # 如果有现有配置，显示当前设置
    if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$USE_EXTERNAL_REDIS" ]; then
        if [ "$USE_EXTERNAL_REDIS" = "true" ]; then
            echo "当前配置: 使用外部Redis ($REDIS_HOST:$REDIS_PORT)"
        else
            echo "当前配置: 使用内部Redis"
        fi
        echo ""
        echo -e "${YELLOW}是否修改Redis连接配置？${NC}"
        echo "  1) 保持当前配置"
        echo "  2) 重新配置Redis连接"
        echo -e "请选择 [1-2，默认1]: "

        read -r modify_redis
        case $modify_redis in
            2)
                # 重新配置
                ;;
            *)
                log_info "保持当前Redis连接配置"
                echo ""
                return
                ;;
        esac
    fi

    if [[ " ${SELECTED_COMPONENTS[*]} " =~ " redis " ]]; then
        echo "检测到已选择部署 Redis 组件"
        echo -e "${YELLOW}请选择 Redis 连接方式:${NC}"
        echo "  1) 使用内部 Redis (推荐)"
        echo "  2) 使用外部 Redis"
        echo -e "请选择 [1-2，默认1]: "

        read -r redis_choice
        case $redis_choice in
            2)
                echo -e "${YELLOW}请配置外部 Redis 连接:${NC}"
                echo -e "${CYAN}💡 提示: 后台应用使用host网络，建议使用 127.0.0.1${NC}"

                # 使用现有配置作为默认值
                local default_redis_host="${REDIS_HOST:-127.0.0.1}"
                local default_redis_port="${REDIS_PORT:-6379}"

                read_input "Redis 主机地址" "$default_redis_host" "REDIS_HOST"
                read_input "Redis 端口" "$default_redis_port" "REDIS_PORT"

                # 处理密码
                if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$REDIS_PASSWORD" ]; then
                    echo -e "${YELLOW}是否使用现有Redis密码？${NC}"
                    echo "  1) 使用现有密码"
                    echo "  2) 重新输入密码"
                    echo -e "请选择 [1-2，默认1]: "

                    read -r password_choice
                    case $password_choice in
                        2)
                            read_external_password "Redis 密码" "REDIS_PASSWORD"
                            ;;
                        *)
                            log_info "使用现有Redis密码"
                            ;;
                    esac
                else
                    read_external_password "Redis 密码" "REDIS_PASSWORD"
                fi

                # 标记不部署内部Redis
                USE_EXTERNAL_REDIS="true"
                ;;
            *)
                echo -e "${GREEN}使用内部 Redis 连接${NC}"
                # 使用内部配置的值（已在 configure_redis 中设置）
                USE_EXTERNAL_REDIS="false"
                ;;
        esac
    else
        echo -e "${YELLOW}未部署 Redis，请配置外部 Redis 连接:${NC}"
        echo -e "${CYAN}💡 提示: 后台应用使用host网络，建议使用 127.0.0.1${NC}"

        # 使用现有配置作为默认值
        local default_redis_host="${REDIS_HOST:-127.0.0.1}"
        local default_redis_port="${REDIS_PORT:-6379}"

        read_input "Redis 主机地址" "$default_redis_host" "REDIS_HOST"
        read_input "Redis 端口" "$default_redis_port" "REDIS_PORT"

        # 处理密码
        if [ "$USE_EXISTING_CONFIG" = "true" ] && [ -n "$REDIS_PASSWORD" ]; then
            echo -e "${YELLOW}是否使用现有Redis密码？${NC}"
            echo "  1) 使用现有密码"
            echo "  2) 重新输入密码"
            echo -e "请选择 [1-2，默认1]: "

            read -r password_choice
            case $password_choice in
                2)
                    read_external_password "Redis 密码" "REDIS_PASSWORD"
                    ;;
                *)
                    log_info "使用现有Redis密码"
                    ;;
            esac
        else
            read_external_password "Redis 密码" "REDIS_PASSWORD"
        fi

        # 标记不部署内部Redis
        USE_EXTERNAL_REDIS="true"
    fi
    echo ""
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

# Docker 仓库登录
docker_login() {
    if [[ "$NEED_DOCKER_LOGIN" == "true" ]]; then
        log_info "登录 Docker 私有仓库: $REGISTRY"
        
        # 使用环境变量传递密码，避免在命令行中暴露
        if echo "$DOCKER_PASSWORD" | docker login "$REGISTRY" --username "$DOCKER_USERNAME" --password-stdin; then
            log_info "Docker 仓库登录成功"
        else
            log_error "Docker 仓库登录失败，请检查用户名和密码"
            exit 1
        fi
    else
        log_info "跳过 Docker 仓库登录"
    fi
}

# 检查镜像是否存在本地
check_image_exists() {
    local image="$1"
    
    # 使用更可靠的检测方法
    if docker images --format "{{.Repository}}:{{.Tag}}" | grep -Fxq "$image"; then
        return 0  # 镜像存在
    else
        return 1  # 镜像不存在
    fi
}

# 获取组件需要的镜像列表（基于选中的组件，不考虑外部服务）
get_component_images() {
    local images=()

    # 根据选中的组件获取对应镜像，暂时不考虑是否使用外部服务
    for component in "${SELECTED_COMPONENTS[@]}"; do
        case $component in
            redis)
                local redis_image="redis:7-alpine"
                if [ -n "$REGISTRY" ]; then
                    redis_image="$REGISTRY/redis:7-alpine"
                fi
                images+=("$redis_image")
                ;;
            postgres)
                local postgres_image="pgvector/pgvector:pg17"
                if [ -n "$REGISTRY" ]; then
                    postgres_image="$REGISTRY/pgvector/pgvector:pg17"
                fi
                images+=("$postgres_image")
                ;;
            backend)
                # 直接使用配置的后台镜像
                local backend_image="${BACKEND_IMAGE:-docker.zhouke.tech/gs_kh/backend:dev}"
                images+=("$backend_image")
                ;;
        esac
    done

    echo "${images[@]}"
}

# 获取部署阶段实际需要的镜像（考虑外部服务选择）
get_deployment_images() {
    local images=()

    # 根据外部服务配置决定实际需要的镜像
    for component in "${SELECTED_COMPONENTS[@]}"; do
        case $component in
            redis)
                # 只有不使用外部Redis时才需要镜像
                if [[ "${USE_EXTERNAL_REDIS:-false}" != "true" ]]; then
                    local redis_image="redis:7-alpine"
                    if [ -n "$REGISTRY" ]; then
                        redis_image="$REGISTRY/redis:7-alpine"
                    fi
                    images+=("$redis_image")
                fi
                ;;
            postgres)
                # 只有不使用外部数据库时才需要镜像
                if [[ "${USE_EXTERNAL_DB:-false}" != "true" ]]; then
                    local postgres_image="pgvector/pgvector:pg17"
                    if [ -n "$REGISTRY" ]; then
                        postgres_image="$REGISTRY/pgvector/pgvector:pg17"
                    fi
                    images+=("$postgres_image")
                fi
                ;;
            backend)
                # 后台应用总是需要镜像
                local backend_image="${BACKEND_IMAGE:-docker.zhouke.tech/gs_kh/backend:dev}"
                images+=("$backend_image")
                ;;
        esac
    done

    echo "${images[@]}"
}

# 选择组件后立即检查和下载镜像
check_and_pull_images() {
    log_step "检查组件镜像"
    echo ""
    
    local images=($(get_component_images))
    
    if [ ${#images[@]} -eq 0 ]; then
        log_info "✅ 所选组件无需镜像"
        return 0
    fi
    
    echo -e "${CYAN}所选组件需要以下镜像:${NC}"
    for image in "${images[@]}"; do
        echo "  - $image"
    done
    echo ""
    
    local total=${#images[@]}
    local current=0
    local need_download=()
    local already_exists=()
    
    # 检查镜像状态
    log_info "📋 检查镜像状态..."
    for image in "${images[@]}"; do
        current=$((current + 1))
        if check_image_exists "$image"; then
            already_exists+=("$image")
            log_info "[$current/$total] ✅ 镜像已存在: $image"
        else
            need_download+=("$image")
            log_info "[$current/$total] ❌ 镜像不存在: $image"
        fi
    done
    
    echo ""
    
    # 显示检查结果
    if [ ${#already_exists[@]} -gt 0 ]; then
        log_info "✅ 已存在的镜像 (${#already_exists[@]}/${total}):"
        for image in "${already_exists[@]}"; do
            echo "  - $image"
        done
        echo ""
    fi
    
    if [ ${#need_download[@]} -eq 0 ]; then
        log_info "🎉 所有镜像都已存在，可以继续配置！"
        return 0
    fi
    
    # 必须下载缺失的镜像才能继续
    log_warn "❌ 以下镜像缺失，必须先下载 (${#need_download[@]}/${total}):"
    for image in "${need_download[@]}"; do
        echo "  - $image"
    done
    echo ""
    
    echo -e "${YELLOW}必须下载缺失的镜像才能继续部署${NC}"
    echo "  1) 立即下载镜像"
    echo "  2) 退出脚本，手动下载后重新运行"
    echo -e "请选择 [1-2，默认1]: "
    
    read -r download_choice
    case $download_choice in
        2)
            log_info "部署已取消"
            echo ""
            log_info "手动下载命令："
            for image in "${need_download[@]}"; do
                echo "  docker pull $image"
            done
            exit 0
            ;;
        *)
            log_info "开始下载缺失的镜像..."
            ;;
    esac
    
    echo ""
    
    # 下载缺失的镜像
    local failed_images=()
    current=0
    
    for image in "${need_download[@]}"; do
        current=$((current + 1))
        log_info "⬇️ [$current/${#need_download[@]}] 下载镜像: $image"
        
        # 显示下载提示
        if [[ "$image" == *"backend"* ]]; then
            echo "💡 提示: 后台镜像较大(~3GB)，请耐心等待..."
            echo "💡 监控: 可在另一终端运行 'docker images | grep backend' 查看进度"
        fi
        
        if docker pull "$image"; then
            log_info "✅ 下载成功: $image"
        else
            log_error "❌ 下载失败: $image"
            failed_images+=("$image")
        fi
        echo ""
    done
    
    # 处理下载失败的镜像
    if [ ${#failed_images[@]} -gt 0 ]; then
        log_error "以下镜像下载失败："
        for failed_image in "${failed_images[@]}"; do
            echo "  - $failed_image"
        done
        echo ""
        log_error "镜像下载失败，无法继续部署"
        echo ""
        log_info "请解决网络问题后手动下载，或稍后重新运行脚本"
        log_info "手动下载命令："
        for failed_image in "${failed_images[@]}"; do
            echo "  docker pull $failed_image"
        done
        exit 1
    else
        log_info "🎉 所有镜像下载完成，可以开始配置参数！"
    fi
    echo ""
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
    mkdir -p "$DATA_DIR"/{redis,postgres-data,postgres-init,maxkb-logs,maxkb-local,maxkb-models,maxkb-python-packages,maxkb-sandbox,maxkb-cache}

    # 设置合适的目录权限，确保容器内应用可以写入
    chmod 755 "$DATA_DIR"
    chmod 777 "$DATA_DIR"/maxkb-logs    # 日志目录需要写权限
    chmod 777 "$DATA_DIR"/maxkb-local   # 本地存储需要写权限
    chmod 777 "$DATA_DIR"/maxkb-models  # 模型目录需要写权限
    chmod 777 "$DATA_DIR"/maxkb-python-packages  # Python包目录需要写权限
    chmod 777 "$DATA_DIR"/maxkb-sandbox # Sandbox目录需要写权限
    chmod 777 "$DATA_DIR"/maxkb-cache   # 缓存目录需要写权限
    chmod 755 "$DATA_DIR"/redis
    chmod 755 "$DATA_DIR"/postgres-data
    chmod 755 "$DATA_DIR"/postgres-init
    
    # 预创建关键日志文件，避免权限问题
    touch "$DATA_DIR"/maxkb-logs/drf_exception.log
    touch "$DATA_DIR"/maxkb-logs/maxkb.log
    chmod 666 "$DATA_DIR"/maxkb-logs/*.log 2>/dev/null || true
    
    # 设置目录所有者（如果是root运行）
    if [ "$(id -u)" = "0" ]; then
        chown -R 1000:1000 "$DATA_DIR"/maxkb-logs "$DATA_DIR"/maxkb-local "$DATA_DIR"/maxkb-models "$DATA_DIR"/maxkb-python-packages "$DATA_DIR"/maxkb-sandbox "$DATA_DIR"/maxkb-cache 2>/dev/null || true
    fi
    
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
    docker stop "$REDIS_CONTAINER" 2>/dev/null || true
    docker rm "$REDIS_CONTAINER" 2>/dev/null || true
    
    # 启动 Redis 容器
    docker run -d \
        --name "$REDIS_CONTAINER" \
        --network "$NETWORK" \
        -p "$REDIS_PORT:6379" \
        -v "$DATA_DIR/redis:/data" \
        -e REDIS_PASSWORD="$REDIS_PASSWORD" \
        --restart unless-stopped \
        "$image" \
        redis-server --requirepass "$REDIS_PASSWORD" --appendonly yes
    
    log_info "Redis 部署完成"
}

# 部署 PostgreSQL
deploy_postgres() {
    log_info "部署 PostgreSQL+pgvector 服务..."
    
    local image="pgvector/pgvector:pg17"
    if [ -n "$REGISTRY" ]; then
        image="$REGISTRY/pgvector/pgvector:pg17"
    fi
    
    # 停止并删除现有容器
    docker stop "$DB_CONTAINER" 2>/dev/null || true
    docker rm "$DB_CONTAINER" 2>/dev/null || true
    
    # 创建数据目录和初始化脚本目录
    mkdir -p "$DATA_DIR/postgres-data"
    mkdir -p "$DATA_DIR/postgres-init"
    
    # 创建初始化脚本
    cat > "$DATA_DIR/postgres-init/init.sql" << EOF
CREATE DATABASE ${DB_NAME};
\c ${DB_NAME};
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
EOF
    
    # 启动 PostgreSQL 容器
    docker run -d \
        --name "$DB_CONTAINER" \
        --network "$NETWORK" \
        -p "$DB_PORT:5432" \
        -v "$DATA_DIR/postgres-data:/var/lib/postgresql/data" \
        -v "$DATA_DIR/postgres-init/init.sql:/docker-entrypoint-initdb.d/init.sql" \
        -e POSTGRES_DB=postgres \
        -e POSTGRES_USER="$DB_USER" \
        -e POSTGRES_PASSWORD="$DB_PASSWORD" \
        -e POSTGRES_MAX_CONNECTIONS=1000 \
        --restart unless-stopped \
        "$image"
    
    log_info "PostgreSQL 部署完成"
}

# 部署后台应用
deploy_backend() {
    log_info "部署 MaxKB 后台应用..."
    
    # 使用配置的后台镜像（已在 configure_backend_image 中处理了仓库前缀）
    local image="${BACKEND_IMAGE:-maxkb/backend:v2.0}"
    
    # 停止并删除现有容器
    docker stop gs-backend 2>/dev/null || true
    docker rm gs-backend 2>/dev/null || true
    
    # 启动后台应用容器（使用host网络模式以避免与宿主机服务的连接问题）
    docker run -d \
        --name gs-backend \
        --network host \
        -v "$DATA_DIR/maxkb-logs:/opt/maxkb/logs" \
        -v "$DATA_DIR/maxkb-local:/opt/maxkb/local" \
        -v "$DATA_DIR/maxkb-models:/opt/maxkb-app/model" \
        -v "$DATA_DIR/maxkb-python-packages:/opt/maxkb/python-packages" \
        -v "$DATA_DIR/maxkb-sandbox:/opt/maxkb-app/sandbox" \
        -v "$DATA_DIR/maxkb-cache:/opt/maxkb/cache" \
        -e MAXKB_CONFIG_TYPE=ENV \
        -e MAXKB_DB_NAME="$DB_NAME" \
        -e MAXKB_DB_HOST="$DB_HOST" \
        -e MAXKB_DB_PORT="$DB_PORT" \
        -e MAXKB_DB_USER="$DB_USER" \
        -e MAXKB_DB_PASSWORD="$DB_PASSWORD" \
        -e MAXKB_REDIS_HOST="$REDIS_HOST" \
        -e MAXKB_REDIS_PORT="$REDIS_PORT" \
        -e MAXKB_REDIS_PASSWORD="$REDIS_PASSWORD" \
        -e MAXKB_REDIS_DB=0 \
        -e MAXKB_LOG_LEVEL="$LOG_LEVEL" \
        --restart unless-stopped \
        "$image"
    
    log_info "MaxKB 后台应用部署完成"
}



# 保存配置信息
save_config() {
    cat > "$DATA_DIR/maxkb-config.env" << EOF
# MaxKB 交互式部署配置
REGISTRY=$REGISTRY
NETWORK=$NETWORK
DATA_DIR=$DATA_DIR

# Docker 认证配置
NEED_DOCKER_LOGIN=${NEED_DOCKER_LOGIN:-false}
DOCKER_USERNAME=${DOCKER_USERNAME:-}

# 部署组件
DEPLOYED_COMPONENTS="${SELECTED_COMPONENTS[*]}"

# 外部服务标记
USE_EXTERNAL_DB=${USE_EXTERNAL_DB:-false}
USE_EXTERNAL_REDIS=${USE_EXTERNAL_REDIS:-false}

# Redis 配置 (如果部署)
REDIS_CONTAINER=${REDIS_CONTAINER:-}
REDIS_HOST=${REDIS_HOST:-}
REDIS_PORT=${REDIS_PORT:-}
REDIS_PASSWORD=${REDIS_PASSWORD:-}

# PostgreSQL 配置 (如果部署)
DB_CONTAINER=${DB_CONTAINER:-}
DB_HOST=${DB_HOST:-}
DB_PORT=${DB_PORT:-}
DB_NAME=${DB_NAME:-}
DB_USER=${DB_USER:-}
DB_PASSWORD=${DB_PASSWORD:-}

# 后台应用配置 (如果部署)
BACKEND_IMAGE=${BACKEND_IMAGE:-}
BACKEND_HOST=${BACKEND_HOST:-}
BACKEND_PORT=${BACKEND_PORT:-}
LOG_LEVEL=${LOG_LEVEL:-}

# 部署时间
DEPLOY_TIME=$(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    log_info "配置信息已保存到: $DATA_DIR/maxkb-config.env"
}

# Python依赖管理辅助函数
manage_python_dependencies() {
    log_info "Python依赖管理"
    echo ""
    echo "Python依赖包目录: $DATA_DIR/maxkb-python-packages"
    echo ""
    echo "管理方式："
    echo "  方法1 - 宿主机直接安装（推荐）："
    echo "    pip install --target $DATA_DIR/maxkb-python-packages <包名>"
    echo ""
    echo "  方法2 - 容器内安装："
    echo "    docker exec -it gs-backend bash"
    echo "    source /opt/py3/bin/activate"
    echo "    pip install --target /opt/maxkb/python-packages <包名>"
    echo ""
    echo "  方法3 - 批量安装："
    echo "    # 创建requirements.txt到 $DATA_DIR/maxkb-local/requirements.txt"
    echo "    # 然后执行："
    echo "    docker exec gs-backend bash -c \\"
    echo "      source /opt/py3/bin/activate && \\"
    echo "      pip install --target /opt/maxkb/python-packages -r /opt/maxkb/local/requirements.txt\""
    echo ""
    log_info "💡 提示: 使用Volume挂载，容器更新后依赖包会自动保留！"
    echo ""
}

# 显示部署摘要
show_summary() {
    echo ""
    echo -e "${CYAN}=================================${NC}"
    echo -e "${CYAN}        部署完成摘要            ${NC}"
    echo -e "${CYAN}=================================${NC}"
    echo ""
    
    log_info "已部署组件: ${SELECTED_COMPONENTS[*]}"
    echo ""
    
    if [[ " ${SELECTED_COMPONENTS[*]} " =~ " redis " ]]; then
        echo -e "${GREEN}✓ Redis 缓存服务${NC}"
        echo "  - 容器名: $REDIS_CONTAINER"
        echo "  - 端口: $REDIS_PORT"
        echo "  - 密码: $REDIS_PASSWORD"
        echo ""
    fi
    
    if [[ " ${SELECTED_COMPONENTS[*]} " =~ " postgres " ]]; then
        echo -e "${GREEN}✓ PostgreSQL 数据库${NC}"
        echo "  - 容器名: $DB_CONTAINER"
        echo "  - 端口: $DB_PORT"
        echo "  - 数据库: $DB_NAME"
        echo "  - 用户名: $DB_USER"
        echo "  - 密码: $DB_PASSWORD"
        echo ""
    fi
    
    if [[ " ${SELECTED_COMPONENTS[*]} " =~ " backend " ]]; then
        echo -e "${GREEN}✓ MaxKB 后台应用${NC}"
        echo "  - 网络模式: host（直接使用宿主机网络）"
        echo "  - 端口: $BACKEND_PORT"
        echo "  - 数据库连接: $DB_HOST:$DB_PORT/$DB_NAME"
        echo "  - Redis 连接: $REDIS_HOST:$REDIS_PORT"
        echo ""
    fi

    echo -e "${CYAN}访问地址:${NC}"
    if [[ " ${SELECTED_COMPONENTS[*]} " =~ " backend " ]]; then
        echo "  API 文档: http://localhost:${BACKEND_PORT:-8080}/api/docs"
    fi
    
    echo ""
    echo -e "${CYAN}数据目录:${NC}"
    echo "  - 日志目录: $DATA_DIR/maxkb-logs"
    echo "  - 本地存储: $DATA_DIR/maxkb-local"
    echo "  - 模型目录: $DATA_DIR/maxkb-models"
    echo "  - Python包: $DATA_DIR/maxkb-python-packages"
    echo "  - Sandbox: $DATA_DIR/maxkb-sandbox"
    echo "  - 缓存目录: $DATA_DIR/maxkb-cache"
    echo ""
    echo -e "${CYAN}配置文件: $DATA_DIR/maxkb-config.env${NC}"
    echo ""

    # 显示Python依赖管理信息
    if [[ " ${SELECTED_COMPONENTS[*]} " =~ " backend " ]]; then
        manage_python_dependencies
    fi
}

# 主函数
main() {
    # 显示欢迎信息
    show_welcome

    # 检查 Docker 环境
    check_docker
    echo ""

    # 加载现有配置
    log_info "正在检查现有配置..."

    # 直接在这里实现配置加载逻辑
    local config_file="$DEFAULT_DATA_DIR/maxkb-config.env"
    log_info "检查配置文件: $config_file"

    if [ -f "$config_file" ]; then
        log_info "检测到现有配置文件: $config_file"
        echo ""
        echo -e "${YELLOW}是否使用现有配置作为默认值？${NC}"
        echo "  1) 是，使用现有配置（推荐，可修改tag等参数）"
        echo "  2) 否，重新配置所有参数"
        echo -e "请选择 [1-2，默认1]: "

        read -r use_existing
        case $use_existing in
            2)
                log_info "将重新配置所有参数"
                USE_EXISTING_CONFIG="false"
                ;;
            *)
                log_info "加载现有配置作为默认值"
                USE_EXISTING_CONFIG="true"

                # 加载配置文件
                source "$config_file"

                # 显示当前配置摘要
                echo ""
                log_info "当前配置摘要:"
                echo "  - 镜像仓库: ${REGISTRY:-未设置}"
                echo "  - 数据目录: ${DATA_DIR:-$DEFAULT_DATA_DIR}"
                echo "  - 已部署组件: ${DEPLOYED_COMPONENTS:-无}"
                echo "  - 后台镜像: ${BACKEND_IMAGE:-未设置}"
                echo "  - 外部数据库: $([ "$USE_EXTERNAL_DB" = "true" ] && echo "是" || echo "否")"
                echo "  - 外部Redis: $([ "$USE_EXTERNAL_REDIS" = "true" ] && echo "是" || echo "否")"
                echo ""
                ;;
        esac
    else
        log_info "未检测到现有配置文件，将进行全新配置"
        USE_EXISTING_CONFIG="false"
    fi
    echo ""

    # 选择组件
    select_components
    
    # 配置通用参数（包含私有仓库信息）
    configure_general
    
    # 根据选择的组件配置参数（在检查镜像前先配置，特别是后台镜像）
    for component in "${SELECTED_COMPONENTS[@]}"; do
        case $component in
            redis)
                configure_redis
                ;;
            postgres)
                configure_postgres
                ;;
            backend)
                configure_backend
                ;;
        esac
    done
    
    # Docker 仓库登录（在检查镜像前登录）
    docker_login
    
    # 检查和下载组件镜像（配置完成后检查）
    check_and_pull_images
    
    # 确认部署
    echo ""
    echo -e "${CYAN}=================================${NC}"
    echo -e "${CYAN}      配置完成，准备部署        ${NC}"
    echo -e "${CYAN}=================================${NC}"
    echo ""
    echo -e "${YELLOW}确认开始部署? [y/N]${NC}: "
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "部署已取消"
        exit 0
    fi
    
    echo ""
    log_step "开始部署..."
    
    # 创建网络和目录
    create_network
    create_data_dirs
    
    # 部署组件
    for component in "${SELECTED_COMPONENTS[@]}"; do
        case $component in
            redis)
                # 只有在使用内部Redis时才部署Redis
                if [[ "${USE_EXTERNAL_REDIS:-false}" != "true" ]]; then
                    deploy_redis
                else
                    log_info "跳过 Redis 部署（使用外部 Redis）"
                fi
                ;;
            postgres)
                # 只有在使用内部数据库时才部署PostgreSQL
                if [[ "${USE_EXTERNAL_DB:-false}" != "true" ]]; then
                    deploy_postgres
                    sleep 10  # 等待数据库启动
                else
                    log_info "跳过 PostgreSQL 部署（使用外部数据库）"
                fi
                ;;
            backend)
                deploy_backend
                ;;
        esac
    done
    
    # 保存配置
    save_config
    
    # 显示摘要
    show_summary
    
    log_info "MaxKB 交互式部署完成！"
}

# 检查参数
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "MaxKB v2.0 交互式部署脚本"
    echo ""
    echo "用法: $0"
    echo ""
    echo "这个脚本会引导你完成交互式部署配置"
    echo "支持选择性部署 Redis、PostgreSQL、后台应用"
    exit 0
fi

# 执行主函数
main "$@"