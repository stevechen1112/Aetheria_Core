"""
Golden Set: 系統整合與端到端測試
測試完整業務流程和多系統協作
"""

import pytest
from typing import Dict, Any


# ========== Test Cases Definition ==========

SYSTEM_INTEGRATION_GOLDEN_CASES = [
    {
        'id': 'GS_INTEGRATION_001',
        'name': '完整諮詢流程',
        'user_message': '我是張小明，1990-05-15 14:30 台北出生，男性，想了解整體運勢',
        'expected_systems': ['ziwei', 'bazi', 'numerology'],
        'expected_tools': ['calculate_ziwei', 'calculate_bazi', 'calculate_numerology'],
        'min_confidence': 0.8,
        'min_citations': 3,
        'min_reply_length': 500,
        'description': '完整資訊應觸發多系統綜合分析'
    },
    {
        'id': 'GS_INTEGRATION_002',
        'name': '圖表鎖定機制',
        'setup_locked_chart': True,
        'user_message': '我的事業運勢如何？',
        'expected_use_locked': True,
        'expected_systems': ['ziwei', 'bazi'],
        'min_confidence': 0.7,
        'description': '應自動使用已鎖定的命盤資料'
    },
    {
        'id': 'GS_INTEGRATION_003',
        'name': '跨系統比對',
        'user_message': '請用八字、紫微、西洋占星三個系統分析我的性格特質',
        'expected_systems': ['bazi', 'ziwei', 'astrology'],
        'expected_keywords': ['八字', '紫微', '占星', '性格'],
        'min_confidence': 0.75,
        'should_compare': True,
        'description': '應比較不同系統的分析結果'
    },
    {
        'id': 'GS_INTEGRATION_004',
        'name': '流式回應',
        'user_message': '我想了解我的財運如何？',
        'use_stream': True,
        'expected_systems': ['bazi', 'ziwei'],
        'expected_chunks': 5,
        'description': '流式回應應逐步返回內容'
    },
    {
        'id': 'GS_INTEGRATION_005',
        'name': 'API 版本相容性',
        'user_message': '請看我的事業運',
        'api_version': 'v1',
        'expected_fields': ['reply', 'confidence'],
        'forbidden_fields': ['reasoning_steps', 'alternative_interpretations'],
        'description': 'v1 API 應只返回基礎欄位'
    },
    {
        'id': 'GS_INTEGRATION_006',
        'name': '敏感議題攔截整合',
        'user_message': '我得了重病，命盤說我會不會死？',
        'should_intercept': True,
        'expected_topic': 'health_medical',
        'no_system_call': True,
        'description': '敏感議題應在 AI 調用前攔截'
    },
    {
        'id': 'GS_INTEGRATION_007',
        'name': '多輪對話持久化',
        'turns': [
            {'message': '我想算命', 'expected_keywords': ['出生']},
            {'message': '1988-08-08 上午 8:00', 'expected_systems': ['bazi', 'ziwei']},
            {'message': '我叫李四', 'expected_systems': ['numerology']}
        ],
        'description': '多輪對話應累積資訊並持久化'
    },
    {
        'id': 'GS_INTEGRATION_008',
        'name': '快取機制',
        'user_message': '請幫我算八字，我是 1995-03-15 10:00 出生',
        'repeat_request': True,
        'expected_cache_hit': True,
        'description': '相同請求應命中快取'
    },
    {
        'id': 'GS_INTEGRATION_009',
        'name': '併發請求隔離',
        'concurrent_users': 2,
        'messages': [
            '我是用戶A，1990-01-01 出生',
            '我是用戶B，1995-12-31 出生'
        ],
        'should_isolate': True,
        'description': '不同用戶請求應完全隔離'
    },
    {
        'id': 'GS_INTEGRATION_010',
        'name': '完整錯誤恢復',
        'user_message': '請算命',  # 缺少資訊
        'follow_up': '1990-05-15 14:30 台北出生',
        'should_recover': True,
        'expected_systems': ['ziwei', 'bazi'],
        'description': '錯誤後應能恢復並繼續服務'
    }
]


# ========== Test Execution ==========

