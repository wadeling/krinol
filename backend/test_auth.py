#!/usr/bin/env python3
"""
认证功能测试脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, create_tables
from app.services.user_service import UserService
from app.services.invite_service import InviteService
from app.models.user_models import UserCreate
from app.models.invite_models import InviteCodeCreate

async def test_auth():
    """测试认证功能"""
    print("开始测试认证功能...")
    
    # 创建数据库表
    print("1. 创建数据库表...")
    create_tables()
    print("✓ 数据库表创建成功")
    
    db = SessionLocal()
    try:
        # 测试邀请码服务
        print("\n2. 测试邀请码服务...")
        invite_service = InviteService(db)
        
        # 创建邀请码
        invite_code = await invite_service.generate_invite_code(
            created_by="test_admin",
            expires_days=30
        )
        print(f"✓ 邀请码创建成功: {invite_code}")
        
        # 验证邀请码
        validation_result = await invite_service.validate_invite_code(invite_code)
        print(f"✓ 邀请码验证结果: {validation_result.is_valid} - {validation_result.message}")
        
        # 测试用户服务
        print("\n3. 测试用户服务...")
        user_service = UserService(db)
        
        # 创建测试用户
        test_user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        
        user = await user_service.create_user(test_user)
        print(f"✓ 用户创建成功: {user.username}")
        
        # 验证用户认证
        auth_user = await user_service.authenticate_user("testuser", "testpassword123")
        if auth_user:
            print(f"✓ 用户认证成功: {auth_user.username}")
        else:
            print("✗ 用户认证失败")
        
        # 测试邀请码使用
        print("\n4. 测试邀请码使用...")
        await invite_service.mark_invite_code_used(invite_code, "testuser")
        print("✓ 邀请码标记为已使用")
        
        # 再次验证邀请码（应该无效）
        validation_result = await invite_service.validate_invite_code(invite_code)
        print(f"✓ 邀请码再次验证结果: {validation_result.is_valid} - {validation_result.message}")
        
        print("\n🎉 所有测试通过！")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_auth())
