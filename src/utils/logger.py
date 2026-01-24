"""
結構化日誌系統
提供統一的日誌記錄接口
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json


class JSONFormatter(logging.Formatter):
    """JSON 格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        將日誌記錄格式化為 JSON
        
        Args:
            record: 日誌記錄
            
        Returns:
            JSON 格式字串
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加額外的欄位
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'extra_data'):
            log_data['extra_data'] = record.extra_data
        
        # 添加異常資訊
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class AetheriaLogger:
    """Aetheria 日誌管理器"""
    
    def __init__(
        self,
        name: str = 'aetheria',
        log_dir: str = 'logs',
        log_level: str = 'INFO',
        enable_console: bool = True,
        enable_file: bool = True,
        json_format: bool = False
    ):
        """
        初始化日誌管理器
        
        Args:
            name: Logger 名稱
            log_dir: 日誌檔案目錄
            log_level: 日誌級別
            enable_console: 是否啟用控制台輸出
            enable_file: 是否啟用檔案輸出
            json_format: 是否使用 JSON 格式
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.logger.handlers.clear()  # 清除既有的 handler
        
        # 建立日誌目錄
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # 選擇格式化器
        if json_format:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # 控制台 Handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 檔案 Handler
        if enable_file:
            # 一般日誌
            file_handler = logging.FileHandler(
                log_path / f'aetheria_{datetime.now().strftime("%Y%m%d")}.log',
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            # 錯誤日誌（單獨檔案）
            error_handler = logging.FileHandler(
                log_path / f'error_{datetime.now().strftime("%Y%m%d")}.log',
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """記錄 DEBUG 級別日誌"""
        self._log(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs):
        """記錄 INFO 級別日誌"""
        self._log(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """記錄 WARNING 級別日誌"""
        self._log(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """記錄 ERROR 級別日誌"""
        self._log(logging.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """記錄 CRITICAL 級別日誌"""
        self._log(logging.CRITICAL, message, kwargs)
    
    def _log(self, level: int, message: str, extra: Dict[str, Any]):
        """
        內部日誌記錄方法
        
        Args:
            level: 日誌級別
            message: 日誌訊息
            extra: 額外資訊
        """
        # 建立 extra 字典
        log_extra = {}
        if 'user_id' in extra:
            log_extra['user_id'] = extra.pop('user_id')
        if 'request_id' in extra:
            log_extra['request_id'] = extra.pop('request_id')
        if extra:
            log_extra['extra_data'] = extra
        
        self.logger.log(level, message, extra=log_extra if log_extra else None)
    
    def log_api_request(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """
        記錄 API 請求
        
        Args:
            endpoint: API 端點
            method: HTTP 方法
            user_id: 用戶 ID
            **kwargs: 其他資訊
        """
        self.info(
            f"API Request: {method} {endpoint}",
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            **kwargs
        )
    
    def log_api_response(
        self,
        endpoint: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ):
        """
        記錄 API 回應
        
        Args:
            endpoint: API 端點
            status_code: HTTP 狀態碼
            duration_ms: 請求耗時（毫秒）
            **kwargs: 其他資訊
        """
        level = logging.INFO if status_code < 400 else logging.ERROR
        self._log(
            level,
            f"API Response: {endpoint} - {status_code} ({duration_ms:.2f}ms)",
            {
                'endpoint': endpoint,
                'status_code': status_code,
                'duration_ms': duration_ms,
                **kwargs
            }
        )
    
    def log_calculation(
        self,
        calc_type: str,
        user_id: str,
        success: bool,
        duration_ms: Optional[float] = None
    ):
        """
        記錄命理計算
        
        Args:
            calc_type: 計算類型（bazi, astrology 等）
            user_id: 用戶 ID
            success: 是否成功
            duration_ms: 計算耗時
        """
        message = f"Calculation {calc_type}: {'Success' if success else 'Failed'}"
        if duration_ms:
            message += f" ({duration_ms:.2f}ms)"
        
        level = logging.INFO if success else logging.ERROR
        self._log(level, message, {
            'calc_type': calc_type,
            'user_id': user_id,
            'success': success,
            'duration_ms': duration_ms
        })


# 全域 Logger 實例
_logger_instance: Optional[AetheriaLogger] = None


def get_logger() -> AetheriaLogger:
    """取得全域 Logger 實例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AetheriaLogger()
    return _logger_instance


def setup_logger(
    log_level: str = 'INFO',
    json_format: bool = False
) -> AetheriaLogger:
    """
    設置全域 Logger
    
    Args:
        log_level: 日誌級別
        json_format: 是否使用 JSON 格式
        
    Returns:
        Logger 實例
    """
    global _logger_instance
    _logger_instance = AetheriaLogger(
        log_level=log_level,
        json_format=json_format
    )
    return _logger_instance
