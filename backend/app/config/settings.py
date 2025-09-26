"""
应用配置模块
使用Pydantic管理配置
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本配置
    app_name: str = Field(default="简历分析系统", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    
    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./resume_analysis.db",
        description="数据库连接URL"
    )
    
    # JWT配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT密钥"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="访问令牌过期时间（分钟）"
    )
    
    # OpenAI配置
    openai_api_key: str = Field(
        default="",
        description="OpenAI API密钥"
    )
    openai_model: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI模型名称"
    )
    
    # 文件上传配置
    upload_dir: str = Field(
        default="uploads",
        description="文件上传目录"
    )
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="最大文件大小（字节）"
    )
    allowed_file_types: list = Field(
        default=["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"],
        description="允许的文件类型"
    )
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    
    # CORS配置
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="允许的CORS源"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    获取配置实例（单例模式）
    
    Returns:
        Settings: 配置实例
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
