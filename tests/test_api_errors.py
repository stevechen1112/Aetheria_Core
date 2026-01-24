"""
API 錯誤處理測試
測試新的統一錯誤處理機制
"""

import pytest
import json


@pytest.mark.unit
class TestErrorHandling:
    """錯誤處理機制測試"""
    
    def test_missing_user_id_on_initial_analysis(self, client):
        """測試初始分析缺少 user_id 參數"""
        response = client.post(
            '/api/chart/initial-analysis',
            json={
                'birth_date': '1990-01-01',
                'birth_time': '12:00',
                'birth_location': '台北市',
                'gender': '男'
                # 缺少 user_id
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        # 新的錯誤格式使用 message 或 error
        assert 'message' in data or 'error' in data
        error_msg = data.get('message', data.get('error', ''))
        assert 'user_id' in error_msg.lower() or data.get('details', {}).get('parameter') == 'user_id'
    
    def test_missing_user_id_on_confirm_lock(self, client):
        """測試確認鎖盤缺少 user_id 參數"""
        response = client.post(
            '/api/chart/confirm-lock',
            json={}  # 空請求
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data or 'error' in data
    
    def test_missing_user_id_on_get_lock(self, client):
        """測試查詢鎖盤缺少 user_id 參數"""
        response = client.get('/api/chart/get-lock')
        # 沒有提供 user_id 查詢參數
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data or 'error' in data
    
    def test_missing_message_on_chat(self, client):
        """測試對話缺少 message 參數"""
        response = client.post(
            '/api/chat/message',
            json={'user_id': 'test_user'}  # 缺少 message
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data or 'error' in data
    
    def test_chart_not_locked_on_chat(self, client):
        """測試未鎖盤用戶進行對話"""
        response = client.post(
            '/api/chat/message',
            json={
                'user_id': 'nonexistent_user_12345',
                'message': '測試訊息'
            }
        )
        
        # 應該返回錯誤（400 或 404）
        assert response.status_code in [400, 404]
        data = response.get_json()
        assert 'message' in data or 'error' in data


@pytest.mark.unit
class TestInputValidation:
    """輸入驗證測試"""
    
    def test_invalid_json_body(self, client):
        """測試無效的 JSON 請求體"""
        response = client.post(
            '/api/chart/initial-analysis',
            data='not valid json',
            content_type='application/json'
        )
        
        # Flask 會返回 400 Bad Request
        assert response.status_code in [400, 500]
    
    def test_empty_json_body(self, client):
        """測試空的 JSON 請求體"""
        response = client.post(
            '/api/chart/initial-analysis',
            json={}
        )
        
        assert response.status_code == 400
    
    def test_missing_required_fields(self, client):
        """測試缺少必要欄位"""
        response = client.post(
            '/api/chart/initial-analysis',
            json={
                'user_id': 'test_user'
                # 缺少 birth_date, birth_time, birth_location, gender
            }
        )
        
        # 應該返回錯誤
        assert response.status_code in [400, 500]


@pytest.mark.unit
class TestSynastryValidation:
    """合盤端點驗證測試"""
    
    def test_missing_user_a_id(self, client):
        """測試婚配合盤缺少 user_a_id"""
        response = client.post(
            '/api/synastry/marriage',
            json={'user_b_id': 'user_b'}
        )
        
        assert response.status_code == 400
    
    def test_missing_user_b_id(self, client):
        """測試婚配合盤缺少 user_b_id"""
        response = client.post(
            '/api/synastry/marriage',
            json={'user_a_id': 'user_a'}
        )
        
        assert response.status_code == 400
    
    def test_both_users_missing(self, client):
        """測試合盤兩個用戶 ID 都缺少"""
        response = client.post(
            '/api/synastry/partnership',
            json={}
        )
        
        assert response.status_code == 400


@pytest.mark.unit  
class TestFortuneValidation:
    """流年端點驗證測試"""
    
    def test_fortune_annual_missing_user_id(self, client):
        """測試流年分析缺少 user_id"""
        response = client.post(
            '/api/fortune/annual',
            json={'target_year': 2026}
        )
        
        assert response.status_code == 400
    
    def test_fortune_monthly_missing_user_id(self, client):
        """測試流月分析缺少 user_id"""
        response = client.post(
            '/api/fortune/monthly',
            json={'target_year': 2026, 'target_month': 1}
        )
        
        assert response.status_code == 400
    
    def test_fortune_question_missing_fields(self, client):
        """測試流年問題分析缺少欄位"""
        response = client.post(
            '/api/fortune/question',
            json={'user_id': 'test_user'}  # 缺少 question
        )
        
        assert response.status_code == 400
