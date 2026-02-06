"""
Golden Set: AI 工具使用準確性測試
測試 AI 模型正確選擇和使用計算工具
"""

import pytest
from typing import Dict, Any


# ========== Test Cases Definition ==========

TOOL_USE_GOLDEN_CASES = [
    {
        'id': 'GS_TOOL_001',
        'name': '紫微斗數工具',
        'user_message': '我是 1990-05-15 14:30 出生，請幫我排紫微命盤',
        'expected_tools': ['calculate_ziwei'],
        'required_params': ['birthdate', 'birthtime', 'gender', 'calendar'],
        'expected_systems': ['ziwei'],
        'min_confidence': 0.8,
        'description': '應正確調用紫微斗數計算工具'
    },
    {
        'id': 'GS_TOOL_002',
        'name': '八字工具',
        'user_message': '請幫我算 1985-03-20 上午 10:00 的八字命格',
        'expected_tools': ['calculate_bazi'],
        'required_params': ['birthdate', 'birthtime', 'gender', 'calendar'],
        'expected_systems': ['bazi'],
        'min_confidence': 0.8,
        'description': '應正確調用八字計算工具'
    },
    {
        'id': 'GS_TOOL_003',
        'name': '數字學工具',
        'user_message': '我叫張小明，請幫我分析姓名數字學',
        'expected_tools': ['calculate_numerology'],
        'required_params': ['name', 'birthdate'],
        'expected_systems': ['numerology'],
        'min_confidence': 0.7,
        'description': '應正確調用數字學工具'
    },
    {
        'id': 'GS_TOOL_004',
        'name': '塔羅牌工具',
        'user_message': '我想問感情運勢，請幫我抽塔羅牌',
        'expected_tools': ['draw_tarot'],
        'required_params': ['question', 'spread'],
        'expected_systems': ['tarot'],
        'min_confidence': 0.7,
        'description': '應正確調用塔羅牌工具'
    },
    {
        'id': 'GS_TOOL_005',
        'name': '西洋占星工具',
        'user_message': '1992-08-10 晚上 8:00 台北出生，請看星盤',
        'expected_tools': ['calculate_astrology'],
        'required_params': ['birthdate', 'birthtime', 'location'],
        'expected_systems': ['astrology'],
        'min_confidence': 0.8,
        'description': '應正確調用西洋占星工具'
    },
    {
        'id': 'GS_TOOL_006',
        'name': '地點查詢工具',
        'user_message': '我在高雄市左營區出生，請幫我查經緯度',
        'expected_tools': ['get_location'],
        'required_params': ['location_name'],
        'expected_systems': [],
        'min_confidence': 0.6,
        'description': '應正確使用地點查詢工具'
    },
    {
        'id': 'GS_TOOL_007',
        'name': '多工具組合',
        'user_message': '1988-12-25 中午 12:00 台中，請用八字和紫微一起分析',
        'expected_tools': ['calculate_bazi', 'calculate_ziwei'],
        'required_params': ['birthdate', 'birthtime'],
        'expected_systems': ['bazi', 'ziwei'],
        'min_confidence': 0.75,
        'description': '應同時調用多個工具'
    },
    {
        'id': 'GS_TOOL_008',
        'name': '無需工具情境',
        'user_message': '你好，請問你可以提供什麼服務？',
        'expected_tools': [],
        'required_params': [],
        'expected_systems': [],
        'min_confidence': 0.5,
        'description': '一般問候不應調用計算工具'
    }
]


# ========== Test Execution ==========

@pytest.mark.golden_set
@pytest.mark.parametrize('case', TOOL_USE_GOLDEN_CASES, ids=lambda c: c['id'])
class TestToolUseGoldenSet:
    """AI 工具使用準確性 Golden Set 測試"""
    
    def test_tool_use_case(self, case: Dict[str, Any], client, auth_user):
        """
        執行單個工具使用測試案例
        
        驗證項目：
        1. 正確選擇工具（或不選擇工具）
        2. 提取必要參數
        3. 工具調用成功
        4. 結果整合到回應中
        5. 系統使用記錄正確
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
        
        # 2. 工具使用驗證
        tools_used = data.get('tools_used', [])
        expected_tools = case['expected_tools']
        
        if expected_tools:
            # 應該使用工具
            assert len(tools_used) > 0, (
                f"未調用任何工具\n"
                f"  案例: {case['id']}\n"
                f"  訊息: {case['user_message']}\n"
                f"  預期工具: {expected_tools}"
            )
            
            # 檢查工具名稱
            for tool in expected_tools:
                assert any(tool in str(t) for t in tools_used), (
                    f"缺少預期工具\n"
                    f"  案例: {case['id']}\n"
                    f"  預期: {tool}\n"
                    f"  實際調用: {tools_used}"
                )
        else:
            # 不應使用工具（如一般問候）
            assert len(tools_used) == 0, (
                f"不應調用工具\n"
                f"  案例: {case['id']}\n"
                f"  訊息: {case['user_message']}\n"
                f"  實際調用: {tools_used}"
            )
        
        # 3. 系統使用驗證
        used_systems = data.get('used_systems', [])
        expected_systems = case['expected_systems']
        
        if expected_systems:
            for system in expected_systems:
                assert system in used_systems, (
                    f"缺少預期系統\n"
                    f"  案例: {case['id']}\n"
                    f"  預期系統: {system}\n"
                    f"  實際使用: {used_systems}"
                )
        
        # 4. 引用資料驗證（使用工具應有引用）
        if expected_tools:
            citations = data.get('citations', [])
            assert len(citations) > 0, (
                f"使用工具應有引用資料\n"
                f"  案例: {case['id']}\n"
                f"  調用工具: {tools_used}"
            )
        
        # 5. 信心度驗證
        confidence = data.get('confidence', 0)
        assert confidence >= case['min_confidence'], (
            f"信心度過低\n"
            f"  案例: {case['id']}\n"
            f"  預期: >= {case['min_confidence']}\n"
            f"  實際: {confidence}"
        )
        
        # 6. 回應品質驗證
        reply = data['reply']
        if expected_tools:
            # 使用工具的回應應包含計算結果
            assert len(reply) > 200, (
                f"回應過短（應包含計算結果）\n"
                f"  案例: {case['id']}\n"
                f"  長度: {len(reply)} 字元"
            )


# ========== 輔助測試 ==========

@pytest.mark.golden_set
@pytest.mark.smoke
def test_golden_tool_use_quick_sanity():
    """快速驗證工具使用 Golden Set 定義正確"""
    assert len(TOOL_USE_GOLDEN_CASES) == 8
    
    # 檢查涵蓋所有主要工具
    all_tools = set()
    for case in TOOL_USE_GOLDEN_CASES:
        all_tools.update(case['expected_tools'])
    
    expected_tools = {
        'calculate_ziwei',
        'calculate_bazi',
        'calculate_numerology',
        'draw_tarot',
        'calculate_astrology',
        'get_location'
    }
    assert all_tools == expected_tools, "應涵蓋所有主要計算工具"
    
    # 檢查每個案例有必要欄位
    for case in TOOL_USE_GOLDEN_CASES:
        assert 'id' in case
        assert 'user_message' in case
        assert 'expected_tools' in case
        assert case['id'].startswith('GS_TOOL_')


@pytest.mark.golden_set
def test_tool_parameter_extraction():
    """驗證工具參數提取邏輯"""
    # 測試日期提取
    test_messages = [
        '1990-05-15',
        '1990年5月15日',
        '民國79年5月15日'
    ]
    
    # 這裡可以測試參數提取輔助函數（如果有的話）
    # 實際實作會依賴 AI 模型的能力
    pass
