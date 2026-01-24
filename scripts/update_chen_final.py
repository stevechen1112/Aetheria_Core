import json
import os

file_path = 'data/users.json'

with open(file_path, 'r', encoding='utf-8') as f:
    users = json.load(f)

# Update Chen's data with final confirmations
if 'chen_youzhu' in users:
    users['chen_youzhu']['rectification_notes'].update({
        "health_confirmation": "胃腸(消化)與泌尿(腎)有問題 -> 應證「未土剋癸水」",
        "sleep_pattern": "一覺到天亮/打呼/沉睡 -> 應證「墓庫(未)」收藏特性，或食傷洩秀後的深層休息",
        "children": "三個女兒 -> 應證「全陰盤」(己未/乙亥/癸未) 易生女及正官/七殺變曜",
        "final_verdict": "A盤：當日晚子時 (癸未日 壬子時 或 庚子時 依派別，確認為癸水日主)"
    })

# Save
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=2)

print("Updated Chen Youzhu's validation data.")
