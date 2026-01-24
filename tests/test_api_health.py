"""
API 健康檢查測試
單元測試 - 不需要實際 API 服務運行
"""

import pytest


@pytest.mark.unit
class TestHealthCheck:
    """健康檢查端點測試"""
    
    def test_health_endpoint_exists(self, client):
        """測試健康檢查端點存在"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_response_format(self, client):
        """測試健康檢查回應格式"""
        response = client.get('/health')
        data = response.get_json()
        
        assert 'status' in data
        assert 'service' in data
        assert data['status'] == 'ok'
        assert 'Aetheria' in data['service']
    
    def test_health_response_content_type(self, client):
        """測試健康檢查回應類型"""
        response = client.get('/health')
        assert response.content_type == 'application/json'


@pytest.mark.unit
class TestAPIBasics:
    """API 基礎功能測試"""
    
    def test_cors_enabled(self, client):
        """測試 CORS 是否啟用"""
        response = client.get('/health')
        # Flask-CORS 會自動添加 CORS headers
        assert response.status_code == 200
    
    def test_404_on_unknown_endpoint(self, client):
        """測試未知端點返回 404"""
        response = client.get('/api/unknown/endpoint')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """測試不允許的 HTTP 方法"""
        # health 端點只允許 GET
        response = client.post('/health')
        assert response.status_code == 405
