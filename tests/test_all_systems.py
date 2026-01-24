"""
Aetheria Core 六大命理系統完整測試
=====================================
整合測試腳本，驗證所有六大系統功能正常

系統清單：
1. 紫微斗數 - LLM-First 架構
2. 八字命理 - BaziCalculator + sxtwl
3. 西洋占星術 - Swiss Ephemeris
4. 靈數學 - NumerologyCalculator
5. 姓名學 - NameCalculator
6. 塔羅牌 - TarotCalculator

版本：v1.8.0
"""

import requests
import json
from datetime import datetime
import time
import sys

# API 基礎地址
BASE_URL = "http://localhost:5001"

# 測試用戶資料（統一用於所有系統）
TEST_USER = {
    "user_id": "test_user_001",
    "name": "陳宥竹",
    "year": 1979,
    "month": 11,
    "day": 12,
    "hour": 23,
    "minute": 58,
    "gender": "male",
    "longitude": 120.52,
    "latitude": 24.08,
    "birth_date": "1979-11-12",
    "full_name": "CHEN YU CHU"
}


def print_header(title):
    """打印大標題"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + title.center(68) + "║")
    print("╚" + "═" * 68 + "╝")


def print_section(title):
    """打印分節標題"""
    print("\n" + "─" * 70)
    print(f"  {title}")
    print("─" * 70)


def check_api_server():
    """檢查 API 伺服器是否運行"""
    print_section("前置檢查：API 伺服器狀態")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"\n✓ API 伺服器運行中 ({BASE_URL})")
            return True
    except requests.exceptions.ConnectionError:
        pass
    
    print(f"\n✗ 無法連接 API 伺服器 ({BASE_URL})")
    print("  請先啟動 API 伺服器：python api_server.py")
    return False


# ============================================================
# 1. 紫微斗數系統測試
# ============================================================

def test_ziwei():
    """測試紫微斗數系統"""
    print_header("系統 1/6：紫微斗數")
    results = []
    
    # 測試 1.1：檢查鎖盤狀態
    print_section("測試 1.1：檢查命盤鎖定狀態")
    url = f"{BASE_URL}/api/chart/get-lock?user_id={TEST_USER['user_id']}"
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('locked'):
            chart = result['chart_structure']['命宮']
            print(f"✓ 命盤已鎖定")
            print(f"  命宮：{chart['宮位']}，主星：{', '.join(chart.get('主星', ['無']))}")
            results.append(("紫微-鎖盤狀態", True))
        else:
            print(f"⚠ 命盤尚未鎖定")
            results.append(("紫微-鎖盤狀態", True))  # 未鎖定也算正常
    else:
        print(f"✗ 檢查失敗：{response.status_code}")
        results.append(("紫微-鎖盤狀態", False))
    
    # 測試 1.2：流年運勢（若已鎖盤）
    print_section("測試 1.2：流年運勢分析")
    if results[-1][1] and response.status_code == 200 and response.json().get('locked'):
        url = f"{BASE_URL}/api/fortune/annual"
        test_data = {"user_id": TEST_USER['user_id'], "target_year": 2026}
        
        print("呼叫 AI 分析中（約 30-60 秒）...")
        start = time.time()
        response = requests.post(url, json=test_data, timeout=180)
        duration = time.time() - start
        
        if response.status_code == 200 and 'analysis' in response.json():
            analysis = response.json()['analysis']
            print(f"✓ 流年分析成功（耗時 {duration:.1f}s，{len(analysis)} 字）")
            results.append(("紫微-流年運勢", True))
        else:
            print(f"✗ 流年分析失敗")
            results.append(("紫微-流年運勢", False))
    else:
        print("⚠ 跳過（需要先鎖定命盤）")
        results.append(("紫微-流年運勢", None))
    
    return results


# ============================================================
# 2. 八字命理系統測試
# ============================================================

def test_bazi():
    """測試八字命理系統"""
    print_header("系統 2/6：八字命理")
    results = []
    
    # 測試 2.1：八字排盤
    print_section("測試 2.1：八字排盤計算")
    url = f"{BASE_URL}/api/bazi/calculate"
    test_data = {
        "year": TEST_USER['year'],
        "month": 10,  # 農曆月份
        "day": 11,
        "hour": TEST_USER['hour'],
        "minute": TEST_USER['minute'],
        "gender": TEST_USER['gender'],
        "longitude": TEST_USER['longitude']
    }
    
    response = requests.post(url, json=test_data, timeout=30)

    if response.status_code == 200 and response.json().get('status') == 'success':
        data = response.json()['data']
        pillars = data['四柱']
        print("✓ 八字排盤成功")
        hour_pillar = pillars.get('時柱', pillars.get('时柱', {}))
        print(
            f"  四柱：{pillars['年柱']['天干']}{pillars['年柱']['地支']} "
            f"{pillars['月柱']['天干']}{pillars['月柱']['地支']} "
            f"{pillars['日柱']['天干']}{pillars['日柱']['地支']} "
            f"{hour_pillar.get('天干', '未知')}{hour_pillar.get('地支', '未知')}"
        )
        strength = data.get('強弱', data.get('强弱', {}))
        print(f"  日主：{data['日主']['天干']}（{data['日主']['五行']}），{strength.get('結論', '未知')}")
        results.append(("八字-排盤計算", True))
    else:
        print(f"✗ 八字排盤失敗：{response.text[:100]}")
        results.append(("八字-排盤計算", False))
    
    # 測試 2.2：八字分析
    print_section("測試 2.2：八字命理分析")
    url = f"{BASE_URL}/api/bazi/analysis"
    
    print("呼叫 AI 分析中（約 30-60 秒）...")
    start = time.time()
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        analysis = response.json()['data']['analysis']
        print(f"✓ 八字分析成功（耗時 {duration:.1f}s，{len(analysis)} 字）")
        results.append(("八字-命理分析", True))
    else:
        print(f"✗ 八字分析失敗")
        results.append(("八字-命理分析", False))
    
    return results


# ============================================================
# 3. 西洋占星術系統測試
# ============================================================

def test_astrology():
    """測試西洋占星術系統"""
    print_header("系統 3/6：西洋占星術")
    results = []
    
    # 測試 3.1：本命盤
    print_section("測試 3.1：本命盤分析")
    url = f"{BASE_URL}/api/astrology/natal"
    test_data = {
        "name": TEST_USER['name'],
        "year": TEST_USER['year'],
        "month": TEST_USER['month'],
        "day": TEST_USER['day'],
        "hour": TEST_USER['hour'],
        "minute": TEST_USER['minute'],
        "longitude": TEST_USER['longitude'],
        "latitude": TEST_USER['latitude'],
        "timezone": "Asia/Taipei"
    }
    
    print("呼叫 AI 分析中（約 30-60 秒）...")
    start = time.time()
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        data = response.json()['data']
        chart = data.get('natal_chart', {})
        print(f"✓ 本命盤分析成功（耗時 {duration:.1f}s）")
        if 'sun' in chart:
            print(f"  太陽：{chart['sun'].get('sign', '未知')} {chart['sun'].get('degree', 0):.1f}°")
        if 'moon' in chart:
            print(f"  月亮：{chart['moon'].get('sign', '未知')} {chart['moon'].get('degree', 0):.1f}°")
        if 'ascendant' in chart:
            print(f"  上升：{chart['ascendant'].get('sign', '未知')} {chart['ascendant'].get('degree', 0):.1f}°")
        results.append(("占星-本命盤", True))
    else:
        print(f"✗ 本命盤分析失敗")
        results.append(("占星-本命盤", False))
    
    # 測試 3.2：過境分析
    print_section("測試 3.2：過境分析")
    url = f"{BASE_URL}/api/astrology/transit"
    test_data["transit_date"] = "2026-06-15"
    
    print("呼叫 AI 分析中（約 30-60 秒）...")
    start = time.time()
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        print(f"✓ 過境分析成功（耗時 {duration:.1f}s）")
        results.append(("占星-過境分析", True))
    else:
        print(f"✗ 過境分析失敗")
        results.append(("占星-過境分析", False))
    
    return results


# ============================================================
# 4. 靈數學系統測試
# ============================================================

def test_numerology():
    """測試靈數學系統"""
    print_header("系統 4/6：靈數學")
    results = []
    
    # 測試 4.1：生命靈數
    print_section("測試 4.1：生命靈數計算")
    url = f"{BASE_URL}/api/numerology/life-path"
    test_data = {"birth_date": TEST_USER['birth_date']}
    
    response = requests.post(url, json=test_data, timeout=30)
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        data = response.json()['data']
        print(f"✓ 生命靈數計算成功")
        print(f"  生命靈數：{data.get('life_path', '未知')}")
        print(f"  名稱：{data.get('name', '未知')}")
        print(f"  是否卓越數：{data.get('is_master_number', False)}")
        results.append(("靈數-生命靈數", True))
    else:
        print(f"✗ 生命靈數計算失敗")
        results.append(("靈數-生命靈數", False))
    
    # 測試 4.2：完整靈數檔案
    print_section("測試 4.2：完整靈數檔案")
    url = f"{BASE_URL}/api/numerology/profile"
    test_data = {
        "birth_date": TEST_USER['birth_date'],
        "full_name": TEST_USER['full_name'],
        "analysis_type": "full"
    }
    
    print("呼叫 AI 分析中（約 30-60 秒）...")
    start = time.time()
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        data = response.json()['data']
        print(f"✓ 靈數檔案分析成功（耗時 {duration:.1f}s）")
        print(f"  天賦數：{data.get('expression_number', '未知')}")
        print(f"  靈魂數：{data.get('soul_urge', '未知')}")
        results.append(("靈數-完整檔案", True))
    else:
        print(f"✗ 靈數檔案分析失敗")
        results.append(("靈數-完整檔案", False))
    
    return results


# ============================================================
# 5. 姓名學系統測試
# ============================================================

def test_name():
    """測試姓名學系統"""
    print_header("系統 5/6：姓名學")
    results = []
    
    # 測試 5.1：五格數理
    print_section("測試 5.1：五格數理計算")
    url = f"{BASE_URL}/api/name/five-grids"
    test_data = {"name": TEST_USER['name']}
    
    response = requests.post(url, json=test_data, timeout=30)
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        data = response.json()['data']
        grids = data.get('five_grids', {})
        print(f"✓ 五格數理計算成功")
        print(f"  姓名：{data.get('name', '未知')}")
        print(f"  五格：天{grids.get('天格', '?')} 人{grids.get('人格', '?')} "
              f"地{grids.get('地格', '?')} 外{grids.get('外格', '?')} 總{grids.get('總格', '?')}")
        print(f"  總體運勢：{data.get('overall_fortune', '未知')}")
        results.append(("姓名-五格數理", True))
    else:
        print(f"✗ 五格數理計算失敗")
        results.append(("姓名-五格數理", False))
    
    # 測試 5.2：完整姓名分析
    print_section("測試 5.2：完整姓名分析")
    url = f"{BASE_URL}/api/name/analyze"
    test_data = {"name": TEST_USER['name'], "include_ai": True}
    
    print("呼叫 AI 分析中（約 30-60 秒）...")
    start = time.time()
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        data = response.json()['data']
        print(f"✓ 姓名分析成功（耗時 {duration:.1f}s）")
        if 'ai_interpretation' in data:
            print(f"  AI 解讀長度：{len(data['ai_interpretation'])} 字")
        results.append(("姓名-完整分析", True))
    else:
        print(f"✗ 姓名分析失敗")
        results.append(("姓名-完整分析", False))
    
    return results


# ============================================================
# 6. 塔羅牌系統測試
# ============================================================

def test_tarot():
    """測試塔羅牌系統"""
    print_header("系統 6/6：塔羅牌")
    results = []
    
    # 測試 6.1：每日一牌
    print_section("測試 6.1：每日一牌")
    url = f"{BASE_URL}/api/tarot/daily"
    
    print("呼叫 AI 解讀中（約 20-40 秒）...")
    start = time.time()
    response = requests.get(url, timeout=120)
    duration = time.time() - start
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        data = response.json()['data']
        card = data.get('card', {})
        print(f"✓ 每日一牌成功（耗時 {duration:.1f}s）")
        print(f"  今日牌：{card.get('name', '未知')}（{'逆位' if card.get('reversed') else '正位'}）")
        results.append(("塔羅-每日一牌", True))
    else:
        print(f"✗ 每日一牌失敗")
        results.append(("塔羅-每日一牌", False))
    
    # 測試 6.2：三張牌解讀
    print_section("測試 6.2：三張牌解讀")
    url = f"{BASE_URL}/api/tarot/reading"
    test_data = {
        "spread_type": "three_card",
        "question": "事業發展如何？",
        "context": "career"
    }
    
    print("呼叫 AI 解讀中（約 30-60 秒）...")
    start = time.time()
    response = requests.post(url, json=test_data, timeout=180)
    duration = time.time() - start
    
    if response.status_code == 200 and response.json().get('status') == 'success':
        data = response.json()['data']
        cards = data.get('cards', [])
        print(f"✓ 塔羅解讀成功（耗時 {duration:.1f}s）")
        print(f"  抽到的牌：")
        for card in cards:
            reversed_str = "逆位" if card.get('reversed') else "正位"
            print(f"    {card.get('position', '?')}：{card.get('name', '?')}（{reversed_str}）")
        results.append(("塔羅-三張牌", True))
    else:
        print(f"✗ 塔羅解讀失敗")
        results.append(("塔羅-三張牌", False))
    
    return results


# ============================================================
# 主程式
# ============================================================

def main():
    """主程式"""
    print_header("Aetheria Core 六大命理系統完整測試 v1.8.0")
    print(f"\n開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"測試用戶：{TEST_USER['name']}（{TEST_USER['user_id']}）")
    print(f"API 地址：{BASE_URL}")
    
    # 檢查 API 伺服器
    if not check_api_server():
        print("\n測試終止：API 伺服器未運行")
        sys.exit(1)
    
    # 執行所有測試
    all_results = []
    
    try:
        all_results.extend(test_ziwei())
        all_results.extend(test_bazi())
        all_results.extend(test_astrology())
        all_results.extend(test_numerology())
        all_results.extend(test_name())
        all_results.extend(test_tarot())
    except KeyboardInterrupt:
        print("\n\n⚠ 測試被用戶中斷")
    except Exception as e:
        print(f"\n\n✗ 測試過程發生錯誤：{e}")
    
    # 測試總結
    print_header("測試總結報告")
    
    # 統計
    passed = sum(1 for _, s in all_results if s is True)
    failed = sum(1 for _, s in all_results if s is False)
    skipped = sum(1 for _, s in all_results if s is None)
    total = len(all_results)
    
    print(f"\n測試結果統計：")
    print(f"  ✓ 通過：{passed}")
    print(f"  ✗ 失敗：{failed}")
    print(f"  ⚠ 跳過：{skipped}")
    print(f"  總計：{total}")
    
    # 詳細結果
    print(f"\n詳細結果：")
    for name, status in all_results:
        if status is True:
            print(f"  ✓ {name}")
        elif status is False:
            print(f"  ✗ {name}")
        else:
            print(f"  ⚠ {name}（跳過）")
    
    # 計算通過率
    actual_tests = passed + failed
    if actual_tests > 0:
        pass_rate = passed / actual_tests * 100
        print(f"\n通過率：{pass_rate:.1f}%（{passed}/{actual_tests}）")
    
    print(f"\n完成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 回傳結果碼
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
