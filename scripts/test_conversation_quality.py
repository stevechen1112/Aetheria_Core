#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動化對話品質測試腳本 - 評估修復成果
"""
import requests
import json
import time
import uuid
import re
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:5001"

class ConversationTester:
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"conversation_test_{timestamp}.log"
        self.session_token = None
        self.session_id = None
        self.user_id = None
        self.conversation_history = []
        self.quality_issues = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def register_user(self, username):
        self.log(f"註冊用戶: {username}")
        try:
            response = requests.post(f"{BASE_URL}/api/auth/register",
                json={"username": username, "password": "test123", "email": f"{username}@test.com"}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('token')
                self.user_id = data.get('user_id')
                self.log("[OK] 用戶註冊成功", "SUCCESS")
                return True
            else:
                self.log(f"[ERR] 註冊失敗: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"[ERR] 註冊異常: {e}", "ERROR")
            return False
    
    def login_user(self, username):
        self.log(f"登入用戶: {username}")
        try:
            response = requests.post(f"{BASE_URL}/api/auth/login",
                json={"username": username, "password": "test123", "email": f"{username}@test.com"}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get('token')
                self.session_id = data.get('session_id')
                self.log(f"[OK] 登入成功，Session ID: {self.session_id}", "SUCCESS")
                return True
            else:
                self.log(f"[ERR] 登入失敗: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"[ERR] 登入異常: {e}", "ERROR")
            return False
    
    def send_message(self, message, timeout=120):
        self.log(f"用戶: {message}", "USER")
        try:
            headers = {
                'Authorization': f'Bearer {self.session_token}',
                'Content-Type': 'application/json'
            }
            payload = {'message': message}
            if self.session_id:
                payload['session_id'] = self.session_id
            
            response = requests.post(f"{BASE_URL}/api/chat/consult-stream", 
                headers=headers,
                json=payload, 
                stream=True, timeout=timeout)
            
            if response.status_code != 200:
                self.log(f"[ERR] API 錯誤: {response.status_code} - {response.text[:300]}", "ERROR")
                return None
            
            content_type = response.headers.get('Content-Type', '')
            accumulated_text = ""
            
            if 'text/event-stream' in content_type:
                # SSE 串流格式
                for line in response.iter_lines():
                    if not line:
                        continue
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data:'):
                        try:
                            data_json = json.loads(line_str[5:].strip())
                            if data_json.get('chunk'):
                                chunk_text = data_json['chunk']
                                accumulated_text += chunk_text
                                print(chunk_text, end='', flush=True)
                            if data_json.get('session_id'):
                                self.session_id = data_json['session_id']
                        except:
                            pass
            else:
                # JSON 格式 fallback
                try:
                    data = response.json()
                    accumulated_text = data.get('reply', '') or data.get('response', '')
                    print(accumulated_text[:200], end='')
                except:
                    accumulated_text = response.text
            
            print()
            if accumulated_text:
                self.log(f"AI: {accumulated_text[:200]}{'...' if len(accumulated_text) > 200 else ''}", "AI")
                self.conversation_history.append({'role': 'user', 'content': message})
                self.conversation_history.append({'role': 'assistant', 'content': accumulated_text})
                return accumulated_text
            else:
                self.log("[ERR] AI 無回應", "ERROR")
                return None
        except requests.exceptions.Timeout:
            self.log(f"[ERR] 請求逾時（{timeout}s）", "ERROR")
            return None
        except Exception as e:
            self.log(f"[ERR] 發送訊息異常: {e}", "ERROR")
            return None
    
    def check_quality(self, user_msg, ai_response):
        issues = []
        
        # Fix J: 判斷用戶訊息類型（問候/離題/命理相關）
        is_greeting = bool(re.search(r"^(你好|嗨|哈囉|hi|hello|hey)$", user_msg.strip(), re.IGNORECASE))
        is_off_topic = bool(re.search(r"(天氣|電影|推薦|美食|旅遊|音樂|遊戲)", user_msg)) and not bool(re.search(r"(命|運|盤|算|占|卦)", user_msg))
        
        # Fix J: 判斷對話歷史中是否已提供過生辰資料
        has_provided_birth = False
        for h in self.conversation_history:
            if h.get('role') == 'user':
                if re.search(r'\d{4}年\d{1,2}月\d{1,2}日', h.get('content', '')):
                    has_provided_birth = True
                    break
        # 也檢查當前訊息
        if re.search(r'\d{4}年\d{1,2}月\d{1,2}日', user_msg):
            has_provided_birth = True
        
        # 1. 回應長度（Fix J: 豁免問候語和離題問答）
        if len(ai_response) < 80:
            if is_greeting or is_off_topic:
                self.log(f"[OK] 回應簡短但屬正常（問候/離題）：{len(ai_response)} 字", "SUCCESS")
            else:
                issue = f"回應過短：僅 {len(ai_response)} 字，分析可能不夠深入"
                issues.append(issue)
                self.log(f"[!] {issue}", "QUALITY")
        elif len(ai_response) > 2000:
            self.log(f"[OK] 回應充實：{len(ai_response)} 字", "SUCCESS")
        
        # 2. 重複詢問生辰
        birth_in_message = bool(re.search(r"\d{4}年|\d{1,2}月\d{1,2}日|出生|生辰|八字", user_msg))
        birth_request_in_response = bool(re.search(r"(請提供|需要您的|告訴我).{0,10}(出生|生辰|八字)", ai_response))
        if birth_in_message and birth_request_in_response:
            has_complete = bool(re.search(r"\d{4}年\d{1,2}月\d{1,2}日", user_msg)) and bool(re.search(r"(早上|上午|下午|晚上|凌晨|\d{1,2}點)", user_msg))
            if has_complete:
                issue = "用戶已提供完整生辰資料，但 AI 仍重複詢問"
                issues.append(issue)
                self.log(f"[!] {issue}", "QUALITY")
        
        # 3. 命理內容驗證（Fix J: 僅在用戶已提供生辰時才觸發）
        ziwei_terms = bool(re.search(r"(命宮|身宮|福德|官祿|財帛|遷移|夫妻|子女|兄弟|田宅|疾厄|交友|主星|副星|化祿|化權|化科|化忌)", ai_response))
        bazi_terms = bool(re.search(r"(日主|月支|時柱|年柱|喜用神|忌神|天干|地支|五行)", ai_response))
        numerology_terms = bool(re.search(r"(生命靈數|命運數|天賦數|靈數)", ai_response))
        astrology_terms = bool(re.search(r"(星座|上升|月亮|太陽|星盤|宮位)", ai_response))
        has_chart_terms = ziwei_terms or bazi_terms or numerology_terms or astrology_terms
        mentions_systems = bool(re.search(r"(紫微|八字|占星|塔羅|靈數|姓名學)", ai_response))
        
        if mentions_systems and not has_chart_terms and len(ai_response) > 100 and has_provided_birth:
            issue = "缺乏具體命理內容，可能未調用計算工具或分析不夠深入"
            issues.append(issue)
            self.log(f"[!] {issue}", "QUALITY")
        
        # 4. Fix G 品質檢查：偵測 tool_code 洩漏
        if 'tool_code' in ai_response or 'default_api.' in ai_response:
            issue = "回應中包含 tool_code 技術文字洩漏"
            issues.append(issue)
            self.log(f"[!] {issue}", "QUALITY")
        
        # 5. Fix I 品質檢查：偵測非中文詞彙混入
        non_chinese = re.findall(r'[а-яА-ЯёЁ]{3,}', ai_response)  # 俄語西里爾字母
        if non_chinese:
            issue = f"回應混入非中文詞彙：{', '.join(non_chinese[:3])}"
            issues.append(issue)
            self.log(f"[!] {issue}", "QUALITY")
        
        if not issues:
            self.log("[OK] 回應品質良好", "SUCCESS")
        
        self.quality_issues.extend(issues)
    
    def print_report(self):
        self.log("\n" + "="*80)
        self.log("測試報告")
        self.log("="*80)
        self.log(f"\n對話輪數: {len(self.conversation_history) // 2}")
        self.log(f"品質問題數: {len(self.quality_issues)}")
        
        if self.quality_issues:
            self.log("\n品質問題列表:", "ERROR")
            for i, issue in enumerate(self.quality_issues, 1):
                self.log(f"  {i}. [!] {issue}", "ERROR")
        else:
            self.log("\n[OK] 無品質問題！所有檢測通過！", "SUCCESS")
        
        self.log("\n對話歷史摘要:")
        for i in range(0, len(self.conversation_history), 2):
            self.log(f"\n  --- 第 {i//2 + 1} 輪 ---")
            user_msg = self.conversation_history[i]['content']
            ai_msg = self.conversation_history[i+1]['content'] if i+1 < len(self.conversation_history) else "無回應"
            self.log(f"  用戶: {user_msg[:50]}{'...' if len(user_msg) > 50 else ''}", "USER")
            self.log(f"  AI: {ai_msg[:200]}{'...' if len(ai_msg) > 200 else ''}", "AI")
        
        self.log("\n" + "="*80)
        self.log(f"[OK] 完整日誌已儲存: {self.log_file}", "SUCCESS")
        self.log("="*80 + "\n")

def main():
    print("\n" + "="*60)
    print(" 自動化對話品質測試 ")
    print("="*60)
    tester = ConversationTester()
    print(f"日誌檔案: {tester.log_file}\n")
    
    # 場景 1
    tester.log("\n" + "="*80, "INFO")
    tester.log("場景 1: 首次對話 + 完整生辰 + 多維度分析")
    tester.log("="*80 + "\n")
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    if not tester.register_user(username):
        return
    if not tester.login_user(username):
        return
    
    for msg in ["你好，我想了解我的命盤", "我叫陳美玲，1995年3月15日早上8點30分出生於台北市",
                "我想知道我的事業運勢和發展方向", "那感情方面呢？我今年有機會遇到對象嗎？", "我的財運如何？"]:
        time.sleep(2)
        response = tester.send_message(msg)
        if response:
            tester.check_quality(msg, response)
    tester.print_report()
    
    # 場景 2
    tester.log("\n" + "="*80, "INFO")
    tester.log("場景 2: 自然對話流（模擬真實用戶行為）")
    tester.log("="*80 + "\n")
    tester.quality_issues = []
    tester.conversation_history = []
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    if not tester.register_user(username):
        return
    if not tester.login_user(username):
        return
    
    for msg in ["嗨，最近工作壓力好大，感覺很迷茫", "我不確定現在的工作適不適合我，總覺得施展不開",
                "我是1990年7月22日下午2點15分在高雄出生的", "根據我的命盤，我適合做什麼類型的工作？", "那創業呢？我適合創業嗎？"]:
        time.sleep(2)
        response = tester.send_message(msg)
        if response:
            tester.check_quality(msg, response)
    tester.print_report()
    
    # 場景 3
    tester.log("\n" + "="*80, "INFO")
    tester.log("場景 3: 離題偵測與引導測試")
    tester.log("="*80 + "\n")
    tester.quality_issues = []
    tester.conversation_history = []
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    if not tester.register_user(username):
        return
    if not tester.login_user(username):
        return
    
    for msg in ["你好", "今天天氣怎麼樣？", "推薦我一部好看的電影吧", "好吧，那幫我算算命吧，我是1988年5月10日早上9點出生"]:
        time.sleep(2)
        response = tester.send_message(msg)
        if response:
            tester.check_quality(msg, response)
    tester.print_report()
    
    # 場景 4
    tester.log("\n" + "="*80, "INFO")
    tester.log("場景 4: 測試記憶與上下文理解")
    tester.log("="*80 + "\n")
    tester.quality_issues = []
    tester.conversation_history = []
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    if not tester.register_user(username):
        return
    if not tester.login_user(username):
        return
    
    for msg in ["我想算命", "我是1992年12月25日凌晨1點在台南出生", "我的事業運如何？",
                "剛才你提到的那個特質，能再詳細說明嗎？", "那這個特質會影響我的感情嗎？"]:
        time.sleep(2)
        response = tester.send_message(msg)
        if response:
            tester.check_quality(msg, response)
    tester.print_report()
    
    print("\n" + "="*60)
    print(" 所有場景測試完成 ")
    print("="*60)
    print(f"總品質問題數: {len(tester.quality_issues)}")
    print(f"完整日誌: {tester.log_file}")

if __name__ == "__main__":
    main()
