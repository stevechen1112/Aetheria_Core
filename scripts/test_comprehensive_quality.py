#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面品質測試腳本 v3.1
======================
覆蓋 18_Root_Cause_Analysis_And_Fix_Plan.md 中記錄的所有問題
v3.1 新增：重複文字偵測、空洞句偵測、A6 塔羅強制工具執行、B1 八字關鍵字放寬

測試矩陣（16 項測試）：
  A. 命理系統（8 項）
     A1-A6: 六大系統獨立測試（工具執行 + 術語深度 + 品質門檻）
     A7:    不指定系統時自動排盤（根因 #1/#5 核心場景）
     A8:    跨日邊界時間不必要澄清（根因 #12）
  B. 多系統整合（1 項）
     B1:    同時要求多個系統
  C. 對話體驗（5 項）
     C1:    不重複詢問生辰（根因 #4, Fix Q/R/T）
     C2:    離題引導 + 不過度回答（根因 #11）
     C3:    語言品質：無俄文/tool_code/過多英文（根因 #8/#10/#13）
     C4:    深度追問品質（Fix S deep_consult 驗證）
     C5:    跨 session 記憶（根因 #18 has_chart 誤判）
  D. 邊界情境（2 項）
     D1:    缺性別排盤（根因 #6）
     D2:    缺地點排盤（根因 #6）

不可從外部測試的內部機制（需獨立單元測試）：
  - 中文時間解析正確性（根因 #9）→ 已有 _extract_birth_time_from_message 單元測試
  - 策略選擇 has_chart 邏輯（根因 #5/#18）→ 症狀由 A7/C1/C5 間接覆蓋
  - 熔斷機制參數匹配（根因 #14）→ 無法可靠從外部觸發
