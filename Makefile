# 简历分析系统 Makefile

.PHONY: help install dev build test clean docker-up docker-down

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
	docker-compose up -d
	@echo "服务已启动!"
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:8000"
	@echo "API文档: http://localhost:8000/docs"

docker-down:
	@echo "停止Docker容器..."
	docker-compose down
	@echo "容器已停止!"

docker-build:
	@echo "构建Docker镜像..."
	docker-compose build
	@echo "镜像构建完成!"

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
