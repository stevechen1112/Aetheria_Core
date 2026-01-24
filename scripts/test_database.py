#!/usr/bin/env python3
"""測試 SQLite 資料庫模組"""

from src.utils.database import AetheriaDatabase
import os

# 測試用資料庫
db = AetheriaDatabase('data/test_aetheria.db')

# 測試創建用戶
user_data = {
    'user_id': 'test_001',
    'name': '測試用戶',
    'gender': 'male',
    'year': 1990,
    'month': 5,
    'day': 15,
    'hour': 14,
    'minute': 30
}

print('✅ 測試創建用戶...')
db.create_user(user_data)

print('✅ 測試讀取用戶...')
user = db.get_user('test_001')
print(f'   用戶名稱: {user["name"]}')

print('✅ 測試保存命盤鎖定...')
chart_data = {'type': 'bazi', 'data': '測試資料'}
db.save_chart_lock('test_001', 'bazi', chart_data, '測試分析')

print('✅ 測試讀取命盤鎖定...')
lock = db.get_chart_lock('test_001')
print(f'   命盤類型: {lock["chart_type"]}')

print('✅ 測試保存分析歷史...')
db.save_analysis_history('test_001', 'bazi_analysis', {'test': 'request'}, {'test': 'response'})

print('✅ 測試讀取分析歷史...')
history = db.get_analysis_history('test_001')
print(f'   歷史記錄數: {len(history)}')

# 清理測試資料
os.remove('data/test_aetheria.db')
print('\n🎉 SQLite 資料庫模組測試通過！')
