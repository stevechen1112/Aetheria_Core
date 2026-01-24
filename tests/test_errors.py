"""
錯誤處理模組測試
測試自定義異常和錯誤碼
"""

import pytest
from src.utils.errors import (
    AetheriaException,
    ErrorCode,
    MissingParameterException,
    InvalidParameterException,
    UserNotFoundException,
    ChartNotFoundException,
    ChartNotLockedException,
    AIAPIException,
    format_error_response
)


class TestErrorCodes:
    """錯誤碼測試"""
    
    def test_error_code_values(self):
        """測試錯誤碼數值範圍"""
        # 驗證錯誤碼在合理範圍內
        assert ErrorCode.MISSING_PARAMETER.value >= 1000
        assert ErrorCode.USER_NOT_FOUND.value >= 2000
        assert ErrorCode.AI_API_ERROR.value >= 4000
    
    def test_error_code_uniqueness(self):
        """測試錯誤碼唯一性"""
        codes = [e.value for e in ErrorCode]
        assert len(codes) == len(set(codes))


class TestAetheriaException:
    """基礎異常測試"""
    
    def test_exception_creation(self):
        """測試異常建立"""
        exc = AetheriaException(
            message='缺少必要參數',
            error_code=ErrorCode.MISSING_PARAMETER,
            details={'param': 'user_id'}
        )
        
        assert exc.error_code == ErrorCode.MISSING_PARAMETER
        assert exc.message == '缺少必要參數'
        assert exc.details == {'param': 'user_id'}
    
    def test_exception_string(self):
        """測試異常字串表示"""
        exc = AetheriaException(
            message='驗證失敗',
            error_code=ErrorCode.VALIDATION_ERROR
        )
        
        str_repr = str(exc)
        assert '驗證失敗' in str_repr
    
    def test_exception_to_dict(self):
        """測試異常轉字典"""
        exc = AetheriaException(
            message='無效參數',
            error_code=ErrorCode.INVALID_PARAMETER,
            details={'param': 'date', 'value': 'invalid'}
        )
        
        d = exc.to_dict()
        assert d['error_code'] == ErrorCode.INVALID_PARAMETER.value
        assert d['message'] == '無效參數'
        assert d['details']['param'] == 'date'


class TestSpecificExceptions:
    """特定異常類別測試"""
    
    def test_missing_parameter_exception(self):
        """測試缺少參數異常"""
        exc = MissingParameterException('user_id')
        
        assert exc.code == ErrorCode.MISSING_PARAMETER
        assert 'user_id' in exc.message
        assert exc.http_status == 400
    
    def test_invalid_parameter_exception(self):
        """測試無效參數異常"""
        exc = InvalidParameterException('birth_date', '日期格式錯誤')
        
        assert exc.code == ErrorCode.INVALID_PARAMETER
        assert 'birth_date' in exc.message
        assert exc.http_status == 400
    
    def test_user_not_found_exception(self):
        """測試用戶不存在異常"""
        exc = UserNotFoundException('user_123')
        
        assert exc.code == ErrorCode.USER_NOT_FOUND
        assert 'user_123' in exc.message
        assert exc.http_status == 404
    
    def test_chart_not_found_exception(self):
        """測試命盤不存在異常"""
        exc = ChartNotFoundException('user_123')
        
        assert exc.code == ErrorCode.CHART_NOT_FOUND
        assert exc.http_status == 404
    
    def test_chart_not_locked_exception(self):
        """測試命盤未鎖定異常"""
        exc = ChartNotLockedException('user_123')
        
        assert exc.code == ErrorCode.CHART_NOT_LOCKED
        assert exc.http_status == 400
    
    def test_ai_api_exception(self):
        """測試 AI API 異常"""
        exc = AIAPIException('API 連線逾時')
        
        assert exc.code == ErrorCode.AI_API_ERROR
        assert exc.http_status == 503


class TestFormatErrorResponse:
    """格式化錯誤回應測試"""
    
    def test_format_basic_error(self):
        """測試基本錯誤格式化"""
        response = format_error_response(
            ErrorCode.VALIDATION_ERROR,
            '驗證失敗'
        )
        
        assert 'error' in response
        assert 'error_code' in response
        assert response['error'] == '驗證失敗'
    
    def test_format_error_with_details(self):
        """測試帶詳情的錯誤格式化"""
        response = format_error_response(
            ErrorCode.MISSING_PARAMETER,
            '缺少參數',
            {'param': 'user_id', 'location': 'body'}
        )
        
        assert response['details']['param'] == 'user_id'
    
    def test_format_error_excludes_none_details(self):
        """測試不包含 None 詳情"""
        response = format_error_response(
            ErrorCode.INTERNAL_ERROR,
            '內部錯誤',
            None
        )
        
        assert 'details' not in response


class TestExceptionInheritance:
    """異常繼承關係測試"""
    
    def test_all_exceptions_inherit_from_base(self):
        """測試所有異常都繼承自基礎類別"""
        exceptions = [
            MissingParameterException('test'),
            InvalidParameterException('test', 'reason'),
            UserNotFoundException('user'),
            ChartNotFoundException('user'),
            ChartNotLockedException('user'),
            AIAPIException('error')
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AetheriaException)
            assert isinstance(exc, Exception)
    
    def test_exceptions_can_be_caught_by_base(self):
        """測試可以用基礎類別捕獲所有異常"""
        def raise_missing_param():
            raise MissingParameterException('test')
        
        with pytest.raises(AetheriaException):
            raise_missing_param()
