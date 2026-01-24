"""
測試 GenerationConfig 參數
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM_INSTRUCTION = """
你是 Aetheria，精通紫微斗數的 AI 命理顧問。

重要原則：
1. 準確性最重要，不可編造星曜
2. 晚子時（23:00-01:00）的判定邏輯要明確說明
3. 必須明確說出命宮位置、主星、格局

輸出風格：結構清晰，先說命盤結構，再說性格。
"""

model = genai.GenerativeModel(
    model_name='gemini-3-pro-preview',
    system_instruction=SYSTEM_INSTRUCTION
)

prompt = """
請為以下用戶提供紫微斗數命盤分析（專注於命盤結構）：

出生日期：農曆68年9月23日
出生時間：23:58
出生地點：台灣彰化市
性別：男

請按以下格式輸出（約800字）：

### 一、命盤基礎結構
1. **時辰判定**：說明 23:58 如何處理（晚子時算當日或隔日）
2. **命宮**：位於哪個宮位？主星是什麼？
3. **核心格局**：屬於什麼格局？（如日月並明、殺破狼等）

**注意**：必須明確說出宮位（如「戌宮」「申宮」），不可模糊帶過。
"""

# 測試1：無 config
print("[TEST 1] 無 GenerationConfig")
try:
    response = model.generate_content(
        prompt,
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    )
    print(f"[OK] 成功，{len(response.text)} 字")
except Exception as e:
    print(f"[ERROR] {e}")

# 測試2：有 temperature 和 top_p
print("\n[TEST 2] 有 temperature, top_p")
try:
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.4,
            top_p=0.95
        ),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    )
    print(f"[OK] 成功，{len(response.text)} 字")
except Exception as e:
    print(f"[ERROR] {e}")

# 測試3：加上 top_k（可能是問題所在）
print("\n[TEST 3] 加上 top_k=40")
try:
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.4,
            top_p=0.95,
            top_k=40
        ),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    )
    print(f"[OK] 成功，{len(response.text)} 字")
except Exception as e:
    print(f"[ERROR] {e}")

# 測試4：加上 max_output_tokens
print("\n[TEST 4] 加上 max_output_tokens=2048")
try:
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.4,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048
        ),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    )
    print(f"[OK] 成功，{len(response.text)} 字")
except Exception as e:
    print(f"[ERROR] {e}")
    print(f"finish_reason: {response.candidates[0].finish_reason if 'response' in locals() and response.candidates else 'N/A'}")
