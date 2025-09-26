# 简历分析系统

基于大模型的智能简历分析Web应用，采用前后端分离架构，提供简历上传、AI分析和结果展示功能。

## 🚀 功能特性

- **简历上传**: 支持PDF、DOCX、TXT格式的简历文件上传
- **AI分析**: 基于大模型的智能简历分析，包括：
  - 总体评分（0-100分）
  - 优势点分析
  - 待改进点识别
  - 改进建议提供
  - 工作经验分析
  - 技能分析
  - 教育背景分析
- **用户管理**: 用户注册、登录、个人信息管理
- **结果展示**: 直观的分析结果展示和详细报告
- **响应式设计**: 支持桌面端和移动端访问

## 🛠 技术栈

### 后端
- **框架**: FastAPI
- **语言**: Python 3.11+
- **数据库**: PostgreSQL / SQLite
- **认证**: JWT
- **文件处理**: PyPDF2, python-docx
- **AI集成**: OpenAI API

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

### 部署
- **容器化**: Docker & Docker Compose
- **Web服务器**: Nginx
- **数据库**: PostgreSQL
- **缓存**: Redis

## 📁 项目结构

```
krinol/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # API路由
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── config/         # 配置文件
│   ├── main.py             # 应用入口
│   ├── requirements.txt    # Python依赖
│   └── Dockerfile          # Docker配置
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   ├── router/         # 路由配置
│   │   └── utils/          # 工具函数
│   ├── package.json        # 前端依赖
│   └── Dockerfile          # Docker配置
├── docker-compose.yml      # Docker编排
├── Makefile               # 构建脚本
└── README.md              # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (可选)

### 本地开发

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd krinol
   ```

2. **安装依赖**
   ```bash
   make install
   ```

3. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp backend/env.example backend/.env
   
   # 编辑配置文件
   vim backend/.env
   ```

4. **启动开发服务**
   ```bash
   make dev
   ```

5. **访问应用**
   - 前端: http://localhost:3000
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

### Docker部署

1. **启动所有服务**
   ```bash
   make docker-up
   ```

2. **访问应用**
   - 前端: http://localhost:3000
   - 后端API: http://localhost:8000

## ⚙️ 配置说明

### 后端配置

在 `backend/.env` 文件中配置以下参数：

```env
# 应用配置
APP_NAME=简历分析系统
DEBUG=true

# 数据库配置
DATABASE_URL=sqlite:///./resume_analysis.db

# JWT配置
SECRET_KEY=your-secret-key-change-in-production

# OpenAI配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# 文件上传配置
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

### 前端配置

前端配置在 `frontend/vite.config.js` 中，主要配置API代理：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## 📖 API文档

### 认证接口

- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取当前用户信息
- `POST /auth/logout` - 用户登出

### 简历管理

- `POST /resumes/upload` - 上传简历
- `GET /resumes/` - 获取简历列表
- `GET /resumes/{resume_id}` - 获取简历详情
- `DELETE /resumes/{resume_id}` - 删除简历

### 分析功能

- `POST /analysis/analyze` - 开始分析
- `GET /analysis/{analysis_id}` - 获取分析结果
- `GET /analysis/` - 获取分析列表

详细的API文档可以在运行后端服务后访问 http://localhost:8000/docs 查看。

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
make test

# 只运行后端测试
cd backend && python -m pytest tests/ -v

# 只运行前端测试
cd frontend && npm run test
```

### 代码质量检查

```bash
# 格式化代码
make format

# 代码检查
make lint
```

## 🚀 部署

### 生产环境部署

1. **配置生产环境变量**
   ```bash
   # 设置生产环境配置
   export NODE_ENV=production
   export DEBUG=false
   export SECRET_KEY=your-production-secret-key
   export OPENAI_API_KEY=your-openai-api-key
   ```

2. **构建和启动**
   ```bash
   # 构建前端
   make build
   
   # 启动Docker服务
   make docker-up
   ```

### 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 必填 |
| `SECRET_KEY` | JWT密钥 | 必填 |
| `DATABASE_URL` | 数据库连接URL | sqlite:///./resume_analysis.db |
| `DEBUG` | 调试模式 | false |
| `UPLOAD_DIR` | 文件上传目录 | uploads |
| `MAX_FILE_SIZE` | 最大文件大小 | 10485760 |

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如果您遇到任何问题或有任何建议，请：

1. 查看 [Issues](https://github.com/your-repo/krinol/issues) 页面
2. 创建新的 Issue
3. 联系开发团队

## 🔄 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 实现基本的简历上传和分析功能
- 支持PDF、DOCX、TXT格式
- 集成OpenAI API进行智能分析
- 提供完整的用户管理功能
- 响应式前端界面

---

**注意**: 请确保在生产环境中使用强密码和安全的API密钥，并定期更新依赖包以保持安全性。
