#!/bin/bash

# Krinol AI Dashboard 构建脚本

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

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 构建后端镜像
build_backend() {
    log_info "构建后端 Docker 镜像..."
    cd "$PROJECT_ROOT"
    docker build --no-cache -f build/backend/Dockerfile -t krinol-backend:latest .
    log_info "后端镜像构建完成"
}

# 构建前端镜像
build_frontend() {
    log_info "构建前端 Docker 镜像..."
    cd "$PROJECT_ROOT"
    
    # 设置默认API URL
    VUE_APP_API_URL="${VUE_APP_API_URL:-/api}"
    log_info "使用API URL: $VUE_APP_API_URL"
    
    # 检测架构
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" || "$ARCH" == "aarch64" ]]; then
        log_info "检测到ARM64架构，使用专用Dockerfile..."
        docker build --no-cache \
            --build-arg VUE_APP_API_URL="$VUE_APP_API_URL" \
            -f build/frontend/Dockerfile.arm64 \
            -t krinol-frontend:latest .
    else
        docker build --no-cache \
            --build-arg VUE_APP_API_URL="$VUE_APP_API_URL" \
            -f build/frontend/Dockerfile \
            -t krinol-frontend:latest .
    fi
    
    log_info "前端镜像构建完成"
}

# 构建所有镜像
build_all() {
    log_info "构建所有 Docker 镜像..."
    build_backend
    build_frontend
    log_info "所有镜像构建完成"
}

# 清理构建缓存
clean_build() {
    log_info "清理构建缓存..."
    docker builder prune -f
    log_info "构建缓存清理完成"
}

# 推送镜像到仓库
push_images() {
    local registry="${1:-localhost:5000}"
    log_info "推送镜像到仓库: $registry"
    
    # 标记镜像
    docker tag krinol-backend:latest $registry/krinol-backend:latest
    docker tag krinol-frontend:latest $registry/krinol-frontend:latest
    
    # 推送镜像
    docker push $registry/krinol-backend:latest
    docker push $registry/krinol-frontend:latest
    
    log_info "镜像推送完成"
}

# 主函数
main() {
    case "${1:-help}" in
        "backend")
            build_backend
            ;;
        "frontend")
            build_frontend
            ;;
        "all")
            build_all
            ;;
        "clean")
            clean_build
            ;;
        "push")
            push_images "$2"
            ;;
        "help"|*)
            echo "用法: $0 {backend|frontend|all|clean|push|help}"
            echo ""
            echo "命令说明:"
            echo "  backend   - 构建后端 Docker 镜像"
            echo "  frontend  - 构建前端 Docker 镜像"
            echo "  all       - 构建所有 Docker 镜像"
            echo "  clean     - 清理构建缓存"
            echo "  push      - 推送镜像到仓库 (可选指定仓库地址)"
            echo "  help      - 显示此帮助信息"
            echo ""
            echo "示例:"
            echo "  $0 all                    # 构建所有镜像"
            echo "  $0 push myregistry.com    # 推送到指定仓库"
            ;;
    esac
}

main "$@"
