# 构建目录

这个目录包含用于构建Docker镜像的相关文件。

## 目录结构

```
build/
├── backend/              # 后端构建文件
│   ├── Dockerfile       # 后端Dockerfile
│   └── .dockerignore    # 后端Docker忽略文件
├── frontend/             # 前端构建文件
│   ├── Dockerfile       # 前端Dockerfile
│   └── .dockerignore    # 前端Docker忽略文件
├── build.sh             # 构建脚本
└── README.md            # 本文件
```

## 使用方法

### 使用构建脚本

```bash
# 构建所有镜像
./build.sh all

# 只构建后端镜像
./build.sh backend

# 只构建前端镜像
./build.sh frontend

# 清理构建缓存
./build.sh clean

# 推送镜像到仓库
./build.sh push myregistry.com
```

### 使用Makefile

```bash
# 构建后端镜像
make docker-build-backend

# 构建前端镜像
make docker-build-frontend

# 构建所有镜像
make docker-build
```

### 直接使用Docker

```bash
# 构建后端镜像
docker build -f build/backend/Dockerfile -t krinol-backend:latest .

# 构建前端镜像
docker build -f build/frontend/Dockerfile -t krinol-frontend:latest .
```

## 镜像说明

### 后端镜像 (krinol-backend)
- 基于Python 3.11-slim
- 包含FastAPI应用
- 暴露8000端口
- 包含所有Python依赖

### 前端镜像 (krinol-frontend)
- 基于Nginx Alpine
- 包含Vue.js构建产物
- 暴露80端口
- 包含Nginx配置

## 注意事项

1. 构建前确保在项目根目录执行
2. 确保Docker服务正在运行
3. 构建过程中会下载依赖，请确保网络连接正常
4. 生产环境建议使用多阶段构建优化镜像大小
