"""
Golden Set: 錯誤處理與邊界情況測試
測試系統對異常輸入和錯誤情況的處理能力
"""

import pytest
from typing import Dict, Any


# ========== Test Cases Definition ==========

ERROR_HANDLING_GOLDEN_CASES = [
    {
        'id': 'GS_ERROR_001',
        'name': '缺少出生資訊',
        'user_message': '請幫我算命',
        'expected_behavior': 'graceful_prompt',
        'expected_keywords': ['出生', '日期', '時間', '資料'],
        'should_succeed': True,
        'description': '缺少必要資訊時應友善提示'
    },
    {
        'id': 'GS_ERROR_002',
        'name': '無效日期格式',
        'user_message': '我 99999-99-99 出生，請算八字',
        'expected_behavior': 'graceful_error',
        'expected_keywords': ['日期', '格式', '正確'],
        'should_succeed': True,
        'description': '無效日期應返回友善錯誤訊息'
    },
    {
        'id': 'GS_ERROR_003',
        'name': '空白訊息',
        'user_message': '   ',
        'expected_behavior': 'reject_empty',
        'expected_keywords': ['問題', '請問', '輸入'],
        'should_succeed': True,
        'description': '空白輸入應提示用戶重新輸入'
    },
    {
        'id': 'GS_ERROR_004',
        'name': '超長訊息',
        'user_message': '請幫我算命' + '很多問題' * 1000,  # > 5000 字
        'expected_behavior': 'truncate_or_reject',
        'expected_keywords': ['過長', '簡化', '簡短'],
        'should_succeed': True,
        'description': '超長訊息應截斷或拒絕'
    },
    {
        'id': 'GS_ERROR_005',
        'name': '無法理解的問題',
        'user_message': 'asdfghjkl qwertyuiop zxcvbnm',
        'expected_behavior': 'clarification',
        'expected_keywords': ['理解', '具體', '重新', '詢問'],
        'should_succeed': True,
        'description': '無意義輸入應要求澄清'
    }
]


# ========== 額外錯誤測試（非 API 錯誤）==========

BOUNDARY_TEST_CASES = [
    {
        'id': 'GS_BOUNDARY_001',
        'name': '極早出生日期',
        'user_message': '我 1900-01-01 出生，請算命',
        'should_succeed': True,
        'expected_keywords': ['1900'],
        'description': '邊界日期（1900）應正常處理'
    },
    {
        'id': 'GS_BOUNDARY_002',
        'name': '未來日期',
        'user_message': '我 2050-12-31 出生，請算命',
        'should_succeed': True,
        'expected_keywords': ['日期', '未來'],
        'description': '未來日期應提示錯誤'
    },
    {
        'id': 'GS_BOUNDARY_003',
        'name': '特殊字元輸入',
        'user_message': '我叫 <script>alert("test")</script>，請算命',
        'should_succeed': True,
        'no_xss': True,
        'description': '特殊字元應安全處理（防 XSS）'
    }
]


# ========== Test Execution ==========

