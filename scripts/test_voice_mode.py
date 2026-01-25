#!/usr/bin/env python3
"""
Voice Mode E2E Test Script
测试语音模式 API 功能
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5001"

def test_health():
    """测试 API 健康状态"""
    print("\n=== 1. Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ API is healthy")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Is the server running?")
        return False

def test_register_and_login():
    """注册测试用户并登录"""
    print("\n=== 2. Register & Login ===")
    test_email = "voice_test@example.com"
    test_password = "test123456"
    
    # 尝试注册
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "display_name": "Voice Test User"
        },
        timeout=10
    )
    reg_data = register_response.json()
    
    if reg_data.get("status") == "success":
        print(f"✓ Registration successful: {reg_data.get('user_id')}")
        return reg_data.get("token"), reg_data.get("user_id")
    elif register_response.status_code == 409:  # Email 已存在
        print("  User already registered, attempting login...")
        # 尝试登录
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": test_email, "password": test_password},
            timeout=10
        )
        login_data = login_response.json()
        if login_data.get("status") == "success":
            print(f"✓ Login successful: {login_data.get('user_id')}")
            return login_data.get("token"), login_data.get("user_id")
        else:
            print(f"✗ Login failed: {login_data.get('message')}")
            return None, None
    else:
        print(f"✗ Registration failed: {reg_data.get('message')}")
        return None, None

def test_consult_text_mode(token):
    """测试文字模式 (voice_mode=False)"""
    print("\n=== 3. Consult Text Mode ===")
    response = requests.post(
        f"{BASE_URL}/api/chat/consult",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "今年我的事业运势如何？",
            "voice_mode": False
        },
        timeout=60
    )
    data = response.json()
    if data.get("status") == "success":
        reply = data.get("reply", "")
        print(f"✓ Text mode reply ({len(reply)} chars):")
        print(f"  {reply[:150]}...")
        print(f"  Citations: {len(data.get('citations', []))}")
        print(f"  Confidence: {data.get('confidence', 0):.1%}")
        return data.get("session_id")
    else:
        print(f"✗ Text mode failed: {data.get('error')}")
        return None

def test_consult_voice_mode(token, session_id=None):
    """测试语音模式 (voice_mode=True)"""
    print("\n=== 4. Consult Voice Mode ===")
    payload = {
        "message": "我的财运怎么样？",
        "voice_mode": True
    }
    if session_id:
        payload["session_id"] = session_id
    
    response = requests.post(
        f"{BASE_URL}/api/chat/consult",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=60
    )
    data = response.json()
    if data.get("status") == "success":
        reply = data.get("reply", "")
        print(f"✓ Voice mode reply ({len(reply)} chars):")
        print(f"  {reply[:200]}")
        print(f"  Citations: {len(data.get('citations', []))}")
        print(f"  Confidence: {data.get('confidence', 0):.1%}")
        
        # 检查语音模式特征 (应该更短、更口语化)
        if len(reply) <= 200:
            print(f"  ✓ Reply length suitable for voice ({len(reply)} chars)")
        else:
            print(f"  ! Reply may be too long for voice ({len(reply)} chars)")
        
        return True
    else:
        print(f"✗ Voice mode failed: {data.get('error')}")
        return False

def test_voice_mode_comparison(token):
    """比较语音和文字模式的回复差异"""
    print("\n=== 5. Mode Comparison ===")
    question = "我应该注意什么？"
    
    # Text mode
    text_response = requests.post(
        f"{BASE_URL}/api/chat/consult",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": question, "voice_mode": False},
        timeout=60
    ).json()
    
    # Voice mode
    voice_response = requests.post(
        f"{BASE_URL}/api/chat/consult",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": question, "voice_mode": True},
        timeout=60
    ).json()
    
    if text_response.get("status") == "success" and voice_response.get("status") == "success":
        text_len = len(text_response.get("reply", ""))
        voice_len = len(voice_response.get("reply", ""))
        print(f"  Text mode reply: {text_len} chars")
        print(f"  Voice mode reply: {voice_len} chars")
        
        if voice_len < text_len:
            print(f"  ✓ Voice mode reply is shorter (as expected)")
        else:
            print(f"  ! Voice mode reply is not shorter than text mode")
        
        return True
    else:
        print("✗ Comparison test failed")
        return False

def main():
    print("=" * 50)
    print("Voice Mode E2E Test")
    print("=" * 50)
    
    # 1. Health check
    if not test_health():
        print("\n请先启动 API 服务器: python run.py")
        sys.exit(1)
    
    # 2. Register & Login
    token, user_id = test_register_and_login()
    if not token:
        print("\n登录失败，无法继续测试")
        sys.exit(1)
    
    # 3. Text mode test
    session_id = test_consult_text_mode(token)
    
    # 4. Voice mode test
    test_consult_voice_mode(token, session_id)
    
    # 5. Mode comparison (optional, may take time)
    # test_voice_mode_comparison(token)
    
    print("\n" + "=" * 50)
    print("E2E Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
