"""測試通過 Flask API 發送 SDP"""
import requests
import json

# 模擬前端發送的請求（真正的 CRLF 換行）
sdp = 'v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:test123\r\na=ice-pwd:testpassword12345678901234\r\na=fingerprint:sha-256 AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99\r\na=setup:actpass\r\na=mid:0\r\na=sendrecv\r\na=rtpmap:111 opus/48000/2\r\n'

print(f'SDP 長度: {len(sdp)}')
print(f'前 50 字元: {repr(sdp[:50])}')
print(f'包含 CRLF: {chr(13)+chr(10) in sdp}')

response = requests.post(
    'http://127.0.0.1:5001/api/voice/session',
    headers={
        'Authorization': 'Bearer 7ad064960e26425aa82701d27097fb60',
        'Content-Type': 'application/json'
    },
    json={'sdp': sdp, 'voice': 'alloy'},
    timeout=30
)

print(f'狀態碼: {response.status_code}')
if response.status_code == 200:
    print('成功！')
    data = response.json()
    if 'sdp' in data:
        answer = data['sdp']
        print(f'Answer SDP 前 200 字元:\n{answer[:200]}')
else:
    print(f'錯誤: {response.text}')
