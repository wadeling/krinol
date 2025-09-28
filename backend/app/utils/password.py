"""
密码处理工具函数
"""

import bcrypt
import hashlib


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码
        
    Returns:
        bool: 密码是否正确
    """
    try:
        # 使用bcrypt直接验证
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 加密后的密码
    """
    # 如果密码超过72字节，先进行SHA256哈希
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # 使用SHA256哈希长密码
        password_hash = hashlib.sha256(password_bytes).hexdigest()
        password = password_hash
    
    # 使用bcrypt加密
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
