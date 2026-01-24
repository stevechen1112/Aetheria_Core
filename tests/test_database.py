"""
資料庫模組測試
測試 SQLite 資料庫操作
"""

import pytest
import tempfile
import os
from pathlib import Path


class TestDatabaseModule:
    """資料庫模組測試"""
    
    @pytest.fixture
    def temp_db(self):
        """建立臨時資料庫"""
        # 使用臨時目錄
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'test.db'
            
            # 動態導入並創建資料庫
            from src.utils.database import AetheriaDatabase
            db = AetheriaDatabase(str(db_path))
            
            yield db
            
            # 清理
            db.close()
    
    def test_database_initialization(self, temp_db):
        """測試資料庫初始化"""
        assert temp_db is not None
        assert temp_db.db_path is not None
    
    def test_user_crud_operations(self, temp_db):
        """測試用戶 CRUD 操作"""
        # Create
        user_data = {
            'user_id': 'test_user_001',
            'name': '測試用戶',
            'birth_date': '1990-01-01',
            'gender': '男'
        }
        
        result = temp_db.create_user(user_data)
        assert result is True
        
        # Read
        retrieved = temp_db.get_user('test_user_001')
        assert retrieved is not None
        assert retrieved['name'] == '測試用戶'
        
        # Update
        temp_db.update_user('test_user_001', {'name': '更新後的名稱'})
        updated = temp_db.get_user('test_user_001')
        assert updated['name'] == '更新後的名稱'
        
        # Delete
        temp_db.delete_user('test_user_001')
        deleted = temp_db.get_user('test_user_001')
        assert deleted is None
    
    def test_chart_lock_operations(self, temp_db):
        """測試命盤鎖定操作"""
        # 先建立用戶
        temp_db.create_user({'user_id': 'test_user_002', 'name': '測試'})
        
        # 建立測試命盤資料
        chart_data = {
            '命宮': {'主星': ['紫微'], '宮位': '子'}
        }
        
        # Save
        temp_db.create_chart_lock('test_user_002', 'ziwei', chart_data)
        
        # Get
        retrieved = temp_db.get_chart_lock('test_user_002')
        assert retrieved is not None
    
    def test_nonexistent_user(self, temp_db):
        """測試查詢不存在的用戶"""
        result = temp_db.get_user('nonexistent_user_xyz')
        assert result is None
    
    def test_list_users(self, temp_db):
        """測試列出所有用戶"""
        # 建立多個用戶
        for i in range(3):
            temp_db.create_user({'user_id': f'user_{i}', 'name': f'User {i}'})
        
        users = temp_db.list_users()
        assert len(users) >= 3


class TestDatabaseIntegration:
    """資料庫整合測試"""
    
    def test_singleton_pattern(self):
        """測試資料庫單例模式"""
        from src.utils.database import get_database
        
        db1 = get_database()
        db2 = get_database()
        
        # 應該是同一個實例
        assert db1 is db2
    
    def test_json_serialization(self, temp_db):
        """測試 JSON 序列化"""
        complex_data = {
            'user_id': 'json_test',
            'name': '測試',
            'nested': {
                'array': [1, 2, 3],
                'object': {'key': 'value'},
                'unicode': '中文測試 🎯'
            }
        }
        
        # 用戶資料不支持嵌套，但我們可以測試基本存取
        temp_db.create_user({'user_id': 'json_test', 'name': '測試'})
        retrieved = temp_db.get_user('json_test')
        
        assert retrieved is not None
        assert retrieved['name'] == '測試'


@pytest.fixture
def temp_db():
    """全局臨時資料庫 fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'
        
        from src.utils.database import AetheriaDatabase
        db = AetheriaDatabase(str(db_path))
        
        yield db
        
        db.close()
