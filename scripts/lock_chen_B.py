import json
import os
from datetime import datetime

file_path = 'data/users.json'
with open(file_path, 'r', encoding='utf-8') as f:
    users = json.load(f)

# Final Lock for Chen Youzhu (Chart B)
# 1979/11/13 00:00+ (Legal 11/12 23:58 treated as Next Day Early Zi)
# Bazi: Ji Wei / Yi Hai / Jia Shen / Jia Zi

if 'chen_youzhu' in users:
    users['chen_youzhu']['rectification_notes'] = {
        "final_verdict": "B盤 (甲申日/早子時)",
        "confirmed_traits": "母親強勢/支柱, 金錢務實, 太太賢內助, 180cm, 生女",
        "bazi_structure": "年(己未) 月(乙亥) 日(甲申) 時(甲子)",
        "ziwei_structure": "命宮(戌)太陰 遷移(辰)太陽",
        "user_feedback": "B盤很準 (金錢務實/家族體制型/賢內助)"
    }
    # Update birth time to logical next day 00:00 for simple calculators if needed, 
    # but keep original string "23:58" for record.
    # We will use the Bazi structure directly for analysis.

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=2)

print("Finalized Chen Youzhu as Chart B (Jia Shen).")
