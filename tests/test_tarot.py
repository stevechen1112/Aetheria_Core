"""
塔羅牌系統測試腳本
測試主要功能：
1. 塔羅牌解讀 (reading)
2. 每日一牌 (daily)
3. 牌陣列表 (spreads)
4. 牌卡資訊 (card)
"""

import requests
import json
from datetime import datetime
import time

# API 基礎地址
BASE_URL = "http://localhost:5001"


def print_section(title):
    """打印分節標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_daily():
    """測試1：每日一牌（需要 AI 解讀，約 20-40 秒）"""
    print_section("測試 1/4：每日一牌")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 20-40 秒...")
    
    url = f"{BASE_URL}/api/tarot/daily"
    
    print(f"\n發送請求時間：{datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    response = requests.get(url, timeout=120)
    duration = time.time() - start_time
    
    print(f"回應時間：{duration:.1f} 秒")
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 每日一牌成功！")
            
            # 顯示抽到的牌
            card = data.get('card', {})
            if card:
                print(f"\n  今日指引牌：")
                print(f"    牌名：{card.get('name', '未知')}")
                print(f"    英文名：{card.get('name_en', '未知')}")
                print(f"    正逆位：{'逆位' if card.get('reversed') else '正位'}")
                print(f"    類型：{card.get('type', '未知')}")
            
            # 顯示 AI 解讀
            if 'interpretation' in data:
                interpretation = data['interpretation']
                print(f"\n  AI 解讀長度：{len(interpretation)} 字符")
                print(f"\n今日指引：")
                print("-" * 60)
                print(interpretation[:300] + "..." if len(interpretation) > 300 else interpretation)
                print("-" * 60)
            
            return True, data
        else:
            print(f"\n✗ 抽牌失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_reading():
    """測試2：塔羅牌解讀（三張牌陣，需要 AI 解讀，約 30-60 秒）"""
    print_section("測試 2/4：塔羅牌解讀（三張牌陣）")
    print("\n提示：此測試需要調用 Gemini AI，預計耗時 30-60 秒...")
    
    url = f"{BASE_URL}/api/tarot/reading"
    
    test_data = {
        "spread_type": "three_card",
        "question": "接下來的事業發展如何？",
        "context": "career",
        "allow_reversed": True
    }
    
    print(f"\n牌陣類型：三張牌（過去-現在-未來）")
    print(f"問題：{test_data['question']}")
    print(f"情境：{test_data['context']}")
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
            
            print(f"\n✓ 塔羅解讀成功！")
            print(f"\n  牌陣名稱：{data.get('spread_name', '未知')}")
            print(f"  解讀 ID：{data.get('reading_id', '未知')}")
            
            # 顯示抽到的牌
            cards = data.get('cards', [])
            if cards:
                print(f"\n  抽到的牌：")
                for card in cards:
                    position = card.get('position', '未知')
                    name = card.get('name', '未知')
                    reversed_str = '（逆位）' if card.get('reversed') else '（正位）'
                    print(f"    {position}：{name} {reversed_str}")
            
            # 顯示 AI 解讀
            if 'interpretation' in data:
                interpretation = data['interpretation']
                print(f"\n  AI 解讀長度：{len(interpretation)} 字符")
                print(f"\n解讀預覽（前 300 字）：")
                print("-" * 60)
                print(interpretation[:300] + "...")
                print("-" * 60)
                
                # 保存完整解讀
                filename = f"tarot_reading_{datetime.now().strftime('%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"塔羅牌解讀報告\n{'='*60}\n")
                    f.write(f"牌陣：{data.get('spread_name', '未知')}\n")
                    f.write(f"問題：{test_data['question']}\n")
                    f.write(f"解讀時間：{data.get('timestamp', datetime.now().isoformat())}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write("抽到的牌：\n")
                    for card in cards:
                        position = card.get('position', '未知')
                        name = card.get('name', '未知')
                        reversed_str = '（逆位）' if card.get('reversed') else '（正位）'
                        f.write(f"  {position}：{name} {reversed_str}\n")
                    f.write(f"\n{'='*60}\n\n")
                    f.write(interpretation)
                print(f"\n完整解讀已保存：{filename}")
            
            return True, data
        else:
            print(f"\n✗ 解讀失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_spreads():
    """測試3：牌陣列表（快速）"""
    print_section("測試 3/4：牌陣列表")
    
    url = f"{BASE_URL}/api/tarot/spreads"
    
    response = requests.get(url)
    
    print(f"\n狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 牌陣列表取得成功！")
            
            spreads = data.get('spreads', [])
            if isinstance(spreads, dict):
                spreads = [
                    {
                        'type': spread_type,
                        'name': spread_info.get('name', spread_type),
                        'name_en': spread_info.get('name_en', '未知'),
                        'cards': len(spread_info.get('positions', []))
                    }
                    for spread_type, spread_info in spreads.items()
                ]
            if spreads:
                print(f"\n  可用牌陣（共 {len(spreads)} 種）：")
                for spread in spreads:
                    name = spread.get('name', '未知')
                    name_en = spread.get('name_en', '未知')
                    cards = spread.get('cards', '未知')
                    print(f"    - {name}（{name_en}）- {cards} 張牌")
            
            return True, data
        else:
            print(f"\n✗ 取得失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def test_card_info():
    """測試4：牌卡資訊（快速）"""
    print_section("測試 4/4：牌卡資訊")
    
    # 查詢愚者牌（ID = 0）
    card_id = 0
    url = f"{BASE_URL}/api/tarot/card/{card_id}"
    
    print(f"\n查詢牌卡 ID：{card_id}")
    
    response = requests.get(url)
    
    print(f"狀態碼：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print(f"\n✓ 牌卡資訊取得成功！")
            
            print(f"\n  牌名：{data.get('name', '未知')}")
            print(f"  英文名：{data.get('name_en', '未知')}")
            print(f"  編號：{data.get('number', '未知')}")
            print(f"  類型：{data.get('type', '未知')}")
            
            # 正位意義
            upright = data.get('upright_meaning', {})
            if upright:
                keywords = upright.get('keywords', [])
                if keywords:
                    print(f"\n  正位關鍵詞：{', '.join(keywords)}")
            
            # 逆位意義
            reversed_meaning = data.get('reversed_meaning', {})
            if reversed_meaning:
                keywords = reversed_meaning.get('keywords', [])
                if keywords:
                    print(f"  逆位關鍵詞：{', '.join(keywords)}")
            
            return True, data
        else:
            print(f"\n✗ 取得失敗：{result.get('message', '未知錯誤')}")
            return False, None
    else:
        print(f"\n✗ 請求失敗：{response.text}")
        return False, None


def run_all_tests():
    """運行所有測試"""
    print("\n" + "=" * 60)
    print("  塔羅牌系統功能測試")
    print("  時間：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    results = []
    
    # 測試1：每日一牌
    success, _ = test_daily()
    results.append(("每日一牌", success))
    
    # 測試2：塔羅牌解讀
    success, _ = test_reading()
    results.append(("塔羅牌解讀", success))
    
    # 測試3：牌陣列表
    success, _ = test_spreads()
    results.append(("牌陣列表", success))
    
    # 測試4：牌卡資訊
    success, _ = test_card_info()
    results.append(("牌卡資訊", success))
    
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
