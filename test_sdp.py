"""測試 SDP 處理"""
import json
import os
import requests
from requests_toolbelt import MultipartEncoder
from dotenv import load_dotenv

load_dotenv()

# 模擬前端發送的 JSON（使用 Python 的真正 CRLF）
test_sdp = 'v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:test123\r\na=ice-pwd:testpassword12345678901234\r\na=fingerprint:sha-256 AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99\r\na=setup:actpass\r\na=mid:0\r\na=sendrecv\r\na=rtpmap:111 opus/48000/2\r\n'

print("1. 測試 SDP")
print(f"   SDP 長度: {len(test_sdp)}")
print(f"   前 50 字元: {repr(test_sdp[:50])}")
print(f"   末尾 10 字元: {repr(test_sdp[-10:])}")
print()

print("2. 正規化 SDP (Server 做法)")
sdp_normalized = test_sdp.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
print(f"   正規化後長度: {len(sdp_normalized)}")
print()

print("3. 使用完整 session config 測試 OpenAI API")
key = os.getenv('OPENAI_API_KEY')

# 與 server.py 相同的 session_config
system_instructions = "你是 Aetheria 命理顧問。"
session_config = {
    'type': 'realtime',
    'model': 'gpt-4o-realtime-preview',
    'audio': {
        'output': {
            'voice': 'alloy'
        }
    },
    'instructions': system_instructions,
    'input_audio_transcription': {
        'model': 'whisper-1'
    }
}

m = MultipartEncoder(
    fields={
        'sdp': sdp_normalized,
        'session': json.dumps(session_config)
    }
)

print(f"   Session config: {json.dumps(session_config)[:200]}...")

response = requests.post(
    'https://api.openai.com/v1/realtime/calls',
    headers={
        'Authorization': f'Bearer {key}',
        'Content-Type': m.content_type
    },
    data=m,
    timeout=30
)

print(f"   狀態碼: {response.status_code}")
if response.status_code == 201:
    print("   成功！")
    print(f"   回應前 200 字元: {response.text[:200]}")
else:
    print(f"   錯誤: {response.text}")
