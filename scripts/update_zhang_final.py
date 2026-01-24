import json
import os
from datetime import datetime

file_path = 'data/users.json'

def update_zhang_naiwen():
    # Load existing
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                users = json.load(f)
            except:
                users = {}
    else:
        users = {}

    # Define Zhang Naiwen with Updated Time
    zhang_id = 'zhang_naiwen'
    users[zhang_id] = {
        'user_id': zhang_id,
        'name': '張乃文',
        'gender': '女',
        'birth_year': 1979,
        'birth_month': 10,
        'birth_day': 23,
        'birth_time': '06:00', # FINAL RECTIFICATION: Ding Mao
        'birth_location': '台北市',
        'longitude': 121.5654,
        'latitude': 25.0330,
        'rectification_notes': {
            'confirmed_hour': '丁卯時 (05:00-07:00)',
            'reasoning': '2017卯酉沖(桃花外遇離異) + 2025木生火(雙貴人化解官司虛驚)',
            'key_events': [
                '2017離異：前夫外遇，應證卯酉桃花正沖', 
                '2025事業：在職碩士畢業+升高階主管，應證卯巳相生貴人運',
                '2025官司：紫微預測有誤，實則無事，應證非寅時(無寅巳相刑)'
            ],
            'habits': '飲酒(八字缺水)',
            'children': '一女一子，卯木食神得位，子女優秀'
        },
        'created_at': datetime.now().isoformat()
    }

    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    print(f'Successfully updated user {zhang_id} to {file_path}')

if __name__ == '__main__':
    update_zhang_naiwen()
