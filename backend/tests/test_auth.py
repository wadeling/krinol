"""
认证相关测试
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register():
    """测试用户注册"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]


def test_register_duplicate_email():
    """测试重复邮箱注册"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser2",
        "full_name": "Test User 2",
        "password": "testpassword123"
    }
    
    # 第一次注册
    client.post("/auth/register", json=user_data)
    
    # 第二次注册相同邮箱
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400


def test_login():
    """测试用户登录"""
    # 先注册用户
    user_data = {
        "email": "login@example.com",
        "username": "loginuser",
        "full_name": "Login User",
        "password": "loginpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    # 登录
    login_data = {
        "username": "login@example.com",
        "password": "loginpassword123"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """测试无效凭据登录"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 401


def test_get_current_user():
    """测试获取当前用户信息"""
    # 先注册并登录
    user_data = {
        "email": "current@example.com",
        "username": "currentuser",
        "full_name": "Current User",
        "password": "currentpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "current@example.com",
        "password": "currentpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # 获取当前用户信息
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
