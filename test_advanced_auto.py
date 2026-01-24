"""
自動測試進階功能（不需要交互）
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def create_test_user_002():
    """創建第二個測試用戶並完成定盤"""
    print("\n" + "="*60)
    print("【準備】檢查測試用戶 test_user_002")
    print("="*60)
    
    # 先檢查用戶是否已存在並已鎖定
    try:
        check_response = requests.get(f'{BASE_URL}/api/chart/get-lock?user_id=test_user_002')
        if check_response.status_code == 200:
            data = check_response.json()
            if data.get('locked'):
                print(f"✓ 用戶已存在且已定盤")
                return True
    except:
        pass
    
    # 用戶不存在，創建新用戶
    print("正在創建新用戶...")
    response = requests.post(
        f'{BASE_URL}/api/chart/initial-analysis',
        json={
            'user_id': 'test_user_002',
            'birth_date': '農曆70年5月15日',
            'birth_time': '14:30',
            'birth_location': '台灣台北市',
            'gender': '女'
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 用戶創建成功")
        print(f"✓ 命盤分析完成")
        
        # 2. 鎖定命盤
        time.sleep(2)
        lock_response = requests.post(
            f'{BASE_URL}/api/chart/lock',
            json={'user_id': 'test_user_002'}
        )
        
        if lock_response.status_code == 200:
            print(f"✓ 命盤已鎖定")
            return True
        else:
            print(f"✗ 鎖定失敗: {lock_response.text}")
            return False
    else:
        print(f"✗ 創建失敗: {response.text}")
        return False


def test_synastry_quick():
    """測試快速合盤（最快的測試）"""
    print("\n" + "="*60)
    print("【測試 1】快速合盤評估")
    print("="*60)
    print("正在生成分析...")
    
    start_time = time.time()
    response = requests.post(
        f'{BASE_URL}/api/synastry/quick',
        json={
            'user_a_id': 'test_user_001',
            'user_b_id': 'test_user_002',
            'analysis_type': '婚配'
        }
    )
    duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 對象 A: {result['user_a_id']}")
        print(f"✓ 對象 B: {result['user_b_id']}")
        print(f"✓ 評估類型: {result['analysis_type']}")
        print(f"✓ 生成時間: {duration:.2f} 秒")
        print(f"\n✓ 快速評估:")
        print("-" * 60)
        print(result['analysis'])
        print("-" * 60)
        return True
    else:
        print(f"✗ 錯誤: {response.text}")
        return False


def test_date_selection_business():
    """測試開業擇日"""
    print("\n" + "="*60)
    print("【測試 2】開業擇日")
    print("="*60)
    print("正在生成分析...")
    
    start_time = time.time()
    response = requests.post(
        f'{BASE_URL}/api/date-selection/business',
        json={
            'owner_id': 'test_user_001',
            'target_year': 2026,
            'business_type': 'AI 命理諮詢工作室',
            'business_nature': '服務業',
            'business_direction': '東方',
            'preferred_months': '3月、4月、9月',
            'other_requirements': '希望選在週末開幕'
        }
    )
    duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 負責人: {result['owner_id']}")
        print(f"✓ 目標年份: {result['target_year']}")
        print(f"✓ 事業類型: {result['business_type']}")
        print(f"✓ 生成時間: {duration:.2f} 秒")
        print(f"\n✓ 擇日分析（前1500字）:")
        print("-" * 60)
        analysis = result['analysis']
        print(analysis[:1500] if len(analysis) > 1500 else analysis)
        if len(analysis) > 1500:
            print("\n... (後續內容省略) ...")
        print("-" * 60)
        return True
    else:
        print(f"✗ 錯誤: {response.text}")
        return False


def test_synastry_partnership():
    """測試合夥分析"""
    print("\n" + "="*60)
    print("【測試 3】合夥關係分析")
    print("="*60)
    print("正在生成分析...")
    
    start_time = time.time()
    response = requests.post(
        f'{BASE_URL}/api/synastry/partnership',
        json={
            'user_a_id': 'test_user_001',
            'user_b_id': 'test_user_002',
            'partnership_info': '計劃合作開設 AI 命理諮詢工作室，預計投資 500 萬，股權分配未定'
        }
    )
    duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 合夥人 A: {result['user_a_id']}")
        print(f"✓ 合夥人 B: {result['user_b_id']}")
        print(f"✓ 合夥項目: {result['partnership_info']}")
        print(f"✓ 生成時間: {duration:.2f} 秒")
        print(f"\n✓ 分析結果（前1500字）:")
        print("-" * 60)
        analysis = result['analysis']
        print(analysis[:1500] if len(analysis) > 1500 else analysis)
        if len(analysis) > 1500:
            print("\n... (後續內容省略) ...")
        print("-" * 60)
        return True
    else:
        print(f"✗ 錯誤: {response.text}")
        return False


def main():
    """主測試流程"""
    print("="*60)
    print("Aetheria 進階功能自動測試")
    print("="*60)
    
    # 準備測試用戶
    if not create_test_user_002():
        print("\n✗ 測試用戶準備失敗，測試終止")
        return
    
    # 執行測試
    results = []
    
    print("\n" + "="*60)
    print("開始執行測試...")
    print("="*60)
    
    results.append(("快速合盤評估", test_synastry_quick()))
    time.sleep(2)
    
    results.append(("開業擇日", test_date_selection_business()))
    time.sleep(2)
    
    results.append(("合夥關係分析", test_synastry_partnership()))
    
    # 總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n通過: {passed}/{total}")
    print("\n詳細結果:")
    for test_name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"  {status} - {test_name}")
    
    print("\n" + "="*60)
    if passed == total:
        print("所有測試通過！進階功能已成功實現。")
    else:
        print(f"有 {total - passed} 個測試失敗，請檢查錯誤信息。")
    print("="*60)


if __name__ == '__main__':
    main()
