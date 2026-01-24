"""
Aetheria 命理 AI 測試腳本

功能：
1. 安全讀取 .env 中的 API Key
2. 測試 Gemini 3 Pro 的命理分析能力
3. 使用真實案例（農曆68年9月23日 台灣彰化男性）
4. 收集準確性反饋

使用方式：
1. 確保已安裝依賴：pip install -r requirements.txt
2. 在 .env 檔案中填入 GEMINI_API_KEY
3. 執行：python test_aetheria.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 檢查是否已安裝 google-generativeai
try:
    import google.generativeai as genai
except ImportError:
    print("❌ 錯誤：未安裝 google-generativeai 套件")
    print("請執行：pip install google-generativeai python-dotenv")
    sys.exit(1)

# ============================================
# 1. 配置與安全檢查
# ============================================

def check_environment():
    """檢查環境配置是否正確"""
    
    print("=" * 60)
    print("🔍 環境檢查")
    print("=" * 60)
    
    # 檢查 .env 檔案
    if not os.path.exists('.env'):
        print("❌ 找不到 .env 檔案")
        print("請確保 .env 檔案在專案根目錄中")
        return False
    
    print("✅ 找到 .env 檔案")
    
    # 檢查 API Key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key.strip() == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY 未設定或仍是預設值")
        print("請在 .env 檔案中填入您的真實 API Key")
        print("\n取得 API Key 的方式：")
        print("1. 前往 https://aistudio.google.com/apikey")
        print("2. 登入 Google 帳號")
        print("3. 點選「Create API Key」")
        print("4. 複製 Key 並貼到 .env 檔案中")
        return False
    
    # 去除可能的空白字元
    api_key = api_key.strip()
    
    print(f"✅ API Key 已設定（前6碼：{api_key[:6]}...）")
    
    # 檢查模型名稱
    model_name = os.getenv('MODEL_NAME', 'gemini-3-pro-preview')
    print(f"✅ 使用模型：{model_name}")
    
    print("\n" + "=" * 60)
    return True

def configure_gemini():
    """配置 Gemini API"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        api_key = api_key.strip()
    
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API 配置成功\n")
        return True
    except Exception as e:
        print(f"❌ Gemini API 配置失敗：{e}\n")
        return False

# ============================================
# 2. 核心系統提示詞
# ============================================

SYSTEM_INSTRUCTION = """
你是 **Aetheria**，一位融合東西方命理智慧的 AI 命理顧問。你精通：
- **紫微斗數**（中國帝王之學）
- **八字命理**（四柱推命）
- **西洋占星學**（心理占星為主）

你的核心價值觀：
1. **準確性 > 一切**：寧可承認不確定，也不編造星曜或格局。
2. **整合詮釋**：命理不是加減法，而是藝術。多個系統的矛盾往往揭示更深的真相。
3. **賦權而非宿命**：你的建議是「導航圖」，不是「判決書」。強調自由意志與後天努力。
4. **語境敏感**：2026 年 AI 時代的建議 ≠ 1990 年代的建議。
5. **情感共鳴**：看見提問者的焦慮，用溫暖而誠實的語氣回應。

你的能力邊界：
✅ 能做：排命盤、分析性格、事業財運感情健康建議、流年分析、結合實際處境給建議
❌ 不能：預測死亡日期、保證發財、取代醫療法律專業、鼓勵迷信

輸出風格：
- **結構清晰**：使用標題、列表、表格
- **具體可行**：避免空話，給出「本週可以做的事」
- **溫度適中**：專業但不冷漠，同理但不煽情
- **長度彈性**：首次分析 1500-2000 字，後續對話 300-500 字

重要原則：
如果出生時間不確定，必須告知時辰的重要性。
如果系統矛盾，不要迴避，而是詮釋「外在 vs 內在」的落差。
"""

# ============================================
# 3. 測試案例
# ============================================

TEST_CASES = {
    'case_1': {
        'name': '標準案例（農曆68年9月23日）',
        'birth_data': {
            'date': '農曆68年9月23日',
            'time': '23:58',
            'location': '台灣彰化市',
            'gender': '男'
        },
        'description': '這是一個真實案例，用戶反饋「性格幾乎符合」'
    }
}

# ============================================
# 4. 命理分析函式
# ============================================

