"""
认证工具模块
处理JWT令牌的创建和验证
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..config.settings import get_settings
from ..models.user_models import UserResponse
from ..services.user_service import UserService
from ..utils.logger import get_logger

logger = get_logger(__name__)

settings = get_settings()
user_service = UserService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# JWT配置
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    验证令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        dict: 解码后的数据，如果无效返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    获取当前用户（依赖注入）
    
    Args:
        token: JWT令牌
        
    Returns:
        UserResponse: 当前用户信息
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        user = await user_service.get_user_by_id(user_id)
        if user is None:
            raise credentials_exception
        
        return user
        
    except Exception as e:
        logger.error(f"用户认证失败: {str(e)}")
        raise credentials_exception
