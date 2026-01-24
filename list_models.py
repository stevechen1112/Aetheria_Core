"""列出所有可用的 Gemini 模型"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("可用的 Gemini 模型：\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
        print(f"  支援方法：{model.supported_generation_methods}")
        print()
