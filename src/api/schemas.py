"""
API Schema 定義與版本化
支援向後相容與版本追蹤
版本: v1.0.0
最後更新: 2026-02-05
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


# ========== Request Schemas ==========

@dataclass
class ChatConsultRequest:
    """聊天諮詢請求 Schema"""
    schema_version: str = "1.0.0"
    message: str = ""
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """驗證請求"""
        if not self.message or not self.message.strip():
            return False, "message 不能為空"
        if len(self.message) > 2000:
            return False, "message 不能超過 2000 字"
        return True, None


@dataclass
class CalculateChartRequest:
    """計算命盤請求 Schema"""
    schema_version: str = "1.0.0"
    system: str = ""  # 'ziwei', 'bazi', 'astrology', etc.
    birth_date: str = ""
    birth_time: str = ""
    birth_location: Optional[str] = None
    gender: Optional[str] = None
    chinese_name: Optional[str] = None
    timezone: Optional[str] = None
    ruleset: Optional[Dict[str, Any]] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """驗證請求"""
        valid_systems = ['ziwei', 'bazi', 'astrology', 'tarot', 'numerology', 'name']
        if self.system not in valid_systems:
            return False, f"system 必須是以下之一: {', '.join(valid_systems)}"
        if not self.birth_date:
            return False, "birth_date 不能為空"
        if not self.birth_time and self.system in ['ziwei', 'bazi', 'astrology']:
            return False, f"{self.system} 系統需要 birth_time"
        return True, None


# ========== Response Schemas ==========

@dataclass
class ApiResponse:
    """標準 API 回應 Schema"""
    schema_version: str = "1.0.0"
    status: str = "success"  # 'success' | 'error'
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        result = {
            "schema_version": self.schema_version,
            "status": self.status,
            "timestamp": self.timestamp
        }
        if self.data is not None:
            result["data"] = self.data
        if self.error is not None:
            result["error"] = self.error
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result


@dataclass
class ErrorResponse:
    """錯誤回應 Schema"""
    code: str = ""
    message: str = ""
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict:
        result = {
            "code": self.code,
            "message": self.message
        }
        if self.details:
            result["details"] = self.details
        return result


# ========== SSE Event Schemas ==========

@dataclass
class SSEEvent:
    """Server-Sent Events 事件 Schema"""
    event_version: str = "1.0.0"
    event: str = ""  # 'text' | 'tool' | 'widget' | 'system' | 'done' | 'error'
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
    
    def to_sse_format(self) -> str:
        """轉換為 SSE 格式字串"""
        import json
        data_json = json.dumps({
            **self.data,
            "event_version": self.event_version
        }, ensure_ascii=False)
        return f"event: {self.event}\ndata: {data_json}\n\n"


@dataclass
class TextChunkEvent:
    """文字片段事件"""
    chunk: str = ""
    accumulated_length: Optional[int] = None
    
    def to_sse_event(self) -> SSEEvent:
        return SSEEvent(
            event="text",
            data=asdict(self)
        )


@dataclass
class ToolExecutionEvent:
    """工具執行事件"""
    status: str = ""  # 'executing' | 'completed' | 'error'
    name: str = ""
    args: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    
    def to_sse_event(self) -> SSEEvent:
        data = {"status": self.status, "name": self.name}
        if self.args is not None:
            data["args"] = self.args
        if self.result is not None:
            data["result"] = self.result
        if self.error is not None:
            data["error"] = self.error
        if self.execution_time_ms is not None:
            data["execution_time_ms"] = self.execution_time_ms
        
        return SSEEvent(event="tool", data=data)


@dataclass
class WidgetEvent:
    """Widget 注入事件"""
    type: str = ""  # 'chart' | 'insight' | 'system_card' | 'progress'
    widget_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.widget_data is None:
            self.widget_data = {}
    
    def to_sse_event(self) -> SSEEvent:
        return SSEEvent(
            event="widget",
            data={
                "type": self.type,
                **self.widget_data
            }
        )


@dataclass
class SystemEvent:
    """系統事件"""
    type: str = ""  # 'emotion_detected' | 'strategy_change' | 'safety_warning' | 'task_progress'
    payload: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.payload is None:
            self.payload = {}
    
    def to_sse_event(self) -> SSEEvent:
        return SSEEvent(
            event="system",
            data={
                "type": self.type,
                **self.payload
            }
        )


@dataclass
class DoneEvent:
    """完成事件"""
    session_id: str = ""
    total_length: int = 0
    tool_calls: int = 0
    widgets_sent: int = 0
    safety_intervention: bool = False
    
    def to_sse_event(self) -> SSEEvent:
        return SSEEvent(
            event="done",
            data=asdict(self)
        )


# ========== Widget Schemas ==========

@dataclass
class ChartWidgetData:
    """Chart Widget 數據 Schema"""
    system: str = ""  # 'ziwei' | 'bazi' | 'astrology' | etc.
    user_name: Optional[str] = None
    birth_info: Optional[Dict[str, str]] = None
    analysis: Optional[Dict[str, Any]] = None
    chart_data: Optional[Dict[str, Any]] = None
    compact: bool = True
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class InsightWidgetData:
    """Insight Widget 數據 Schema"""
    title: str = ""
    content: str = ""
    icon: str = "💡"
    confidence: float = 0.8
    source_system: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SystemCardWidgetData:
    """System Card Widget 數據 Schema"""
    system_name: str = ""
    summary: str = ""
    details: Optional[str] = None
    icon: str = "🔮"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ProgressWidgetData:
    """Progress Widget 數據 Schema"""
    task_name: str = ""
    progress: float = 0.0  # 0.0 - 1.0
    status: str = "running"  # 'running' | 'completed' | 'error' | 'paused'
    message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ========== Schema Registry ==========

SCHEMA_VERSIONS = {
    "1.0.0": {
        "release_date": "2026-02-05",
        "breaking_changes": [],
        "deprecated_fields": [],
        "new_fields": [
            "schema_version in all requests/responses",
            "event_version in SSE events",
            "intelligence context in system events"
        ]
    }
}


def get_current_schema_version() -> str:
    """取得當前 Schema 版本"""
    return "1.0.0"


def validate_schema_version(version: str) -> bool:
    """驗證 Schema 版本是否支援"""
    return version in SCHEMA_VERSIONS


def get_schema_info(version: str) -> Optional[Dict]:
    """取得 Schema 版本資訊"""
    return SCHEMA_VERSIONS.get(version)