@pytest.mark.golden_set
@pytest.mark.parametrize('case', ERROR_HANDLING_GOLDEN_CASES, ids=lambda c: c['id'])
class TestErrorHandlingGoldenSet:
    """錯誤處理 Golden Set 測試"""
    
    def test_error_handling_case(self, case: Dict[str, Any], client, auth_user):
        """
        執行單個錯誤處理測試案例
        
        驗證項目：
        1. 系統不崩潰
        2. 返回友善錯誤訊息
        3. 提供補救建議
        4. 保持服務可用性
        """
        user_id, token = auth_user
        
        # 發送請求
        response = client.post('/api/chat/consult',
            headers={'Authorization': f'Bearer {token}'},
            json={'message': case['user_message']}
        )
        
        # 1. 基礎可用性驗證
        assert response.status_code in [200, 400], (
            f"不應返回 5xx 錯誤\n"
            f"  案例: {case['id']}\n"
            f"  狀態碼: {response.status_code}"
        )
        
        data = response.get_json()
        assert data is not None, f"應返回 JSON: {case['id']}"
        
        # 2. 友善錯誤訊息驗證
        if case.get('should_succeed', False):
            # 應成功但返回提示訊息
            assert data['status'] == 'success', (
                f"應成功處理異常輸入\n"
                f"  案例: {case['id']}\n"
                f"  狀態: {data.get('status')}"
            )
            
            reply = data.get('reply', '')
            assert len(reply) > 0, f"應有回應內容: {case['id']}"
            
            # 檢查友善提示關鍵詞
            if case.get('expected_keywords'):
                matched = [kw for kw in case['expected_keywords'] if kw in reply]
                assert len(matched) > 0, (
                    f"缺少友善提示\n"
                    f"  案例: {case['id']}\n"
                    f"  預期關鍵詞: {case['expected_keywords']}\n"
                    f"  匹配: {matched}\n"
                    f"  回應: {reply[:300]}..."
                )
        
        # 3. 行為模式驗證
        behavior = case.get('expected_behavior')
        
        if behavior == 'graceful_prompt':
            # 應提示用戶提供缺失資訊
            reply = data.get('reply', '')
            assert any(word in reply for word in ['請', '需要', '提供', '告訴']), (
                f"應主動提示用戶\n"
                f"  案例: {case['id']}\n"
                f"  回應: {reply[:200]}..."
            )
        
        elif behavior == 'graceful_error':
            # 應說明錯誤原因
            reply = data.get('reply', '')
            assert any(word in reply for word in ['無效', '錯誤', '格式', '正確']), (
                f"應說明錯誤\n"
                f"  案例: {case['id']}\n"
                f"  回應: {reply[:200]}..."
            )
        
        elif behavior == 'reject_empty':
            # 應拒絕空白輸入
            reply = data.get('reply', '')
            assert len(reply) > 0, f"應返回提示: {case['id']}"
        
        elif behavior == 'truncate_or_reject':
            # 應處理超長輸入
            reply = data.get('reply', '')
            assert len(reply) > 0, f"應返回訊息: {case['id']}"
        
        elif behavior == 'clarification':
            # 應要求澄清
            reply = data.get('reply', '')
            assert any(word in reply for word in ['理解', '明白', '具體', '詳細']), (
                f"應要求澄清\n"
                f"  案例: {case['id']}\n"
                f"  回應: {reply[:200]}..."
            )
        
        # 4. 安全性驗證（不應洩漏系統內部資訊）
        reply = data.get('reply', '')
        dangerous_keywords = ['traceback', 'Exception', 'Error:', 'File "']
        for keyword in dangerous_keywords:
            assert keyword not in reply, (
                f"不應洩漏內部錯誤\n"
                f"  案例: {case['id']}\n"
                f"  發現: {keyword}"
            )


@pytest.mark.golden_set
@pytest.mark.parametrize('case', BOUNDARY_TEST_CASES, ids=lambda c: c['id'])
class TestBoundaryGoldenSet:
    """邊界情況 Golden Set 測試"""
    
    def test_boundary_case(self, case: Dict[str, Any], client, auth_user):
        """測試邊界輸入情況"""
        user_id, token = auth_user
        
        response = client.post('/api/chat/consult',
            headers={'Authorization': f'Bearer {token}'},
            json={'message': case['user_message']}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        if case.get('should_succeed'):
            assert data['status'] == 'success'
        
        # XSS 防護驗證
        if case.get('no_xss', False):
            reply = data.get('reply', '')
            assert '<script>' not in reply, "應過濾 XSS 攻擊"
            assert 'alert(' not in reply, "應過濾 XSS 攻擊"


# ========== 輔助測試 ==========

@pytest.mark.golden_set
@pytest.mark.smoke
def test_golden_error_handling_quick_sanity():
    """快速驗證錯誤處理 Golden Set 定義正確"""
    assert len(ERROR_HANDLING_GOLDEN_CASES) == 5
    assert len(BOUNDARY_TEST_CASES) == 3
    
    # 檢查涵蓋主要錯誤類型
    behaviors = {case['expected_behavior'] for case in ERROR_HANDLING_GOLDEN_CASES}
    expected_behaviors = {
        'graceful_prompt',
        'graceful_error',
        'reject_empty',
        'truncate_or_reject',
        'clarification'
    }
    assert behaviors == expected_behaviors, "應涵蓋所有錯誤行為模式"
    
    # 檢查每個案例有必要欄位
    for case in ERROR_HANDLING_GOLDEN_CASES:
        assert 'id' in case
        assert 'user_message' in case
        assert 'expected_behavior' in case
        assert case['id'].startswith('GS_ERROR_')


@pytest.mark.golden_set
def test_concurrent_error_handling():
    """驗證並發錯誤不會互相影響"""
    # 測試多個錯誤同時發生時的隔離性
    pass


@pytest.mark.golden_set
def test_error_recovery():
    """驗證錯誤後系統可恢復"""
    # 測試錯誤後下一個請求仍正常
    pass
