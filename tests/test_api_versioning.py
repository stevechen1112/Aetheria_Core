"""
API Schema 版本化系統測試
測試 Phase 3.2 的版本協商、向後兼容、棄用警告
"""

import pytest
from src.utils.api_versioning import (
    APIVersion,
    ResponseVersioner,
    get_client_version,
    is_version_supported,
    get_version_info,
    CURRENT_VERSION,
    SUPPORTED_VERSIONS,
    DEPRECATED_VERSIONS
)


class TestAPIVersioning:
    """API 版本化核心功能測試"""
    
    def test_current_version_defined(self):
        """測試當前版本已定義"""
        assert CURRENT_VERSION == APIVersion.V3_0
        assert CURRENT_VERSION.value == "3.0.0"
    
    def test_supported_versions_list(self):
        """測試支援版本清單"""
        assert APIVersion.V2_0 in SUPPORTED_VERSIONS
        assert APIVersion.V3_0 in SUPPORTED_VERSIONS
        assert len(SUPPORTED_VERSIONS) >= 2
    
    def test_deprecated_versions_list(self):
        """測試棄用版本清單"""
        assert APIVersion.V1_0 in DEPRECATED_VERSIONS
    
    def test_is_version_supported_valid(self):
        """測試版本支援檢查（有效版本）"""
        assert is_version_supported("2.0.0") == True
        assert is_version_supported("3.0.0") == True
    
    def test_is_version_supported_deprecated(self):
        """測試版本支援檢查（棄用版本）"""
        assert is_version_supported("1.0.0") == True  # 棄用但仍支援
    
    def test_is_version_supported_invalid(self):
        """測試版本支援檢查（無效版本）"""
        assert is_version_supported("99.99.99") == False
        assert is_version_supported("invalid") == False
    
    def test_get_version_info(self):
        """測試版本資訊端點資料"""
        info = get_version_info()
        
        assert 'current_version' in info
        assert info['current_version'] == "3.0.0"
        
        assert 'supported_versions' in info
        assert isinstance(info['supported_versions'], list)
        assert "2.0.0" in info['supported_versions']
        
        assert 'deprecated_versions' in info
        assert isinstance(info['deprecated_versions'], list)
        
        assert 'version_history' in info
        assert isinstance(info['version_history'], dict)


class TestResponseVersioner:
    """回應版本化處理器測試"""
    
    def test_versioner_initialization_default(self):
        """測試版本處理器初始化（預設版本）"""
        versioner = ResponseVersioner()
        assert versioner.target_version == CURRENT_VERSION.value
    
    def test_versioner_initialization_specific(self):
        """測試版本處理器初始化（指定版本）"""
        versioner = ResponseVersioner("2.0.0")
        assert versioner.target_version == "2.0.0"
    
    def test_version_response_adds_schema_version(self):
        """測試版本化回應添加 schema_version 欄位"""
        versioner = ResponseVersioner("3.0.0")
        response = {'status': 'success', 'data': 'test'}
        
        versioned = versioner.version_response(response)
        
        assert 'schema_version' in versioned
        assert versioned['schema_version'] == "3.0.0"
        assert versioned['status'] == 'success'  # 原始資料保留
    
    def test_version_response_current_version(self):
        """測試當前版本（v3.0）回應"""
        versioner = ResponseVersioner("3.0.0")
        response = {
            'status': 'success',
            'reply': 'test reply',
            'citations': ['ref1'],
            'used_systems': ['ziwei'],
            'confidence': 0.85,
            'sensitive_topic_detected': 'none'
        }
        
        versioned = versioner.version_response(response)
        
        # 所有欄位應保留
        assert 'schema_version' in versioned
        assert 'reply' in versioned
        assert 'citations' in versioned
        assert 'used_systems' in versioned
        assert 'confidence' in versioned
        assert 'sensitive_topic_detected' in versioned
    
    def test_version_response_downgrade_to_v2(self):
        """測試降級到 v2.0（移除 v3 欄位）"""
        versioner = ResponseVersioner("2.0.0")
        response = {
            'status': 'success',
            'reply': 'test reply',
            'citations': ['ref1'],
            'used_systems': ['ziwei'],
            'confidence': 0.85,
            'sensitive_topic_detected': 'suicide_death'  # v3 新增
        }
        
        versioned = versioner.version_response(response)
        
        # v2 欄位應保留
        assert 'reply' in versioned
        assert 'citations' in versioned
        assert 'used_systems' in versioned
        assert 'confidence' in versioned
        
        # v3 欄位應移除
        assert 'sensitive_topic_detected' not in versioned
        assert 'schema_version' not in versioned
    
    def test_version_response_downgrade_to_v1(self):
        """測試降級到 v1.0（移除 v2+ 欄位）"""
        versioner = ResponseVersioner("1.0.0")
        response = {
            'status': 'success',
            'reply': 'test reply',
            'citations': ['ref1'],          # v2 新增
            'used_systems': ['ziwei'],      # v2 新增
            'confidence': 0.85,             # v2 新增
            'sensitive_topic_detected': 'none'  # v3 新增
        }
        
        versioned = versioner.version_response(response)
        
        # 基礎欄位應保留
        assert 'status' in versioned
        assert 'reply' in versioned
        
        # v2+ 欄位應全部移除
        assert 'citations' not in versioned
        assert 'used_systems' not in versioned
        assert 'confidence' not in versioned
        assert 'sensitive_topic_detected' not in versioned
        assert 'schema_version' not in versioned
    
    def test_deprecated_version_warning(self):
        """測試棄用版本警告"""
        versioner = ResponseVersioner("1.0.0")
        response = {'status': 'success', 'data': 'test'}
        
        versioned = versioner.version_response(response)
        
        assert '_deprecated_warning' in versioned
        assert 'message' in versioned['_deprecated_warning']
        assert 'deprecated' in versioned['_deprecated_warning']['message'].lower()
        assert 'sunset_date' in versioned['_deprecated_warning']
        assert 'upgrade_to' in versioned['_deprecated_warning']
        assert versioned['_deprecated_warning']['upgrade_to'] == CURRENT_VERSION.value
    
    def test_no_warning_for_current_version(self):
        """測試當前版本無警告"""
        versioner = ResponseVersioner("3.0.0")
        response = {'status': 'success', 'data': 'test'}
        
        versioned = versioner.version_response(response)
        
        assert '_deprecated_warning' not in versioned


