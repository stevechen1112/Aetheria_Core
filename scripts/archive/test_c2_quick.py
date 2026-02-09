"""Quick test for C2 - off-topic handling"""
import requests, json, time, re

BASE = "http://localhost:5001"

def test():
    # Register
    uname = f"c2test{int(time.time())}"
    email = f"{uname}@test.com"
    r = requests.post(f"{BASE}/api/auth/register", json={"username":uname,"password":"testpass123","email":email})
    print(f"Register: {r.status_code}")
    token = r.json().get("token","")
    
    headers = {"Authorization": f"Bearer {token}"}
    sid = f"c2test_{int(time.time())}"
    
    def send(msg):
        payload = {"message": msg}
        if hasattr(send, 'sid') and send.sid:
            payload["session_id"] = send.sid
        r = requests.post(f"{BASE}/api/chat/consult-stream", json=payload, headers=headers, stream=True, timeout=(10,120))
        text = ""
        for line in r.iter_lines():
            if not line: continue
            line_str = line.decode('utf-8')
            if line_str.startswith("data:"):
                try:
                    d = json.loads(line_str[5:].strip())
                    if d.get("chunk"):
                        text += d["chunk"]
                    if d.get("session_id"):
                        send.sid = d["session_id"]
                except: pass
        return text
    send.sid = None
    
    # Turn 1: greeting
    t1 = send("你好")
    print(f"Turn 1: {len(t1)} chars")
    time.sleep(2)
    
    # Turn 2: weather (off-topic)
    t2 = send("今天天氣怎麼樣？")
    print(f"Turn 2 (天氣): {len(t2)} chars")
    has_guidance = bool(re.search(r'命理|命盤|運勢|占卜|算命|排盤|分析', t2))
    print(f"  引導回命理: {'✅' if has_guidance else '❌'}")
    time.sleep(2)
    
    # Turn 3: movie recommendation (off-topic)
    t3 = send("推薦一部好看的電影")
    print(f"Turn 3 (電影): {len(t3)} chars")
    print(f"  回應: {t3[:200]}")
    
    movie_names = re.findall(r'《[^》]+》', t3)
    is_detailed = len(movie_names) >= 1 and len(t3) > 150
    print(f"  電影名: {movie_names}")
    print(f"  過度回答: {'❌ FAIL' if is_detailed else '✅ PASS'}")

test()
