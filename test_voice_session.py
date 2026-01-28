#!/usr/bin/env python3
"""測試語音 session API"""
import sqlite3
import requests
import uuid
from datetime import datetime, timedelta

# 檢查資料庫 (使用 data 目錄的資料庫)
conn = sqlite3.connect('data/aetheria.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 列出表格
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in cursor.fetchall()])

# 列出 sessions (member_sessions 表)
cursor.execute("SELECT * FROM member_sessions LIMIT 3")
sessions = cursor.fetchall()
print(f"\nSessions ({len(sessions)}):")
for s in sessions:
    print(dict(s))

# 列出 users
cursor.execute("SELECT user_id FROM users LIMIT 3")
users = cursor.fetchall()
print(f"\nUsers ({len(users)}):")
for u in users:
    print(dict(u))

# 建立測試 session
if users:
    user_id = users[0]['user_id']
    token = f"test_{uuid.uuid4().hex[:16]}"
    expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
    
    cursor.execute(
        "INSERT OR REPLACE INTO member_sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
        (token, user_id, expires_at)
    )
    conn.commit()
    print(f"\nCreated test session:")
    print(f"  token: {token}")
    print(f"  user_id: {user_id}")
    print(f"  expires_at: {expires_at}")
    
    # 測試 API
    print("\n--- Testing API ---")
    try:
        resp = requests.post(
            'http://127.0.0.1:5001/api/voice/session',
            json={'sdp': 'v=0', 'voice': 'alloy'},
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            timeout=30
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

conn.close()
