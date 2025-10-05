# 简历分析系统 Makefile
registryname ?= $(or $(REGISTRY_NAME),ccr.ccs.tencentyun.com)
reponame ?= $(or $(REPO_NAME),krinol)
imagetag ?= $(or $(IMAGE_TAG),latest)
platform ?= $(or $(PLATFORM),linux/arm64)


# 镜像名称
backend_image=$(registryname)/$(reponame)/krinol-backend:$(imagetag)
frontend_image=$(registryname)/$(reponame)/krinol-frontend:$(imagetag)

.PHONY: help install dev build test clean docker-up docker-down docker-build docker-build-backend docker-build-frontend docker-push docker-push-backend docker-push-frontend

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  install     - 安装所有依赖"
	@echo "  dev         - 启动开发环境"
	@echo "  build       - 构建生产版本"
	@echo "  test        - 运行测试"
	@echo "  clean       - 清理临时文件"
	@echo "  docker-up   - 启动Docker容器"
	@echo "  docker-down - 停止Docker容器"
	@echo "  docker-build         - 构建所有Docker镜像"
	@echo "  docker-build-backend - 构建后端Docker镜像"
	@echo "  docker-build-frontend- 构建前端Docker镜像"
	@echo "  docker-push          - 推送所有Docker镜像到仓库"
	@echo "  docker-push-backend  - 推送后端Docker镜像到仓库"
	@echo "  docker-push-frontend - 推送前端Docker镜像到仓库"
	@echo ""
	@echo "配置变量:"
	@echo "  registryname - 镜像仓库地址 (默认: $(registryname))"
	@echo "  reponame     - 仓库名称 (默认: $(reponame))"
	@echo "  imagetag     - 镜像标签 (默认: $(imagetag))"
	@echo "  platform     - 构建平台 (默认: $(platform))"

# 安装依赖
install:
	@echo "安装后端依赖..."
	cd backend && pip install -r requirements.txt
	@echo "安装前端依赖..."
	cd frontend && npm install

# 开发环境
dev:
	@echo "启动开发环境..."
	@echo "后端服务: http://localhost:8000"
	@echo "前端服务: http://localhost:3000"
	@echo "API文档: http://localhost:8000/docs"
	@echo "按 Ctrl+C 停止服务"
	@echo ""
	@echo "启动后端服务..."
	cd backend && python main.py &
	@echo "启动前端服务..."
	cd frontend && npm run dev

# 构建生产版本
build:
	@echo "构建前端..."
	cd frontend && npm run build
	@echo "构建完成!"

# 运行测试
test:
	@echo "运行后端测试..."
	cd backend && python -m pytest tests/ -v
	@echo "运行前端测试..."
	cd frontend && npm run test

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf backend/.pytest_cache
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf frontend/.vite
	@echo "清理完成!"

# Docker相关命令
docker-up:
	@echo "启动Docker容器..."
	cd deploy && docker-compose -f docker-compose.yaml up -d
	@echo "服务已启动!"
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:8000"
	@echo "API文档: http://localhost:8000/docs"

docker-down:
	@echo "停止Docker容器..."
	cd deploy && docker-compose -f docker-compose.yaml down
	@echo "容器已停止!"

docker-build:
	@echo "构建Docker镜像..."
	@echo "使用平台: $(platform)"
	@echo "后端镜像: $(backend_image)"
	@echo "前端镜像: $(frontend_image)"
	cd deploy && PLATFORM=$(platform) docker-compose -f docker-compose.prod.yaml build
	@echo "镜像构建完成!"

# 构建Docker镜像（单独构建）
docker-build-backend:
	@echo "构建后端Docker镜像..."
	@echo "使用平台: $(platform)"
	@echo "镜像名称: $(backend_image)"
	docker buildx build --no-cache --platform $(platform) -f build/backend/Dockerfile -t $(backend_image) -t krinol-backend:latest --load .

docker-build-frontend:
	@echo "构建前端Docker镜像..."
	@echo "使用平台: $(platform)"
	@echo "镜像名称: $(frontend_image)"
	docker buildx build --no-cache --platform $(platform) -f build/frontend/Dockerfile -t $(frontend_image) -t krinol-frontend:latest --load .

# 推送镜像到仓库
docker-push:
	@echo "推送Docker镜像到仓库..."
	@echo "后端镜像: $(backend_image)"
	@echo "前端镜像: $(frontend_image)"
	docker push $(backend_image)
	docker push $(frontend_image)
	@echo "镜像推送完成!"

docker-push-backend:
	@echo "推送后端Docker镜像..."
	@echo "镜像名称: $(backend_image)"
	docker push $(backend_image)
	@echo "后端镜像推送完成!"

docker-push-frontend:
	@echo "推送前端Docker镜像..."
	@echo "镜像名称: $(frontend_image)"
	docker push $(frontend_image)
	@echo "前端镜像推送完成!"

# 数据库相关
db-migrate:
	@echo "运行数据库迁移..."
	cd backend && alembic upgrade head

db-reset:
	@echo "重置数据库..."
	cd backend && alembic downgrade base
	cd backend && alembic upgrade head

# 代码格式化
format:
	@echo "格式化Python代码..."
	cd backend && black . && isort .
	@echo "格式化前端代码..."
	cd frontend && npm run format

# 代码检查
lint:
	@echo "检查Python代码..."
	cd backend && flake8 .
	@echo "检查前端代码..."
	cd frontend && npm run lint
