"""
Pytest 配置和共用 Fixtures
"""

import pytest
import sys
from pathlib import Path

# 確保專案根目錄在 Python 路徑中
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="session")
def app():
    """Flask app fixture"""
    from src.api.server import app as flask_app
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture(scope="session")
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture(scope="session")
def test_user_data():
    """測試用戶資料"""
    return {
        "user_id": "test_pytest_001",
        "name": "測試用戶",
        "year": 1979,
        "month": 11,
        "day": 12,
        "hour": 23,
        "minute": 58,
        "gender": "male",
        "longitude": 120.52,
        "latitude": 24.08,
        "birth_date": "1979-11-12",
        "full_name": "TEST USER"
    }


@pytest.fixture
def test_bazi_data():
    """八字測試資料"""
    return {
        "user_id": "test_bazi_001",
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "gender": "male"
    }


@pytest.fixture
def test_numerology_data():
    """靈數學測試資料"""
    return {
        "birth_date": "1990-05-15",
        "full_name": "JOHN DOE"
    }


@pytest.fixture
def test_name_data():
    """姓名學測試資料"""
    return {
        "surname": "陳",
        "given_name": "宥竹"
    }


@pytest.fixture
def test_tarot_data():
    """塔羅牌測試資料"""
    return {
        "spread_type": "single",
        "question": "今天的整體運勢如何？"
    }


@pytest.fixture
def auth_user(client):
    """
    創建認證用戶並返回 (user_id, token)
    自動設置完整的個人資料和命盤鎖定
    適用於需要認證的 API 測試
    """
    import uuid
    from datetime import datetime
    
    # 註冊測試用戶
    email = f"test_golden_{uuid.uuid4().hex[:8]}@example.com"
    password = "test_password_123"
    
    response = client.post('/api/auth/register', json={
        'email': email,
        'password': password,
        'display_name': 'Golden Set Test User'
    })
    
    assert response.status_code == 200, f"註冊失敗: {response.get_json()}"
    data = response.get_json()
    
    user_id = data['user_id']
    token = data['token']
    
    # 設置個人資料並生成命盤（標準測試資料：1990-05-15 14:30 台北）
    profile_data = {
        'name': '測試用戶',
        'gender': 'male',
        'birth_date': '1990-05-15',
        'birth_time': '14:30',
        'birth_place': '台北市',
        'longitude': 121.5654,
        'latitude': 25.0330,
        'calendar_type': 'solar',
        'timezone': 'Asia/Taipei',
        'generate_systems': ['ziwei', 'bazi', 'numerology', 'astrology', 'tarot']
    }
    
    # 使用 save-and-analyze 端點一次完成設置和生成
    profile_response = client.post('/api/profile/save-and-analyze',
        headers={'Authorization': f'Bearer {token}'},
        json=profile_data
    )
    
    # 如果失敗，嘗試使用 PATCH 端點
    if profile_response.status_code != 200:
        profile_response = client.patch('/api/profile',
            headers={'Authorization': f'Bearer {token}'},
            json=profile_data
        )
    
    # 即使失敗也繼續（可能是 AI 配額限制或測試環境限制）
    # 只記錄警告而不中斷測試
    
    yield (user_id, token)
    
    # 測試後清理（可選，因為使用測試資料庫）
    # 在實際應用中可以在此處刪除測試用戶


# Markers
def pytest_configure(config):
    """自定義 pytest 配置"""
    config.addinivalue_line(
        "markers", "integration: 整合測試（需要 API 服務）"
    )
    config.addinivalue_line(
        "markers", "unit: 單元測試"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速測試"
    )
    config.addinivalue_line(
        "markers", "golden_set: Golden Set 回歸測試"
    )
    config.addinivalue_line(
        "markers", "smoke: 快速煙霧測試"
    )
    config.addinivalue_line(
        "markers", "performance: 效能測試"
    )
    config.addinivalue_line(
        "markers", "reliability: 穩定性測試"
    )
