"""
Aetheria Core Golden Set - 迴歸測試黃金標準
================================================

此目錄包含系統的 Golden Set 測試用例，用於：
1. 確保核心功能始終正常運作
2. 防止功能退化（Regression）
3. 建立行為基準（Baseline）
4. 快速煙霧測試（Smoke Test）

測試分類
--------
- basic_conversation: 基礎對話流程測試（10 cases）
- tool_use: AI 工具選擇與使用準確性（8 cases）
- sensitive_topics: 敏感議題偵測與保護（5 cases）
- multi_turn: 多輪對話上下文管理（7 cases）
- error_handling: 錯誤處理與邊界情況（8 cases）
- system_integration: 系統整合與端到端測試（10 cases）

**總計：48 個 Golden Test Cases**

使用方法
--------
```bash
# 運行所有 Golden Set 測試（需啟動 API server）
pytest tests/golden_set/ -v

# 運行特定分類
pytest tests/golden_set/test_basic_conversation.py -v
pytest tests/golden_set/test_sensitive_topics.py -v

# 運行快速驗證（smoke test，不需 API）
pytest tests/golden_set/ -m smoke -v

# 運行整合測試
pytest tests/golden_set/ -m integration -v

# 查看 Golden Set 覆蓋統計
pytest tests/golden_set/ --cov=src --cov-report=html

# 生成測試報告
pytest tests/golden_set/ --html=golden_set_report.html
```

測試標記（Markers）
-------------------
- @pytest.mark.golden_set: 所有 Golden Set 測試
- @pytest.mark.smoke: 快速煙霧測試（不需 API）
- @pytest.mark.integration: 整合測試（需完整環境）
- @pytest.mark.performance: 效能測試
- @pytest.mark.reliability: 穩定性測試

測試案例命名規則
----------------
- GS_BASIC_001-010: 基礎對話測試
- GS_TOOL_001-008: 工具使用測試
- GS_SENSITIVE_001-005: 敏感議題測試
- GS_MULTI_001-007: 多輪對話測試
- GS_ERROR_001-005 + BOUNDARY_001-003: 錯誤處理測試
- GS_INTEGRATION_001-010: 系統整合測試

維護準則
--------
1. **不可刪除**：Golden Set 測試用例一旦建立，不應刪除
2. **只能新增**：可以新增測試用例，ID 向後遞增
3. **失敗必修**：Golden Set 測試失敗必須立即修復或更新預期行為
4. **定期審查**：每季度審查測試用例的有效性
5. **文件同步**：修改測試時同步更新 description

版本: v1.0.0
最後更新: 2026-01-25
"""

# Golden Set 測試分類
GOLDEN_SET_CATEGORIES = {
    'basic_conversation': '基礎對話流程',
    'tool_use': '工具使用準確性',
    'sensitive_topics': '敏感議題處理',
    'multi_turn': '多輪對話上下文',
    'error_handling': '錯誤處理',
    'system_integration': '系統整合'
}

# 每個類別的預期測試數量（用於完整性檢查）
EXPECTED_TEST_COUNTS = {
    'basic_conversation': 10,     # GS_BASIC_001-010
    'tool_use': 8,                # GS_TOOL_001-008
    'sensitive_topics': 5,         # GS_SENSITIVE_001-005
    'multi_turn': 7,              # GS_MULTI_001-007
    'error_handling': 8,          # GS_ERROR_001-005 + GS_BOUNDARY_001-003
    'system_integration': 10      # GS_INTEGRATION_001-010
}

# Golden Set 總計
TOTAL_GOLDEN_CASES = sum(EXPECTED_TEST_COUNTS.values())  # 48

# 測試執行配置
GOLDEN_SET_CONFIG = {
    'require_api_server': True,
    'require_gemini_api': True,
    'timeout_per_test': 30,  # 秒
    'retry_on_failure': 1,
    'parallel_execution': False
}

