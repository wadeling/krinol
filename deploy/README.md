# 部署目录

这个目录包含用于部署应用的相关文件和配置。

## 目录结构

```
deploy/
├── docker-compose.dev.yaml  # 开发环境配置
├── docker-compose.prod.yaml # 生产环境配置
├── env.example              # 环境变量示例
├── deploy.sh                # 部署脚本
├── test-mysql.sh            # MySQL连接测试脚本
└── README.md                # 本文件
```

## 环境配置

### 开发环境
- 使用MySQL数据库
- 启用热重载
- 暴露调试端口
- 数据持久化

### 生产环境
- 使用MySQL数据库
- 使用Redis缓存
- 启用日志持久化
- 配置健康检查
- 数据持久化

## 使用方法

### 使用部署脚本

```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看日志
./deploy.sh logs

# 构建镜像
./deploy.sh build

# 清理资源
./deploy.sh cleanup
```

### 使用Docker Compose

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yaml up -d

# 启动生产环境
docker-compose -f docker-compose.prod.yaml up -d

# 停止服务
docker-compose -f docker-compose.yaml down
```

### 使用Makefile

```bash
# 启动Docker容器
make docker-up

# 停止Docker容器
make docker-down

# 构建Docker镜像
make docker-build
```

## 环境变量

复制 `env.example` 为 `.env` 并配置以下变量：

### 必需配置
- `SECRET_KEY`: JWT密钥
- `OPENAI_API_KEY`: OpenAI API密钥
- `MYSQL_USER`: MySQL用户名
- `MYSQL_PASSWORD`: MySQL密码
- `MYSQL_DATABASE`: MySQL数据库名
- `MYSQL_ROOT_PASSWORD`: MySQL root密码

### 可选配置
- `DATABASE_URL`: 数据库连接URL（自动生成）
- `LOG_LEVEL`: 日志级别
- `CORS_ORIGINS`: 允许的CORS源

## 服务访问

### 开发环境
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API文档: http://localhost:8000/docs

### 生产环境
- 前端: http://localhost:80
- 后端: http://localhost:8000
- API文档: http://localhost:8000/docs

## 监控和日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.yaml logs

# 查看特定服务日志
docker-compose -f docker-compose.yaml logs backend

# 实时查看日志
docker-compose -f docker-compose.yaml logs -f
```

## MySQL测试

使用测试脚本验证MySQL连接：

```bash
# 测试MySQL连接
./test-mysql.sh
```

## 故障排除

### 常见问题

1. **端口冲突**: 检查端口是否被占用
2. **权限问题**: 确保脚本有执行权限
3. **环境变量**: 检查.env文件配置
4. **镜像构建失败**: 检查Dockerfile和依赖
5. **MySQL连接失败**: 检查MySQL容器状态和配置

### 清理和重置

```bash
# 停止并删除所有容器
docker-compose -f docker-compose.yaml down -v

# 删除所有镜像
docker rmi $(docker images -q)

# 清理系统
docker system prune -a
```
