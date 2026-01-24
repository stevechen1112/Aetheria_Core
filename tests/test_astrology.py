"""
西洋占星術系統測試腳本
測試主要功能：
1. 本命盤分析 (natal)
2. 合盤分析 (synastry)
3. 過境分析 (transit)
"""

import requests
import json
from datetime import datetime
import time

# API 基礎地址
BASE_URL = "http://localhost:5001"

# 測試用戶資料（本命盤）
TEST_PERSON = {
    "name": "陳宥竹",
    "year": 1979,
    "month": 11,
    "day": 12,
    "hour": 23,
    "minute": 58,
    "city": "彰化市",
    "longitude": 120.52,
    "latitude": 24.08,
    "timezone": "Asia/Taipei"
}

# 第二人資料（用於合盤測試）
TEST_PERSON2 = {
    "name": "配對對象",
    "year": 1985,
    "month": 6,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "city": "台北市",
    "longitude": 121.5654,
    "latitude": 25.0330,
    "timezone": "Asia/Taipei"
}


def print_section(title):
    """打印分節標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_natal_chart():
    """測試1：本命盤分析"""
    print_section("測試 1/3：本命盤分析")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    url = f"{BASE_URL}/api/astrology/natal"
    
    print(f"\n發送請求時間：{datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    response = requests.post(url, json=TEST_PERSON, timeout=180)
    duration = time.time() - start_time
    
    print(f"回應時間：{duration:.1f} 秒")
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 本命盤分析成功！")
            
            # 顯示星盤資料
            if 'natal_chart' in data:
                chart = data['natal_chart']
                print(f"\n  星盤資訊：")
                
                # 太陽星座
                if 'sun' in chart:
                    sun = chart['sun']
                    print(f"    太陽：{sun.get('sign', '未知')} {sun.get('degree', 0):.2f}°")
                
                # 月亮星座
                if 'moon' in chart:
                    moon = chart['moon']
                    print(f"    月亮：{moon.get('sign', '未知')} {moon.get('degree', 0):.2f}°")
                
                # 上升星座
                if 'ascendant' in chart:
                    asc = chart['ascendant']
                    print(f"    上升：{asc.get('sign', '未知')} {asc.get('degree', 0):.2f}°")
            
            # 顯示分析內容
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"\n  分析長度：{len(analysis)} 字符")
                print(f"\n分析預覽（前 300 字）：")
                print("-" * 60)
                print(analysis[:300] + "...")
                print("-" * 60)
                
                # 保存完整分析
                filename = f"astrology_natal_{datetime.now().strftime('%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"西洋占星術本命盤分析\n{'='*60}\n")
                    f.write(f"姓名：{TEST_PERSON['name']}\n")
                    f.write(f"出生時間：{TEST_PERSON['year']}/{TEST_PERSON['month']}/{TEST_PERSON['day']} ")
                    f.write(f"{TEST_PERSON['hour']}:{TEST_PERSON['minute']}\n")
                    f.write(f"出生地點：{TEST_PERSON['city']}\n")
                    f.write(f"分析時間：{data.get('timestamp', datetime.now().isoformat())}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(analysis)
                print(f"\n完整分析已保存：{filename}")
            
            return True, data
        else:
            print(f"\n✗ 分析失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_synastry():
    """測試2：合盤分析（兩人關係）"""
    print_section("測試 2/3：合盤分析")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    url = f"{BASE_URL}/api/astrology/synastry"
    
    test_data = {
        "person1": TEST_PERSON,
        "person2": TEST_PERSON2,
        "relationship_type": "romantic"
    }
    
    print(f"\n發送請求時間：{datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start_time
    
    print(f"回應時間：{duration:.1f} 秒")
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 合盤分析成功！")
            
            # 顯示分析內容
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"\n  分析長度：{len(analysis)} 字符")
                print(f"\n分析預覽（前 300 字）：")
                print("-" * 60)
                print(analysis[:300] + "...")
                print("-" * 60)
            
            return True, data
        else:
            print(f"\n✗ 分析失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_transit():
    """測試3：過境分析"""
    print_section("測試 3/3：過境分析")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    url = f"{BASE_URL}/api/astrology/transit"
    
    test_data = {
        **TEST_PERSON,
        "transit_date": "2026-06-15"
    }
    
    print(f"\n查詢日期：{test_data['transit_date']}")
    print(f"發送請求時間：{datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start_time
    
    print(f"回應時間：{duration:.1f} 秒")
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 過境分析成功！")
            
            # 顯示過境行星
            if 'transit_planets' in data:
                print(f"\n  過境行星位置：")
                for planet, info in list(data['transit_planets'].items())[:5]:
                    print(f"    {planet}: {info.get('sign', '未知')} {info.get('degree', 0):.1f}°")
            
            # 顯示分析內容
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"\n  分析長度：{len(analysis)} 字符")
                print(f"\n分析預覽（前 300 字）：")
                print("-" * 60)
                print(analysis[:300] + "...")
                print("-" * 60)
            
            return True, data
        else:
            print(f"\n✗ 分析失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def run_all_tests():
    """運行所有測試"""
    print("\n" + "=" * 60)
    print("  西洋占星術系統功能測試")
    print("  時間：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    results = []
    
    # 測試1：本命盤分析
    success, _ = test_natal_chart()
    results.append(("本命盤分析", success))
    
    # 測試2：合盤分析
    success, _ = test_synastry()
    results.append(("合盤分析", success))
    
    # 測試3：過境分析
    success, _ = test_transit()
    results.append(("過境分析", success))
    
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
