"""
用户相关数据模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    is_active: bool = Field(default=True, description="是否激活")


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str = Field(..., min_length=6, description="密码")


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    invite_code: str = Field(..., description="邀请码")


class UserRegisterWithInvite(BaseModel):
    """使用邀请码注册请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    invite_code: str = Field(..., description="邀请码")


class InviteCodeValidate(BaseModel):
    """邀请码验证请求模型"""
    invite_code: str = Field(..., description="邀请码")


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = Field(None, description="用户名")


class User(UserBase):
    """用户模型（用于内部使用）"""
    id: int = Field(..., description="用户ID")
    hashed_password: str = Field(..., description="加密后的密码")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")