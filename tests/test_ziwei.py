"""
紫微斗數系統測試腳本
測試主要功能：
1. 首次命盤分析
2. 確認鎖盤
3. 取得鎖盤狀態
4. 年度流年運勢
5. 流月運勢
"""

import requests
import json
from datetime import datetime
import time

# API 基礎地址
BASE_URL = "http://localhost:5001"

# 測試用戶資料
TEST_USER = {
    "user_id": "test_user_001",
    "birth_date": "農曆68年9月23日",
    "birth_time": "23:58",
    "birth_location": "台灣彰化市",
    "gender": "男"
}


def print_section(title):
    """打印分節標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_get_lock_status():
    """測試1：檢查命盤鎖定狀態"""
    print_section("測試 1/5：檢查命盤鎖定狀態")
    
    url = f"{BASE_URL}/api/chart/get-lock?user_id={TEST_USER['user_id']}"
    response = requests.get(url)
    
    print(f"\n狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('locked'):
            chart = result['chart_structure']['命宮']
            print(f"\n✓ 用戶命盤已鎖定")
            print(f"  命宮：{chart['宮位']}")
            main_stars = chart.get('主星', [])
            if main_stars:
                print(f"  主星：{', '.join(main_stars)}")
            else:
                print(f"  主星：無主星（空宮）")
            print(f"  鎖定時間：{result.get('locked_at', '未知')}")
            
            # 顯示格局
            if '格局' in result['chart_structure']:
                print(f"  格局：{', '.join(result['chart_structure']['格局'])}")
            
            return True, result
        else:
            print(f"\n⚠ 用戶尚未鎖定命盤")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_initial_analysis():
    """測試2：首次命盤分析（需要 AI 生成，約 30-60 秒）"""
    print_section("測試 2/5：首次命盤分析")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    print("        若用戶已有鎖盤，將跳過此測試")
    
    # 先檢查是否已有鎖盤
    check_url = f"{BASE_URL}/api/chart/get-lock?user_id={TEST_USER['user_id']}"
    check_response = requests.get(check_url)
    
    if check_response.status_code == 200 and check_response.json().get('locked'):
        print(f"\n⚠ 用戶已有鎖定命盤，跳過首次分析測試")
        return True, None
    
    url = f"{BASE_URL}/api/chart/initial-analysis"
    
    print(f"\n發送請求時間：{datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    response = requests.post(url, json=TEST_USER, timeout=180)
    duration = time.time() - start_time
    
    print(f"回應時間：{duration:.1f} 秒")
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if 'analysis' in result:
            print(f"\n✓ 命盤分析成功！")
            print(f"  分析長度：{len(result['analysis'])} 字符")
            print(f"  需要確認：{result.get('needs_confirmation', False)}")
            
            if 'structure' in result:
                structure = result['structure']
                if '命宮' in structure:
                    print(f"  命宮：{structure['命宮'].get('宮位', '未知')}")
                    print(f"  主星：{', '.join(structure['命宮'].get('主星', []))}")
            
            print(f"\n分析預覽（前 300 字）：")
            print("-" * 60)
            print(result['analysis'][:300] + "...")
            print("-" * 60)
            
            return True, result
        else:
            print(f"\n✗ 回應缺少分析內容")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_confirm_lock():
    """測試3：確認鎖盤"""
    print_section("測試 3/5：確認鎖盤")
    
    # 先檢查是否已有鎖盤
    check_url = f"{BASE_URL}/api/chart/get-lock?user_id={TEST_USER['user_id']}"
    check_response = requests.get(check_url)
    
    if check_response.status_code == 200 and check_response.json().get('locked'):
        print(f"\n⚠ 用戶已有鎖定命盤，跳過確認鎖盤測試")
        return True, None
    
    url = f"{BASE_URL}/api/chart/confirm-lock"
    
    response = requests.post(url, json={"user_id": TEST_USER['user_id']})
    
    print(f"\n狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 命盤鎖定成功！")
        print(f"  狀態：{result.get('status', '未知')}")
        print(f"  訊息：{result.get('message', '未知')}")
        print(f"  鎖定時間：{result.get('locked_at', '未知')}")
        return True, result
    else:
        print(f"\n✗ 鎖盤失敗：{response.text}")
        return False, None


def test_fortune_annual():
    """測試4：年度流年運勢（需要 AI 分析，約 30-60 秒）"""
    print_section("測試 4/5：年度流年運勢分析")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    # 先檢查是否有鎖盤
    check_url = f"{BASE_URL}/api/chart/get-lock?user_id={TEST_USER['user_id']}"
    check_response = requests.get(check_url)
    
    if check_response.status_code != 200 or not check_response.json().get('locked'):
        print(f"\n⚠ 用戶尚未鎖定命盤，無法測試流年運勢")
        return False, None
    
    url = f"{BASE_URL}/api/fortune/annual"
    test_data = {
        "user_id": TEST_USER['user_id'],
        "target_year": 2026
    }
    
    print(f"\n查詢年份：{test_data['target_year']} 年")
    print(f"發送請求時間：{datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start_time
    
    print(f"回應時間：{duration:.1f} 秒")
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if 'analysis' in result:
            print(f"\n✓ 流年運勢分析成功！")
            print(f"  分析長度：{len(result['analysis'])} 字符")
            
            if 'fortune_data' in result:
                fd = result['fortune_data']
                if 'da_xian' in fd:
                    print(f"\n  大限資訊：")
                    print(f"    大限宮位：{fd['da_xian'].get('palace_name', '未知')}")
                if 'liu_nian' in fd:
                    print(f"  流年資訊：")
                    print(f"    流年宮位：{fd['liu_nian'].get('palace_name', '未知')}")
            
            print(f"\n分析預覽（前 300 字）：")
            print("-" * 60)
            print(result['analysis'][:300] + "...")
            print("-" * 60)
            
            # 保存完整分析
            filename = f"ziwei_fortune_{test_data['target_year']}_{datetime.now().strftime('%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"紫微斗數流年運勢分析\n{'='*60}\n")
                f.write(f"用戶：{TEST_USER['user_id']}\n")
                f.write(f"查詢年份：{test_data['target_year']} 年\n")
                f.write(f"分析時間：{datetime.now().isoformat()}\n")
                f.write(f"{'='*60}\n\n")
                f.write(result['analysis'])
            print(f"\n完整分析已保存：{filename}")
            
            return True, result
        else:
            print(f"\n✗ 回應缺少分析內容")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_fortune_monthly():
    """測試5：流月運勢（需要 AI 分析，約 30-60 秒）"""
    print_section("測試 5/5：流月運勢分析")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    # 先檢查是否有鎖盤
    check_url = f"{BASE_URL}/api/chart/get-lock?user_id={TEST_USER['user_id']}"
    check_response = requests.get(check_url)
    
    if check_response.status_code != 200 or not check_response.json().get('locked'):
        print(f"\n⚠ 用戶尚未鎖定命盤，無法測試流月運勢")
        return False, None
    
    url = f"{BASE_URL}/api/fortune/monthly"
    test_data = {
        "user_id": TEST_USER['user_id'],
        "target_year": 2026,
        "target_month": 6
    }
    
    print(f"\n查詢時間：{test_data['target_year']} 年 {test_data['target_month']} 月")
    print(f"發送請求時間：{datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start_time
    
    print(f"回應時間：{duration:.1f} 秒")
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if 'analysis' in result:
            print(f"\n✓ 流月運勢分析成功！")
            print(f"  分析長度：{len(result['analysis'])} 字符")
            
            print(f"\n分析預覽（前 300 字）：")
            print("-" * 60)
            print(result['analysis'][:300] + "...")
            print("-" * 60)
            
            return True, result
        else:
            print(f"\n✗ 回應缺少分析內容")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def run_all_tests():
    """運行所有測試"""
    print("\n" + "=" * 60)
    print("  紫微斗數系統功能測試")
    print("  時間：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    results = []
    
    # 測試1：檢查鎖盤狀態
    success, _ = test_get_lock_status()
    results.append(("檢查鎖盤狀態", success))
    
    # 測試2：首次命盤分析（若已鎖盤則跳過）
    success, _ = test_initial_analysis()
    results.append(("首次命盤分析", success))
    
    # 測試3：確認鎖盤（若已鎖盤則跳過）
    success, _ = test_confirm_lock()
    results.append(("確認鎖盤", success))
    
    # 測試4：年度流年運勢
    success, _ = test_fortune_annual()
    results.append(("年度流年運勢", success))
    
    # 測試5：流月運勢
    success, _ = test_fortune_monthly()
    results.append(("流月運勢", success))
    
    # 測試總結
    print_section("測試總結")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\n測試結果：{passed}/{total} 通過\n")
    for name, success in results:
        status = "✓ 通過" if success else "✗ 失敗"
        print(f"  {status}  {name}")
    
    print(f"\n測試完成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total


if __name__ == "__main__":
    run_all_tests()