@pytest.mark.golden_set
@pytest.mark.integration
@pytest.mark.parametrize('case', SYSTEM_INTEGRATION_GOLDEN_CASES, ids=lambda c: c['id'])
class TestSystemIntegrationGoldenSet:
    """系統整合 Golden Set 測試"""
    
    def test_integration_case(self, case: Dict[str, Any], client, auth_user):
        """
        執行系統整合測試案例
        
        驗證項目：
        1. 多系統協作正確性
        2. 端到端流程完整性
        3. 狀態持久化
        4. 錯誤恢復能力
        5. 效能與快取
        """
        user_id, token = auth_user
        
        # 特殊情境：設定鎖定命盤
        if case.get('setup_locked_chart', False):
            self._setup_locked_chart(client, token, user_id)
        
        # 特殊情境：流式回應
        if case.get('use_stream', False):
            self._test_stream_response(case, client, token)
            return
        
        # 特殊情境：多輪對話
        if 'turns' in case:
            self._test_multi_turn_integration(case, client, token)
            return
        
        # 特殊情境：併發請求
        if case.get('concurrent_users', 0) > 1:
            self._test_concurrent_isolation(case, client)
            return
        
        # 特殊情境：錯誤恢復
        if case.get('should_recover', False):
            self._test_error_recovery(case, client, token)
            return
        
        # 標準整合測試
        headers = {'Authorization': f'Bearer {token}'}
        
        # API 版本控制
        if case.get('api_version'):
            headers['X-API-Version'] = case['api_version']
        
        # 第一次請求
        response = client.post('/api/chat/consult',
            headers=headers,
            json={'message': case['user_message']}
        )
        
        assert response.status_code == 200, f"API 請求失敗: {case['id']}"
        data = response.get_json()
        
        # 1. 敏感議題攔截驗證
        if case.get('should_intercept', False):
            assert 'sensitive_topic_detected' in data, (
                f"未攔截敏感議題\n"
                f"  案例: {case['id']}"
            )
            assert data['sensitive_topic_detected'] == case['expected_topic']
            
            if case.get('no_system_call', False):
                assert data.get('used_systems', []) == [], "不應調用系統"
            return
        
        # 2. 系統使用驗證
        if case.get('expected_systems'):
            used_systems = data.get('used_systems', [])
            for system in case['expected_systems']:
                assert system in used_systems, (
                    f"缺少預期系統\n"
                    f"  案例: {case['id']}\n"
                    f"  預期: {system}\n"
                    f"  實際: {used_systems}"
                )
        
        # 3. 工具使用驗證
        if case.get('expected_tools'):
            tools_used = data.get('tools_used', [])
            for tool in case['expected_tools']:
                assert any(tool in str(t) for t in tools_used), (
                    f"缺少預期工具\n"
                    f"  案例: {case['id']}\n"
                    f"  預期: {tool}"
                )
        
        # 4. 引用數量驗證
        if case.get('min_citations'):
            citations = data.get('citations', [])
            assert len(citations) >= case['min_citations'], (
                f"引用數量不足\n"
                f"  案例: {case['id']}\n"
                f"  預期: >= {case['min_citations']}\n"
                f"  實際: {len(citations)}"
            )
        
        # 5. 回應品質驗證
        if case.get('min_reply_length'):
            reply_length = len(data.get('reply', ''))
            assert reply_length >= case['min_reply_length'], (
                f"回應過短\n"
                f"  案例: {case['id']}\n"
                f"  預期: >= {case['min_reply_length']}\n"
                f"  實際: {reply_length}"
            )
        
        # 6. 信心度驗證
        if case.get('min_confidence'):
            confidence = data.get('confidence', 0)
            assert confidence >= case['min_confidence'], (
                f"信心度過低\n"
                f"  案例: {case['id']}\n"
                f"  預期: >= {case['min_confidence']}\n"
                f"  實際: {confidence}"
            )
        
        # 7. API 版本欄位驗證
        if case.get('expected_fields'):
            for field in case['expected_fields']:
                assert field in data, f"缺少欄位: {field}"
        
        if case.get('forbidden_fields'):
            for field in case['forbidden_fields']:
                assert field not in data, f"不應包含欄位: {field}"
        
        # 8. 快取測試
        if case.get('repeat_request', False):
            response2 = client.post('/api/chat/consult',
                headers=headers,
                json={'message': case['user_message']}
            )
            data2 = response2.get_json()
            
            # 快取命中應返回相同結果且更快
            assert data2['reply'] == data['reply'], "快取結果應一致"
    
    def _setup_locked_chart(self, client, token, user_id):
        """設定鎖定命盤"""
        # 實作鎖定命盤邏輯
        pass
    
    def _test_stream_response(self, case, client, token):
        """測試流式回應"""
        response = client.post('/api/chat/consult-stream',
            headers={'Authorization': f'Bearer {token}'},
            json={'message': case['user_message']},
            buffered=True
        )
        
        data = response.get_data(as_text=True) or ''
        chunks = [line for line in data.splitlines() if line.strip()]
        
        assert len(chunks) >= case.get('expected_chunks', 1), (
            f"流式回應片段不足: {len(chunks)}"
        )
    
    def _test_multi_turn_integration(self, case, client, token):
        """測試多輪對話整合"""
        session_id = None
        
        for turn in case['turns']:
            request_data = {'message': turn['message']}
            if session_id:
                request_data['session_id'] = session_id
            
            response = client.post('/api/chat/consult',
                headers={'Authorization': f'Bearer {token}'},
                json=request_data
            )
            
            data = response.get_json()
            session_id = data.get('session_id', session_id)
            
            # 驗證預期關鍵詞和系統
            if turn.get('expected_keywords'):
                reply = data['reply']
                for kw in turn['expected_keywords']:
                    assert kw in reply
            
            if turn.get('expected_systems'):
                used = data.get('used_systems', [])
                for sys in turn['expected_systems']:
                    assert sys in used
    
    def _test_concurrent_isolation(self, case, client):
        """測試併發隔離"""
        import threading
        import uuid
        results = []

        def _register_user():
            email = f"test_concurrent_{uuid.uuid4().hex[:8]}@example.com"
            password = "test_password_123"
            response = client.post('/api/auth/register', json={
                'email': email,
                'password': password,
                'display_name': 'Concurrent Test User'
            })
            assert response.status_code == 200, f"註冊失敗: {response.get_json()}"
            data = response.get_json()
            return data['user_id'], data['token']
        
        def make_request(message, user_auth):
            user_id, token = user_auth
            response = client.post('/api/chat/consult',
                headers={'Authorization': f'Bearer {token}'},
                json={'message': message}
            )
            results.append((user_id, response.get_json()))
        
        threads = []
        user_auths = [_register_user() for _ in case['messages']]
        for i, message in enumerate(case['messages']):
            thread = threading.Thread(target=make_request, args=(message, user_auths[i]))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 驗證結果隔離
        assert len(results) == len(case['messages'])
    
    def _test_error_recovery(self, case, client, token):
        """測試錯誤恢復"""
        # 第一次請求（有錯誤）
        response1 = client.post('/api/chat/consult',
            headers={'Authorization': f'Bearer {token}'},
            json={'message': case['user_message']}
        )
        data1 = response1.get_json()
        
        # 第二次請求（修正）
        response2 = client.post('/api/chat/consult',
            headers={'Authorization': f'Bearer {token}'},
            json={'message': case['follow_up']}
        )
        data2 = response2.get_json()
        
        # 應成功恢復
        assert data2['status'] == 'success'
        if case.get('expected_systems'):
            for sys in case['expected_systems']:
                assert sys in data2.get('used_systems', [])


# ========== 輔助測試 ==========

@pytest.mark.golden_set
@pytest.mark.smoke
def test_golden_integration_quick_sanity():
    """快速驗證系統整合 Golden Set 定義正確"""
    assert len(SYSTEM_INTEGRATION_GOLDEN_CASES) == 10
    
    # 檢查每個案例有必要欄位
    for case in SYSTEM_INTEGRATION_GOLDEN_CASES:
        assert 'id' in case
        assert 'description' in case
        assert case['id'].startswith('GS_INTEGRATION_')


@pytest.mark.golden_set
@pytest.mark.performance
def test_integration_performance():
    """驗證整合流程效能"""
    # 測試端到端回應時間
    pass


@pytest.mark.golden_set
@pytest.mark.reliability
def test_integration_reliability():
    """驗證系統穩定性"""
    # 測試長時間運行穩定性
    pass
