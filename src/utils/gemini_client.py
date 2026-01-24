"""
Gemini API 客戶端包裝器
遷移到新的 google.genai SDK
"""

import os
from typing import Optional, Dict, Any
from google import genai
from google.genai import types


class GeminiClient:
    """Gemini API 統一客戶端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-exp",
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
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        model_name: Optional[str] = None
    ) -> str:
        """
        生成內容
        
        Args:
            prompt: 提示詞
            temperature: 覆蓋預設溫度
            max_output_tokens: 覆蓋預設最大 Token 數
            model_name: 覆蓋預設模型
            
        Returns:
            生成的文字內容
            
        Raises:
            Exception: API 呼叫失敗
        """
        config = types.GenerateContentConfig(
            temperature=temperature or self.default_config['temperature'],
            max_output_tokens=max_output_tokens or self.default_config['max_output_tokens'],
        )
        
        try:
            response = self.client.models.generate_content(
                model=model_name or self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API 呼叫失敗: {str(e)}")
    
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
