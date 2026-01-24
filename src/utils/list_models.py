"""列出所有可用的 Gemini 模型"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("未提供 GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("可用的 Gemini 模型：\n")
for model in client.models.list():
    supported = getattr(model, "supported_generation_methods", None)
    if supported and 'generateContent' in supported:
        print(f"- {model.name}")
        print(f"  支援方法：{supported}")
        print()
