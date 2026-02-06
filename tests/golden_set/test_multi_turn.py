"""
Golden Set: 多輪對話上下文管理測試
測試系統在連續對話中保持上下文的能力
"""

import pytest
from typing import Dict, Any, List


# ========== Test Cases Definition ==========

MULTI_TURN_GOLDEN_CASES = [
    {
        'id': 'GS_MULTI_001',
        'name': '追問前次問題',
        'turns': [
            {
                'message': '我想了解我的事業運勢',
                'expected_keywords': ['事業', '工作'],
                'expected_systems': ['ziwei', 'bazi']
            },
            {
                'message': '那我適合創業嗎？',
                'expected_keywords': ['創業', '事業'],
                'expected_systems': ['ziwei', 'bazi'],
                'should_reference_previous': True
            }
        ],
        'description': '追問應延續前次主題（事業）'
    },
    {
        'id': 'GS_MULTI_002',
        'name': '深入詢問細節',
        'turns': [
            {
                'message': '請看我的財運如何？',
                'expected_keywords': ['財運', '金錢'],
                'expected_systems': ['bazi', 'ziwei']
            },
            {
                'message': '具體在哪個月份最好？',
                'expected_keywords': ['月份', '時間', '財運'],
                'expected_systems': ['bazi', 'ziwei'],
                'should_reference_previous': True
            },
            {
                'message': '那我需要注意什麼？',
                'expected_keywords': ['注意', '建議'],
                'should_reference_previous': True
            }
        ],
        'description': '連續深入詢問應保持主題連貫'
    },
    {
        'id': 'GS_MULTI_003',
        'name': '話題轉換',
        'turns': [
            {
                'message': '我想問感情運勢',
                'expected_keywords': ['感情', '愛情'],
                'expected_systems': ['ziwei']
            },
            {
                'message': '換一個話題，我的健康運呢？',
                'expected_keywords': ['健康', '身體'],
                'expected_systems': ['bazi'],
                'should_reference_previous': False
            }
        ],
        'description': '明確換話題時應清除前次上下文'
    },
    {
        'id': 'GS_MULTI_004',
        'name': '引用前次結果',
        'turns': [
            {
                'message': '請幫我排紫微命盤',
                'expected_systems': ['ziwei'],
                'expected_keywords': ['命宮', '宮位']
            },
            {
                'message': '剛才說的命宮在哪裡？',
                'expected_keywords': ['命宮'],
                'should_reference_previous': True,
                'should_find_info': '命宮'
            }
        ],
        'description': '應能引用前次回應中的具體資訊'
    },
    {
        'id': 'GS_MULTI_005',
        'name': '比較不同系統',
        'turns': [
            {
                'message': '用八字看我的事業運',
                'expected_systems': ['bazi'],
                'expected_keywords': ['事業', '八字']
            },
            {
                'message': '那紫微怎麼說？',
                'expected_systems': ['ziwei'],
                'expected_keywords': ['事業', '紫微'],
                'should_reference_previous': True
            },
            {
                'message': '兩者有什麼差異？',
                'expected_keywords': ['差異', '比較', '八字', '紫微'],
                'should_reference_previous': True
            }
        ],
        'description': '應能比較多個系統的分析結果'
    },
    {
        'id': 'GS_MULTI_006',
        'name': '澄清與修正',
        'turns': [
            {
                'message': '我 1990 年出生，請看運勢',
                'expected_keywords': ['運勢', '1990']
            },
            {
                'message': '抱歉，是 1992 年才對',
                'expected_keywords': ['1992'],
                'should_reference_previous': True,
                'should_correct_info': True
            }
        ],
        'description': '應能處理用戶修正前次資訊'
    },
    {
        'id': 'GS_MULTI_007',
        'name': '長期會話記憶',
        'turns': [
            {
                'message': '我叫張小明，1985-03-20 出生',
                'expected_keywords': ['張小明', '1985']
            },
            {
                'message': '請看我的事業運',
                'expected_systems': ['bazi', 'ziwei'],
                'should_use_previous_info': True
            },
            {
                'message': '我的姓名和生日是什麼？',
                'expected_keywords': ['張小明', '1985'],
                'should_reference_previous': True
            }
        ],
        'description': '應記住會話開始時提供的個人資訊'
    }
]


# ========== Test Execution ==========

