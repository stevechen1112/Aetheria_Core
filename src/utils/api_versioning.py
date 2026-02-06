"""
API Schema 版本化系統
管理 API 回應格式的向後兼容性

版本: v1.0.0
最後更新: 2026-02-05
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class APIVersion(Enum):
    """API 版本定義"""
    V1_0 = "1.0.0"  # Phase 1: 基礎功能
    V2_0 = "2.0.0"  # Phase 2: 深度優化（當前版本）
    V3_0 = "3.0.0"  # Phase 3: 敏感議題攔截 + 版本化


# 當前穩定版本
CURRENT_VERSION = APIVersion.V3_0

# 支援的版本範圍
SUPPORTED_VERSIONS = [APIVersion.V2_0, APIVersion.V3_0]

# 棄用警告版本
DEPRECATED_VERSIONS = [APIVersion.V1_0]


@dataclass
class SchemaVersion:
    """Schema 版本資訊"""
    version: str
    released_date: str
    deprecated: bool = False
    sunset_date: Optional[str] = None  # 棄用日期
    breaking_changes: List[str] = None
    
    def __post_init__(self):
        if self.breaking_changes is None:
            self.breaking_changes = []


# 版本歷史記錄
VERSION_HISTORY = {
    "1.0.0": SchemaVersion(
        version="1.0.0",
        released_date="2026-01-15",
        deprecated=True,
        sunset_date="2026-06-01",
        breaking_changes=[
            "初始版本，無破壞性變更"
        ]
    ),
    "2.0.0": SchemaVersion(
        version="2.0.0",
        released_date="2026-01-25",
        deprecated=False,
        breaking_changes=[
            "新增 citations 陣列",
            "新增 used_systems 陣列",
            "新增 confidence 浮點數",
            "fortune_profile 結構優化"
        ]
    ),
    "3.0.0": SchemaVersion(
        version="3.0.0",
        released_date="2026-02-05",
        deprecated=False,
        breaking_changes=[
            "新增 schema_version 欄位",
            "新增 sensitive_topic_detected 欄位（可選）",
            "敏感議題攔截回應格式標準化"
        ]
    )
}


class ResponseVersioner:
    """API 回應版本化處理器"""
    
    def __init__(self, target_version: Optional[str] = None):
        """
        初始化版本處理器
        
        Args:
            target_version: 目標版本（預設使用最新版本）
        """
        if target_version and is_version_supported(target_version):
            self.target_version = target_version
        else:
            self.target_version = CURRENT_VERSION.value
    
    def version_response(self, response_data: Dict[str, Any], endpoint: str = None) -> Dict[str, Any]:
        """
        為回應添加版本資訊並確保向後兼容
        
        Args:
            response_data: 原始回應資料
            endpoint: API 端點名稱（用於日誌）
            
        Returns:
            版本化後的回應資料
        """
        # 複製回應以避免修改原始資料
        versioned = dict(response_data)
        
        # 添加 schema_version 欄位
        versioned['schema_version'] = self.target_version
        
        # 如果使用舊版本，進行向下兼容轉換
        if self.target_version == "1.0.0":
            versioned = self._downgrade_to_v1(versioned)
        elif self.target_version == "2.0.0":
            versioned = self._downgrade_to_v2(versioned)
        
        # 添加棄用警告（如果需要）
        if self.target_version in [v.value for v in DEPRECATED_VERSIONS]:
            versioned['_deprecated_warning'] = {
                'message': f'API version {self.target_version} is deprecated',
                'sunset_date': VERSION_HISTORY[self.target_version].sunset_date,
                'upgrade_to': CURRENT_VERSION.value
            }
        
        return versioned
    
    def _downgrade_to_v1(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """降級到 v1.0.0 格式（移除 v2+ 欄位）"""
        # 移除 v2+ 新增的欄位
        data.pop('citations', None)
        data.pop('used_systems', None)
        data.pop('confidence', None)
        data.pop('sensitive_topic_detected', None)
        data.pop('schema_version', None)
        
        # 簡化 fortune_profile
        if 'fortune_profile' in data and isinstance(data['fortune_profile'], dict):
            data['fortune_profile'] = {
                'facts': data['fortune_profile'].get('facts', [])
            }
        
        return data
    
    def _downgrade_to_v2(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """降級到 v2.0.0 格式（移除 v3+ 欄位）"""
        # 移除 v3+ 新增的欄位
        data.pop('sensitive_topic_detected', None)
        data.pop('schema_version', None)
        
        return data


def get_client_version(headers: Dict[str, str]) -> Optional[str]:
    """
    從請求標頭中獲取客戶端期望的 API 版本
    
    支援多種標頭格式：
    - Accept-Version: 2.0.0
    - X-API-Version: 2.0.0
    - API-Version: 2.0.0
    
    Args:
        headers: Flask request.headers
        
    Returns:
        版本字串或 None（使用預設版本）
    """
    # 嘗試多種標頭格式
    version_headers = [
        'Accept-Version',
        'X-API-Version',
        'API-Version',
        'X-Aetheria-Version'
    ]
    
    for header in version_headers:
        if header in headers:
            requested_version = headers[header].strip()
            # 驗證版本格式
            if _is_valid_version(requested_version) and is_version_supported(requested_version):
                return requested_version
    
    return None


def _is_valid_version(version: str) -> bool:
    """驗證版本字串格式（X.Y.Z）"""
    import re
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))


def is_version_supported(version: str) -> bool:
    """檢查版本是否受支援"""
    try:
        api_version = APIVersion(version)
        return api_version in SUPPORTED_VERSIONS or api_version in DEPRECATED_VERSIONS
    except ValueError:
        return False


def get_version_info() -> Dict[str, Any]:
    """獲取 API 版本資訊（用於 /version 端點）"""
    return {
        'current_version': CURRENT_VERSION.value,
        'supported_versions': [v.value for v in SUPPORTED_VERSIONS],
        'deprecated_versions': [v.value for v in DEPRECATED_VERSIONS],
        'version_history': {
            ver: {
                'version': info.version,
                'released_date': info.released_date,
                'deprecated': info.deprecated,
                'sunset_date': info.sunset_date,
                'breaking_changes': info.breaking_changes
            }
            for ver, info in VERSION_HISTORY.items()
        }
    }


# 全局版本處理器實例
_default_versioner = None


def get_response_versioner(version: Optional[str] = None) -> ResponseVersioner:
    """
    獲取版本處理器實例
    
    Args:
        version: 目標版本（None 則使用當前版本）
        
    Returns:
        ResponseVersioner 實例
    """
    global _default_versioner
    
    if version and is_version_supported(version):
        return ResponseVersioner(version)
    
    if _default_versioner is None:
        _default_versioner = ResponseVersioner()
    
    return _default_versioner
