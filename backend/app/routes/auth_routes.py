"""
认证相关路由
处理用户注册、登录、令牌验证等
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional

from ..models.user_models import UserCreate, UserResponse, Token, UserLogin
from ..services.user_service import UserService
from ..utils.auth import create_access_token, get_current_user
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])
user_service = UserService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    用户注册
    
    Args:
        user_data: 用户注册数据
        
    Returns:
        UserResponse: 注册成功的用户信息
    """
    try:
        user = await user_service.create_user(user_data)
        logger.info(f"用户注册成功: {user.email}")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        raise HTTPException(status_code=500, detail="注册失败")


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录
    
    Args:
        form_data: 登录表单数据
        
    Returns:
        Token: 访问令牌
    """
    try:
        user = await user_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.id, "username": user.username})
        logger.info(f"用户登录成功: {user.email}")
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="登录失败")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户（通过依赖注入获取）
        
    Returns:
        UserResponse: 当前用户信息
    """
    return current_user


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    用户登出
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 登出成功消息
    """
    logger.info(f"用户登出: {current_user.email}")
    return {"message": "登出成功"}
