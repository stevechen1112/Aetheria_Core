"""
Gemini API 客戶端包裝器
遷移到新的 google.genai SDK
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types

logger = logging.getLogger('aetheria')


class GeminiClient:
    """Gemini API 統一客戶端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-3-flash-preview",
        temperature: float = 0.4,
        max_output_tokens: int = 8192
    ):
        """
        初始化 Gemini 客戶端
        
        Args:
            api_key: Gemini API Key（若為 None 則從環境變數讀取）
            model_name: 模型名稱
            temperature: 生成溫度（0-1）
            max_output_tokens: 最大輸出 Token 數
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("未提供 GEMINI_API_KEY")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        self.default_config = {
            'temperature': temperature,
            'max_output_tokens': max_output_tokens,
        }
        # 429 retry 設定
        self.max_retries = 3
        self.base_delay = 5  # 秒

    def _is_rate_limit_error(self, e: Exception) -> bool:
        """判斷是否為 429 rate limit 錯誤"""
        err_str = str(e)
        return '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str

    def _retry_delay(self, attempt: int) -> float:
        """指數退避延遲：5s, 10s, 20s"""
        return self.base_delay * (2 ** attempt)
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        model_name: Optional[str] = None,
        response_mime_type: Optional[str] = None,
        tools: Optional[list] = None
    ) -> Any:
        """
        生成內容（支援 Function Calling）
        
        Args:
            prompt: 提示詞
            temperature: 覆蓋預設溫度
            max_output_tokens: 覆蓋預設最大 Token 數
            model_name: 覆蓋預設模型
            response_mime_type: 響應格式 (例如 'application/json')
            tools: Function Calling 工具定義列表
            
        Returns:
            若有 tools，返回完整 response 對象；否則返回文字內容
            
        Raises:
            Exception: API 呼叫失敗
        """
        tools_config = None
        if tools:
            function_declarations = []
            for tool in tools:
                if isinstance(tool, dict):
                    function_declarations.append(
                        types.FunctionDeclaration(
                            name=tool.get("name"),
                            description=tool.get("description"),
                            parameters=tool.get("parameters")
                        )
                    )
                else:
                    function_declarations.append(tool)
            tools_config = [types.Tool(function_declarations=function_declarations)]

        config = types.GenerateContentConfig(
            temperature=temperature or self.default_config['temperature'],
            max_output_tokens=max_output_tokens or self.default_config['max_output_tokens'],
            response_mime_type=None if tools else response_mime_type,
            tools=tools_config
        )
        
        try:
            last_err = None
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.client.models.generate_content(
                        model=model_name or self.model_name,
                        contents=prompt,
                        config=config
                    )
                    break  # 成功，跳出 retry
                except Exception as inner_e:
                    last_err = inner_e
                    if self._is_rate_limit_error(inner_e) and attempt < self.max_retries:
                        delay = self._retry_delay(attempt)
                        logger.warning(f"[Gemini] 429 rate limit，{delay}s 後重試 ({attempt+1}/{self.max_retries})")
                        time.sleep(delay)
                    else:
                        raise
            else:
                raise last_err

            
            # 若指定了 tools，返回完整 response 供後續處理
            if tools:
                return response
            
            # 檢查回應是否有效
            if response is None:
                raise Exception("API 返回空回應")
            if not hasattr(response, 'text') or response.text is None:
                # 嘗試從候選項中獲取
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        parts = candidate.content.parts
                        if parts:
                            return parts[0].text
                raise Exception("API 回應沒有有效內容")
            
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API 呼叫失敗: {str(e)}")
    
    def _build_tools_config(self, tools: Optional[list]):
        """共用：將工具定義清單轉成 Gemini SDK 格式"""
        if not tools:
            return None
        function_declarations = []
        for tool in tools:
            if isinstance(tool, dict):
                function_declarations.append(
                    types.FunctionDeclaration(
                        name=tool.get("name"),
                        description=tool.get("description"),
                        parameters=tool.get("parameters")
                    )
                )
            else:
                function_declarations.append(tool)
        return [types.Tool(function_declarations=function_declarations)]

    def generate_content_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        model_name: Optional[str] = None,
        tools: Optional[list] = None
    ):
        """
        生成內容（Streaming 模式，支援 Function Calling）
        
        Args:
            prompt: 提示詞（字串或 contents 列表）
            system_instruction: 系統指令
            temperature: 覆蓋預設溫度
            max_output_tokens: 覆蓋預設最大 Token 數
            model_name: 覆蓋預設模型
            tools: Function Calling 工具定義列表
            
        Yields:
            串流的 response chunks
            
        Raises:
            Exception: API 呼叫失敗
        """
        tools_config = self._build_tools_config(tools)
        
        config = types.GenerateContentConfig(
            temperature=temperature or self.default_config['temperature'],
            max_output_tokens=max_output_tokens or self.default_config['max_output_tokens'],
            system_instruction=system_instruction,
            tools=tools_config
        )
        
        try:
            last_err = None
            for attempt in range(self.max_retries + 1):
                try:
                    response_stream = self.client.models.generate_content_stream(
                        model=model_name or self.model_name,
                        contents=prompt,
                        config=config
                    )
                    
                    for chunk in response_stream:
                        yield chunk
                    return  # 成功完成，直接結束
                except Exception as inner_e:
                    last_err = inner_e
                    if self._is_rate_limit_error(inner_e) and attempt < self.max_retries:
                        delay = self._retry_delay(attempt)
                        logger.warning(f"[Gemini] Streaming 429 rate limit，{delay}s 後重試 ({attempt+1}/{self.max_retries})")
                        time.sleep(delay)
                    else:
                        raise
            if last_err:
                raise last_err
                
        except Exception as e:
            raise Exception(f"Gemini API Streaming 失敗: {str(e)}")

    def generate_non_stream_with_contents(
        self,
        contents,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        model_name: Optional[str] = None,
        tools: Optional[list] = None
    ):
        """
        非串流生成（接受 contents 列表，支援 multi-turn Function Calling）
        
        用於 Tool Use 迴圈：每次迭代收集完整 response 再決定是否繼續。
        
        Args:
            contents: Gemini Contents 列表（支援 user / model / tool role）
            system_instruction: 系統指令
            tools: Function Calling 工具定義列表
            
        Returns:
            完整 response 對象
        """
        tools_config = self._build_tools_config(tools)
        
        config = types.GenerateContentConfig(
            temperature=temperature or self.default_config['temperature'],
            max_output_tokens=max_output_tokens or self.default_config['max_output_tokens'],
            system_instruction=system_instruction,
            tools=tools_config
        )
        
        try:
            last_err = None
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.client.models.generate_content(
                        model=model_name or self.model_name,
                        contents=contents,
                        config=config
                    )
                    return response
                except Exception as inner_e:
                    last_err = inner_e
                    if self._is_rate_limit_error(inner_e) and attempt < self.max_retries:
                        delay = self._retry_delay(attempt)
                        logger.warning(f"[Gemini] Multi-turn 429 rate limit，{delay}s 後重試 ({attempt+1}/{self.max_retries})")
                        time.sleep(delay)
                    else:
                        raise
            raise last_err
        except Exception as e:
            raise Exception(f"Gemini API (multi-turn) 失敗: {str(e)}")
    
    def generate_with_config(
        self,
        prompt: str,
        config: Dict[str, Any]
    ) -> str:
        """
        使用自訂配置生成內容
        
        Args:
            prompt: 提示詞
            config: 完整的生成配置
            
        Returns:
            生成的文字內容
        """
        return self.generate(
            prompt=prompt,
            temperature=config.get('temperature'),
            max_output_tokens=config.get('max_output_tokens'),
            model_name=config.get('model_name')
        )


# 全域客戶端實例（向後相容）
_global_client: Optional[GeminiClient] = None


def get_global_client() -> GeminiClient:
    """取得全域 Gemini 客戶端實例"""
    global _global_client
    if _global_client is None:
        _global_client = GeminiClient()
    return _global_client


def configure(api_key: str):
    """配置全域客戶端（向後相容）"""
    global _global_client
    _global_client = GeminiClient(api_key=api_key)
