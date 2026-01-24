import json
import os
from datetime import datetime

file_path = 'data/users.json'

def save_user():
    # Load existing
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                users = json.load(f)
            except:
                users = {}
    else:
        users = {}

    # Define Zhang Naiwen
    zhang_id = 'zhang_naiwen'
    users[zhang_id] = {
        'user_id': zhang_id,
        'name': '張乃文',
        'gender': '女',
        'birth_year': 1979,
        'birth_month': 10,
        'birth_day': 23,
        'birth_time': '04:00', # Rectified
        'birth_location': '台北市',
        'longitude': 121.5654,
        'latitude': 25.0330,
        'rectification_notes': {
            'confirmed_hour': '丙寅時 (03:00-05:00)',
            'key_events': [
                '2008結婚',
                '2017離異', 
                '2020-2023感情空白(重心在子)',
                '2026預計忙碌(三合火局)'
            ],
            'habits': '飲酒(缺水補償)',
            'children': '一女(高一)一子(國二)，與子關係緊密(寅亥合)'
        },
        'created_at': datetime.now().isoformat()
    }

    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    print(f'Successfully saved user {zhang_id} to {file_path}')

if __name__ == '__main__':
    save_user()
