"""
路由模块
定义API路由和端点
"""

from .auth_routes import router as auth_router
from .resume_routes import router as resume_router
from .analysis_routes import router as analysis_router

__all__ = [
    "auth_router",
    "resume_router", 
    "analysis_router"
]