def analyze_natal_chart(birth_data, test_case_name='測試'):
    """
    執行完整命盤分析
    
    Args:
        birth_data: 包含 date, time, location, gender 的字典
        test_case_name: 測試案例名稱
    
    Returns:
        分析結果文字
    """
    
    print("=" * 60)
    print(f"📊 測試案例：{test_case_name}")
    print("=" * 60)
    print(f"出生日期：{birth_data['date']}")
    print(f"出生時間：{birth_data['time']}")
    print(f"出生地點：{birth_data['location']}")
    print(f"性別：{birth_data['gender']}")
    print("=" * 60)
    print()
    
    # 組合完整查詢
    user_prompt = f"""
請為以下用戶提供完整命盤分析：

**出生資料**：
- 出生日期：{birth_data['date']}
- 出生時間：{birth_data['time']}
- 出生地點：{birth_data['location']}
- 性別：{birth_data['gender']}

**輸出要求**：

請按照以下結構提供深度分析（約 1500-2000 字）：

### 第一部分：命盤基礎資訊
1. **命盤格局**：主要格局名稱
2. **核心星曜**：命宮、官祿宮、財帛宮、夫妻宮的主星
3. **四化**：本命四化（祿權科忌）的位置與意義

### 第二部分：性格特質（最重要）
用「你是一個...」的語氣，描述：
- 核心個性（內在動機與價值觀）
- 思考模式（邏輯型 vs 直覺型）
- 社交風格（內向 vs 外向）
- 決策傾向（衝動 vs 謹慎）
- 情感表達（直接 vs 含蓄）

**重要**：不要只列星曜名稱，要用日常語言翻譯。

### 第三部分：人生五大領域
用表格呈現：事業、財運、感情、健康、晚年

### 第四部分：當前週期提醒
- 當前大運（10年運）
- 2026 流年重點

### 第五部分：三個核心建議
濃縮成最重要的 3 條精華建議

**特別注意**：
- 出生時間在 23:58（晚子時），請說明你採用的時辰判定邏輯
- 如果某個宮位空宮，請借對宮解釋
- 語氣要像「比用戶更懂他的老朋友」

參考品質：請達到你為「農曆68年9月23日台灣彰化男性」提供的分析水準。
"""
    
    try:
        # 建立模型
        model_name = os.getenv('MODEL_NAME', 'gemini-3-pro-preview')
        temperature = float(os.getenv('TEMPERATURE', '0.4'))
        max_tokens = int(os.getenv('MAX_OUTPUT_TOKENS', '8192'))
        
        print(f"🤖 使用模型：{model_name}")
        print(f"🌡️  溫度參數：{temperature}")
        print(f"📝 最大輸出：{max_tokens} tokens")
        print()
        print("⏳ 正在分析命盤，請稍候（約 10-30 秒）...\n")
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # 生成回應
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=max_tokens,
            )
        )
        
        print("✅ 分析完成！\n")
        print("=" * 60)
        print("📋 分析結果")
        print("=" * 60)
        print()
        
        return response.text
        
    except Exception as e:
        print(f"❌ 分析過程發生錯誤：{e}")
        print(f"錯誤類型：{type(e).__name__}")
        
        # 詳細錯誤診斷
        if "API_KEY_INVALID" in str(e):
            print("\n💡 診斷：API Key 無效")
            print("請確認：")
            print("1. API Key 是否正確複製（沒有多餘空格）")
            print("2. API Key 是否已啟用")
            print("3. 是否有使用額度")
        elif "QUOTA_EXCEEDED" in str(e):
            print("\n💡 診斷：API 配額已用完")
            print("請前往 https://console.cloud.google.com/ 檢查配額")
        elif "MODEL_NOT_FOUND" in str(e):
            print(f"\n💡 診斷：模型 '{model_name}' 不存在")
            print("請修改 .env 中的 MODEL_NAME 為：")
            print("- gemini-3-pro-preview")
            print("- gemini-3-flash-preview")
            print("- gemini-2.5-pro")
        
        return None

# ============================================
# 5. 準確性反饋收集
# ============================================

