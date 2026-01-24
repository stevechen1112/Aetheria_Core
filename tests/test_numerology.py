"""
靈數學系統測試腳本
測試主要功能：
1. 完整靈數檔案 (profile)
2. 生命靈數計算 (life-path)
3. 流年運勢 (personal-year)
4. 靈數配對 (compatibility)
"""

import requests
import json
from datetime import datetime
import time

# API 基礎地址
BASE_URL = "http://localhost:5001"

# 測試用戶資料
TEST_USER = {
    "birth_date": "1979-11-12",
    "full_name": "CHEN YU CHU"
}

# 第二人資料（用於配對測試）
TEST_USER2 = {
    "birth_date": "1985-06-15",
    "full_name": "TEST PARTNER"
}


def print_section(title):
    """打印分節標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_life_path():
    """測試1：生命靈數計算（快速）"""
    print_section("測試 1/4：生命靈數計算")
    
    url = f"{BASE_URL}/api/numerology/life-path"
    
    response = requests.post(url, json={"birth_date": TEST_USER["birth_date"]})
    
    print(f"\n狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 生命靈數計算成功！")
            print(f"\n  生命靈數：{data.get('life_path', '未知')}")
            print(f"  是否卓越數：{data.get('is_master_number', False)}")
            print(f"  名稱：{data.get('name', '未知')}")
            print(f"  英文名稱：{data.get('name_en', '未知')}")
            
            keywords = data.get('keywords', [])
            if keywords:
                print(f"  關鍵詞：{', '.join(keywords)}")
            
            description = data.get('description', '')
            if description:
                print(f"\n  描述：")
                print(f"    {description[:100]}...")
            
            return True, data
        else:
            print(f"\n✗ 計算失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_profile():
    """測試2：完整靈數檔案（需要 AI 分析，約 30-60 秒）"""
    print_section("測試 2/4：完整靈數檔案")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    url = f"{BASE_URL}/api/numerology/profile"
    
    test_data = {
        **TEST_USER,
        "analysis_type": "full",
        "context": "general"
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
            
            print(f"\n✓ 靈數檔案分析成功！")
            
            # 顯示核心靈數
            print(f"\n  核心靈數：")
            print(f"    生命靈數：{data.get('life_path', '未知')}")
            print(f"    天賦數：{data.get('expression_number', '未知')}")
            print(f"    靈魂數：{data.get('soul_urge', '未知')}")
            print(f"    人格數：{data.get('personality_number', '未知')}")
            
            # 顯示生日數
            if 'birthday_number' in data:
                print(f"    生日數：{data['birthday_number']}")
            
            # 顯示生命週期
            if 'life_cycles' in data:
                print(f"\n  生命週期數：")
                for cycle in data['life_cycles']:
                    print(f"    {cycle.get('name', '未知')}：{cycle.get('number', '未知')}")
            
            # 顯示 AI 解讀
            if 'interpretation' in data:
                interpretation = data['interpretation']
                print(f"\n  AI 解讀長度：{len(interpretation)} 字符")
                print(f"\n解讀預覽（前 300 字）：")
                print("-" * 60)
                print(interpretation[:300] + "...")
                print("-" * 60)
                
                # 保存完整分析
                filename = f"numerology_profile_{datetime.now().strftime('%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"靈數學完整檔案分析\n{'='*60}\n")
                    f.write(f"出生日期：{TEST_USER['birth_date']}\n")
                    f.write(f"英文姓名：{TEST_USER['full_name']}\n")
                    f.write(f"分析時間：{datetime.now().isoformat()}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(interpretation)
                print(f"\n完整分析已保存：{filename}")
            
            return True, data
        else:
            print(f"\n✗ 分析失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_personal_year():
    """測試3：流年運勢"""
    print_section("測試 3/4：流年運勢")
    
    url = f"{BASE_URL}/api/numerology/personal-year"
    
    test_data = {
        "birth_date": TEST_USER["birth_date"],
        "target_year": 2026
    }
    
    print(f"\n查詢年份：{test_data['target_year']} 年")
    
    response = requests.post(url, json=test_data, timeout=60)
    
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 流年運勢計算成功！")
            print(f"\n  個人年份數：{data.get('personal_year', '未知')}")
            print(f"  名稱：{data.get('name', '未知')}")
            
            keywords = data.get('keywords', [])
            if keywords:
                print(f"  關鍵詞：{', '.join(keywords)}")
            
            description = data.get('description', '')
            if description:
                print(f"\n  描述：")
                print(f"    {description[:150]}...")
            
            return True, data
        else:
            print(f"\n✗ 計算失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_compatibility():
    """測試4：靈數配對（需要 AI 分析，約 30-60 秒）"""
    print_section("測試 4/4：靈數配對分析")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    url = f"{BASE_URL}/api/numerology/compatibility"
    
    test_data = {
        "person1": TEST_USER,
        "person2": TEST_USER2,
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
            
            print(f"\n✓ 靈數配對分析成功！")
            
            # 顯示雙方靈數
            if 'person1' in data:
                print(f"\n  第一人生命靈數：{data['person1'].get('life_path', '未知')}")
            if 'person2' in data:
                print(f"  第二人生命靈數：{data['person2'].get('life_path', '未知')}")
            
            # 顯示配對分數
            if 'compatibility_score' in data:
                print(f"\n  配對分數：{data['compatibility_score']}")
            
            # 顯示 AI 解讀
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"\n  AI 解讀長度：{len(analysis)} 字符")
                print(f"\n解讀預覽（前 300 字）：")
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
    print("  靈數學系統功能測試")
    print("  時間：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    results = []
    
    # 測試1：生命靈數計算
    success, _ = test_life_path()
    results.append(("生命靈數計算", success))
    
    # 測試2：完整靈數檔案
    success, _ = test_profile()
    results.append(("完整靈數檔案", success))
    
    # 測試3：流年運勢
    success, _ = test_personal_year()
    results.append(("流年運勢", success))
    
    # 測試4：靈數配對
    success, _ = test_compatibility()
    results.append(("靈數配對", success))
    
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
