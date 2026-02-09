#!/usr/bin/env python3
"""
簡化的修復驗證測試 - 直接執行無需確認
"""
import subprocess
import sys
import time
from pathlib import Path

def main():
    print("=" * 70)
    print("啟動 Aetheria 修復驗證測試")
    print("=" * 70)
    
    # 1. 啟動服務器
    print("\n[步驟 1/3] 啟動 API 伺服器...")
    server_process = subprocess.Popen(
        [sys.executable, "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Path(__file__).parent
    )
    
    print("等待伺服器啟動（15秒）...")
    time.sleep(15)
    
    # 2. 執行測試
    print("\n[步驟 2/3] 執行對話品質測試...")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, "scripts/test_conversation_quality.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=300  # 5分鐘超時
        )
        
        print(result.stdout)
        if result.stderr:
            print("錯誤輸出:", result.stderr)
        
        print("\n[步驟 3/3] 測試完成")
        
    except subprocess.TimeoutExpired:
        print("測試超時（5分鐘）")
    except Exception as e:
        print(f"執行測試時發生錯誤: {e}")
    finally:
        # 3. 關閉服務器
        print("\n關閉伺服器...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        
        print("測試流程結束")

if __name__ == "__main__":
    main()