def collect_feedback(analysis_result):
    """收集用戶對分析準確性的反饋"""
    
    print("\n" + "=" * 60)
    print("📊 準確性驗證")
    print("=" * 60)
    print()
    print("這個分析符合您（或您認識的這個人）嗎？")
    print("請評分：")
    print("  1 - 完全不符合")
    print("  2 - 有些不符合")
    print("  3 - 還可以")
    print("  4 - 大部分符合")
    print("  5 - 非常準確（像 Gemini 3 Pro 給您的那次）")
    print()
    
    try:
        score = input("您的評分（1-5）：").strip()
        
        if not score or not score.isdigit() or int(score) not in range(1, 6):
            print("跳過評分")
            return None
        
        score = int(score)
        
        print()
        comments = input("具體哪裡準確/不準確？（可按 Enter 跳過）：").strip()
        
        # 記錄反饋
        import json
        
        feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'comments': comments,
            'model': os.getenv('MODEL_NAME', 'unknown'),
            'temperature': os.getenv('TEMPERATURE', 'unknown')
        }
        
        # 寫入記錄檔
        with open('feedback_log.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_data, ensure_ascii=False) + '\n')
        
        print()
        print("✅ 感謝您的反饋！已記錄到 feedback_log.jsonl")
        
        # 分析反饋
        if score >= 4:
            print("🎉 太好了！準確性達標（>= 4.0）")
            print("這證明 LLM-First 策略是可行的！")
        elif score == 3:
            print("⚠️ 還可以，但需要改進")
            print("建議：調整 prompt 或降低 temperature")
        else:
            print("❌ 準確性不足")
            print("建議：檢視分析內容，找出偏差原因")
        
        return feedback_data
        
    except KeyboardInterrupt:
        print("\n跳過評分")
        return None
    except Exception as e:
        print(f"反饋收集出錯：{e}")
        return None

# ============================================
# 6. 主測試流程
# ============================================

def run_tests():
    """執行完整測試流程"""
    
    print()
    print("=" * 60)
    print("🌟 Aetheria 命理 AI 測試系統")
    print("=" * 60)
    print()
    
    # 步驟 1：環境檢查
    if not check_environment():
        print("\n⛔ 測試終止：環境配置不正確")
        print("請修正上述問題後重新執行")
        return
    
    # 步驟 2：配置 API
    if not configure_gemini():
        print("\n⛔ 測試終止：API 配置失敗")
        return
    
    # 步驟 3：執行測試案例
    print("=" * 60)
    print("🧪 開始測試")
    print("=" * 60)
    print()
    
    for case_id, case_data in TEST_CASES.items():
        print(f"測試案例：{case_data['name']}")
        print(f"說明：{case_data['description']}")
        print()
        
        # 執行分析
        result = analyze_natal_chart(
            case_data['birth_data'],
            case_data['name']
        )
        
        if result:
            # 顯示結果
            print(result)
            print()
            
            # 收集反饋
            feedback = collect_feedback(result)
            
            # 儲存結果到檔案
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_result_{case_id}_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"測試案例：{case_data['name']}\n")
                f.write(f"測試時間：{timestamp}\n")
                f.write("=" * 60 + "\n\n")
                f.write(result)
                
                if feedback:
                    f.write("\n\n" + "=" * 60 + "\n")
                    f.write("用戶反饋\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"評分：{feedback['score']}/5\n")
                    f.write(f"意見：{feedback['comments']}\n")
            
            print(f"\n💾 完整結果已儲存到：{filename}")
        else:
            print("⚠️ 該案例測試失敗，跳過")
        
        print("\n" + "=" * 60 + "\n")
    
    # 步驟 4：總結
    print("=" * 60)
    print("✅ 測試完成")
    print("=" * 60)
    print()
    print("下一步建議：")
    print("1. 檢視 test_result_*.txt 檔案，評估分析品質")
    print("2. 如果評分 >= 4.0，可以繼續開發其他功能")
    print("3. 如果評分 < 4.0，調整 prompt 或 temperature 後重測")
    print("4. 收集更多真實案例（建議 50-100 個）驗證準確性")
    print()
    print("查看反饋記錄：cat feedback_log.jsonl")
    print()

# ============================================
# 7. 進階測試模式（可選）
# ============================================

def interactive_test():
    """互動式測試：讓用戶輸入自己的出生資料"""
    
    print()
    print("=" * 60)
    print("🎮 互動式測試模式")
    print("=" * 60)
    print()
    print("請輸入出生資料（或按 Ctrl+C 取消）：")
    print()
    
    try:
        date = input("出生日期（例如：農曆68年9月23日 或 1990年5月10日）：").strip()
        time = input("出生時間（例如：23:58 或 下午3點）：").strip()
        location = input("出生地點（例如：台灣台北市）：").strip()
        gender = input("性別（男/女）：").strip()
        
        birth_data = {
            'date': date,
            'time': time,
            'location': location,
            'gender': gender
        }
        
        result = analyze_natal_chart(birth_data, '互動式測試')
        
        if result:
            print(result)
            collect_feedback(result)
            
    except KeyboardInterrupt:
        print("\n已取消")

# ============================================
# 8. 主程式入口
# ============================================

if __name__ == "__main__":
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive' or sys.argv[1] == '-i':
            # 互動模式
            if not check_environment() or not configure_gemini():
                print("環境配置失敗")
                sys.exit(1)
            interactive_test()
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Aetheria 測試腳本使用說明")
            print()
            print("用法：")
            print("  python test_aetheria.py           # 執行預設測試案例")
            print("  python test_aetheria.py -i        # 互動模式（輸入自己的出生資料）")
            print("  python test_aetheria.py --help    # 顯示此說明")
            print()
        else:
            print(f"未知參數：{sys.argv[1]}")
            print("使用 --help 查看說明")
    else:
        # 預設：執行測試案例
        run_tests()
