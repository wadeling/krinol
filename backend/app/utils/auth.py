"""
认证相关工具函数
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.models.user_models import TokenData
from app.database import get_db

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# JWT配置
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes




def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间差
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Optional[dict]: 解码后的数据，如果无效则返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI依赖函数：获取当前用户
    """
    from ..utils.logger import get_logger
    logger = get_logger(__name__)
    
    logger.info(f"开始验证用户身份，token: {token[:20] if token else 'None'}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.info(f"JWT解析成功，用户名: {username}")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError as e:
        logger.error(f"JWT解析失败: {str(e)}")
        raise credentials_exception
    
    # 直接查询用户，避免循环导入
    from app.services.user_service import User as UserModel
    logger.info(f"开始查询用户: {username}")
    user = db.query(UserModel).filter(UserModel.username == token_data.username).first()
    if user is None:
        logger.error(f"用户不存在: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    logger.info(f"用户验证成功: {user.username}")
    return user