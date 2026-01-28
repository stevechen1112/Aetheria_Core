"""用標準函式庫測試 OpenAI Realtime API"""
import os
import json
import http.client
import uuid
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('OPENAI_API_KEY')

sdp = 'v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:test123\r\na=ice-pwd:testpassword12345678901234\r\na=fingerprint:sha-256 AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99\r\na=setup:actpass\r\na=mid:0\r\na=sendrecv\r\na=rtpmap:111 opus/48000/2\r\n'

# 之前成功的格式
session_config = {
    'type': 'realtime',
    'model': 'gpt-4o-realtime-preview',
    'audio': {
        'output': {
            'voice': 'alloy'
        }
    },
    'instructions': 'Test'
}

# Use standard library multipart
boundary = str(uuid.uuid4())

body_parts = []
body_parts.append(f'--{boundary}')
body_parts.append('Content-Disposition: form-data; name="sdp"')
body_parts.append('')
body_parts.append(sdp)
body_parts.append(f'--{boundary}')
body_parts.append('Content-Disposition: form-data; name="session"')
body_parts.append('')
body_parts.append(json.dumps(session_config))
body_parts.append(f'--{boundary}--')

body = '\r\n'.join(body_parts)

print(f'Body 長度: {len(body)}')
print(f'前 300 字元:\n{repr(body[:300])}')
print()

# Send request
conn = http.client.HTTPSConnection('api.openai.com')
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': f'multipart/form-data; boundary={boundary}'
}

conn.request('POST', '/v1/realtime/calls', body.encode('utf-8'), headers)
res = conn.getresponse()
print(f'狀態碼: {res.status}')
response_body = res.read().decode('utf-8')
if res.status == 201:
    print('成功!')
    print(f'回應前 200 字元:\n{response_body[:200]}')
else:
    print(f'錯誤: {response_body}')
