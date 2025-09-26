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

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    docker-compose -f docker-compose.yaml build --no-cache
    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose -f docker-compose.yaml up -d
    log_info "服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose -f docker-compose.yaml down
    log_info "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose -f docker-compose.yaml restart
    log_info "服务重启完成"
}

# 查看日志
view_logs() {
    docker-compose -f docker-compose.yaml logs -f
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
            build_images
            ;;
        "start")
            check_docker
            check_env
            start_services
            ;;
        "stop")
            check_docker
            stop_services
            ;;
        "restart")
            check_docker
            restart_services
            ;;
        "logs")
            check_docker
            view_logs
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "help"|*)
            echo "用法: $0 {build|start|stop|restart|logs|cleanup|help}"
            echo ""
            echo "命令说明:"
            echo "  build    - 构建 Docker 镜像"
            echo "  start    - 启动服务"
            echo "  stop     - 停止服务"
            echo "  restart  - 重启服务"
            echo "  logs     - 查看日志"
            echo "  cleanup  - 清理未使用的镜像和容器"
            echo "  help     - 显示此帮助信息"
            ;;
    esac
}

main "$@"
