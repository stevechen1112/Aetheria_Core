#!/usr/bin/env python3
"""
張乃文女士 命理分析腳本
出生日期: 1979年10月23日（國曆）
出生地點: 台灣台北市
性別: 女
"""

import sys
sys.path.insert(0, '/Users/yuchuchen/Desktop/Aetheria_Core')

from src.calculators.numerology import NumerologyCalculator
from src.calculators.name import NameCalculator
from src.calculators.astrology import AstrologyCalculator
from src.calculators.bazi import BaziCalculator
from datetime import datetime

print("=" * 80)
print("張乃文女士 命理分析報告".center(80))
print("=" * 80)
print(f"\n基本資料:")
print(f"  姓名: 張乃文")
print(f"  性別: 女")
print(f"  出生日期: 1979年10月23日（國曆）")
print(f"  出生地點: 台灣台北市")
print(f"  經緯度: 121.5654° E, 25.0330° N")

# ============================================================================
# 第一部分：靈數學分析（不需時辰）
# ============================================================================
print("\n" + "=" * 80)
print("【第一部分】靈數學分析（不需出生時間）".center(70))
print("=" * 80)

calc_num = NumerologyCalculator()
birth_date = datetime(1979, 10, 23)
# Use Pinyin for Pythagorean Numerology
profile = calc_num.calculate_full_profile(birth_date, "ZHANG NAI WEN")

print(f"\n核心靈數:")
print(f"  生命靈數: {profile.life_path}")
print(f"  天賦數: {profile.expression}")
print(f"  靈魂數: {profile.soul_urge}")
print(f"  人格數: {profile.personality}")
print(f"  生日數: {profile.birthday}")
# print(f"  成熟數: {profile.maturity}") # Not available in current version

# 生命靈數詳解
meaning = calc_num.get_number_meaning(profile.life_path)
print(f"\n生命靈數 {profile.life_path} 特質:")
print(f"  關鍵詞: {meaning['keywords']}")
print(f"  正面特質: {', '.join(meaning.get('positive_traits', [])[:5])}")
print(f"  挑戰特質: {', '.join(meaning.get('negative_traits', [])[:3])}")
print(f"  適合職業: {', '.join(meaning.get('career', [])[:5])}")
print(f"  生命課題: {meaning.get('life_lesson', '未知')}")

# 2026年流年
personal_year, _, _ = calc_num.calculate_personal_year(birth_date, 2026)
year_meaning = calc_num.get_number_meaning(personal_year, number_type="personal_year")
print(f"\n2026年個人年: {personal_year}")
print(f"  主題: {year_meaning.get('theme', '未知')}")
print(f"  關鍵詞: {year_meaning.get('keywords', '未知')}")

# ============================================================================
# 第二部分：姓名學分析（不需時辰）
# ============================================================================
print("\n" + "=" * 80)
print("【第二部分】姓名學分析（不需出生時間）".center(70))
print("=" * 80)

calc_name = NameCalculator()
name_analysis = calc_name.analyze("張乃文")

print(f"\n五格數理:")
print(f"  天格: {name_analysis.five_grids.天格} ({name_analysis.grid_analyses['天格'].fortune})")
print(f"  人格: {name_analysis.five_grids.人格} ({name_analysis.grid_analyses['人格'].fortune})")
print(f"  地格: {name_analysis.five_grids.地格} ({name_analysis.grid_analyses['地格'].fortune})")
print(f"  外格: {name_analysis.five_grids.外格} ({name_analysis.grid_analyses['外格'].fortune})")
print(f"  總格: {name_analysis.five_grids.總格} ({name_analysis.grid_analyses['總格'].fortune})")

print(f"\n三才配置: {name_analysis.three_talents['combination']}")
print(f"  吉凶: {name_analysis.three_talents['fortune']}")

# 人格主運
ren_ge = name_analysis.grid_analyses['人格']
print(f"\n人格 {ren_ge.number} 主運解讀:")
print(f"  五行: {ren_ge.element}")
print(f"  含義: {ren_ge.description}")
print(f"  關鍵詞: {', '.join(ren_ge.keywords)}")

# ============================================================================
# 第三部分：西洋占星分析（定盤確認）
# ============================================================================
print("\n" + "=" * 80)
print("【第三部分】西洋占星分析（定盤時間：04:00）".center(70))
print("=" * 80)

calc_astro = AstrologyCalculator()

# 使用確認時間 04:00
natal_chart = calc_astro.calculate_natal_chart(
    name="張乃文",
    year=1979,
    month=10,
    day=23,
    hour=4,
    minute=0,
    city="Taipei",
    nation="TW",
    longitude=121.5654,
    latitude=25.0330,
    timezone_str="Asia/Taipei"
)

print(f"\n主要行星位置:")
for planet_key in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
    if planet_key in natal_chart['planets']:
        planet = natal_chart['planets'][planet_key]
        retro = "（逆行）" if planet['retrograde'] else ""
        print(f"  {planet['name_zh']}: {planet['sign_zh']} {planet['degree']:.1f}° {retro} (第 {planet.get('house', '?')} 宮)")

