"""
簡化版測試 - 直接測試 API 功能
"""

import requests
import json
from time import sleep

BASE_URL = 'http://localhost:5000'

print('='*60)
print('Aetheria 定盤系統測試')
print('='*60)

# 測試 1: 健康檢查
print('\n[測試 1] 健康檢查')
try:
    response = requests.get(f'{BASE_URL}/health', timeout=5)
    print(f'✓ 狀態: {response.json()["status"]}')
except Exception as e:
    print(f'✗ 失敗: {e}')
    print('請確認 API 服務正在運行: python api_server.py')
    exit(1)

# 測試 2: 首次命盤分析
print('\n[測試 2] 首次命盤分析')
print('正在生成命盤...')

test_data = {
    'user_id': 'test_user_001',
    'birth_date': '農曆68年9月23日',
    'birth_time': '23:58',
    'birth_location': '台灣彰化市',
    'gender': '男'
}

try:
    response = requests.post(
        f'{BASE_URL}/api/chart/initial-analysis',
        json=test_data,
        timeout=120  # 增加到 120 秒
    )
    
    if response.status_code == 200:
        result = response.json()
        structure = result['structure']
        
        print('\n命盤結構:')
        print(f"  命宮: {', '.join(structure['命宮']['主星'])} ({structure['命宮']['宮位']}宮)")
        print(f"  格局: {', '.join(structure['格局'])}")
        
        print('\n關鍵宮位:')
        for palace in ['官祿宮', '財帛宮', '夫妻宮']:
            if palace in structure['十二宮']:
                info = structure['十二宮'][palace]
                stars = ', '.join(info['主星']) if info['主星'] else '空宮'
                print(f"  {palace}: {stars} ({info['宮位']}宮)")
        
        print('\n✓ 命盤分析完成')
    else:
        print(f'✗ 失敗: {response.json()}')
        exit(1)
        
except Exception as e:
    print(f'✗ 失敗: {e}')
    exit(1)

sleep(2)

# 測試 3: 確認鎖定
print('\n[測試 3] 確認並鎖定命盤')

try:
    response = requests.post(
        f'{BASE_URL}/api/chart/confirm-lock',
        json={'user_id': 'test_user_001'},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f'✓ {result["message"]}')
    else:
        print(f'✗ 失敗: {response.json()}')
        exit(1)
        
except Exception as e:
    print(f'✗ 失敗: {e}')
    exit(1)

sleep(1)

# 測試 4: 查詢鎖定
print('\n[測試 4] 查詢鎖定狀態')

try:
    response = requests.get(
        f'{BASE_URL}/api/chart/get-lock',
        params={'user_id': 'test_user_001'},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['locked']:
            print(f'✓ 命盤已鎖定於 {result["locked_at"]}')
        else:
            print('✗ 命盤未鎖定')
            exit(1)
    else:
        print(f'✗ 失敗: {response.json()}')
        exit(1)
        
except Exception as e:
    print(f'✗ 失敗: {e}')
    exit(1)

sleep(1)

# 測試 5: 對話功能
print('\n[測試 5] 對話功能（注入鎖定結構）')

question = '我最近工作不順利，該如何改善？'
print(f'問題: {question}')
print('正在生成回應...')

try:
    response = requests.post(
        f'{BASE_URL}/api/chat/message',
        json={
            'user_id': 'test_user_001',
            'message': question
        },
        timeout=120  # 增加到 120 秒
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f'\n✓ Aetheria 回應:')
        print('-'*60)
        print(result['response'][:500] + '...' if len(result['response']) > 500 else result['response'])
        print('-'*60)
        print(f'\n結構已注入: {result["chart_injected"]}')
    else:
        print(f'✗ 失敗: {response.json()}')
        exit(1)
        
except Exception as e:
    print(f'✗ 失敗: {e}')
    exit(1)

# 測試完成
print('\n' + '='*60)
print('✓ 所有測試通過')
print('='*60)
