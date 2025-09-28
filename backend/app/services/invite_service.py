"""
邀请码相关服务
"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from app.models.invite_models import InviteCode, InviteCodeCreate, InviteCodeValidateResponse
from app.database import Base
from app.utils.logger import get_logger

logger = get_logger(__name__)


class InviteCode(Base):
    """邀请码数据库模型"""
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    created_by = Column(String(100), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_by = Column(String(100), nullable=True)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    description = Column(Text, nullable=True)


class InviteService:
    """邀请码服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_invite_code(self, invite_data: InviteCodeCreate) -> InviteCode:
        """
        创建邀请码
        
        Args:
            invite_data: 邀请码创建数据
            
        Returns:
            InviteCode: 创建的邀请码
        """
        db_invite = InviteCode(
            code=invite_data.code,
            created_by=invite_data.created_by,
            expires_at=invite_data.expires_at,
            description=invite_data.description
        )
        self.db.add(db_invite)
        self.db.commit()
        self.db.refresh(db_invite)
        return db_invite
    
    async def get_invite_code(self, code: str) -> Optional[InviteCode]:
        """
        根据邀请码获取邀请码对象
        
        Args:
            code: 邀请码
            
        Returns:
            Optional[InviteCode]: 邀请码对象或None
        """
        return self.db.query(InviteCode).filter(InviteCode.code == code).first()
    
    async def validate_invite_code(self, code: str) -> InviteCodeValidateResponse:
        """
        验证邀请码
        
        Args:
            code: 邀请码
            
        Returns:
            InviteCodeValidateResponse: 验证结果
        """
        invite_code = await self.get_invite_code(code)
        logger.info(f"邀请码: {invite_code}")
        
        if not invite_code:
            return InviteCodeValidateResponse(
                is_valid=False,
                message="邀请码不存在"
            )
        
        if invite_code.is_used:
            return InviteCodeValidateResponse(
                is_valid=False,
                message="邀请码已被使用"
            )
        
        if invite_code.expires_at and invite_code.expires_at < datetime.utcnow():
            return InviteCodeValidateResponse(
                is_valid=False,
                message="邀请码已过期"
            )
        
        return InviteCodeValidateResponse(
            is_valid=True,
            message="邀请码有效",
            expires_at=invite_code.expires_at
        )
    
    async def mark_invite_code_used(self, code: str, used_by: str) -> bool:
        """
        标记邀请码为已使用
        
        Args:
            code: 邀请码
            used_by: 使用者
            
        Returns:
            bool: 是否成功标记
        """
        invite_code = await self.get_invite_code(code)
        if not invite_code:
            return False
        
        invite_code.is_used = True
        invite_code.used_by = used_by
        invite_code.used_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    async def generate_invite_code(self, created_by: str, expires_days: int = 30) -> str:
        """
        生成邀请码
        
        Args:
            created_by: 创建者
            expires_days: 过期天数
            
        Returns:
            str: 生成的邀请码
        """
        import secrets
        import string
        
        # 生成8位随机邀请码
        alphabet = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(8))
        
        # 确保邀请码唯一
        while await self.get_invite_code(code):
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
        
        # 设置过期时间
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        # 创建邀请码
        invite_data = InviteCodeCreate(
            code=code,
            created_by=created_by,
            expires_at=expires_at,
            description=f"由 {created_by} 创建，有效期 {expires_days} 天"
        )
        
        await self.create_invite_code(invite_data)
        return code
