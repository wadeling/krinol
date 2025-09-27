# 前端Dockerfile - 多阶段构建
# 第一阶段：构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY frontend/package*.json ./

# 清理可能的缓存和锁文件，解决ARM64架构下的rollup依赖问题
RUN rm -rf node_modules package-lock.json

# 设置npm配置
RUN npm config set fund false && \
    npm config set audit false

# 安装依赖（包含开发依赖）
RUN npm install

# 复制源代码
COPY frontend/ .

# 构建应用
RUN npm run build

# 第二阶段：生产阶段
FROM nginx:alpine

# 复制nginx配置
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# 设置权限
RUN chown -R nextjs:nodejs /usr/share/nginx/html && \
    chown -R nextjs:nodejs /var/cache/nginx && \
    chown -R nextjs:nodejs /var/log/nginx && \
    chown -R nextjs:nodejs /etc/nginx/conf.d

# 创建nginx运行目录
RUN touch /var/run/nginx.pid && \
    chown -R nextjs:nodejs /var/run/nginx.pid

# 切换到非root用户
USER nextjs

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]