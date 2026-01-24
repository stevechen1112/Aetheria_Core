"""
統一錯誤處理模組
定義標準錯誤類型和處理機制
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """錯誤代碼枚舉"""
    # 通用錯誤 (1000-1999)
    UNKNOWN_ERROR = 1000
    INVALID_REQUEST = 1001
    MISSING_PARAMETER = 1002
    INVALID_PARAMETER = 1003
    VALIDATION_ERROR = 1004
    INTERNAL_ERROR = 1005
    
    # 用戶相關 (2000-2999)
    USER_NOT_FOUND = 2000
    USER_ALREADY_EXISTS = 2001
    INVALID_USER_DATA = 2002
    
    # 命盤相關 (3000-3999)
    CHART_NOT_FOUND = 3000
    CHART_NOT_LOCKED = 3001
    CHART_ALREADY_LOCKED = 3002
    CHART_CALCULATION_ERROR = 3003
    CHART_EXTRACTION_ERROR = 3004
    
    # AI 相關 (4000-4999)
    AI_API_ERROR = 4000
    AI_TIMEOUT = 4001
    AI_RATE_LIMIT = 4002
    AI_INVALID_RESPONSE = 4003
    
    # 資料庫相關 (5000-5999)
    DATABASE_ERROR = 5000
    DATABASE_CONNECTION_ERROR = 5001
    DATABASE_QUERY_ERROR = 5002


class AetheriaException(Exception):
    """Aetheria 基礎異常類別"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        """
        初始化異常
        
        Args:
            message: 錯誤訊息
            error_code: 錯誤代碼
            details: 詳細資訊
            status_code: HTTP 狀態碼
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式（用於 API 回應）"""
        return {
            'status': 'error',
            'error_code': self.error_code.value,
            'error_name': self.error_code.name,
            'message': self.message,
            'details': self.details
        }


# ==================== 特定異常類型 ====================

class InvalidRequestException(AetheriaException):
    """無效請求異常"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_REQUEST,
            details=details,
            status_code=400
        )


class MissingParameterException(AetheriaException):
    """缺少參數異常"""
    
    def __init__(self, parameter_name: str):
        super().__init__(
            message=f"缺少必要參數: {parameter_name}",
            error_code=ErrorCode.MISSING_PARAMETER,
            details={'parameter': parameter_name},
            status_code=400
        )
        self.code = ErrorCode.MISSING_PARAMETER
        self.http_status = 400


class InvalidParameterException(AetheriaException):
    """無效參數異常"""
    
    def __init__(self, parameter_name: str, reason: str = ''):
        message = f"無效參數: {parameter_name}"
        if reason:
            message += f" - {reason}"
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_PARAMETER,
            details={'parameter': parameter_name, 'reason': reason},
            status_code=400
        )
        self.code = ErrorCode.INVALID_PARAMETER
        self.http_status = 400


class UserNotFoundException(AetheriaException):
    """用戶不存在異常"""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"用戶不存在: {user_id}",
            error_code=ErrorCode.USER_NOT_FOUND,
            details={'user_id': user_id},
            status_code=404
        )
        self.code = ErrorCode.USER_NOT_FOUND
        self.http_status = 404


class ChartNotFoundException(AetheriaException):
    """命盤不存在異常"""
    
    def __init__(self, user_id: str, message: str = None):
        super().__init__(
            message=message or f"用戶命盤不存在: {user_id}",
            error_code=ErrorCode.CHART_NOT_FOUND,
            details={'user_id': user_id},
            status_code=404
        )
        self.code = ErrorCode.CHART_NOT_FOUND
        self.http_status = 404


class ChartNotLockedException(AetheriaException):
    """命盤未鎖定異常"""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"用戶命盤尚未鎖定: {user_id}",
            error_code=ErrorCode.CHART_NOT_LOCKED,
            details={'user_id': user_id},
            status_code=400
        )
        self.code = ErrorCode.CHART_NOT_LOCKED
        self.http_status = 400


class AIAPIException(AetheriaException):
    """AI API 異常"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"AI API 錯誤: {message}",
            error_code=ErrorCode.AI_API_ERROR,
            details=details,
            status_code=503
        )
        self.code = ErrorCode.AI_API_ERROR
        self.http_status = 503


class DatabaseException(AetheriaException):
    """資料庫異常"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"資料庫錯誤: {message}",
            error_code=ErrorCode.DATABASE_ERROR,
            details=details,
            status_code=500
        )


# ==================== 輔助函數 ====================

def format_error_response(
    error_code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    格式化錯誤回應
    
    Args:
        error_code: 錯誤代碼
        message: 錯誤訊息
        details: 詳細資訊（可選）
    
    Returns:
        格式化的錯誤字典
    """
    response = {
        'status': 'error',
        'error_code': error_code.value,
        'error_name': error_code.name,
        'message': message,
        'error': message
    }
    
    if details:
        response['details'] = details
    
    return response


# ==================== 錯誤處理裝飾器 ====================

def handle_errors(func):
    """
    錯誤處理裝飾器
    自動捕獲異常並轉換為標準格式
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AetheriaException:
            # 已經是我們的異常，直接拋出
            raise
        except Exception as e:
            # 未知異常，包裝成 AetheriaException
            raise AetheriaException(
                message=str(e),
                error_code=ErrorCode.UNKNOWN_ERROR,
                details={'original_error': type(e).__name__}
            )
    
    return wrapper


# ==================== Flask 錯誤處理器 ====================

def register_error_handlers(app):
    """
    註冊 Flask 錯誤處理器
    
    Args:
        app: Flask app 實例
    """
    from flask import jsonify
    
    @app.errorhandler(AetheriaException)
    def handle_aetheria_exception(error: AetheriaException):
        """處理 Aetheria 異常"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """處理 404 錯誤"""
        return jsonify({
            'status': 'error',
            'error_code': 404,
            'message': '請求的資源不存在'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """處理 405 錯誤"""
        return jsonify({
            'status': 'error',
            'error_code': 405,
            'message': '不允許的 HTTP 方法'
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """處理 500 錯誤"""
        return jsonify({
            'status': 'error',
            'error_code': 500,
            'message': '伺服器內部錯誤'
        }), 500