print(f"\n上升星座 (ASC): {natal_chart.get('houses', {}).get(1, {}).get('sign_zh', '計算中')} (第一宮起點)")

print(f"\n元素分佈:")
for element, count in natal_chart['elements'].items():
    print(f"  {element}: {count}")

print(f"\n特質分佈:")
for quality, count in natal_chart['qualities'].items():
    print(f"  {quality}: {count}")

print(f"\n主導元素: {natal_chart['dominant_element']}")
print(f"主導特質: {natal_chart['dominant_quality']}")

# ============================================================================
# 第四部分：八字分析（定盤確認：丙寅時）
# ============================================================================
print("\n" + "=" * 80)
print("【第四部分】八字與定盤分析（確認時辰：丙寅時 03:00-05:00）".center(70))
print("=" * 80)

calc_bazi = BaziCalculator()

# 定盤時辰：1979-10-23 04:00 (丙寅時)
confirmed_hour = 4 

bazi = calc_bazi.calculate_bazi(
    year=1979,
    month=10,
    day=23,
    hour=confirmed_hour,
    minute=0,
    gender="女",
    longitude=121.5654,
    use_apparent_solar_time=True
)

# 處理簡繁體金鑰相容性
try:
    strength = bazi['強弱']['結論'] 
except KeyError:
    strength = bazi['強弱'].get('结论', '未知')

print(f"\n【命盤結構】")
print(f"定盤依據: 外強中乾性格、飲酒習慣(缺水補水)、2017離異(傷官見官)、2026忙碌(三合火局)。")
print(f"驗證確認: 育有一女(高一)一子(國二)，皆聰明好學(食傷吐秀)，與子關係緊密(寅亥合)。")
print(f"格局: 傷官生財格 (時干透丙火，坐寅木長生)")

print(f"\n四柱八字:")
print(f"  年柱: {bazi['四柱']['年柱']['天干']}{bazi['四柱']['年柱']['地支']} - [十神: {bazi['四柱']['年柱']['十神']}]")
print(f"  月柱: {bazi['四柱']['月柱']['天干']}{bazi['四柱']['月柱']['地支']} - [十神: {bazi['四柱']['月柱']['十神']}]")
print(f"  日柱: {bazi['四柱']['日柱']['天干']}{bazi['四柱']['日柱']['地支']} - [日元: {bazi['日主']['天干']}]")
print(f"  時柱: {bazi['四柱']['時柱']['天干']}{bazi['四柱']['時柱']['地支']} - [十神: {bazi['四柱']['時柱']['十神']}]")

print(f"\n原本特質解讀:")
print(f"  1. 日主{bazi['日主']['天干']}({bazi['日主']['五行']})：本質溫柔敏感，內在細膩。")
print(f"  2. 身強身弱：{strength}。生於戌月土旺，日支午火耗身，時柱丙寅火木洩氣。")
print(f"     -> 極度身弱。內心缺乏安全感，抗壓性較低。")
print(f"  3. 外在表現(時柱)：丙火(太陽)。")
print(f"     -> 給人熱情、強勢、有能力的印象。這是您的「保護色」。")

# ============================================================================
# 第五部分：2026年運勢前瞻與建議
# ============================================================================
print("\n" + "=" * 80)
print("【第五部分】2026年 (丙午年) 運勢前瞻與建議".center(70))
print("=" * 80)

print("流年: 丙午 (天干丙火 / 地支午火)")

print("\n1. 核心現象：寅午戌 三合火局")
print("   - 流年午(馬) + 月支戌(狗) + 時支寅(虎) -> 合成巨大的「火」能量。")
print("   - 火為癸水之「財星」。")
print("   - 解讀：事業宮(時)、父母/內心宮(月) 全被引動。")
print("   - 預測：極度忙碌，工作量爆炸，業務機會大增。是展現能力的高峰期。")

print("\n2. 風險預警：財多身弱 & 午午自刑")
print("   - 財(火)太旺，日主(水)太弱 -> 『富屋貧人』之象，看得到吃不到，或為了賺錢賠上健康。")
print("   - 自刑 (午午)：容易自我糾結、鑽牛角尖、情緒內耗。")

print("\n3. 關鍵建議：")
print("   [健康]：火炎土燥，水被燒乾。")
print("        -> 注意腎臟、泌尿系統、婦科、血液循環。")
print("        -> 避免過度飲酒 (酒雖是水，但乙醇生火)，改喝溫水、花草茶。")
print("   [心態]：承認自己的脆弱，不需要時時刻刻當強人。")
print("   [開運]：多接觸「水」元素 (游泳、海邊、黑色衣物、藍寶石)。")

print("\n" + "=" * 80)
print("詳細分析報告結束".center(80))
print("=" * 80)
