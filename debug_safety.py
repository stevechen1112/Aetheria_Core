"""
診斷安全過濾問題
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 測試1：簡單問候
print("[TEST 1] 簡單問候")
model = genai.GenerativeModel('gemini-3-pro-preview')
response = model.generate_content("你好")
print(f"結果: {response.text[:50]}")

# 測試2：命理關鍵字
print("\n[TEST 2] 命理關鍵字")
response = model.generate_content("請解釋紫微斗數")
print(f"結果: {response.text[:50]}")

# 測試3：完整出生資料（無 system instruction）
print("\n[TEST 3] 完整出生資料")
try:
    prompt = """
請分析：
出生：農曆68年9月23日 23:58
地點：台灣彰化
性別：男
    """
    response = model.generate_content(
        prompt,
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    )
    print(f"結果: {response.text[:100]}")
except Exception as e:
    print(f"失敗: {e}")
    print(f"prompt_feedback: {response.prompt_feedback if 'response' in locals() else 'N/A'}")
    print(f"candidates: {response.candidates if 'response' in locals() else 'N/A'}")

# 測試4：加上 system instruction
print("\n[TEST 4] 加上 system instruction")
try:
    model_with_sys = genai.GenerativeModel(
        model_name='gemini-3-pro-preview',
        system_instruction="你是 Aetheria，精通紫微斗數的 AI 命理顧問。"
    )
    response = model_with_sys.generate_content(
        "分析：農曆68年9月23日 23:58 出生的男性",
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    )
    print(f"結果: {response.text[:100]}")
except Exception as e:
    print(f"失敗: {e}")