class TestClientVersionNegotiation:
    """客戶端版本協商測試"""
    
    def test_get_client_version_accept_version_header(self):
        """測試 Accept-Version 標頭"""
        headers = {'Accept-Version': '2.0.0'}
        version = get_client_version(headers)
        assert version == '2.0.0'
    
    def test_get_client_version_x_api_version_header(self):
        """測試 X-API-Version 標頭"""
        headers = {'X-API-Version': '3.0.0'}
        version = get_client_version(headers)
        assert version == '3.0.0'
    
    def test_get_client_version_api_version_header(self):
        """測試 API-Version 標頭"""
        headers = {'API-Version': '2.0.0'}
        version = get_client_version(headers)
        assert version == '2.0.0'
    
    def test_get_client_version_no_header(self):
        """測試無版本標頭（使用預設）"""
        headers = {}
        version = get_client_version(headers)
        assert version is None  # 應返回 None，交由 versioner 使用預設
    
    def test_get_client_version_invalid_format(self):
        """測試無效版本格式"""
        headers = {'Accept-Version': 'invalid-version'}
        version = get_client_version(headers)
        assert version is None

    def test_get_client_version_unsupported_version(self):
        """測試不支援版本應回退"""
        headers = {'Accept-Version': '4.0.0'}
        version = get_client_version(headers)
        assert version is None
    
    def test_get_client_version_priority(self):
        """測試多個標頭時的優先級"""
        headers = {
            'Accept-Version': '2.0.0',
            'X-API-Version': '3.0.0'
        }
        version = get_client_version(headers)
        # Accept-Version 應優先
        assert version == '2.0.0'


