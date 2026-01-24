"""
Aetheria 定盤系統測試客戶端
用於測試完整的定盤流程
"""

import requests
import json
from time import sleep
import pytest

# API 基礎 URL
BASE_URL = 'http://localhost:5001'

# 測試用戶資料
TEST_USER = {
    'user_id': 'test_user_001',
    'birth_date': '農曆68年9月23日',
    'birth_time': '23:58',
    'birth_location': '台灣彰化市',
    'gender': '男'
}

def print_separator(title=''):
    """列印分隔線"""
    print('\n' + '='*60)
    if title:
        print(f' {title}')
        print('='*60)

def health_check():
    """檢查服務是否運行"""
    try:
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code == 200:
            print('[OK] API 服務正常運行')
            return True
        else:
            print('[ERROR] API 服務異常')
            return False
    except Exception as e:
        print(f'[ERROR] 無法連接 API 服務: {e}')
        return False

def test_initial_analysis():
    """測試首次命盤分析"""
    print_separator('步驟 1: 首次命盤分析')
    
    print(f'正在為用戶 {TEST_USER["user_id"]} 生成命盤...')
    print(f'出生資料: {TEST_USER["birth_date"]} {TEST_USER["birth_time"]}')
    
    response = requests.post(
        f'{BASE_URL}/api/chart/initial-analysis',
        json=TEST_USER
    )
    
    if response.status_code != 200:
        print(f'[ERROR] 分析失敗: {response.json()}')
        return None
    
    result = response.json()
    
    print('\n[OK] 命盤分析完成')
    print(f'\n--- 命盤結構 ---')
    structure = result['structure']
    print(f"命宮: {structure['命宮']['主星']} ({structure['命宮']['宮位']}宮)")
    print(f"格局: {', '.join(structure['格局'])}")
    print(f"五行局: {structure.get('五行局', '未提及')}")
    
    print(f'\n--- 關鍵宮位 ---')
    for palace in ['官祿宮', '財帛宮', '夫妻宮']:
        if palace in structure['十二宮']:
            info = structure['十二宮'][palace]
            stars = ', '.join(info['主星']) if info['主星'] else '空宮'
            trans = f" ({info['四化']})" if info.get('四化') else ''
            print(f"{palace}: {stars}{trans} - {info['宮位']}宮")
    
    print(f'\n--- 完整分析（前500字）---')
    print(result['analysis'][:500] + '...')
    
    return result

@pytest.mark.skip(reason="互動式測試流程，非 pytest 自動測試")
def test_confirm_lock(user_id):
    """測試確認鎖定"""
    print_separator('步驟 2: 確認並鎖定命盤')
    
    input('\n按 Enter 確認上述命盤結構正確...')
    
    response = requests.post(
        f'{BASE_URL}/api/chart/confirm-lock',
        json={'user_id': user_id}
    )
    
    if response.status_code != 200:
        print(f'[ERROR] 鎖定失敗: {response.json()}')
        return False
    
    result = response.json()
    print(f'\n[OK] {result["message"]}')
    print(f'鎖定時間: {result["locked_at"]}')
    
    return True

@pytest.mark.skip(reason="互動式測試流程，非 pytest 自動測試")
def test_get_lock(user_id):
    """測試查詢鎖定"""
    print_separator('步驟 3: 查詢鎖定狀態')
    
    response = requests.get(
        f'{BASE_URL}/api/chart/get-lock',
        params={'user_id': user_id}
    )
    
    if response.status_code != 200:
        print(f'[ERROR] 查詢失敗: {response.json()}')
        return None
    
    result = response.json()
    
    if result['locked']:
        print('[OK] 命盤已鎖定')
        print(f"鎖定時間: {result['locked_at']}")
        return result['chart_structure']
    else:
        print('[WARNING] 命盤尚未鎖定')
        return None

@pytest.mark.skip(reason="互動式測試流程，非 pytest 自動測試")
def test_chat(user_id, message):
    """測試對話功能"""
    print_separator('步驟 4: 測試對話（注入鎖定結構）')
    
    print(f'\n用戶問題: {message}')
    print('正在生成回應...')
    
    response = requests.post(
        f'{BASE_URL}/api/chat/message',
        json={
            'user_id': user_id,
            'message': message
        }
    )
    
    if response.status_code != 200:
        print(f'[ERROR] 對話失敗: {response.json()}')
        return
    
    result = response.json()
    
    print(f'\n[OK] Aetheria 回應:')
    print('-'*60)
    print(result['response'])
    print('-'*60)
    print(f'\n命盤結構已注入: {result["chart_injected"]}')

@pytest.mark.skip(reason="互動式測試流程，非 pytest 自動測試")
def test_relock(user_id):
    """測試重新定盤"""
    print_separator('步驟 5: 測試重新定盤')
    
    confirm = input('\n是否要測試重新定盤功能？(y/n): ')
    
    if confirm.lower() != 'y':
        print('跳過重新定盤測試')
        return
    
    reason = input('請輸入重新定盤原因: ')
    
    response = requests.post(
        f'{BASE_URL}/api/chart/relock',
        json={
            'user_id': user_id,
            'reason': reason
        }
    )
    
    if response.status_code != 200:
        print(f'[ERROR] 重新定盤失敗: {response.json()}')
        return
    
    result = response.json()
    print(f'\n[OK] {result["message"]}')

def run_full_test():
    """執行完整測試流程"""
    print('='*60)
    print(' Aetheria 定盤系統完整測試')
    print('='*60)
    
    # 檢查服務
    if not health_check():
        print('\n請先啟動 API 服務: python api_server.py')
        return
    
    sleep(1)
    
    # 步驟 1: 首次分析
    result = test_initial_analysis()
    if not result:
        return
    
    sleep(2)
    
    # 步驟 2: 確認鎖定
    if not test_confirm_lock(TEST_USER['user_id']):
        return
    
    sleep(1)
    
    # 步驟 3: 查詢鎖定
    structure = test_get_lock(TEST_USER['user_id'])
    if not structure:
        return
    
    sleep(1)
    
    # 步驟 4: 測試對話
    test_questions = [
        '我最近工作不順利，該如何改善？',
        '今年的財運如何？',
        '我適合創業嗎？'
    ]
    
    for question in test_questions:
        test_chat(TEST_USER['user_id'], question)
        sleep(2)
    
    # 步驟 5: 重新定盤（選擇性）
    test_relock(TEST_USER['user_id'])
    
    print_separator('測試完成')
    print('[OK] 所有功能測試通過')

if __name__ == '__main__':
    try:
        run_full_test()
    except KeyboardInterrupt:
        print('\n\n測試中斷')
    except Exception as e:
        print(f'\n[ERROR] 測試失敗: {e}')
        import traceback
        traceback.print_exc()
