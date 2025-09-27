"""
用户相关服务
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from app.models.user_models import User, UserCreate, UserUpdate
from app.utils.password import get_password_hash, verify_password
from app.database import Base


class User(Base):
    """用户数据库模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user: UserCreate) -> User:
        """
        创建用户
        
        Args:
            user: 用户创建数据
            
        Returns:
            User: 创建的用户
        """
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=user.is_active
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 用户对象或None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            Optional[User]: 用户对象或None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据用户ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象或None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户身份
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[User]: 验证成功的用户或None
        """
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_update: 更新数据
            
        Returns:
            Optional[User]: 更新后的用户或None
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user