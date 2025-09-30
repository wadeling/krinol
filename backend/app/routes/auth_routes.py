"""
认证相关路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt import PyJWTError

from app.models.user_models import (
    UserCreate, UserLogin, UserRegister, UserRegisterWithInvite,
    Token, TokenData, UserResponse, InviteCodeValidate
)
from app.services.user_service import User
from app.models.invite_models import InviteCode, InviteCodeValidateResponse
from app.services.user_service import UserService
from app.services.invite_service import InviteService
from app.utils.auth import create_access_token
from app.utils.password import verify_password, get_password_hash
from app.config.settings import get_settings
from app.database import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
settings = get_settings()


async def get_current_user_dependency(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI依赖函数：获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/validate-invite", response_model=InviteCodeValidateResponse)
async def validate_invite_code(
    invite_data: InviteCodeValidate,
    db: Session = Depends(get_db)
):
    """
    验证邀请码
    """
    logger.info(f"验证邀请码: {invite_data.invite_code}")
    invite_service = InviteService(db)
    result = await invite_service.validate_invite_code(invite_data.invite_code)
    return result


@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegisterWithInvite,
    db: Session = Depends(get_db)
):
    """
    用户注册（需要邀请码）
    """
    # 验证邀请码
    invite_service = InviteService(db)
    invite_result = await invite_service.validate_invite_code(user_data.invite_code)
    
    if not invite_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=invite_result.message
        )
    
    # 检查用户名和邮箱是否已存在
    user_service = UserService(db)
    
    # 检查用户名
    existing_user = await user_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱
    existing_email = await user_service.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    user_create = UserCreate(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    user = await user_service.create_user(user_create)
    
    # 标记邀请码为已使用
    await invite_service.mark_invite_code_used(user_data.invite_code, user.username)
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录
    """
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user_dependency)):
    """
    获取当前用户信息
    """
    return UserResponse.from_orm(current_user)

