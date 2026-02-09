#!/usr/bin/env python3
"""
快速測試修復效果
"""
import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_fix():
    print("=" * 60)
    print("Aetheria 修復驗證測試")
    print("=" * 60)
    
    # 1. 註冊測試用戶
    username = f"test_fix_{int(time.time())}"
    print(f"\n[1] 註冊用戶: {username}")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": username,
                "password": "test123",
                "email": f"{username}@test.com"
            },
            timeout=10
        )
        data = resp.json()
        if data.get("status") != "success":
            print(f"   ✗ 註冊失敗: {data}")
            return
        print(f"   ✓ 註冊成功")
    except Exception as e:
        print(f"   ✗ 異常: {e}")
        return
    
    # 2. 登入
    print(f"\n[2] 登入用戶")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": username,
                "password": "test123"
            },
            timeout=10
        )
        data = resp.json()
        if data.get("status") != "success":
            print(f"   ✗ 登入失敗: {data}")
            return
        token = data.get("token")
        session_id = data.get("session_id")
        print(f"   ✓ 登入成功 (Session: {session_id})")
    except Exception as e:
        print(f"   ✗ 異常: {e}")
        return
    
    # 3. 提供生辰資料
    print(f"\n[3] 發送包含生辰資料的訊息")
    message = "你好！我是1990年7月22日下午2點15分出生的，男生，在高雄。想了解我的命盤。"
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/chat/consult-stream",
            json={
                "message": message,
                "session_id": session_id
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
            stream=True
        )
        
        print(f"   發送訊息: {message}")
        print(f"\n   AI 回應:")
        
        tool_calls = []
        text_chunks = []
        fuse_triggered = False
        
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode('utf-8')
            
            # 解析 SSE
            if line.startswith('event:'):
                event_type = line.split(':', 1)[1].strip()
            elif line.startswith('data:'):
                data_str = line.split(':', 1)[1].strip()
                try:
                    data = json.loads(data_str)
                    
                    if event_type == 'text':
                        chunk = data.get('chunk', '')
                        print(chunk, end='', flush=True)
                        text_chunks.append(chunk)
                    
                    elif event_type == 'tool':
                        status = data.get('status')
                        name = data.get('name')
                        if status == 'executing':
                            print(f"\n   [工具執行] {name}")
                            tool_calls.append(name)
                            if data.get('fuse_triggered'):
                                fuse_triggered = True
                                print(f"   ⚡ [熔斷機制觸發]")
                    
                    elif event_type == 'done':
                        print(f"\n\n   ✓ 對話完成")
                        break
                        
                except json.JSONDecodeError:
                    pass
        
        # 分析結果
        print(f"\n{'=' * 60}")
        print(f"測試結果分析:")
        print(f"{'=' * 60}")
        
        full_text = ''.join(text_chunks)
        
        print(f"\n✓ AI 回應長度: {len(full_text)} 字元")
        print(f"✓ 工具調用次數: {len(tool_calls)}")
        print(f"✓ 調用的工具: {tool_calls}")
        
        if fuse_triggered:
            print(f"⚡ 熔斷機制觸發: 是")
        
        # 關鍵檢查點
        success_count = 0
        total_checks = 4
        
        print(f"\n檢查項目:")
        
        # Check 1: AI 有排盤
        if len(tool_calls) > 0:
            print(f"  [✓] AI 主動排盤")
            success_count += 1
        else:
            print(f"  [✗] AI 未排盤")
        
        # Check 2: 排盤工具包含計算類
        calculate_tools = [t for t in tool_calls if 'calculate' in t]
        if len(calculate_tools) > 0:
            print(f"  [✓] 執行了計算工具: {calculate_tools}")
            success_count += 1
        else:
            print(f"  [✗] 未執行計算工具")
        
        # Check 3: 沒有反覆詢問
        question_count = full_text.count('?') + full_text.count('？')
        if question_count < 3:
            print(f"  [✓] 沒有過度詢問（問號數: {question_count}）")
            success_count += 1
        else:
            print(f"  [✗] 疑似反覆詢問（問號數: {question_count}）")
        
        # Check 4: 有具體分析內容
        keywords = ['命宮', '主星', '八字', '日主', '太陽', '上升', '宮位']
        found_keywords = [kw for kw in keywords if kw in full_text]
        if len(found_keywords) > 0:
            print(f"  [✓] 包含命理術語: {found_keywords[:3]}")
            success_count += 1
        else:
            print(f"  [✗] 缺少命理分析內容")
        
        print(f"\n{'=' * 60}")
        print(f"總評: {success_count}/{total_checks} 項通過")
        
        if success_count >= 3:
            print(f"✓✓✓ 修復效果良好！")
        elif success_count >= 2:
            print(f"⚠ 部分改善，仍需調整")
        else:
            print(f"✗✗✗ 修復未生效")
        
        print(f"{'=' * 60}")
        
    except Exception as e:
        print(f"   ✗ 異常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fix()
