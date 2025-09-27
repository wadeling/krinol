"""
邀请码相关数据模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class InviteCode(Base):
    """邀请码数据库模型"""
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    created_by = Column(String(100), nullable=False)  # 创建者
    is_used = Column(Boolean, default=False, nullable=False)
    used_by = Column(String(100), nullable=True)  # 使用者
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # 过期时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    description = Column(Text, nullable=True)  # 描述


class InviteCodeBase(BaseModel):
    """邀请码基础模型"""
    code: str = Field(..., description="邀请码")
    created_by: str = Field(..., description="创建者")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    description: Optional[str] = Field(None, description="描述")


class InviteCodeCreate(InviteCodeBase):
    """创建邀请码请求模型"""
    pass


class InviteCodeResponse(InviteCodeBase):
    """邀请码响应模型"""
    id: int
    is_used: bool
    used_by: Optional[str] = None
    used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InviteCodeValidate(BaseModel):
    """邀请码验证请求模型"""
    code: str = Field(..., description="邀请码")


class InviteCodeValidateResponse(BaseModel):
    """邀请码验证响应模型"""
    is_valid: bool = Field(..., description="是否有效")
    message: str = Field(..., description="验证消息")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
