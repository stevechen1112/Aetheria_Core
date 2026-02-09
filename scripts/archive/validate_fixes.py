#!/usr/bin/env python3
"""
修復驗證腳本 - 驗證所有修復是否正確實施
"""
import os
import sys
import ast
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent

class FixValidator:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def check(self, name: str, condition: bool, details: str = ""):
        """檢查項目"""
        if condition:
            self.passed += 1
            status = "✓"
            color = "\033[92m"  # Green
        else:
            self.failed += 1
            status = "✗"
            color = "\033[91m"  # Red
        
        reset = "\033[0m"
        print(f"{color}[{status}]{reset} {name}")
        if details:
            print(f"    {details}")
        
        self.results.append({
            'name': name,
            'passed': condition,
            'details': details
        })
        return condition
    
    def print_summary(self):
        """打印總結"""
        total = self.passed + self.failed
        print(f"\n{'=' * 70}")
        print(f"驗證總結: {self.passed}/{total} 項通過")
        print(f"{'=' * 70}")
        
        if self.failed == 0:
            print("\033[92m✓✓✓ 所有檢查通過！修復已正確實施。\033[0m")
        else:
            print(f"\033[91m✗✗✗ {self.failed} 項檢查失敗，請檢查實施。\033[0m")
        
        return self.failed == 0


