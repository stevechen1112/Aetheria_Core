"""
流年運勢功能測試
"""

import requests
import json

BASE_URL = 'http://localhost:5000'
USER_ID = 'test_user_001'

print('='*60)
print('Aetheria 流年運勢功能測試')
print('='*60)

# 測試 1: 年度流年分析
print('\n[測試 1] 2026 年流年運勢分析')
print('正在生成...')

try:
    response = requests.post(
        f'{BASE_URL}/api/fortune/annual',
        json={
            'user_id': USER_ID,
            'target_year': 2026
        },
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        fortune = result['fortune_data']
        
        print(f"\n✓ 流年資訊:")
        print(f"  年齡: {fortune['current_age']} 歲")
        print(f"  大限: 第{fortune['da_xian']['da_xian_number']}大限 ({fortune['da_xian']['palace_name']})")
        print(f"  流年: {fortune['liu_nian']['gan_zhi']}年 ({fortune['liu_nian']['palace_name']})")
        
        print(f"\n✓ Aetheria 分析:")
        print('-'*60)
        # 只顯示前800字
        analysis = result['analysis']
        print(analysis[:800] + '...' if len(analysis) > 800 else analysis)
        print('-'*60)
    else:
        print(f'✗ 失敗: {response.json()}')
        exit(1)
        
except Exception as e:
    print(f'✗ 失敗: {e}')
    exit(1)

input('\n按 Enter 繼續測試流月分析...')

# 測試 2: 流月分析
print('\n[測試 2] 2026 年 1 月流月運勢分析')
print('正在生成...')

try:
    response = requests.post(
        f'{BASE_URL}/api/fortune/monthly',
        json={
            'user_id': USER_ID,
            'target_year': 2026,
            'target_month': 1
        },
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        fortune = result['fortune_data']
        
        print(f"\n✓ 流月資訊:")
        print(f"  流月: {fortune['liu_yue']['year']}年{fortune['liu_yue']['month']}月")
        print(f"  宮位: {fortune['liu_yue']['palace_name']}")
        
        print(f"\n✓ Aetheria 分析:")
        print('-'*60)
        print(result['analysis'][:600] + '...')
        print('-'*60)
    else:
        print(f'✗ 失敗: {response.json()}')
        exit(1)
        
except Exception as e:
    print(f'✗ 失敗: {e}')
    exit(1)

input('\n按 Enter 繼續測試特定問題分析...')

# 測試 3: 特定問題的流年分析
print('\n[測試 3] 特定問題：今年適合換工作嗎？')
print('正在分析...')

try:
    response = requests.post(
        f'{BASE_URL}/api/fortune/question',
        json={
            'user_id': USER_ID,
            'question': '今年適合換工作嗎？'
        },
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✓ Aetheria 回應:")
        print('-'*60)
        print(result['analysis'][:800] + '...')
        print('-'*60)
    else:
        print(f'✗ 失敗: {response.json()}')
        exit(1)
        
except Exception as e:
    print(f'✗ 失敗: {e}')
    exit(1)

# 測試完成
print('\n' + '='*60)
print('✓ 流年運勢功能測試完成')
print('='*60)
