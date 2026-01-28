#!/usr/bin/env python3
"""
完整流程測試腳本
測試從資料儲存到六大系統報告生成的完整流程
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

# 測試用戶資料（您的資料）
TEST_USER = {
    "chinese_name": "陳宥竹",
    "gender": "男",
    "birth_date": "1979-11-12",
    "birth_time": "23:58",
    "birth_location": "台灣彰化市"
}

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_health():
    """測試健康檢查"""
    print_section("1. 健康檢查")
    r = requests.get(f"{BASE_URL}/health")
    print(f"狀態: {r.json().get('status')}")
    return r.status_code == 200

def test_register_and_login():
    """測試註冊和登入"""
    print_section("2. 註冊/登入")
    
    email = f"test_full_{int(time.time())}@example.com"
    
    # 註冊
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "password": "test123456",
        "display_name": TEST_USER["chinese_name"]
    })
    
    if r.status_code == 200:
        data = r.json()
        print(f"註冊成功: user_id={data.get('user_id')[:8]}...")
        return data.get('user_id'), data.get('token')
    else:
        print(f"註冊失敗: {r.text}")
        return None, None

def test_save_and_analyze(user_id, token):
    """測試儲存資料並批次生成報告"""
    print_section("3. 儲存資料並生成報告 (save-and-analyze)")
    
    payload = {
        "user_id": user_id,
        **TEST_USER
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"發送請求...")
    print(f"  姓名: {TEST_USER['chinese_name']}")
    print(f"  出生: {TEST_USER['birth_date']} {TEST_USER['birth_time']}")
    print(f"  地點: {TEST_USER['birth_location']}")
    
    start = time.time()
    r = requests.post(f"{BASE_URL}/api/profile/save-and-analyze", 
                      json=payload, headers=headers, timeout=300)
    elapsed = time.time() - start
    
    print(f"\n回應時間: {elapsed:.1f} 秒")
    
    if r.status_code == 200:
        data = r.json()
        print(f"狀態: {data.get('status')}")
        print(f"\n報告生成結果:")
        
        reports = data.get('reports_generated', {})
        errors = data.get('generation_errors', {})
        
        for system in ['name', 'numerology', 'bazi', 'ziwei', 'astrology']:
            status = "✅" if reports.get(system) else "❌"
            error = errors.get(system, '')
            error_msg = f" ({error[:50]}...)" if error else ""
            print(f"  {system:12} {status}{error_msg}")
        
        return data
    else:
        print(f"失敗: {r.status_code}")
        print(r.text[:500])
        return None

def test_get_reports(user_id, token):
    """測試獲取報告"""
    print_section("4. 獲取報告 (reports/get)")
    
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/reports/get?user_id={user_id}", 
                     headers=headers, timeout=30)
    
    if r.status_code == 200:
        data = r.json()
        print(f"找到報告: {data.get('found')}")
        print(f"可用系統: {data.get('available_systems')}")
        
        reports = data.get('reports', {})
        for system, report_data in reports.items():
            report = report_data.get('report', {})
            analysis = report.get('analysis', '')
            print(f"\n  【{system}】")
            print(f"    分析長度: {len(analysis)} 字元")
            if analysis:
                preview = analysis[:200].replace('\n', ' ')
                print(f"    預覽: {preview}...")
        
        return reports
    else:
        print(f"失敗: {r.status_code}")
        return None

def test_individual_apis(user_id, token):
    """測試各系統獨立 API"""
    print_section("5. 測試各系統獨立 API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 5.1 姓名學
    print("\n  【姓名學 API】")
    r = requests.post(f"{BASE_URL}/api/name/analyze", json={
        "name": TEST_USER["chinese_name"],
        "analysis_type": "basic",
        "include_ai": True
    }, headers=headers, timeout=120)
    if r.status_code == 200:
        data = r.json().get('data', {})
        print(f"    五格: 天格{data.get('天格', {}).get('數理')} "
              f"人格{data.get('人格', {}).get('數理')} "
              f"地格{data.get('地格', {}).get('數理')} "
              f"外格{data.get('外格', {}).get('數理')} "
              f"總格{data.get('總格', {}).get('數理')}")
        print(f"    AI解讀: {len(data.get('ai_interpretation', ''))} 字元")
    else:
        print(f"    失敗: {r.status_code} - {r.text[:100]}")
    
    # 5.2 靈數學
    print("\n  【靈數學 API】")
    r = requests.post(f"{BASE_URL}/api/numerology/profile", json={
        "birth_date": TEST_USER["birth_date"],
        "full_name": "CHEN YU CHU",
        "analysis_type": "full"
    }, headers=headers, timeout=120)
    if r.status_code == 200:
        data = r.json().get('data', {})
        print(f"    生命靈數: {data.get('life_path')}")
        print(f"    AI解讀: {len(data.get('interpretation', ''))} 字元")
    else:
        print(f"    失敗: {r.status_code} - {r.text[:100]}")
    
    # 5.3 八字
    print("\n  【八字 API】")
    r = requests.post(f"{BASE_URL}/api/bazi/analysis", json={
        "user_id": user_id,
        "year": 1979,
        "month": 11,
        "day": 12,
        "hour": 23,
        "minute": 58,
        "gender": "male"
    }, headers=headers, timeout=120)
    if r.status_code == 200:
        data = r.json().get('data', {})
        chart = data.get('bazi_chart', {})
        pillars = chart.get('四柱', {})
        print(f"    四柱: {pillars.get('年柱', {}).get('天干', '')}{pillars.get('年柱', {}).get('地支', '')} "
              f"{pillars.get('月柱', {}).get('天干', '')}{pillars.get('月柱', {}).get('地支', '')} "
              f"{pillars.get('日柱', {}).get('天干', '')}{pillars.get('日柱', {}).get('地支', '')} "
              f"{pillars.get('時柱', {}).get('天干', '')}{pillars.get('時柱', {}).get('地支', '')}")
        print(f"    AI分析: {len(data.get('analysis', ''))} 字元")
    else:
        print(f"    失敗: {r.status_code} - {r.text[:100]}")
    
    # 5.4 紫微斗數
    print("\n  【紫微斗數 API】")
    r = requests.post(f"{BASE_URL}/api/chart/initial-analysis", json={
        "user_id": user_id,
        "birth_date": TEST_USER["birth_date"],
        "birth_time": TEST_USER["birth_time"],
        "birth_location": TEST_USER["birth_location"],
        "gender": TEST_USER["gender"]
    }, headers=headers, timeout=180)
    if r.status_code == 200:
        data = r.json()
        structure = data.get('structure', {})
        ming = structure.get('命宮', {})
        print(f"    命宮: {ming.get('宮位')}宮 - {ming.get('主星', [])}")
        print(f"    五行局: {structure.get('五行局')}")
        print(f"    格局: {structure.get('格局', [])}")
    else:
        print(f"    失敗: {r.status_code} - {r.text[:100]}")
    
    # 5.5 西洋占星
    print("\n  【西洋占星 API】")
    r = requests.post(f"{BASE_URL}/api/astrology/natal", json={
        "name": TEST_USER["chinese_name"],
        "year": 1979,
        "month": 11,
        "day": 12,
        "hour": 23,
        "minute": 58,
        "city": "彰化市"
    }, headers=headers, timeout=180)
    if r.status_code == 200:
        data = r.json().get('data', {})
        chart = data.get('natal_chart', {})
        print(f"    太陽: {chart.get('sun', {}).get('sign')}")
        print(f"    月亮: {chart.get('moon', {}).get('sign')}")
        print(f"    上升: {chart.get('ascendant', {}).get('sign')}")
        print(f"    AI分析: {len(data.get('analysis', ''))} 字元")
    else:
        print(f"    失敗: {r.status_code} - {r.text[:100]}")
    
    # 5.6 塔羅牌
    print("\n  【塔羅牌 API】")
    r = requests.post(f"{BASE_URL}/api/tarot/draw", json={
        "spread_type": "single",
        "question": "今日運勢如何？"
    }, headers=headers, timeout=60)
    if r.status_code == 200:
        data = r.json().get('data', {})
        cards = data.get('cards', [])
        if cards:
            card = cards[0]
            print(f"    抽到: {card.get('name')} ({card.get('name_en')})")
            print(f"    正逆位: {'逆位' if card.get('reversed') else '正位'}")
    else:
        print(f"    失敗: {r.status_code} - {r.text[:100]}")

def validate_report_quality(reports):
    """從命理老師觀點驗證報告品質"""
    print_section("6. 報告品質驗證 (命理老師觀點)")
    
    quality_checks = {
        'ziwei': {
            'name': '紫微斗數',
            'required_elements': ['命宮', '五行局', '十二宮', '四化', '格局'],
            'min_analysis_length': 1000
        },
        'bazi': {
            'name': '八字命理',
            'required_elements': ['四柱', '日主', '五行', '用神', '大運'],
            'min_analysis_length': 1000
        },
        'astrology': {
            'name': '西洋占星',
            'required_elements': ['太陽', '月亮', '上升', '行星', '宮位'],
            'min_analysis_length': 1000
        },
        'numerology': {
            'name': '靈數學',
            'required_elements': ['生命靈數', '天賦數', '命運數'],
            'min_analysis_length': 500
        },
        'name': {
            'name': '姓名學',
            'required_elements': ['天格', '人格', '地格', '總格', '五行'],
            'min_analysis_length': 500
        }
    }
    
    results = {}
    
    for system, checks in quality_checks.items():
        print(f"\n  【{checks['name']}】")
        report_data = reports.get(system, {})
        report = report_data.get('report', {})
        analysis = report.get('analysis', '')
        
        # 檢查分析長度
        length_ok = len(analysis) >= checks['min_analysis_length']
        print(f"    分析長度: {len(analysis)} 字元 "
              f"(需要 >= {checks['min_analysis_length']}) "
              f"{'✅' if length_ok else '❌'}")
        
        # 檢查必要元素
        found_elements = []
        missing_elements = []
        for element in checks['required_elements']:
            if element in analysis or element in str(report):
                found_elements.append(element)
            else:
                missing_elements.append(element)
        
        elements_ok = len(missing_elements) == 0
        print(f"    必要元素: {len(found_elements)}/{len(checks['required_elements'])} "
              f"{'✅' if elements_ok else '❌'}")
        if missing_elements:
            print(f"      缺少: {missing_elements}")
        
        # 檢查是否有實質內容（非模板文字）
        content_ok = len(set(analysis.split())) > 50 if analysis else False
        print(f"    內容豐富度: {'✅' if content_ok else '❌'}")
        
        results[system] = {
            'length_ok': length_ok,
            'elements_ok': elements_ok,
            'content_ok': content_ok,
            'overall': length_ok and elements_ok and content_ok
        }
    
    return results

def main():
    print("\n" + "="*60)
    print("  Aetheria Core - 完整流程測試")
    print("  測試時間:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # 1. 健康檢查
    if not test_health():
        print("後端服務未運行，請先啟動服務")
        return
    
    # 2. 註冊登入
    user_id, token = test_register_and_login()
    if not user_id:
        print("註冊失敗")
        return
    
    # 3. 儲存並生成報告
    result = test_save_and_analyze(user_id, token)
    
    # 4. 獲取報告
    reports = test_get_reports(user_id, token)
    
    # 5. 測試獨立 API
    test_individual_apis(user_id, token)
    
    # 6. 品質驗證
    if reports:
        quality = validate_report_quality(reports)
        
        print_section("7. 測試總結")
        print(f"\n  用戶 ID: {user_id}")
        print(f"\n  批次生成結果:")
        if result:
            for system, ok in result.get('reports_generated', {}).items():
                print(f"    {system}: {'✅' if ok else '❌'}")
        
        print(f"\n  品質驗證:")
        for system, q in quality.items():
            print(f"    {system}: {'✅ 通過' if q['overall'] else '❌ 需改進'}")
        
        all_passed = all(q['overall'] for q in quality.values())
        print(f"\n  整體評估: {'✅ 全部通過' if all_passed else '⚠️ 部分需要改進'}")

if __name__ == "__main__":
    main()
