"""
用户服务模块
处理用户相关的业务逻辑
"""

import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta

from ..models.user_models import User, UserCreate, UserUpdate, UserResponse
from ..utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """用户管理服务"""
    
    def __init__(self):
        # 这里应该初始化数据库连接
        # 为了演示，使用内存存储
        self._users: dict = {}
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        创建用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            UserResponse: 用户响应数据
        """
        try:
            # 检查用户是否已存在
            if await self.get_user_by_email(user_data.email):
                raise ValueError("用户邮箱已存在")
            
            # 生成用户ID
            user_id = secrets.token_urlsafe(16)
            
            # 加密密码
            hashed_password = self._hash_password(user_data.password)
            
            # 创建用户对象
            user = User(
                id=user_id,
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存用户（实际应该保存到数据库）
            self._users[user_id] = user
            
            logger.info(f"用户创建成功: {user_data.email}")
            
            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
        except Exception as e:
            logger.error(f"用户创建失败: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserResponse: 用户数据，如果不存在返回None
        """
        user = self._users.get(user_id)
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        根据邮箱获取用户
        
        Args:
            email: 用户邮箱
            
        Returns:
            UserResponse: 用户数据，如果不存在返回None
        """
        for user in self._users.values():
            if user.email == email:
                return UserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
        return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 更新数据
            
        Returns:
            UserResponse: 更新后的用户数据，如果用户不存在返回None
        """
        user = self._users.get(user_id)
        if not user:
            return None
        
        try:
            # 更新用户信息
            if user_data.username is not None:
                user.username = user_data.username
            if user_data.full_name is not None:
                user.full_name = user_data.full_name
            if user_data.password is not None:
                user.hashed_password = self._hash_password(user_data.password)
            
            user.updated_at = datetime.now()
            
            logger.info(f"用户信息更新成功: {user_id}")
            
            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
        except Exception as e:
            logger.error(f"用户信息更新失败: {str(e)}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        if user_id not in self._users:
            return False
        
        try:
            del self._users[user_id]
            logger.info(f"用户删除成功: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"用户删除失败: {str(e)}")
            return False
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        """
        用户认证
        
        Args:
            email: 用户邮箱
            password: 密码
            
        Returns:
            UserResponse: 认证成功的用户数据，认证失败返回None
        """
        user = None
        for u in self._users.values():
            if u.email == email:
                user = u
                break
        
        if not user or not self._verify_password(password, user.hashed_password):
            return None
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def _hash_password(self, password: str) -> str:
        """加密密码"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{pwd_hash.hex()}"
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            salt, stored_hash = hashed_password.split(':')
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return pwd_hash.hex() == stored_hash
        except ValueError:
            return False
