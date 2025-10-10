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
        default="mysql+pymysql://root:password@localhost:3306/krinol_db",
        description="数据库连接URL"
    )
    
    # MySQL配置
    mysql_host: str = Field(default="localhost", description="MySQL主机")
    mysql_port: int = Field(default=3306, description="MySQL端口")
    mysql_user: str = Field(default="root", description="MySQL用户名")
    mysql_password: str = Field(default="password", description="MySQL密码")
    mysql_database: str = Field(default="krinol_db", description="MySQL数据库名")
    
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
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API基础地址"
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
    max_batch_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        description="批量上传最大总大小（字节）"
    )
    max_batch_files: int = Field(
        default=20,
        description="批量上传最大文件数量"
    )
    allowed_file_types: str = Field(
        default="application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain",
        description="允许的文件类型，用逗号分隔"
    )
    
    @property
    def allowed_file_types_list(self) -> list:
        """将逗号分隔的字符串转换为列表"""
        return [file_type.strip() for file_type in self.allowed_file_types.split(",")]
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    
    # CORS配置
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080,http://localhost,http://localhost:80",
        description="允许的CORS源，用逗号分隔"
    )
    
    @property
    def cors_origins_list(self) -> list:
        """将逗号分隔的字符串转换为列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
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
