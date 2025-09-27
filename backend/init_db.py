#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal, create_tables
from app.services.invite_service import InviteService
from app.models.invite_models import InviteCodeCreate
from datetime import datetime, timedelta

async def init_database():
    """初始化数据库"""
    print("正在创建数据库表...")
    create_tables()
    print("数据库表创建完成！")
    
    # 创建初始邀请码
    print("正在创建初始邀请码...")
    db = SessionLocal()
    try:
        invite_service = InviteService(db)
        
        # 创建一个30天有效期的邀请码
        invite_code = await invite_service.generate_invite_code(
            created_by="system",
            expires_days=30
        )
        
        print(f"初始邀请码已创建: {invite_code}")
        print("请保存此邀请码，用于用户注册！")
        
    except Exception as e:
        print(f"创建邀请码时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(init_database())
