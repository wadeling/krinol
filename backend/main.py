from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config.settings import get_settings
from app.routes import auth_routes, resume_routes, analysis_routes
from app.database import create_tables
from app.utils.logger import get_logger, setup_logging

# 获取配置
settings = get_settings()

# 初始化日志配置
setup_logging(level=settings.log_level, log_file=settings.log_file)
logger = get_logger(__name__)
logger.info("应用启动中...")

# 定义lifespan事件处理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    create_tables()
    yield
    # 关闭时执行（如果需要的话）

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于大模型的简历分析系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加GZip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 注册路由
app.include_router(auth_routes.router)
app.include_router(resume_routes.router)
app.include_router(analysis_routes.router)
logger.info("路由注册完成")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用Krinol AI Dashboard",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )