"""
用户相关数据模型
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, description="全名")


class User(UserBase):
    """用户模型（用于内部使用）"""
    id: str = Field(..., description="用户ID")
    hashed_password: str = Field(..., description="加密后的密码")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, description="密码")


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    """用户响应模型"""
    id: str = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """令牌模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[str] = None
    username: Optional[str] = None
