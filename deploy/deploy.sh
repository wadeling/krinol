#!/bin/bash

# Krinol AI Dashboard 部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
}

# 检查环境文件
check_env() {
    if [ ! -f ".env" ]; then
        log_warn "环境文件 .env 不存在，从 env.example 复制"
        cp env.example .env
        log_warn "请编辑 .env 文件并填入正确的配置"
        exit 1
    fi
}

# 获取compose文件
get_compose_file() {
    local env=${1:-dev}
    if [ "$env" = "prod" ]; then
        echo "docker-compose.prod.yaml"
    else
        echo "docker-compose.dev.yaml"
    fi
}

# 构建镜像
build_images() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)
    log_info "构建 Docker 镜像 ($env 环境)..."
    
    # 设置前端API URL环境变量
    if [ -f ".env" ]; then
        source .env
        export VUE_APP_API_URL="${VUE_APP_API_URL:-/api}"
        log_info "使用前端API URL: $VUE_APP_API_URL"
    fi
    
    docker-compose -p krinol -f $compose_file build --no-cache
    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)
    log_info "启动服务 ($env 环境)..."
    docker-compose -p krinol -f $compose_file up -d
    log_info "服务启动完成"
}

# 停止服务
stop_services() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)
    log_info "停止服务 ($env 环境)..."
    docker-compose -p krinol -f $compose_file down
    log_info "服务已停止"
}

# 重启服务
restart_services() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)
    log_info "重启服务 ($env 环境)..."
    docker-compose -p krinol -f $compose_file restart
    log_info "服务重启完成"
}

# 查看日志
view_logs() {
    local env=${1:-dev}
    local compose_file=$(get_compose_file $env)
    docker-compose -p krinol -f $compose_file logs -f
}

# 清理
cleanup() {
    log_info "清理未使用的镜像和容器..."
    docker system prune -f
    log_info "清理完成"
}

# 主函数
main() {
    case "${1:-help}" in
        "build")
            check_docker
            build_images "${2:-dev}"
            ;;
        "start")
            check_docker
            check_env
            start_services "${2:-dev}"
            ;;
        "stop")
            check_docker
            stop_services "${2:-dev}"
            ;;
        "restart")
            check_docker
            restart_services "${2:-dev}"
            ;;
        "logs")
            check_docker
            view_logs "${2:-dev}"
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "help"|*)
            echo "用法: $0 {build|start|stop|restart|logs|cleanup|help} [dev|prod]"
            echo ""
            echo "命令说明:"
            echo "  build    - 构建 Docker 镜像"
            echo "  start    - 启动服务"
            echo "  stop     - 停止服务"
            echo "  restart  - 重启服务"
            echo "  logs     - 查看日志"
            echo "  cleanup  - 清理未使用的镜像和容器"
            echo "  help     - 显示此帮助信息"
            echo ""
            echo "环境参数:"
            echo "  dev      - 开发环境 (默认)"
            echo "  prod     - 生产环境"
            echo ""
            echo "示例:"
            echo "  $0 start dev    # 启动开发环境"
            echo "  $0 start prod   # 启动生产环境"
            echo "  $0 build prod   # 构建生产环境镜像"
            ;;
    esac
}

main "$@"