class TestVersioningEdgeCases:
    """版本化邊界條件測試"""
    
    def test_versioner_preserves_original_data(self):
        """測試版本化不修改原始資料"""
        versioner = ResponseVersioner("3.0.0")
        original = {'status': 'success', 'data': 'test'}
        original_copy = dict(original)
        
        versioned = versioner.version_response(original)
        
        # 原始資料應不變
        assert original == original_copy
        # 版本化資料應為新物件
        assert versioned is not original
    
    def test_versioner_handles_empty_response(self):
        """測試空回應"""
        versioner = ResponseVersioner("3.0.0")
        response = {}
        
        versioned = versioner.version_response(response)
        
        assert 'schema_version' in versioned
        assert versioned['schema_version'] == "3.0.0"

    def test_versioner_unsupported_fallback(self):
        """測試不支援版本時回退到最新版本"""
        versioner = ResponseVersioner("4.0.0")
        assert versioner.target_version == CURRENT_VERSION.value
    
    def test_versioner_handles_nested_objects(self):
        """測試巢狀物件"""
        versioner = ResponseVersioner("3.0.0")
        response = {
            'status': 'success',
            'data': {
                'nested': {
                    'deep': 'value'
                }
            }
        }
        
        versioned = versioner.version_response(response)
        
        assert 'schema_version' in versioned
        assert versioned['data']['nested']['deep'] == 'value'
    
    def test_downgrade_preserves_unknown_fields(self):
        """測試降級保留未知欄位"""
        versioner = ResponseVersioner("2.0.0")
        response = {
            'status': 'success',
            'custom_field': 'custom_value',  # 未知欄位
            'sensitive_topic_detected': 'none'  # v3 欄位
        }
        
        versioned = versioner.version_response(response)
        
        # 未知欄位應保留
        assert 'custom_field' in versioned
        assert versioned['custom_field'] == 'custom_value'
        
        # v3 欄位應移除
        assert 'sensitive_topic_detected' not in versioned


class TestVersionHistoryMetadata:
    """版本歷史元資料測試"""
    
    def test_version_info_includes_breaking_changes(self):
        """測試版本資訊包含破壞性變更"""
        info = get_version_info()
        
        v2_info = info['version_history']['2.0.0']
        assert 'breaking_changes' in v2_info
        assert isinstance(v2_info['breaking_changes'], list)
        assert len(v2_info['breaking_changes']) > 0
    
    def test_version_info_includes_release_dates(self):
        """測試版本資訊包含發布日期"""
        info = get_version_info()
        
        v3_info = info['version_history']['3.0.0']
        assert 'released_date' in v3_info
        assert v3_info['released_date'] == "2026-02-05"
    
    def test_version_info_marks_deprecated_versions(self):
        """測試版本資訊標記棄用版本"""
        info = get_version_info()
        
        v1_info = info['version_history']['1.0.0']
        assert 'deprecated' in v1_info
        assert v1_info['deprecated'] == True
        assert 'sunset_date' in v1_info


class TestVersioningIntegration:
    """版本化整合測試（模擬 API 流程）"""
    
    def test_full_workflow_v3_client(self):
        """測試完整流程：v3.0 客戶端"""
        # 模擬客戶端請求
        headers = {'Accept-Version': '3.0.0'}
        client_version = get_client_version(headers)
        
        # 建立回應
        response = {
            'status': 'success',
            'reply': 'AI 回應',
            'citations': ['ref1'],
            'used_systems': ['ziwei'],
            'confidence': 0.85,
            'sensitive_topic_detected': None
        }
        
        # 版本化處理
        versioner = ResponseVersioner(client_version)
        versioned = versioner.version_response(response)
        
        # 驗證
        assert versioned['schema_version'] == '3.0.0'
        assert 'citations' in versioned
        assert 'sensitive_topic_detected' in versioned
        assert '_deprecated_warning' not in versioned
    
    def test_full_workflow_v2_client(self):
        """測試完整流程：v2.0 客戶端（降級）"""
        headers = {'Accept-Version': '2.0.0'}
        client_version = get_client_version(headers)
        
        response = {
            'status': 'success',
            'reply': 'AI 回應',
            'citations': ['ref1'],
            'used_systems': ['ziwei'],
            'confidence': 0.85,
            'sensitive_topic_detected': 'none'  # v3 欄位
        }
        
        versioner = ResponseVersioner(client_version)
        versioned = versioner.version_response(response)
        
        # v2 不應有 v3 欄位
        assert 'sensitive_topic_detected' not in versioned
        # v2 應有基礎欄位
        assert 'citations' in versioned
        assert 'confidence' in versioned
    
    def test_full_workflow_v1_client_with_warning(self):
        """測試完整流程：v1.0 客戶端（棄用警告）"""
        headers = {'Accept-Version': '1.0.0'}
        client_version = get_client_version(headers)
        
        response = {
            'status': 'success',
            'reply': 'AI 回應',
            'citations': ['ref1'],
            'confidence': 0.85
        }
        
        versioner = ResponseVersioner(client_version)
        versioned = versioner.version_response(response)
        
        # 應有棄用警告
        assert '_deprecated_warning' in versioned
        assert 'sunset_date' in versioned['_deprecated_warning']
        
        # 不應有 v2+ 欄位
        assert 'citations' not in versioned
        assert 'confidence' not in versioned
