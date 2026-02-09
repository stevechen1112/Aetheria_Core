#!/usr/bin/env python3
"""快速測試 consult-stream 端點"""
import requests, json

BASE = "http://localhost:5001"

# 註冊
r = requests.post(f"{BASE}/api/auth/register", json={
    "username": "stream_test_001", "password": "test123", "email": "st001@test.com"
}, timeout=10)
print(f"註冊: {r.status_code}")
data = r.json()
token = data['token']
print(f"Token: {token}")

# 發送訊息
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
r = requests.post(f"{BASE}/api/chat/consult-stream", headers=headers,
    json={'message': '你好，我想了解我的命盤'}, stream=True, timeout=60)

print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}")

text = ""
for line in r.iter_lines():
    if not line:
        continue
    s = line.decode('utf-8')
    if s.startswith('data:'):
        try:
            d = json.loads(s[5:].strip())
            if d.get('chunk'):
                text += d['chunk']
                print(d['chunk'], end='', flush=True)
            elif d.get('session_id'):
                print(f"\n[SESSION: {d['session_id']}]")
        except:
            pass

print(f"\n\n--- 總長度: {len(text)} 字 ---")