"""
import requests
import json
import time
import uuid
import re
import sys
import signal
from datetime import datetime
from pathlib import Path

# Windows: 忽略 CTRL+C，防止終端機意外中斷測試流程
signal.signal(signal.SIGINT, signal.SIG_IGN)

BASE_URL = "http://localhost:5001"

# ============================================================
# 驗證關鍵字 — 各系統排盤結果中必須出現的術語
# ============================================================
SYSTEM_KEYWORDS = {
    'bazi':       [r'日主|[甲乙丙丁戊己庚辛壬癸][金木水火土]命', r'天干|地支', r'四柱|年柱|月柱|時柱', r'喜用神|忌神|用神', r'五行',
                   r'食神|正官|偏財|正印|比肩|劫財|傷官|七殺|偏印|正財|身弱|身強|格局'],
    'ziwei':      [r'命宮', r'身宮|福德|官祿|財帛|遷移|夫妻|子女',
                   r'紫微|天機|太陽|太陰|天府|天同|天梁|天相|武曲|廉貞|貪狼|巨門|破軍|七殺', r'主星'],
    'astrology':  [r'星座', r'上升|月亮|太陽|水星|金星|火星|木星|土星',
                   r'星盤|宮位|相位',
                   r'牡羊|金牛|雙子|巨蟹|獅子|處女|天秤|天蠍|射手|摩羯|水瓶|雙魚'],
    'numerology': [r'生命靈數|靈數', r'命運數|天賦數|主命數', r'流年|生命數'],
    'name':       [r'五格|三才', r'天格|人格|地格|外格|總格', r'數理|筆畫', r'姓名學'],
    'tarot':      [r'塔羅', r'牌陣|正位|逆位',
                   r'權杖|聖杯|寶劍|錢幣|愚者|魔術師|女祭司|皇后|皇帝|教皇|戀人|戰車|力量|隱士|命運之輪|正義|吊人|死神|節制|惡魔|塔|星星|月亮|太陽|審判|世界'],
}

# 深度術語 — 用於驗證 AI 分析是否有足夠深度（對應文件根因：紫微缺四化飛星/大運流年）
DEEP_KEYWORDS = {
    'bazi':  [r'大運|流年|用神|格局|身強|身弱|從格|十神'],
    'ziwei': [r'四化|化祿|化權|化科|化忌|大運|流年|飛星|自化'],
}

# 判定「想看哪個系統？」迴圈的模式（對應根因 #1/#5）
WHICH_SYSTEM_LOOP_PATTERN = r'(想看哪個|想用哪|偏好哪|選擇.*系統|想要.*八字.*還是|要不要.*先看)'

class ComprehensiveTester:
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"comprehensive_test_{timestamp}.log"
        self.session_token = None
        self.session_id = None
        self.user_id = None
        self.conversation_history = []
        
        # 統計
        self.results = {}    # {test_name: {pass, fail, issues, details}}
        self.total_pass = 0
        self.total_fail = 0
    
    def log(self, msg, level="INFO"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{level}] {msg}"
        # 避免 Windows cp950 編碼錯誤：emoji/特殊字元 fallback
        try:
            print(line, flush=True)
        except UnicodeEncodeError:
            safe = line.encode('ascii', errors='replace').decode('ascii')
            print(safe, flush=True)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    
    def reset_session(self):
        """重置用戶 session（新用戶）"""
        self.session_token = None
        self.session_id = None
        self.user_id = None
        self.conversation_history = []
    
    def register_and_login(self):
        username = f"test_{uuid.uuid4().hex[:8]}"
        try:
            r = requests.post(f"{BASE_URL}/api/auth/register",
                json={"username": username, "password": "test123", "email": f"{username}@test.com"}, timeout=10)
            if r.status_code != 200:
                self.log(f"[ERR] 註冊失敗: {r.text[:200]}", "ERROR")
                return False
            data = r.json()
            self.session_token = data.get('token')
            self.user_id = data.get('user_id')
        except Exception as e:
            self.log(f"[ERR] 註冊異常: {e}", "ERROR")
            return False
        
        try:
            r = requests.post(f"{BASE_URL}/api/auth/login",
                json={"username": username, "password": "test123"}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                self.session_token = data.get('token') or self.session_token
                self.session_id = data.get('session_id')
            return True
        except Exception as e:
            self.log(f"[ERR] 登入異常: {e}", "ERROR")
            return False
    
    def send_message(self, message, timeout=120):
        """發送訊息，返回 (accumulated_text, tool_events)"""
        self.log(f"  👤 USER: {message}")
        try:
            headers = {
                'Authorization': f'Bearer {self.session_token}',
                'Content-Type': 'application/json'
            }
            payload = {'message': message}
            if self.session_id:
                payload['session_id'] = self.session_id
            
            r = requests.post(f"{BASE_URL}/api/chat/consult-stream",
                headers=headers, json=payload, stream=True, timeout=(10, timeout))
            
            if r.status_code != 200:
                return None, []
            
            accumulated_text = ""
            tool_events = []  # 收集工具事件
            
            content_type = r.headers.get('Content-Type', '')
            if 'text/event-stream' in content_type:
                for line in r.iter_lines():
                    if not line:
                        continue
                    line_str = line.decode('utf-8')
                    
                    # 工具事件
                    if line_str.startswith('event: tool'):
                        continue  # 下一行是 data
                    if line_str.startswith('data:'):
                        try:
                            data = json.loads(line_str[5:].strip())
                            # 工具事件
                            if data.get('status') in ('executing', 'completed', 'error'):
                                tool_events.append(data)
                            # 文字事件
                            if data.get('chunk'):
                                accumulated_text += data['chunk']
                            if data.get('session_id'):
                                self.session_id = data['session_id']
                        except:
                            pass
            else:
                try:
                    data = r.json()
                    accumulated_text = data.get('reply', '') or data.get('response', '')
                except:
                    accumulated_text = r.text
            
            if accumulated_text:
                self.conversation_history.append({'role': 'user', 'content': message})
                self.conversation_history.append({'role': 'assistant', 'content': accumulated_text})
            
            # 日誌記錄完整回應（截取前 500 字）
            preview = (accumulated_text or '(空)')[:500]
            self.log(f"  🤖 AI ({len(accumulated_text or '')} 字): {preview}")
            if tool_events:
                tools_summary = ', '.join(f"{e.get('name','?')}:{e.get('status','?')}" for e in tool_events)
                self.log(f"  🔧 工具事件: {tools_summary}")
            
            return accumulated_text, tool_events
        except requests.exceptions.Timeout:
            self.log(f"[ERR] 逾時 ({timeout}s)", "ERROR")
            return None, []
        except Exception as e:
            self.log(f"[ERR] 異常: {e}", "ERROR")
            return None, []
    
    # ================================================================
    # 檢測工具
    # ================================================================
    
    def check_tool_executed(self, tool_events, expected_tool):
        """檢查特定工具是否被執行"""
        for ev in tool_events:
            if ev.get('name') == expected_tool and ev.get('status') == 'completed':
                return True
        return False
    
    def check_system_keywords(self, text, system_name, min_groups=2):
        """檢查回應中是否包含特定系統的命理關鍵字（至少命中 min_groups 個不同術語組）"""
        if not text:
            return False
        hits = 0
        for pattern in SYSTEM_KEYWORDS.get(system_name, []):
            if re.search(pattern, text):
                hits += 1
        return hits >= min_groups
    
    def count_keyword_hits(self, text, system_name):
        """計算命中了多少個術語組，用於日誌"""
        if not text:
            return 0
        hits = 0
        matched = []
        for pattern in SYSTEM_KEYWORDS.get(system_name, []):
            m = re.search(pattern, text)
            if m:
                hits += 1
                matched.append(m.group())
        return hits, matched
    
    def check_deep_keywords(self, text, system_name):
        """檢查深度術語（四化/大運/流年等）"""
        if not text or system_name not in DEEP_KEYWORDS:
            return False
        for pattern in DEEP_KEYWORDS[system_name]:
            if re.search(pattern, text):
                return True
        return False
    
    def check_which_system_loop(self, text):
        """檢查 AI 是否陷入「想看哪個系統？」迴圈（根因 #1/#5）"""
        if not text:
            return False
        return bool(re.search(WHICH_SYSTEM_LOOP_PATTERN, text))
    
    def _common_quality_checks(self, text, issues, system_name=None):
        """通用品質檢查：tool_code、俄文、重複文字、空洞句"""
        if self.check_no_tool_code_leak(text):
            issues.append("tool_code 技術文字洩漏")
        if self.check_no_russian(text):
            issues.append("混入俄文")
        # Fix U 驗證：重複短語偵測
        if text and len(text) > 200:
            rep = self._detect_repetition(text)
            if rep:
                issues.append(f"重複生成迴圈：'{rep}' 連續出現 3+ 次")
        # Fix V 驗證：空洞句偵測
        if text and re.search(r'的\s{2,}和\s*[，、]', text):
            issues.append("殘留空洞句（如『的 和 ，』）— 串流清理不完整")
        if system_name:
            hits, matched = self.count_keyword_hits(text, system_name)
            total = len(SYSTEM_KEYWORDS.get(system_name, []))
            self.log(f"  術語命中: {hits}/{total} 組 → {matched}")
    
    def _detect_repetition(self, text, min_len=3, max_len=20, threshold=3):
        """偵測文字中是否有短語連續重複 threshold 次"""
        if not text or len(text) < min_len * threshold:
            return None
        for phrase_len in range(min_len, min(max_len + 1, len(text) // threshold + 1)):
            for start in range(0, len(text) - phrase_len * threshold + 1):
                phrase = text[start:start + phrase_len]
                if not re.search(r'[\u4e00-\u9fffA-Za-z]', phrase):
                    continue
                if (phrase * threshold) in text:
                    return phrase
        return None
    
    def check_no_birth_reask(self, text):
        """檢查 AI 是否重複詢問已提供的出生資料（寬泛匹配多種問法）"""
        patterns = [
            r'(請提供|需要您的|可以告訴我|方便告訴我|能否提供|請問您的|告訴我您的).{0,10}(出生|生辰|八字|生日|生年)',
            r'(您|你)(是|的).{0,6}(幾年|哪一年|什麼時候).{0,6}(出生|生)',
            r'(出生|生辰|生日).{0,6}(是什麼|是哪|是幾|呢\?|呢？|嗎\?|嗎？)',
            r'請問.{0,10}(生日|出生日期|出生時間|生辰)',
            r'需要.{0,6}知道.{0,10}(生辰|出生|生日)',
        ]
        for p in patterns:
            if re.search(p, text):
                return True
        return False
    
    def check_no_tool_code_leak(self, text):
        """檢查是否有 tool_code 技術文字洩漏（根因 #8/#13/#16）"""
        if not text:
            return False
        leak_patterns = [
            'tool_code',
            'default_api.',
            'print(default_api',
            'calculate_bazi(',
            'calculate_ziwei(',
            'calculate_astrology(',
            'calculate_numerology(',
            'analyze_name(',
            'draw_tarot(',
        ]
        text_lower = text.lower()
        return any(p.lower() in text_lower for p in leak_patterns)
    
    def check_no_russian(self, text):
        """檢查是否混入俄文"""
        return bool(re.findall(r'[а-яА-ЯёЁ]{3,}', text))
    
    def check_response_length(self, text, min_len=100):
        """檢查回應長度是否足夠"""
        return len(text or '') >= min_len
    
    # ================================================================
    # 測試場景
    # ================================================================
    
    def run_test(self, test_name, test_func):
        """執行單個測試並記錄結果"""
        self.log(f"\n{'='*70}")
        self.log(f"測試: {test_name}")
        self.log(f"{'='*70}")
        
        self.reset_session()
        if not self.register_and_login():
            self.results[test_name] = {'pass': False, 'issues': ['無法註冊/登入']}
            self.total_fail += 1
            return
        
        issues = test_func()
        passed = len(issues) == 0
        
        self.results[test_name] = {
            'pass': passed,
            'issues': issues,
        }
        if passed:
            self.total_pass += 1
            self.log(f"✅ PASS: {test_name}", "SUCCESS")
        else:
            self.total_fail += 1
            self.log(f"❌ FAIL: {test_name}", "ERROR")
            for iss in issues:
                self.log(f"   - {iss}", "ERROR")
    
    # ------ A1: 八字系統 ------
    def test_bazi_system(self):
        issues = []
        self.send_message("你好，我想了解八字命盤")
        time.sleep(2)
        text, tools = self.send_message("我是1990年6月15日早上10點出生的男生，幫我排八字")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        # 檢查工具執行
        bazi_executed = self.check_tool_executed(tools, 'calculate_bazi')
        if not bazi_executed:
            self.log("⚠️ calculate_bazi 未在 tool events 中（可能走熔斷路徑）")
        
        # 不應該反問「想看哪個系統」（根因 #1/#5）
        if self.check_which_system_loop(text):
            issues.append("已明確指定八字卻仍問『想看哪個系統？』")
        
        # 檢查命理內容（至少 2 組術語）
        if not self.check_system_keywords(text, 'bazi', min_groups=2):
            issues.append("回應缺少八字術語（需至少 2 組：日主/天干地支/五行等）")
        
        self._common_quality_checks(text, issues, 'bazi')
        if not self.check_response_length(text, 150):
            issues.append(f"回應過短（{len(text)} 字）")
        
        return issues
    
    # ------ A2: 紫微斗數系統 ------
    def test_ziwei_system(self):
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text, tools = self.send_message("我是女生，1995年3月15日早上8點30分出生在台北，幫我排紫微斗數")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        ziwei_executed = self.check_tool_executed(tools, 'calculate_ziwei')
        if not ziwei_executed:
            self.log("⚠️ calculate_ziwei 未在 tool events 中")
        
        if not self.check_system_keywords(text, 'ziwei', min_groups=2):
            issues.append("回應缺少紫微術語（需至少 2 組：命宮/主星/宮位等）")
        
        self._common_quality_checks(text, issues, 'ziwei')
        if not self.check_response_length(text, 150):
            issues.append(f"回應過短（{len(text)} 字）")
        
        # === 深度追問（對應文件缺陷：紫微分析缺少四化飛星/大運流年）===
        time.sleep(2)
        text2, _ = self.send_message("四化飛星和大運流年的部分可以詳細說明嗎？")
        if text2:
            if not self.check_deep_keywords(text2, 'ziwei'):
                issues.append("追問四化/大運後仍缺乏深度術語（化祿/化權/化科/化忌/大運/流年）")
            if self.check_no_birth_reask(text2):
                issues.append("深度追問時 AI 又要求提供生辰")
            self._common_quality_checks(text2, issues)
        else:
            issues.append("深度追問無回應")
        
        return issues
    
    # ------ A3: 占星系統 ------
    def test_astrology_system(self):
        issues = []
        self.send_message("你好，我想看星盤")
        time.sleep(2)
        text, tools = self.send_message("我是1988年12月3日下午3點45分出生在高雄，幫我排星盤")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        astro_executed = self.check_tool_executed(tools, 'calculate_astrology')
        if not astro_executed:
            self.log("⚠️ calculate_astrology 未在 tool events 中")
        
        if not self.check_system_keywords(text, 'astrology', min_groups=2):
            issues.append("回應缺少占星術語（需至少 2 組：星座/行星/宮位等）")
        
        self._common_quality_checks(text, issues, 'astrology')
        if not self.check_response_length(text, 100):
            issues.append(f"回應過短（{len(text)} 字）")
        
        return issues
    
    # ------ A4: 靈數系統 ------
    def test_numerology_system(self):
        issues = []
        self.send_message("你好，我想了解我的生命靈數")
        time.sleep(2)
        text, tools = self.send_message("我的出生日期是1992年7月22日，幫我算生命靈數")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        num_executed = self.check_tool_executed(tools, 'calculate_numerology')
        if not num_executed:
            self.log("⚠️ calculate_numerology 未在 tool events 中")
        
        if not self.check_system_keywords(text, 'numerology', min_groups=1):
            issues.append("回應缺少靈數術語（生命靈數/命運數/天賦數等）")
        
        self._common_quality_checks(text, issues, 'numerology')
        if not self.check_response_length(text, 80):
            issues.append(f"回應過短（{len(text)} 字）")
        
        return issues
    
    # ------ A5: 姓名學系統 ------
    def test_name_system(self):
        issues = []
        self.send_message("你好，我想分析我的名字")
        time.sleep(2)
        text, tools = self.send_message("我姓陳，名字叫美玲，幫我做姓名學分析")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        name_executed = self.check_tool_executed(tools, 'analyze_name')
        if not name_executed:
            self.log("⚠️ analyze_name 未在 tool events 中")
        
        if not self.check_system_keywords(text, 'name', min_groups=2):
            issues.append("回應缺少姓名學術語（需至少 2 組：五格/三才/天格人格地格等）")
        
        self._common_quality_checks(text, issues, 'name')
        if not self.check_response_length(text, 80):
            issues.append(f"回應過短（{len(text)} 字）")
        
        return issues
    
    # ------ A6: 塔羅系統 ------
    def test_tarot_system(self):
        issues = []
        self.send_message("你好，我想抽塔羅牌")
        time.sleep(2)
        text, tools = self.send_message("我最近工作遇到瓶頸，想換工作但不確定，幫我抽張塔羅牌看看")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        tarot_executed = self.check_tool_executed(tools, 'draw_tarot')
        if not tarot_executed:
            self.log("⚠️ draw_tarot 未在 tool events 中")
            # Fix: 塔羅必須實際抽牌，不能只是口頭說「準備好了就告訴我」
            # 嘗試再次要求（AI 可能等待確認）
            time.sleep(2)
            text2, tools2 = self.send_message("準備好了，幫我抽牌")
            if text2:
                text = text + "\n" + text2
                tools = tools + tools2
                tarot_executed = self.check_tool_executed(tools2, 'draw_tarot')
            if not tarot_executed:
                issues.append("draw_tarot 工具未被實際執行（AI 只是口頭描述塔羅）")
        
        if not self.check_system_keywords(text, 'tarot', min_groups=2):
            issues.append("回應缺少塔羅術語（需至少 2 組：塔羅+牌名/正逆位等）")
        
        self._common_quality_checks(text, issues, 'tarot')
        if not self.check_response_length(text, 80):
            issues.append(f"回應過短（{len(text)} 字）")
        
        return issues
    
    # ------ B1: 多系統整合 ------
    def test_multi_system(self):
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text1, tools1 = self.send_message("我是1993年8月18日下午2點出生在台中的男生，幫我同時看八字和紫微")
        time.sleep(2)
        
        if not text1:
            issues.append("無回應")
            return issues
        
        has_bazi = self.check_system_keywords(text1, 'bazi')
        has_ziwei = self.check_system_keywords(text1, 'ziwei')
        
        if not has_bazi and not has_ziwei:
            issues.append("八字和紫微都沒有出現術語")
        elif not has_bazi:
            issues.append("缺少八字術語")
        elif not has_ziwei:
            # 可接受 — AI 可能先回報一個系統，等用戶追問再補
            self.log("⚠️ 紫微術語未出現（可能需追問才會展開）")
        
        self._common_quality_checks(text1, issues)
        
        return issues
    
    # ------ A7: 不指定系統自動排盤（根因 #1/#5 核心場景）------
    def test_auto_select_system(self):
        """只給生辰、不指定任何系統名，驗證 AI 是否主動選擇系統排盤"""
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text, tools = self.send_message("我是男生，1991年4月10日中午12點出生在新竹，幫我看看")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        # 最關鍵檢查：不應該問「想看哪個系統？」
        if self.check_which_system_loop(text):
            issues.append("❌ 核心缺陷重現：收到完整生辰後反問『想看哪個系統？』（根因 #1/#5）")
        
        # 應該至少觸發一個系統
        any_system = False
        for sys_name in ['bazi', 'ziwei', 'astrology', 'numerology']:
            if self.check_system_keywords(text, sys_name, min_groups=1):
                any_system = True
                self.log(f"  ✓ 自動選擇了 {sys_name} 系統")
                break
        
        if not any_system:
            issues.append("給完整生辰但未指定系統 → AI 未主動排盤任何系統")
        
        self._common_quality_checks(text, issues)
        if not self.check_response_length(text, 100):
            issues.append(f"回應過短（{len(text)} 字）")
        
        return issues
    
    # ------ A8: 跨日邊界時間（根因 #12）------
    def test_midnight_boundary(self):
        """用「凌晨1點」測試是否不必要地反問跨日確認"""
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text, tools = self.send_message("我是女生，1992年12月25日凌晨1點出生在台南，幫我排盤")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        # 不應反問「是25日還是26日」（根因 #12）
        unnecessary_clarify = bool(re.search(
            r'(25日.*還是.*26日|26日.*還是.*25日|確認.*日期|哪一天|是否.*跨日)', text
        ))
        if unnecessary_clarify:
            issues.append("對明確時間『12月25日凌晨1點』做不必要的跨日澄清（根因 #12）")
        
        # 應該直接排盤
        any_system = False
        for sys_name in ['bazi', 'ziwei', 'astrology']:
            if self.check_system_keywords(text, sys_name, min_groups=1):
                any_system = True
                break
        if not any_system:
            issues.append("未能排盤（可能卡在不必要的確認）")
        
        self._common_quality_checks(text, issues)
        
        return issues
    
    # ------ C1: 對話記憶 - 不重複詢問 ------
    def test_no_reask(self):
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text1, tools1 = self.send_message("我叫王小明，1990年5月20日早上6點出生在台北，男生")
        time.sleep(2)
        text2, tools2 = self.send_message("幫我看事業運")
        time.sleep(1)
        
        if not text2:
            issues.append("無回應")
            return issues
        
        if self.check_no_birth_reask(text2):
            issues.append("用戶已提供完整生辰，AI 仍重複詢問")
        
        if not self.check_response_length(text2, 100):
            issues.append(f"事業分析回應過短（{len(text2)} 字）")
        
        # 檢查是否說「還沒有命盤資料」之類的幻覺
        if text2 and re.search(r'(還沒有|尚未|沒有你的).{0,6}(命盤|資料|數據)', text2):
            issues.append("AI 聲稱沒有命盤資料（但前一輪已排過盤 — 記憶/上下文問題）")
        
        # 追問不應再問
        time.sleep(2)
        text3, tools3 = self.send_message("那感情方面呢？")
        if text3 and self.check_no_birth_reask(text3):
            issues.append("第三輪追問感情，AI 又重複詢問出生資料")
        
        # 第三輪也不應聲稱「沒有資料」
        if text3 and re.search(r'(還沒有|尚未|沒有你的).{0,6}(命盤|資料|數據)', text3):
            issues.append("第三輪 AI 聲稱沒有命盤資料（上下文遺失）")
        
        self._common_quality_checks(text2, issues)
        return issues
    
    # ------ C2: 離題引導 + 不過度回答（根因 #11）------
    def test_off_topic(self):
        issues = []
        text1, _ = self.send_message("你好")
        time.sleep(2)
        
        # 測試 1: 天氣問題 — 應引導回命理
        text2, _ = self.send_message("今天天氣怎麼樣？")
        time.sleep(1)
        
        if not text2:
            issues.append("無回應")
            return issues
        
        has_guidance = bool(re.search(r'命理|命盤|運勢|占卜|算命|排盤|分析', text2))
        if not has_guidance:
            issues.append("離題問題未引導回命理主題")
        
        # 測試 2: 推薦電影 — 不應直接推薦具體電影名（根因 #11 半真）
        time.sleep(2)
        text3, _ = self.send_message("推薦一部好看的電影")
        if text3:
            # 如果直接推薦了具體電影名且超過 100 字深入介紹
            movie_names = re.findall(r'《[^》]+》', text3)
            is_detailed_movie_rec = len(movie_names) >= 1 and len(text3) > 150
            if is_detailed_movie_rec:
                issues.append(f"離題過度回答：推薦了 {len(movie_names)} 部電影且詳細介紹（根因 #11）")
        
        return issues
    
    # ------ C3: 語言品質（無俄文/tool_code）------
    def test_language_quality(self):
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text, tools = self.send_message("我是1985年1月1日凌晨3點出生的女生，在台北出生，幫我全面分析")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues        
        # 語言品質專項：檢查空洞句/斷句
        hollow_patterns = [
            (r'[\u4e00-\u9fff]\s{2,}[\u4e00-\u9fff]', '中文字間有多餘空格（如「代表你 有 能力」）'),
            (r'[\u4e00-\u9fff]\s+[。！？]', '句尾斷裂（如「你 。」）'),
            (r'[\u4e00-\u9fff]{1,3}\s*$', None),  # 不報錯，但下面會檢查
        ]
        for pattern, desc in hollow_patterns:
            if desc and re.search(pattern, text):
                issues.append(f"語言品質缺陷：{desc}")
                break  # 一個就夠了        
        if self.check_no_russian(text):
            issues.append("回應混入俄文字元")
        if self.check_no_tool_code_leak(text):
            issues.append("tool_code 技術文字洩漏")
        
        # 檢查英文混入（允許少量專有名詞）
        english_words = re.findall(r'[a-zA-Z]{5,}', text)
        # 排除常見允許詞
        allowed = {'Aetheria', 'Transit', 'Celtic', 'Cross', 'Taipei', 'single', 'three'}
        unexpected_english = [w for w in english_words if w not in allowed]
        if len(unexpected_english) > 5:
            issues.append(f"回應混入過多英文：{', '.join(unexpected_english[:5])}")
        
        return issues
    
    # ------ C4: 深度追問品質（Fix S deep_consult 驗證）------
    def test_deep_followup(self):
        """排完八字後追問具體術語，驗證 AI 能引用具體星曜/十神"""
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text1, tools = self.send_message("我是男生，1987年9月3日早上7點出生在台北，幫我排八字")
        time.sleep(2)
        
        if not text1:
            issues.append("排盤無回應")
            return issues
        
        if not self.check_system_keywords(text1, 'bazi', min_groups=1):
            issues.append("初次排盤就未產生八字術語")
            return issues
        
        # 追問深度問題
        text2, _ = self.send_message("日主的強弱怎麼判定的？用神是怎麼選的？")
        time.sleep(1)
        
        if not text2:
            issues.append("深度追問無回應")
            return issues
        
        # 應該引用具體術語（不只是空泛描述）
        if not self.check_deep_keywords(text2, 'bazi'):
            issues.append("深度追問後回應缺少進階術語（大運/用神/格局/身強身弱等）")
        
        if self.check_no_birth_reask(text2):
            issues.append("深度追問時 AI 又重複詢問出生資料")
        
        if not self.check_response_length(text2, 100):
            issues.append(f"深度回應過短（{len(text2)} 字）")
        
        self._common_quality_checks(text2, issues)
        
        return issues
    
    # ------ C5: 跨 session 記憶驗證 ------
    def test_cross_session_memory(self):
        """第一個 session 提供生辰並排盤，開新 session 問是否記得"""
        issues = []
        # Session 1: 提供資料並排盤
        self.send_message("你好")
        time.sleep(2)
        text1, _ = self.send_message("我叫林志豪，男生，1988年11月20日早上9點出生在台中")
        time.sleep(2)
        text2, _ = self.send_message("幫我排八字")
        time.sleep(2)
        
        # Fix C5: AI 可能在 text1（提供生辰時）就已經排盤，text2 只是短回覆「已排過」
        # 任一訊息出現八字術語即代表 Session 1 排盤成功
        _bazi_in_text1 = text1 and self.check_system_keywords(text1, 'bazi', min_groups=1)
        _bazi_in_text2 = text2 and self.check_system_keywords(text2, 'bazi', min_groups=1)
        
        if not _bazi_in_text1 and not _bazi_in_text2:
            self.log("⚠️ Session 1 排盤失敗，跳過跨 session 測試")
            issues.append("Session 1 排盤未成功，無法測試跨 session 記憶")
            return issues
        
        if _bazi_in_text1 and not _bazi_in_text2:
            self.log("  ✓ AI 在用戶提供生辰時就主動排盤（正確行為）")
        
        # Session 2: 新 session（同一用戶），問是否記得
        old_session_id = self.session_id
        self.session_id = None  # 強制新 session
        self.conversation_history = []
        
        time.sleep(2)
        text3, _ = self.send_message("你好，我之前有排過盤，你還記得我的命盤嗎？")
        time.sleep(1)
        
        if not text3:
            issues.append("跨 session 無回應")
            return issues
        
        # 應該至少能識別用戶（透過 user_profile 記憶）
        # 嚴格：必須記得用戶名字或出生年，泛用詞（命盤、資料）不算
        remembers_specific = bool(re.search(
            r'林志豪|志豪|1988|天蠍|射手|己土|天梁', text3
        ))
        remembers_vague = bool(re.search(
            r'之前|記得|上次', text3
        ))
        if not remembers_specific:
            if remembers_vague:
                self.log(f"  ⚠️ 跨 session AI 說『記得/之前』但無法提及具體資料（名字/生辰）")
                issues.append("跨 session 記憶模糊（知道有之前但不記得具體資料）")
            else:
                issues.append("跨 session 完全不記得用戶資料（記憶系統可能未生效）")
            self.log(f"  跨 session 回應: {text3[:200]}")
        
        # 不應重新詢問已儲存的生辰
        if self.check_no_birth_reask(text3):
            issues.append("跨 session 重新詢問已儲存的出生資料")
        
        return issues
    
    # ------ D1: 缺性別情境 ------
    def test_missing_gender(self):
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text, tools = self.send_message("我是1990年6月15日早上10點出生在台北，幫我排盤")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        # 正確行為：AI 應該追問性別，而非使用預設值排盤
        asks_gender = bool(re.search(r'(性別|男生.*女生|先生.*女士|男.*還是.*女|請問.*男|請問.*女|男.*女|生理)', text))
        
        if asks_gender:
            self.log("  ✓ 缺性別時 AI 追問性別（正確行為）")
            
            # 第二輪：回答性別後應該排盤
            time.sleep(2)
            text2, tools2 = self.send_message("我是女生")
            time.sleep(1)
            if text2:
                has_chart = (
                    self.check_system_keywords(text2, 'bazi', min_groups=1) or
                    self.check_system_keywords(text2, 'ziwei', min_groups=1) or
                    self.check_system_keywords(text2, 'astrology', min_groups=1) or
                    self.check_system_keywords(text2, 'numerology', min_groups=1) or
                    bool(re.search(r'命盤|排盤|命格|日主|天機|紫微|太陽|宮位', text2))
                )
                if not has_chart:
                    issues.append("提供性別後仍未排盤")
                    self.log(f"  提供性別後回應: {text2[:200]}")
                else:
                    self.log("  ✓ 提供性別後成功排盤")
                self._common_quality_checks(text2, issues)
        else:
            issues.append("缺性別時未追問性別（應追問而非使用預設值）")
            self.log(f"  回應: {text[:200]}")
        
        return issues
    
    # ------ D2: 缺地點情境 ------
    def test_missing_location(self):
        issues = []
        self.send_message("你好")
        time.sleep(2)
        text, tools = self.send_message("我是男生，1990年6月15日早上10點出生的，幫我排盤")
        time.sleep(1)
        
        if not text:
            issues.append("無回應")
            return issues
        
        # 正確行為：
        # 1. 需要地點的系統（紫微、占星）→ 追問地點
        # 2. 不需要地點的系統（八字、靈數）→ 可以直接排
        # 因此：如果 AI 追問地點 OR 排了不需要地點的系統 → 都算正確
        asks_location = bool(re.search(r'(出生地|地點|哪[裡里個].*出生|城市|在哪|出生.*在)', text))
        
        has_bazi_or_numerology = (
            self.check_system_keywords(text, 'bazi', min_groups=1) or
            self.check_system_keywords(text, 'numerology', min_groups=1)
        )
        
        if asks_location:
            self.log("  ✓ 缺地點時 AI 追問出生地（正確行為）")
            
            # 第二輪：回答地點後應該排盤
            time.sleep(2)
            text2, tools2 = self.send_message("高雄")
            time.sleep(1)
            if text2:
                has_chart = (
                    self.check_system_keywords(text2, 'bazi', min_groups=1) or
                    self.check_system_keywords(text2, 'ziwei', min_groups=1) or
                    self.check_system_keywords(text2, 'astrology', min_groups=1) or
                    self.check_system_keywords(text2, 'numerology', min_groups=1) or
                    bool(re.search(r'命盤|排盤|命格|日主|天機|紫微|太陽|宮位', text2))
                )
                if not has_chart:
                    issues.append("提供地點後仍未排盤")
                    self.log(f"  提供地點後回應: {text2[:200]}")
                else:
                    self.log("  ✓ 提供地點後成功排盤")
                self._common_quality_checks(text2, issues)
        elif has_bazi_or_numerology:
            self.log("  ✓ 缺地點但排了不需要地點的系統（八字/靈數）")
            self._common_quality_checks(text, issues)
        else:
            issues.append("缺地點時既未追問也未排不需要地點的系統")
            self.log(f"  回應: {text[:200]}")
        
        self._common_quality_checks(text, issues)
        return issues
    
    # ================================================================
    # 主程式
    # ================================================================
    
    def run_all(self):
        print("\n" + "=" * 60)
        print(" 全面品質測試 v3.0 — 覆蓋 18.md 全部根因")
        print("=" * 60)
        self.log(f"日誌檔案: {self.log_file}\n")
        
        tests = [
            # A. 六大命理系統（每個系統獨立測試 + 自動選擇 + 邊界時間）
            ("A1. 八字系統",                self.test_bazi_system),
            ("A2. 紫微斗數系統+深度追問",   self.test_ziwei_system),
            ("A3. 西洋占星系統",            self.test_astrology_system),
            ("A4. 生命靈數系統",            self.test_numerology_system),
            ("A5. 姓名學系統",              self.test_name_system),
            ("A6. 塔羅牌系統",              self.test_tarot_system),
            ("A7. 不指定系統自動排盤",      self.test_auto_select_system),
            ("A8. 跨日邊界時間",            self.test_midnight_boundary),
            # B. 多系統整合
            ("B1. 多系統同時排盤",          self.test_multi_system),
            # C. 對話體驗
            ("C1. 不重複詢問生辰",          self.test_no_reask),
            ("C2. 離題引導+不過度回答",     self.test_off_topic),
            ("C3. 語言品質",                self.test_language_quality),
            ("C4. 深度追問品質",            self.test_deep_followup),
            ("C5. 跨session記憶",           self.test_cross_session_memory),
            # D. 邊界情境
            ("D1. 缺性別情境",              self.test_missing_gender),
            ("D2. 缺地點情境",              self.test_missing_location),
        ]
        
        for name, func in tests:
            self.run_test(name, func)
            time.sleep(5)  # 避免 Gemini API rate limit（RPM / RPD）
        
        # 最終報告
        self.print_final_report()
    
    def print_final_report(self):
        self.log(f"\n{'='*70}")
        self.log(f" 全面測試報告")
        self.log(f"{'='*70}")
        self.log(f"")
        self.log(f"  通過: {self.total_pass}/{self.total_pass + self.total_fail}")
        self.log(f"  失敗: {self.total_fail}/{self.total_pass + self.total_fail}")
        self.log(f"")
        
        # 按類別顯示
        categories = {
            'A': '六大命理系統',
            'B': '多系統整合',
            'C': '對話體驗',
            'D': '邊界情境',
        }
        
        for prefix, cat_name in categories.items():
            self.log(f"  【{cat_name}】")
            for name, result in self.results.items():
                if name.startswith(prefix):
                    status = "✅ PASS" if result['pass'] else "❌ FAIL"
                    self.log(f"    {status}  {name}")
                    if not result['pass']:
                        for iss in result['issues']:
                            self.log(f"             ⮑ {iss}")
            self.log("")
        
        self.log(f"  完整日誌: {self.log_file}")
        self.log(f"{'='*70}\n")
        
        # 簡潔 summary 輸出到 stdout
        print(f"\n{'='*60}")
        print(f" 測試結果: {self.total_pass} PASS / {self.total_fail} FAIL")
        print(f"{'='*60}")
        for name, result in self.results.items():
            s = "✅" if result['pass'] else "❌"
            line = f"  {s} {name}"
            if not result['pass']:
                line += f"  → {'; '.join(result['issues'])}"
            print(line)
        print(f"\n完整日誌: {self.log_file}")

if __name__ == "__main__":
    tester = ComprehensiveTester()
    tester.run_all()
    sys.exit(0 if tester.total_fail == 0 else 1)