def main():
    print("=" * 70)
    print("Aetheria 修復驗證")
    print("=" * 70)
    print()
    
    validator = FixValidator()
    
    # ==================== Fix A: 統一 System Prompt ====================
    print("\n[Fix A] 統一 System Prompt 架構")
    print("-" * 70)
    
    server_py = ROOT_DIR / "src" / "api" / "server.py"
    server_content = server_py.read_text(encoding='utf-8')
    
    # Check 1: 導入 agent_persona
    validator.check(
        "A1: 導入 agent_persona 模組",
        "from src.prompts.agent_persona import" in server_content,
        "在 server.py 中導入 choose_strategy, build_agent_system_prompt"
    )
    
    # Check 2: 使用 choose_strategy
    validator.check(
        "A2: 使用 choose_strategy 函式",
        "conversation_stage = choose_strategy(" in server_content,
        "在 chat_consult_stream 中調用對話狀態機"
    )
    
    # Check 3: 使用 build_agent_system_prompt
    validator.check(
        "A3: 使用 build_agent_system_prompt",
        "base_agent_prompt = build_agent_system_prompt(" in server_content,
        "構建完整的 Agent System Prompt"
    )
    
    # ==================== Fix A2: 統一狀態判定 ====================
    print("\n[Fix A2] 統一狀態判定邏輯")
    print("-" * 70)
    
    # Check 4: has_birth_date 判定
    validator.check(
        "A2.1: 實作 has_birth_date 判定",
        "has_birth_date = False" in server_content and 
        "has_birth_date = bool(" in server_content,
        "統一判定是否有生辰資料"
    )
    
    # Check 5: has_chart 判定
    validator.check(
        "A2.2: 實作 has_chart 判定",
        "has_chart = bool(chart_context" in server_content,
        "統一判定是否已有命盤"
    )
    
    # ==================== Fix F: 熔斷機制 ====================
    print("\n[Fix F] 伺服器端熔斷機制")
    print("-" * 70)
    
    # Check 6: 熔斷觸發條件
    fuse_pattern = r"has_birth_date and.*not has_chart.*no_tool_calls"
    validator.check(
        "F1: 熔斷觸發條件實作",
        bool(re.search(r"has_birth_date\s+and\s+not\s+has_chart", server_content, re.DOTALL)),
        "檢測：有生辰 + 無命盤 + 無工具調用"
    )
    
    # Check 7: 強制執行 calculate_bazi
    validator.check(
        "F2: 強制執行 calculate_bazi",
        "execute_tool('calculate_bazi'" in server_content,
        "熔斷機制執行排盤工具"
    )
    
    # Check 8: 熔斷日誌記錄
    validator.check(
        "F3: 熔斷事件記錄",
        "熔斷機制觸發" in server_content or "fuse_triggered" in server_content,
        "記錄熔斷觸發事件"
    )
    
    # ==================== Fix B: Prompt 強化 ====================
    print("\n[Fix B] Prompt 層強化")
    print("-" * 70)
    
    # Check 9: 改進的 chart_hint
    validator.check(
        "B1: 正面引導提示",
        "請立即選擇適合的系統" in server_content or "請立即" in server_content,
        "改用正面指示而非否定警告"
    )
    
    # ==================== Fix C: 簡化工具定義 ====================
    print("\n[Fix C] 簡化工具定義")
    print("-" * 70)
    
    tools_py = ROOT_DIR / "src" / "utils" / "tools.py"
    tools_content = tools_py.read_text(encoding='utf-8')
    
    # Check 10: 移除 dedup 警告
    validator.check(
        "C1: 移除工具描述中的 dedup 警告",
        "如果系統提示中的「命盤摘要」已包含" not in tools_content,
        "工具描述不再包含「無需重複調用」警告"
    )
    
    # Check 11: 簡化描述
    validator.check(
        "C2: 使用正面描述",
        "當用戶提供" in tools_content or "調用此工具排盤" in tools_content,
        "改用正面的工具描述"
    )
    
    # ==================== Fix D: 擴展上下文 ====================
    print("\n[Fix D] 擴展上下文視窗")
    print("-" * 70)
    
    # Check 12: 擴展歷史記錄
    validator.check(
        "D1: 對話歷史從 6 條增至 12 條",
        "limit=12" in server_content and "6 輪對話" in server_content,
        "擴展對話歷史視窗以減少資料遺失"
    )
    
    # ==================== Intelligence Core 修改 ====================
    print("\n[Intelligence Core] 支援自訂 base_prompt")
    print("-" * 70)
    
    intelligence_py = ROOT_DIR / "src" / "prompts" / "intelligence_core.py"
    intelligence_content = intelligence_py.read_text(encoding='utf-8')
    
    # Check 13: base_prompt 參數
    validator.check(
        "IC1: build_enhanced_system_prompt 支援 base_prompt",
        "base_prompt: Optional[str] = None" in intelligence_content,
        "intelligence_core 支援自訂基礎 prompt"
    )
    
    # ==================== 代碼品質檢查 ====================
    print("\n[Code Quality] 代碼品質檢查")
    print("-" * 70)
    
    # Check 14: 語法檢查
    try:
        with open(server_py, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        syntax_ok_server = True
    except SyntaxError as e:
        syntax_ok_server = False
        print(f"    語法錯誤: {e}")
    
    validator.check(
        "Q1: server.py 語法正確",
        syntax_ok_server,
        "無語法錯誤"
    )
    
    # Check 15: tools.py 語法
    try:
        with open(tools_py, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        syntax_ok_tools = True
    except SyntaxError as e:
        syntax_ok_tools = False
        print(f"    語法錯誤: {e}")
    
    validator.check(
        "Q2: tools.py 語法正確",
        syntax_ok_tools,
        "無語法錯誤"
    )
    
    # Check 16: intelligence_core.py 語法
    try:
        with open(intelligence_py, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        syntax_ok_ic = True
    except SyntaxError as e:
        syntax_ok_ic = False
        print(f"    語法錯誤: {e}")
    
    validator.check(
        "Q3: intelligence_core.py 語法正確",
        syntax_ok_ic,
        "無語法錯誤"
    )
    
    # ==================== 文檔完整性 ====================
    print("\n[Documentation] 文檔完整性")
    print("-" * 70)
    
    # Check 17: 實施報告存在
    impl_report = ROOT_DIR / "docs" / "19_Fix_Implementation_Report.md"
    validator.check(
        "D1: 實施報告已創建",
        impl_report.exists(),
        f"報告路徑: {impl_report}"
    )
    
    # Check 18: 原始計畫存在
    plan_doc = ROOT_DIR / "docs" / "18_Root_Cause_Analysis_And_Fix_Plan.md"
    validator.check(
        "D2: 根因分析計畫存在",
        plan_doc.exists(),
        f"計畫路徑: {plan_doc}"
    )
    
    # ==================== 打印總結 ====================
    success = validator.print_summary()
    
    if success:
        print("\n下一步建議:")
        print("  1. 啟動伺服器: python run.py")
        print("  2. 執行對話測試驗證修復效果")
        print("  3. 監控熔斷機制觸發率")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
