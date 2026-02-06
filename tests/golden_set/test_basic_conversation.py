"""
Golden Set: 基礎對話流程測試
測試系統最基本的命理諮詢能力
"""

import pytest
from typing import Dict, Any


# ========== Test Cases Definition ==========

BASIC_CONVERSATION_GOLDEN_CASES = [
    {
        'id': 'GS_BASIC_001',
        'name': '事業運勢諮詢',
        'user_message': '我想了解我的事業運勢如何？',
        'expected_systems': ['ziwei', 'bazi'],
        'expected_keywords': ['事業', '工作', '職場', '發展'],
        'min_confidence': 0.7,
        'has_citations': True,
        'description': '標準事業運勢諮詢，應引用紫微或八字'
    },
    {
        'id': 'GS_BASIC_002',
        'name': '財運分析',
        'user_message': '今年的財運好嗎？',
        'expected_systems': ['ziwei', 'bazi'],
        'expected_keywords': ['財運', '財富', '財帛', '金錢'],
        'min_confidence': 0.65,
        'has_citations': True,
        'description': '財運諮詢，應涉及財帛宮或財星'
    },
    {
        'id': 'GS_BASIC_003',
        'name': '感情運勢',
        'user_message': '我的感情運勢如何？',
        'expected_systems': ['ziwei', 'astrology'],
        'expected_keywords': ['感情', '愛情', '婚姻', '桃花'],
        'min_confidence': 0.7,
        'has_citations': True,
        'description': '感情諮詢，可能涉及金星或桃花'
    },
    {
        'id': 'GS_BASIC_004',
        'name': '整體運勢',
        'user_message': '請幫我看看整體運勢',
        'expected_systems': ['ziwei', 'bazi', 'astrology'],
        'expected_keywords': ['命宮', '整體', '運勢', '格局'],
        'min_confidence': 0.65,
        'has_citations': True,
        'description': '綜合運勢，應涵蓋多系統'
    },
    {
        'id': 'GS_BASIC_005',
        'name': '貴人運',
        'user_message': '我的貴人運如何？',
        'expected_systems': ['ziwei', 'bazi'],
        'expected_keywords': ['貴人', '天乙', '幫助', '支持'],
        'min_confidence': 0.65,
        'has_citations': True,
        'description': '貴人運諮詢'
    },
    {
        'id': 'GS_BASIC_006',
        'name': '性格分析',
        'user_message': '我的性格特質是什麼？',
        'expected_systems': ['ziwei', 'astrology', 'numerology'],
        'expected_keywords': ['性格', '個性', '特質', '人格'],
        'min_confidence': 0.7,
        'has_citations': True,
        'description': '性格分析，可用多系統'
    },
    {
        'id': 'GS_BASIC_007',
        'name': '流年運勢',
        'user_message': '2026年的流年運勢如何？',
        'expected_systems': ['ziwei', 'bazi'],
        'expected_keywords': ['流年', '2026', '運勢', '大運'],
        'min_confidence': 0.65,
        'has_citations': True,
        'description': '特定年份運勢分析'
    },
    {
        'id': 'GS_BASIC_008',
        'name': '健康運（非敏感）',
        'user_message': '我的身體狀況運勢如何？要注意什麼？',
        'expected_systems': ['ziwei', 'bazi'],
        'expected_keywords': ['健康', '身體', '注意', '保養'],
        'min_confidence': 0.6,
        'has_citations': True,
        'sensitive_topic_detected': False,  # 應不觸發敏感議題
        'description': '健康運勢（模糊問法，不觸發敏感攔截）'
    },
    {
        'id': 'GS_BASIC_009',
        'name': '學業運',
        'user_message': '小孩的學業運勢好嗎？',
        'expected_systems': ['ziwei', 'bazi'],
        'expected_keywords': ['學業', '考試', '學習', '文昌'],
        'min_confidence': 0.65,
        'has_citations': True,
        'description': '學業運勢諮詢'
    },
    {
        'id': 'GS_BASIC_010',
        'name': '簡短問候回應',
        'user_message': '你好',
        'expected_systems': [],
        'expected_keywords': ['你好', '命理', '協助', '諮詢'],
        'min_confidence': 0.0,
        'has_citations': False,
        'description': '簡單問候，無需命理分析'
    }
]


# ========== Test Execution ==========

@pytest.mark.golden_set
@pytest.mark.parametrize('case', BASIC_CONVERSATION_GOLDEN_CASES, ids=lambda c: c['id'])
class TestBasicConversationGoldenSet:
    """基礎對話 Golden Set 測試"""
    
    def test_basic_conversation_case(self, case: Dict[str, Any], client, auth_user):
        """
        執行單個基礎對話測試案例
        
        驗證項目：
        1. API 返回成功
        2. 回應包含預期關鍵詞
        3. 使用正確的系統
        4. 信心度達標
        5. 引用資料（如需要）
        """
        user_id, token = auth_user
        
        # 發送請求
        response = client.post('/api/chat/consult',
            headers={'Authorization': f'Bearer {token}'},
            json={'message': case['user_message']}
        )
        
        assert response.status_code == 200, f"API 請求失敗: {case['id']}"
        
        data = response.get_json()
        
        # 1. 基礎驗證
        assert data['status'] == 'success', f"回應狀態異常: {case['id']}"
        assert 'reply' in data, f"缺少回應內容: {case['id']}"
        assert len(data['reply']) > 0, f"回應為空: {case['id']}"
        
        # 2. 關鍵詞檢查（至少包含一個）
        if case['expected_keywords']:
            reply_lower = data['reply'].lower()
            matched_keywords = [kw for kw in case['expected_keywords'] if kw in reply_lower]
            assert len(matched_keywords) > 0, (
                f"回應未包含預期關鍵詞\n"
                f"  案例: {case['id']}\n"
                f"  預期: {case['expected_keywords']}\n"
                f"  實際回應: {data['reply'][:200]}..."
            )
        
        # 3. 系統使用檢查
        if case['expected_systems']:
            used_systems = data.get('used_systems', [])
            # 至少使用一個預期系統
            matched_systems = [sys for sys in case['expected_systems'] if sys in used_systems]
            assert len(matched_systems) > 0, (
                f"未使用預期系統\n"
                f"  案例: {case['id']}\n"
                f"  預期: {case['expected_systems']}\n"
                f"  實際: {used_systems}"
            )
        
        # 4. 信心度檢查
        if 'min_confidence' in case:
            confidence = data.get('confidence', 0.0)
            assert confidence >= case['min_confidence'], (
                f"信心度低於預期\n"
                f"  案例: {case['id']}\n"
                f"  預期: >= {case['min_confidence']}\n"
                f"  實際: {confidence}"
            )
        
        # 5. 引用檢查
        if case.get('has_citations', False):
            citations = data.get('citations', [])
            assert len(citations) > 0, (
                f"缺少引用資料\n"
                f"  案例: {case['id']}\n"
                f"  應有引用但實際為空"
            )
        
        # 6. 敏感議題檢查（如指定）
        if 'sensitive_topic_detected' in case:
            sensitive = data.get('sensitive_topic_detected')
            if case['sensitive_topic_detected'] == False:
                assert sensitive is None or sensitive == 'none', (
                    f"不應觸發敏感議題攔截\n"
                    f"  案例: {case['id']}\n"
                    f"  實際: {sensitive}"
                )


# ========== 獨立測試（用於快速驗證）==========

@pytest.mark.golden_set
@pytest.mark.smoke
def test_golden_basic_quick_sanity():
    """快速驗證 Golden Set 定義正確"""
    assert len(BASIC_CONVERSATION_GOLDEN_CASES) == 10
    
    # 檢查每個案例有必要欄位
    for case in BASIC_CONVERSATION_GOLDEN_CASES:
        assert 'id' in case
        assert 'user_message' in case
        assert 'expected_systems' in case
        assert 'expected_keywords' in case
        assert case['id'].startswith('GS_BASIC_')