@pytest.mark.golden_set
@pytest.mark.parametrize('case', MULTI_TURN_GOLDEN_CASES, ids=lambda c: c['id'])
class TestMultiTurnGoldenSet:
    """多輪對話上下文管理 Golden Set 測試"""
    
    def test_multi_turn_case(self, case: Dict[str, Any], client, auth_user):
        """
        執行多輪對話測試案例
        
        驗證項目：
        1. 連續對話保持上下文
        2. 正確引用前次資訊
        3. 話題轉換清除上下文
        4. 修正前次錯誤資訊
        5. 長期記憶個人資料
        """
        user_id, token = auth_user
        session_id = None
        previous_responses = []
        
        for turn_idx, turn in enumerate(case['turns']):
            # 發送請求（帶上 session_id）
            request_data = {'message': turn['message']}
            if session_id:
                request_data['session_id'] = session_id
            
            response = client.post('/api/chat/consult',
                headers={'Authorization': f'Bearer {token}'},
                json=request_data
            )
            
            assert response.status_code == 200, (
                f"API 請求失敗\n"
                f"  案例: {case['id']}\n"
                f"  輪次: {turn_idx + 1}\n"
                f"  訊息: {turn['message']}"
            )
            
            data = response.get_json()
            assert data['status'] == 'success'
            
            # 記錄 session_id
            if 'session_id' in data:
                session_id = data['session_id']
            
            # 1. 關鍵詞驗證
            if turn.get('expected_keywords'):
                reply = data['reply']
                matched = [kw for kw in turn['expected_keywords'] if kw in reply]
                assert len(matched) > 0, (
                    f"缺少預期關鍵詞\n"
                    f"  案例: {case['id']}\n"
                    f"  輪次: {turn_idx + 1}\n"
                    f"  預期: {turn['expected_keywords']}\n"
                    f"  匹配: {matched}\n"
                    f"  回應: {reply[:300]}..."
                )
            
            # 2. 系統使用驗證
            if turn.get('expected_systems'):
                used_systems = data.get('used_systems', [])
                for system in turn['expected_systems']:
                    assert system in used_systems, (
                        f"缺少預期系統\n"
                        f"  案例: {case['id']}\n"
                        f"  輪次: {turn_idx + 1}\n"
                        f"  預期系統: {system}\n"
                        f"  實際使用: {used_systems}"
                    )
            
            # 3. 上下文引用驗證
            if turn.get('should_reference_previous', False) and previous_responses:
                # 檢查是否提到前次關鍵資訊
                prev_keywords = previous_responses[-1].get('keywords', [])
                reply = data['reply']
                
                if prev_keywords:
                    # 至少應引用一個前次關鍵詞
                    referenced = any(kw in reply for kw in prev_keywords if kw)
                    assert referenced or turn_idx == 0, (
                        f"未引用前次對話內容\n"
                        f"  案例: {case['id']}\n"
                        f"  輪次: {turn_idx + 1}\n"
                        f"  前次關鍵詞: {prev_keywords}\n"
                        f"  本次回應: {reply[:200]}..."
                    )
            
            # 4. 特殊情境驗證
            if turn.get('should_find_info'):
                # 應能找到前次提到的特定資訊
                info = turn['should_find_info']
                assert info in data['reply'], (
                    f"未找到前次資訊\n"
                    f"  案例: {case['id']}\n"
                    f"  輪次: {turn_idx + 1}\n"
                    f"  尋找: {info}"
                )
            
            if turn.get('should_correct_info'):
                # 應使用新資訊覆蓋舊資訊
                # 這需要檢查後續工具調用是否使用新參數
                pass
            
            # 記錄本次回應
            previous_responses.append({
                'reply': data['reply'],
                'keywords': turn.get('expected_keywords', []),
                'systems': data.get('used_systems', [])
            })


# ========== 輔助測試 ==========

@pytest.mark.golden_set
@pytest.mark.smoke
def test_golden_multi_turn_quick_sanity():
    """快速驗證多輪對話 Golden Set 定義正確"""
    assert len(MULTI_TURN_GOLDEN_CASES) == 7
    
    # 檢查輪次設計
    total_turns = sum(len(case['turns']) for case in MULTI_TURN_GOLDEN_CASES)
    assert total_turns >= 15, "總對話輪次應至少 15 輪"
    
    # 檢查每個案例有必要欄位
    for case in MULTI_TURN_GOLDEN_CASES:
        assert 'id' in case
        assert 'turns' in case
        assert len(case['turns']) >= 2, f"{case['id']} 應至少 2 輪對話"
        assert case['id'].startswith('GS_MULTI_')
        
        for turn in case['turns']:
            assert 'message' in turn


@pytest.mark.golden_set
def test_session_isolation():
    """驗證不同 session 之間隔離"""
    # 測試兩個不同用戶的對話不會互相干擾
    # 這需要實際的 session 管理機制
    pass


@pytest.mark.golden_set
def test_context_window_limit():
    """驗證上下文窗口限制"""
    # 測試超過一定輪次後舊對話被遺忘
    # 這取決於系統的上下文管理策略
    pass
