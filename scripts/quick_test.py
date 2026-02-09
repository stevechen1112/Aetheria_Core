#!/usr/bin/env python3
import requests
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:5001"

# 註冊並登入
username = f"test_{uuid.uuid4().hex[:8]}"
print(f"註冊用戶: {username}")
requests.post(f"{BASE_URL}/api/auth/register", json={"username": username, "password": "test123"})
token = requests.post(f"{BASE_URL}/api/auth/login", json={"username": username, "password": "test123"}).json()["token"]

# 發送測試訊息
message = "你好，我是陳美玲，1995年3月15日早上8點出生於台北，想了解事業運"
print(f"\n發送: {message}\n")

resp = requests.post(f"{BASE_URL}/api/chat/message",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": message},
    stream=True, timeout=60)

text = ""
for line in resp.iter_lines():
    if line and b"data:" in line:
        try:
            data = json.loads(line.decode().split("data:")[1])
            if "chunk" in data:
                chunk = data["chunk"]
                text += chunk
                print(chunk, end="", flush=True)
        except:
            pass

print(f"\n\n回應長度: {len(text)} 字")
print(f"測試完成！")
