"""
测试配置和固件
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """测试客户端固件"""
    return TestClient(app)


@pytest.fixture
def temp_upload_dir():
    """临时上传目录固件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_resume_data():
    """示例简历数据固件"""
    return {
        "filename": "sample_resume.pdf",
        "format": "pdf",
        "content": "这是一个示例简历内容...",
        "file_size": 1024
    }


@pytest.fixture
def sample_user_data():
    """示例用户数据固件"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }
