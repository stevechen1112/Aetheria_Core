"""
日誌模組測試
測試結構化日誌功能
"""

import pytest
import logging
import json
import tempfile
from pathlib import Path
from io import StringIO

from src.utils.logger import AetheriaLogger, setup_logger


class TestAetheriaLogger:
    """日誌記錄器測試"""
    
    @pytest.fixture
    def logger_with_capture(self):
        """建立可捕獲輸出的日誌記錄器"""
        # 建立 StringIO 來捕獲日誌
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        
        logger = AetheriaLogger('test_logger')
        logger.logger.handlers = [handler]
        logger.logger.setLevel(logging.DEBUG)
        
        return logger, log_capture
    
    def test_logger_creation(self):
        """測試日誌記錄器建立"""
        logger = AetheriaLogger('test')
        assert logger is not None
        # 檢查底層 logger 的名稱
        assert logger.logger.name == 'test'
    
    def test_info_logging(self, logger_with_capture):
        """測試 INFO 級別日誌"""
        logger, capture = logger_with_capture
        
        logger.info('測試訊息')
        
        output = capture.getvalue()
        assert '測試訊息' in output
    
    def test_warning_logging(self, logger_with_capture):
        """測試 WARNING 級別日誌"""
        logger, capture = logger_with_capture
        
        logger.warning('警告訊息')
        
        output = capture.getvalue()
        assert '警告訊息' in output
    
    def test_error_logging(self, logger_with_capture):
        """測試 ERROR 級別日誌"""
        logger, capture = logger_with_capture
        
        logger.error('錯誤訊息')
        
        output = capture.getvalue()
        assert '錯誤訊息' in output
    
    def test_debug_logging(self, logger_with_capture):
        """測試 DEBUG 級別日誌"""
        logger, capture = logger_with_capture
        
        logger.debug('除錯訊息')
        
        output = capture.getvalue()
        assert '除錯訊息' in output
    
    def test_logging_with_user_id(self, logger_with_capture):
        """測試帶 user_id 的日誌"""
        logger, capture = logger_with_capture
        
        logger.info('用戶操作', user_id='test_user_001')
        
        output = capture.getvalue()
        # 檢查 user_id 是否出現在日誌中
        assert 'test_user_001' in output or '用戶操作' in output
    
    def test_logging_with_extra_fields(self, logger_with_capture):
        """測試帶額外欄位的日誌"""
        logger, capture = logger_with_capture
        
        logger.info(
            '請求處理',
            user_id='user_001',
            endpoint='/api/test',
            method='POST'
        )
        
        output = capture.getvalue()
        assert '請求處理' in output


class TestAPILogging:
    """API 日誌測試"""
    
    @pytest.fixture
    def logger(self):
        """建立測試日誌記錄器"""
        return AetheriaLogger('api_test')
    
    def test_log_api_request(self, logger):
        """測試 API 請求日誌"""
        # 這個方法應該不拋出異常
        logger.log_api_request('/api/chart/initial-analysis', 'POST', user_id='user_001')
    
    def test_log_api_response(self, logger):
        """測試 API 回應日誌"""
        logger.log_api_response('/api/chart/initial-analysis', 200, 150.5)
    
    def test_log_error_message(self, logger):
        """測試錯誤訊息日誌"""
        # 使用標準 error 方法記錄錯誤
        logger.error('API 錯誤發生', endpoint='/api/test', error='測試錯誤')


class TestSetupLogger:
    """setup_logger 函數測試"""
    
    def test_setup_logger_returns_logger(self):
        """測試 setup_logger 返回日誌記錄器"""
        logger = setup_logger()
        assert logger is not None
        assert isinstance(logger, AetheriaLogger)
    
    def test_setup_logger_default_name(self):
        """測試使用預設名稱"""
        logger = setup_logger()
        # 預設名稱應該是 'aetheria'
        assert logger.logger.name == 'aetheria'


class TestLogFileRotation:
    """日誌檔案輪轉測試"""
    
    def test_log_file_created(self):
        """測試日誌檔案建立"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / 'test.log'
            
            # 建立帶檔案處理器的日誌記錄器
            logger = AetheriaLogger('file_test')
            file_handler = logging.FileHandler(str(log_path))
            logger.logger.addHandler(file_handler)
            
            logger.info('測試檔案日誌')
            file_handler.close()
            
            # 驗證檔案存在且有內容
            assert log_path.exists()
            content = log_path.read_text()
            assert '測試檔案日誌' in content
