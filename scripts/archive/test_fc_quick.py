"""快速測試 function calling 是否正常（thought_signature 修復驗證）"""
import requests, json, uuid, time

BASE = 'http://localhost:5001'
uid = str(uuid.uuid4())[:8]
uname = f'fctest_{uid}'
s = requests.Session()
r1 = s.post(f'{BASE}/api/auth/register', json={'username': uname, 'password': 'test123', 'email': f'{uname}@test.com'})
print(f'Register: {r1.status_code}')
r2 = s.post(f'{BASE}/api/auth/login', json={'username': uname, 'password': 'test123', 'email': f'{uname}@test.com'})
print(f'Login: {r2.status_code}')
if r2.status_code != 200:
    print(f'Login failed: {r2.text[:200]}')
    exit(1)
token = r2.json().get('token', '')
print(f'Token: {token[:20]}...')

# Turn 1
print('Turn 1: greeting')
r = s.post(f'{BASE}/api/chat/consult-stream', json={'message': '你好', 'token': token}, stream=True, timeout=(5,60))
print(f'Status: {r.status_code}')
if r.status_code != 200:
    print(f'Error: {r.text[:500]}')
    exit(1)
t1 = ''
for line in r.iter_lines(decode_unicode=True):
    if line.startswith('data:'):
        d = json.loads(line[5:])
        if 'chunk' in d: t1 += d['chunk']
print(f'AI ({len(t1)} chars): {t1[:100]}...')

time.sleep(1)

# Turn 2: request bazi
print()
print('Turn 2: bazi request')
r = s.post(f'{BASE}/api/chat/consult-stream', json={'message': '我是1990年6月15日早上10點出生的男生，幫我排八字', 'token': token}, stream=True, timeout=(5,120))
t2 = ''
tools = []
for line in r.iter_lines(decode_unicode=True):
    if line.startswith('data:'):
        d = json.loads(line[5:])
        if 'chunk' in d: t2 += d['chunk']
        if 'name' in d and 'status' in d: tools.append(f"{d['name']}:{d['status']}")
print(f'Tools: {tools}')
print(f'AI ({len(t2)} chars): {t2[:300]}...')

if len(t2) > 50:
    print('\n✅ PASS: Function calling works with thought_signature!')
else:
    print('\n❌ FAIL: Response too short - function calling may still be broken')
