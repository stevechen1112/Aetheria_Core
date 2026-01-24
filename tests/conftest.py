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
