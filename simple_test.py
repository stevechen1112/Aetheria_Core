"""
簡化的 Gemini API 測試
用於診斷問題
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# 載入環境變數
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

print(f"API Key: {api_key[:10]}...")

# 配置
genai.configure(api_key=api_key)

# 建立模型
model = genai.GenerativeModel('gemini-3-pro-preview')  # 使用 Gemini 3 Pro

# 簡單測試
print("\n測試 1：簡單問候")
try:
    response = model.generate_content("你好，請簡單介紹自己")
    print(f"✅ 成功：{response.text[:100]}...")
except Exception as e:
    print(f"❌ 失敗：{e}")

# 命理測試
print("\n測試 2：命理分析")
try:
    prompt = """
    請為以下用戶提供紫微斗數命盤簡要分析：
    
    出生：農曆68年9月23日 23:58
    地點：台灣彰化
    性別：男
    
    請簡單說明性格特質（200字內）
    """
    response = model.generate_content(prompt)
    print(f"✅ 成功")
    print(response.text)
except Exception as e:
    print(f"❌ 失敗：{e}")
    print(f"錯誤詳情：{repr(e)}")
