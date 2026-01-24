import json
import os
from datetime import datetime

file_path = 'data/users.json'
with open(file_path, 'r', encoding='utf-8') as f:
    users = json.load(f)

# Update Zhang Naiwen to explicitly confirm Option A verification
if 'zhang_naiwen' in users:
    users['zhang_naiwen']['rectification_notes']['final_confirmation'] = "User verified Option A: 2025 Nobleman Help (Safe), 2017 Clash (Conflict), Good with Children."

# Ensure Chen Youzhu is also fully secure in the file (already done in previous step but good to save together)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=2)

print("Zhang Naiwen locked as Option A (Mao Hour).")
