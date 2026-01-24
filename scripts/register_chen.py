import json
import os
from datetime import datetime

# Load existing users
file_path = 'data/users.json'
with open(file_path, 'r', encoding='utf-8') as f:
    users = json.load(f)

# Define Chen Youzhu
# Confirmed: 1979/11/12 23:30 (Wan Zi -> Gui Wei Day)
# Note: Python datetime for 23:30 is standard. Our bazi calculator confirms this maps to Gui Wei.
# However, we must ensure the "Hour Pillar" interpretation is noted if ambiguous.
# User confirmed "Gentle/Refined/Emotional" -> Gui Water.

chen_data = {
    "user_id": "chen_youzhu",
    "name": "陳宥竹",
    "gender": "男",
    "birth_year": 1979,
    "birth_month": 11,
    "birth_day": 12,
    "birth_time": "23:30",
    "birth_location": "彰化市",
    "longitude": 120.54,
    "latitude": 24.08,
    "rectification_notes": {
        "confirmed_chart": "晚子時 (當日癸未日)",
        "traits_confirmation": "心思婉轉(屬水)、情緒豐富、斯文(180cm/78kg)、三個女兒",
        "career": "2011(辛卯)年後創業顧問，符合食神/偏財流年",
        "life_path": "人生順遂(身強/身弱喜用配合得宜)"
    },
    "created_at": datetime.now().isoformat()
}

users['chen_youzhu'] = chen_data

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=2)

print("Chen Youzhu registered successfully.")
