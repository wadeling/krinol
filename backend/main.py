"""
简历分析系统主入口
使用FastAPI构建的RESTful API服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config.settings import get_settings
from app.routes import auth_router, resume_router, analysis_router
from app.utils.logger import setup_logging, get_logger

# 获取配置
settings = get_settings()

# 设置日志
setup_logging(level=settings.log_level, log_file=settings.log_file)
logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于大模型的智能简历分析系统",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(analysis_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用简历分析系统API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "服务运行正常"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )


if __name__ == "__main__":
    logger.info(f"启动{settings.app_name} v{settings.app_version}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
