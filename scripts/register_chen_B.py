import json
import os
from datetime import datetime

# Load existing users
file_path = 'data/users.json'
with open(file_path, 'r', encoding='utf-8') as f:
    users = json.load(f)

# Define Chen Youzhu - CHART B (Corrected)
# Input: 1979/11/12 23:58 -> Late Zi -> Next Day (Nov 13)
# Day Pillar: Jia Shen (甲申)
# Ziwei: Tai Yin in Xu
# Traits: 180cm (Jia Wood tall), Gentle/Refined (Tai Yin), 3 Daughters (Tai Yin Female Affinity)

chen_data = {
    "user_id": "chen_youzhu",
    "name": "陳宥竹",
    "gender": "男",
    "birth_year": 1979,
    "birth_month": 11,
    "birth_day": 12,
    "birth_time": "23:58",
    "birth_location": "彰化市",
    "longitude": 120.54,
    "latitude": 24.08,
    "rectification_notes": {
        "confirmed_chart": "B盤：早子/隔日 (甲申日)",
        "ziwei_code": "命宮戌(太陰) 遷移辰(太陽+文曲忌) 夫妻申(武曲+天相)",
        "traits_match": {
            "tall": "180cm -> 甲木棟樑 (木主高長)",
            "gentle": "心思婉轉 -> 命宮太陰 (月亮星，主細膩、陰柔、以柔克剛)",
            "children": "三個女兒 -> 命坐太陰(女星)，且田宅/子女宮位見紅鸞/天喜或陰星群聚",
            "health": "胃腸/泌尿 -> B盤遷移宮文曲化忌(水)沖命，或甲木坐申金(絕地)肝膽受剋影響脾胃"
        },
        "life_event": "2011(辛卯)創業 -> 甲木見卯為羊刃/帝旺根基，辛金為正官(事業)來合，名利雙收"
    },
    "created_at": datetime.now().isoformat()
}

users['chen_youzhu'] = chen_data

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=2)

print("Updated Chen Youzhu to Chart B (Jia Shen).")
