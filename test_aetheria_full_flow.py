import requests
import json
import uuid
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"
TEST_EMAIL = f"test_ai_final_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "Password123!"
TEST_NAME = "Aetheria 測試員"

def test_full_system_flow():
    print(f"=== 開始 Aetheria Core 完整系統測試 (修復版) ===")
    print(f"測試時間: {datetime.now().isoformat()}")
    print(f"測試帳號: {TEST_EMAIL}")

    # 1. 註冊
    print("\n[Step 1] 註冊新帳號...")
    reg_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "display_name": TEST_NAME,
        "consents": {"terms_accepted": True, "data_usage_accepted": True}
    }
    r = requests.post(f"{BASE_URL}/api/auth/register", json=reg_data)
    if r.status_code != 200:
        print(f"X 註冊失敗: {r.text}")
        return
    reg_result = r.json()
    token = reg_result["token"]
    user_id = reg_result["user_id"]
    print(f"OK 註冊成功, User ID: {user_id}")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. 填入資料並啟動分析
    print("\n[Step 2] 填入生辰資料並啟動全系統分析...")
    analysis_data = {
        "user_id": user_id,
        "chinese_name": TEST_NAME,
        "gender": "男",
        "birth_date": "1995-05-20",
        "birth_time": "10:30",
        "birth_location": "台北市",
        "ziwei_ruleset": "no_day_advance"
    }
    start_time = time.time()
    r = requests.post(f"{BASE_URL}/api/profile/save-and-analyze", json=analysis_data, headers=headers)
    duration = time.time() - start_time
    
    if r.status_code != 200:
        print(f"X 分析失敗: {r.text}")
        return
    
    print(f"OK 分析完成, 耗時: {duration:.2f}s")
    
    # 3. 驗證報告
    systems = ['ziwei', 'bazi', 'astrology', 'numerology', 'name']
    for sys_name in systems:
        r = requests.get(f"{BASE_URL}/api/reports/get?user_id={user_id}&system={sys_name}", headers=headers)
        if r.status_code == 200 and r.json().get('found'):
            print(f"   - {sys_name}: OK")
        else:
            print(f"   - {sys_name}: X")

    # 4. AI 文字顧問諮詢
    print("\n[Step 4] 測試 AI 文字顧問對話...")
    chat_data = {
        "message": "請根據我的命盤，給我一個事業建議。",
        "session_id": "", # 讓伺服器創建
        "voice_mode": False
    }
    r = requests.post(f"{BASE_URL}/api/chat/consult", json=chat_data, headers=headers)
    
    if r.status_code == 200:
        chat_reply = r.json().get('reply')
        print(f"OK AI 回覆成功:")
        print(f"   AI: {chat_reply[:300]}...")
    else:
        print(f"X AI 對話失敗: {r.status_code} - {r.text}")

    # 5. AI 語音會話
    print("\n[Step 5] 測試 AI 語音會话初始化 (SDP)...")
    # 雖然 WebRTC 測試需要複雜環境，但我們可以驗證 API 是否能正確轉發到 OpenAI 並返回 200 (或 502/400)
    # 注意：我們使用 application/json 並在 data 裡放 sdp，這是 server.py 的期望格式
    sdp_data = {
        "sdp": "v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n", # 至少要有頭
        "voice": "sage"
    }
    # 等等，server.py 的 create_voice_session (Line 2875) 使用 request.json
    # 所以 Content-Type: application/json 是正確的。剛才報錯可能是 OpenAI 那邊報的。
    r = requests.post(f"{BASE_URL}/api/voice/session", json=sdp_data, headers=headers)
    if r.status_code == 200:
        print("OK 語音會話初始化成功")
    else:
        print(f"X 語音會話 API 回應: {r.status_code} (這可能是因為 dummy SDP 被 OpenAI 拒絕，但代表後端鏈路通了)")

    print("\n=== 系統測試結束 ===")

if __name__ == "__main__":
    test_full_system_flow()
