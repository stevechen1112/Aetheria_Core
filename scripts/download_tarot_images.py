#!/usr/bin/env python3
"""
下載 Rider-Waite 塔羅牌圖片到本地
來源：sacred-texts.com (公有領域)
"""

import os
import requests
import time

# 目標資料夾
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'public', 'tarot')

# 基礎 URL
BASE_URL = "https://www.sacred-texts.com/tarot/pkt/img/"

# 大阿爾克那 (22張)
MAJOR_ARCANA = {
    'ar00': '00_The_Fool',
    'ar01': '01_The_Magician',
    'ar02': '02_The_High_Priestess',
    'ar03': '03_The_Empress',
    'ar04': '04_The_Emperor',
    'ar05': '05_The_Hierophant',
    'ar06': '06_The_Lovers',
    'ar07': '07_The_Chariot',
    'ar08': '08_Strength',
    'ar09': '09_The_Hermit',
    'ar10': '10_Wheel_of_Fortune',
    'ar11': '11_Justice',
    'ar12': '12_The_Hanged_Man',
    'ar13': '13_Death',
    'ar14': '14_Temperance',
    'ar15': '15_The_Devil',
    'ar16': '16_The_Tower',
    'ar17': '17_The_Star',
    'ar18': '18_The_Moon',
    'ar19': '19_The_Sun',
    'ar20': '20_Judgement',
    'ar21': '21_The_World',
}

# 小阿爾克那花色
SUITS = {
    'wa': 'Wands',    # 權杖
    'cu': 'Cups',     # 聖杯
    'sw': 'Swords',   # 寶劍
    'pe': 'Pentacles' # 錢幣
}

# 小阿爾克那牌號
MINOR_NUMBERS = {
    'ac': 'Ace',
    '02': 'Two',
    '03': 'Three',
    '04': 'Four',
    '05': 'Five',
    '06': 'Six',
    '07': 'Seven',
    '08': 'Eight',
    '09': 'Nine',
    '10': 'Ten',
    'pa': 'Page',
    'kn': 'Knight',
    'qu': 'Queen',
    'ki': 'King',
}

def download_image(url, filepath, retries=3):
    """下載單張圖片，支援重試"""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return False
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            print(f"({e})", end=" ")
            return False
    return False

def main():
    # 建立資料夾
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    total = 78
    downloaded = 0
    failed = []
    
    print("=" * 50)
    print("🎴 開始下載 Rider-Waite 塔羅牌圖片")
    print("=" * 50)
    print(f"目標資料夾: {os.path.abspath(OUTPUT_DIR)}")
    print()
    
    # 下載大阿爾克那
    print("📦 大阿爾克那 (Major Arcana) - 22張")
    print("-" * 40)
    for code, name in MAJOR_ARCANA.items():
        url = f"{BASE_URL}{code}.jpg"
        filename = f"{name}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"  ⏭️  已存在: {filename}")
            downloaded += 1
            continue
            
        print(f"  ⬇️  下載中: {filename}...", end=" ", flush=True)
        if download_image(url, filepath):
            print("✅")
            downloaded += 1
        else:
            failed.append(filename)
        time.sleep(0.3)  # 避免請求過快
    
    print()
    
    # 下載小阿爾克那
    print("📦 小阿爾克那 (Minor Arcana) - 56張")
    print("-" * 40)
    for suit_code, suit_name in SUITS.items():
        print(f"\n  🎴 {suit_name} (14張)")
        for num_code, num_name in MINOR_NUMBERS.items():
            code = f"{suit_code}{num_code}"
            url = f"{BASE_URL}{code}.jpg"
            filename = f"{num_name}_of_{suit_name}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            if os.path.exists(filepath):
                print(f"    ⏭️  已存在: {filename}")
                downloaded += 1
                continue
                
            print(f"    ⬇️  下載中: {filename}...", end=" ", flush=True)
            if download_image(url, filepath):
                print("✅")
                downloaded += 1
            else:
                failed.append(filename)
            time.sleep(0.3)
    
    # 結果報告
    print()
    print("=" * 50)
    print("📊 下載完成報告")
    print("=" * 50)
    print(f"✅ 成功: {downloaded}/{total}")
    if failed:
        print(f"❌ 失敗: {len(failed)}")
        for f in failed:
            print(f"   - {f}")
    else:
        print("🎉 全部下載成功！")
    print()
    print(f"圖片位置: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()
