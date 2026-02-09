"""
Gemini API 獨立測試腳本
測試 Gemini 2.0 Flash API 的基本功能和 streaming 是否正常
"""
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# 添加項目路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 載入 .env 檔案
load_dotenv()

try:
    import google.generativeai as genai
    from google.generativeai import types
    print("✅ google.generativeai 導入成功")
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

def test_gemini_api():
    """測試 Gemini API 基本功能"""
    
    # 獲取 API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ 環境變數 GEMINI_API_KEY 未設置")
        return False
    
    print(f"✅ API Key 已找到 (長度: {len(api_key)})")
    
    try:
        # 配置 API
        genai.configure(api_key=api_key)
        print("✅ Gemini API 配置成功")
        
        # 創建模型
        model = genai.GenerativeModel('gemini-3-flash-preview')
        print("✅ 模型創建成功: gemini-3-flash-preview")
        
        # 測試 1: 非 streaming 請求
        print("\n" + "="*60)
        print("測試 1: 非 Streaming 請求")
        print("="*60)
        
        start_time = time.time()
        prompt = "請用一句話回答：2+2等於多少？"
        print(f"📤 發送請求: {prompt}")
        
        response = model.generate_content(prompt)
        elapsed = time.time() - start_time
        
        print(f"✅ 收到回應 (耗時: {elapsed:.2f}秒)")
        print(f"📥 回應內容: {response.text}")
        
        # 測試 2: Streaming 請求
        print("\n" + "="*60)
        print("測試 2: Streaming 請求")
        print("="*60)
        
        start_time = time.time()
        prompt = "請用30字以內介紹八字命理"
        print(f"📤 發送 streaming 請求: {prompt}")
        
        response_stream = model.generate_content(prompt, stream=True)
        
        chunks_received = 0
        full_text = ""
        first_chunk_time = None
        
        print("📥 接收 streaming chunks:")
        for chunk in response_stream:
            if first_chunk_time is None:
                first_chunk_time = time.time() - start_time
                print(f"   ⏱️ 首個 chunk 耗時: {first_chunk_time:.2f}秒")
            
            chunks_received += 1
            if hasattr(chunk, 'text'):
                chunk_text = chunk.text
                full_text += chunk_text
                print(f"   Chunk {chunks_received}: {len(chunk_text)} 字元")
        
        elapsed = time.time() - start_time
        print(f"✅ Streaming 完成")
        print(f"   總 chunks: {chunks_received}")
        print(f"   總耗時: {elapsed:.2f}秒")
        print(f"   完整內容: {full_text}")
        
        # 測試 3: 較長的 streaming 請求（模擬實際場景）
        print("\n" + "="*60)
        print("測試 3: 較長 Streaming 請求（模擬命理諮詢）")
        print("="*60)
        
        start_time = time.time()
        prompt = """請你扮演一位命理老師，簡短回答以下問題：
        
用戶說：我1990年5月15日早上8點出生，想了解我的事業運勢。

請用80字以內給出專業回應。"""
        
        print(f"📤 發送複雜 streaming 請求")
        
        response_stream = model.generate_content(prompt, stream=True)
        
        chunks_received = 0
        full_text = ""
        first_chunk_time = None
        timeout_seconds = 30
        
        print("📥 接收 streaming chunks (30秒超時):")
        
        try:
            for chunk in response_stream:
                if first_chunk_time is None:
                    first_chunk_time = time.time() - start_time
                    print(f"   ⏱️ 首個 chunk 耗時: {first_chunk_time:.2f}秒")
                
                chunks_received += 1
                if hasattr(chunk, 'text'):
                    chunk_text = chunk.text
                    full_text += chunk_text
                    print(f"   Chunk {chunks_received}: {len(chunk_text)} 字元")
                
                # 超時檢查
                if time.time() - start_time > timeout_seconds:
                    print(f"⚠️ 超過 {timeout_seconds} 秒，中斷測試")
                    break
            
            elapsed = time.time() - start_time
            
            if chunks_received > 0:
                print(f"✅ Streaming 完成")
                print(f"   總 chunks: {chunks_received}")
                print(f"   總耗時: {elapsed:.2f}秒")
                print(f"   完整內容: {full_text[:200]}...")
            else:
                print(f"❌ 沒有收到任何 chunk (等待了 {elapsed:.2f}秒)")
                return False
                
        except Exception as e:
            print(f"❌ Streaming 過程中發生錯誤: {e}")
            return False
        
        print("\n" + "="*60)
        print("✅ 所有測試通過！Gemini API 工作正常")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ API 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Gemini API 獨立測試")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    success = test_gemini_api()
    
    if success:
        print("\n🎉 結論: Gemini API 工作正常，問題可能在其他地方")
        sys.exit(0)
    else:
        print("\n⚠️ 結論: Gemini API 存在問題，需要進一步排查")
        sys.exit(1)
