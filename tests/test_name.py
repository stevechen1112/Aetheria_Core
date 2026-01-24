"""
姓名學系統測試腳本
測試主要功能：
1. 完整姓名分析 (analyze)
2. 五格數理計算 (five-grids)
3. 命名建議 (suggest)
4. 筆劃查詢 (stroke)
"""

import requests
import json
from datetime import datetime
import time

# API 基礎地址
BASE_URL = "http://localhost:5001"

# 測試姓名
TEST_NAME = "陳宥竹"

# 命名建議測試資料
SUGGEST_DATA = {
    "surname": "陳",
    "gender": "男",
    "bazi_element": "木"
}


def print_section(title):
    """打印分節標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_five_grids():
    """測試1：五格數理計算（快速）"""
    print_section("測試 1/4：五格數理計算")
    
    url = f"{BASE_URL}/api/name/five-grids"
    
    response = requests.post(url, json={"name": TEST_NAME})
    
    print(f"\n狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 五格數理計算成功！")
            print(f"\n  姓名：{data.get('name', '未知')}")
            print(f"  姓氏：{data.get('surname', '未知')}")
            print(f"  名字：{data.get('given_name', '未知')}")
            print(f"  總筆劃：{data.get('total_strokes', '未知')}")
            
            # 顯示五格
            five_grids = data.get('five_grids', {})
            if five_grids:
                print(f"\n  五格數理：")
                print(f"    天格：{five_grids.get('天格', '未知')}")
                print(f"    人格：{five_grids.get('人格', '未知')}")
                print(f"    地格：{five_grids.get('地格', '未知')}")
                print(f"    外格：{five_grids.get('外格', '未知')}")
                print(f"    總格：{five_grids.get('總格', '未知')}")
            
            # 顯示吉凶
            grid_fortunes = data.get('grid_fortunes', {})
            if grid_fortunes:
                print(f"\n  五格吉凶：")
                for grid, fortune in grid_fortunes.items():
                    print(f"    {grid}：{fortune}")
            
            # 顯示三才
            three_talents = data.get('three_talents', {})
            if three_talents:
                print(f"\n  三才配置：")
                print(f"    天地人：{three_talents.get('天', '')} → {three_talents.get('人', '')} → {three_talents.get('地', '')}")
            
            # 顯示總體運勢
            overall = data.get('overall_fortune', '')
            if overall:
                print(f"\n  總體運勢：{overall}")
            
            return True, data
        else:
            print(f"\n✗ 計算失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_analyze():
    """測試2：完整姓名分析（需要 AI 分析，約 30-60 秒）"""
    print_section("測試 2/4：完整姓名分析")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    url = f"{BASE_URL}/api/name/analyze"
    
    test_data = {
        "name": TEST_NAME,
        "analysis_type": "basic",
        "bazi_element": "木",
        "include_ai": True
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
            
            print(f"\n✓ 姓名分析成功！")
            print(f"\n  姓名：{data.get('name', '未知')}")
            
            # 顯示五格
            five_grids = data.get('five_grids', {})
            if five_grids:
                print(f"\n  五格數理：")
                for grid, value in five_grids.items():
                    print(f"    {grid}：{value}")
            
            # 顯示 AI 解讀
            if 'ai_interpretation' in data:
                interpretation = data['ai_interpretation']
                print(f"\n  AI 解讀長度：{len(interpretation)} 字符")
                print(f"\n解讀預覽（前 300 字）：")
                print("-" * 60)
                print(interpretation[:300] + "...")
                print("-" * 60)
                
                # 保存完整分析
                filename = f"name_analysis_{datetime.now().strftime('%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"姓名學完整分析\n{'='*60}\n")
                    f.write(f"姓名：{TEST_NAME}\n")
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


def test_suggest():
    """測試3：命名建議（需要 AI 生成，約 30-60 秒）"""
    print_section("測試 3/4：命名建議")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    url = f"{BASE_URL}/api/name/suggest"
    
    test_data = {
        **SUGGEST_DATA,
        "count": 5
    }
    
    print(f"\n姓氏：{test_data['surname']}")
    print(f"性別：{test_data['gender']}")
    print(f"八字喜用神：{test_data['bazi_element']}")
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
            
            print(f"\n✓ 命名建議成功！")
            
            # 顯示建議名字
            suggestions = data.get('suggestions', [])
            if suggestions:
                print(f"\n  建議名字（前 5 個）：")
                for i, suggestion in enumerate(suggestions[:5], 1):
                    if isinstance(suggestion, dict):
                        name = suggestion.get('name', '未知')
                        score = suggestion.get('score', '未知')
                        print(f"    {i}. {name}（分數：{score}）")
                    else:
                        print(f"    {i}. {suggestion}")
            
            return True, data
        else:
            print(f"\n✗ 建議失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_stroke():
    """測試4：筆劃查詢（快速）"""
    print_section("測試 4/4：筆劃查詢")
    
    test_char = "陳"
    url = f"{BASE_URL}/api/name/stroke/{test_char}"
    
    response = requests.get(url)
    
    print(f"\n查詢字元：{test_char}")
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 筆劃查詢成功！")
            print(f"\n  字元：{data.get('character', '未知')}")
            print(f"  康熙筆劃：{data.get('strokes', '未知')}")
            print(f"  五行：{data.get('element', '未知')}")
            
            return True, data
        else:
            print(f"\n✗ 查詢失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def run_all_tests():
    """運行所有測試"""
    print("\n" + "=" * 60)
    print("  姓名學系統功能測試")
    print("  時間：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    results = []
    
    # 測試1：五格數理計算
    success, _ = test_five_grids()
    results.append(("五格數理計算", success))
    
    # 測試2：完整姓名分析
    success, _ = test_analyze()
    results.append(("完整姓名分析", success))
    
    # 測試3：命名建議
    success, _ = test_suggest()
    results.append(("命名建議", success))
    
    # 測試4：筆劃查詢
    success, _ = test_stroke()
    results.append(("筆劃查詢", success))
    
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
