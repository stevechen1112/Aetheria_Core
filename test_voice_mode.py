"""
测试语音模式API
"""
import requests
import json

# 配置
API_BASE = "http://localhost:5001"
TOKEN = "b4bee66f75f94d4a8b85062c9cc9924a"

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

# 测试1：文字模式
print("=== 测试1：文字模式 ===")
response1 = requests.post(
    f"{API_BASE}/api/chat/consult",
    headers=headers,
    json={
        "message": "我今年财运如何？",
        "voice_mode": False
    }
)
data1 = response1.json()
print(f"回复: {data1.get('reply', '')[:200]}")
print(f"字数: {len(data1.get('reply', ''))}")
print(f"引用系统: {data1.get('used_systems', [])}")
print()

# 测试2：语音模式（同样的问题）
print("=== 测试2：语音模式 ===")
response2 = requests.post(
    f"{API_BASE}/api/chat/consult",
    headers=headers,
    json={
        "message": "我今年财运如何？",
        "voice_mode": True
    }
)
data2 = response2.json()
print(f"回复: {data2.get('reply', '')[:200]}")
print(f"字数: {len(data2.get('reply', ''))}")
print(f"引用系统: {data2.get('used_systems', [])}")
print()

# 对比风格
print("=== 风格对比 ===")
print("文字模式:", "简洁明了" if len(data1.get('reply', '')) < 150 else "详细解说")
print("语音模式:", "口语亲切" if any(word in data2.get('reply', '') for word in ['嗯', '喔', '欸', '让我看看']) else "正式书面")

print("\n✅ 测试完成")
