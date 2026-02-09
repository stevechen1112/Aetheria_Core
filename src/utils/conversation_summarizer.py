"""
對話摘要生成模組
實現自動摘要與記憶壓縮功能
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from src.utils.memory import MemoryManager
from src.utils.gemini_client import GeminiClient
from src.utils.logger import get_logger
import json
import os

logger = get_logger()

# 初始化 Gemini 客戶端
_gemini_client = None

def _get_gemini_client() -> GeminiClient:
    """取得 Gemini 客戶端實例"""
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv('GEMINI_API_KEY')
        _gemini_client = GeminiClient(
            api_key=api_key,
            model_name=os.getenv('MODEL_NAME_CHAT', 'gemini-3-flash-preview'),
            temperature=0.4
        )
    return _gemini_client


class ConversationSummarizer:
    """對話摘要生成器"""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Args:
            memory_manager: 記憶管理器實例
        """
        self.memory = memory_manager
    
    def should_generate_summary(
        self,
        user_id: str,
        session_id: str,
        force: bool = False
    ) -> bool:
        """
        判斷是否應該生成摘要
        
        觸發條件：
        1. 對話輪數 >= 10
        2. Token 數量 >= 3000
        3. 手動觸發（force=True）
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            force: 是否強制生成
        
        Returns:
            是否應該生成摘要
        """
        if force:
            return True
        
        # 取得對話歷史
        conversation = self.memory.get_recent_conversation(session_id, limit=100)
        
        if not conversation:
            return False
        
        # 檢查輪數
        if len(conversation) >= 10:
            return True
        
        # 檢查 Token 數量（以字元數粗估，中文 ~1.5 token/char）
        total_chars = sum(len(msg.get('content', '')) for msg in conversation)
        estimated_tokens = int(total_chars * 1.5)
        if estimated_tokens >= 3000:
            return True
        
        return False
    
    def generate_summary(
        self,
        user_id: str,
        session_id: str,
        conversation: Optional[List[Dict]] = None
    ) -> Optional[Dict]:
        """
        生成對話摘要
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            conversation: 對話歷史（可選，不提供則自動獲取）
        
        Returns:
            摘要字典 {topic, key_points, insights} 或 None（失敗時）
        """
        # 獲取對話歷史
        if conversation is None:
            conversation = self.memory.get_recent_conversation(session_id, limit=50)
        
        if not conversation or len(conversation) < 3:
            logger.warning(f"對話太短，無需摘要: user={user_id}, session={session_id}")
            return None
        
        # 構建對話文本
        conversation_text = self._format_conversation_for_summary(conversation)
        
        # 使用 AI 生成摘要
        summary_prompt = self._build_summary_prompt(conversation_text)
        system_instruction = self._get_summary_system_instruction()
        
        try:
            gemini = _get_gemini_client()
            raw_response = gemini.generate(
                prompt=summary_prompt,
                system_instruction=system_instruction,
                response_mime_type='application/json'
            )
            
            # 解析 JSON
            summary_data = json.loads(raw_response)
            
            logger.info(f"成功生成對話摘要: user={user_id}, session={session_id}")
            return summary_data
        
        except Exception as e:
            logger.error(f"摘要生成失敗: {e}", exc_info=True)
            return None
    
    def save_summary_to_memory(
        self,
        user_id: str,
        session_id: str,
        summary: Dict
    ) -> int:
        """
        儲存摘要到 Layer 2 記憶
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            summary: 摘要字典
        
        Returns:
            摘要 ID
        """
        topic = summary.get('topic', 'general')
        key_points = summary.get('key_points', '')
        
        # 加入洞察（insights）到重點中
        if insights := summary.get('insights'):
            if isinstance(insights, list):
                insight_text = ' | '.join(insights)
                key_points += f"\n【洞察】{insight_text}"
        
        summary_id = self.memory.create_episodic_summary(
            user_id=user_id,
            topic=topic,
            key_points=key_points,
            source_session_ids=[session_id]
        )
        
        logger.info(f"摘要已存入 Layer 2: id={summary_id}, user={user_id}")
        return summary_id
    
    def extract_personality_tags(
        self,
        user_id: str,
        conversation: List[Dict]
    ) -> List[str]:
        """
        從對話中提取用戶人格標籤
        
        Args:
            user_id: 使用者 ID
            conversation: 對話歷史
        
        Returns:
            人格標籤列表
        """
        if not conversation or len(conversation) < 5:
            return []
        
        conversation_text = self._format_conversation_for_summary(conversation)
        
        extract_prompt = (
            "請分析以下對話，提取使用者的人格特質標籤。\n\n"
            "標籤範例：直率、重視事業、感情敏感、理性分析、追求穩定、樂觀、謹慎、重視家庭\n\n"
            f"對話內容：\n{conversation_text}\n\n"
            "請以 JSON 格式回覆：{\"tags\": [\"標籤1\", \"標籤2\", ...]}\n"
            "最多 5 個標籤，每個標籤 2-4 個字。"
        )
        
        try:
            gemini = _get_gemini_client()
            raw_response = gemini.generate(
                prompt=extract_prompt,
                system_instruction="你是一位心理分析專家，擅長從對話中觀察人格特質。",
                response_mime_type='application/json'
            )
            
            data = json.loads(raw_response)
            tags = data.get('tags', [])
            
            # 去重並限制數量
            unique_tags = list(dict.fromkeys(tags))[:5]
            
            if unique_tags:
                # 更新到 Layer 3 記憶
                self.memory.upsert_user_persona(
                    user_id=user_id,
                    personality_tags=unique_tags
                )
                logger.info(f"提取人格標籤: user={user_id}, tags={unique_tags}")
            
            return unique_tags
        
        except Exception as e:
            logger.error(f"人格標籤提取失敗: {e}")
            return []
    
    def compress_and_archive(
        self,
        user_id: str,
        session_id: str
    ) -> Tuple[bool, Optional[int]]:
        """
        壓縮並封存對話
        
        流程：
        1. 生成摘要 → 存入 Layer 2
        2. 提取人格標籤 → 更新 Layer 3
        3. 封存舊對話 → Layer 1 清理
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
        
        Returns:
            (是否成功, 摘要 ID)
        """
        try:
            # 1. 獲取對話
            conversation = self.memory.get_recent_conversation(session_id, limit=50)
            
            if not conversation:
                return False, None
            
            # 2. 生成摘要
            summary = self.generate_summary(user_id, session_id, conversation)
            
            if not summary:
                logger.warning(f"摘要生成失敗，跳過壓縮: user={user_id}")
                return False, None
            
            # 3. 儲存摘要
            summary_id = self.save_summary_to_memory(user_id, session_id, summary)
            
            # 4. 提取人格標籤（背景任務）
            try:
                self.extract_personality_tags(user_id, conversation)
            except Exception as e:
                logger.warning(f"人格標籤提取失敗（非致命）: {e}")
            
            # 5. 封存舊對話
            archived_count = self.memory.archive_old_conversations(session_id, keep_recent=20)
            
            logger.info(
                f"對話壓縮完成: user={user_id}, summary_id={summary_id}, "
                f"archived={archived_count}"
            )
            
            return True, summary_id
        
        except Exception as e:
            logger.error(f"對話壓縮失敗: {e}", exc_info=True)
            return False, None
    
    # ==================== 輔助方法 ====================
    
    def _format_conversation_for_summary(self, conversation: List[Dict]) -> str:
        """格式化對話為摘要用文本"""
        lines = []
        for msg in conversation:
            role = msg.get('role')
            content = msg.get('content', '').strip()
            
            if not content:
                continue
            
            if role == 'user':
                lines.append(f"使用者：{content}")
            elif role == 'assistant':
                lines.append(f"命理師：{content}")
            elif role == 'system_event':
                # 系統事件可選擇性包含
                try:
                    evt = json.loads(content)
                    lines.append(f"[系統] {evt.get('type', 'event')}")
                except:
                    pass
        
        return "\n".join(lines)
    
    def _build_summary_prompt(self, conversation_text: str) -> str:
        """構建摘要生成 Prompt"""
        return f"""請為以下對話生成摘要。

對話內容：
{conversation_text}

請以 JSON 格式回覆，包含以下欄位：
{{
  "topic": "主題分類（從以下選擇：career, relationship, health, wealth, general）",
  "key_points": "對話重點摘要（2-3 句話，80-150 字）",
  "insights": ["洞察1", "洞察2"],
  "user_concerns": ["用戶關注的議題1", "議題2"],
  "next_follow_up": "建議下次對話可以追蹤的方向"
}}

摘要原則：
1. key_points 要具體，不要泛泛而談
2. insights 提取深層需求，不只是表面問題
3. 用繁體中文（台灣用語）
4. 簡潔精煉，去除冗余資訊
"""
    
    def _get_summary_system_instruction(self) -> str:
        """取得摘要系統指令"""
        return (
            "你是一位擅長摘要與分析的 AI 助手。\n\n"
            "你的任務是將對話濃縮為精煉的重點摘要，同時提取深層洞察。\n"
            "摘要必須：\n"
            "1. 準確反映對話核心內容\n"
            "2. 區分表面問題與深層需求\n"
            "3. 保留關鍵的情境脈絡\n"
            "4. 便於未來快速回憶與檢索\n\n"
            "避免：\n"
            "- 過於籠統或模糊的描述\n"
            "- 遺漏重要的討論主題\n"
            "- 添加對話中沒有的內容"
        )


# 全域實例
_summarizer_instance: Optional[ConversationSummarizer] = None


def get_conversation_summarizer(memory_manager: MemoryManager) -> ConversationSummarizer:
    """取得 ConversationSummarizer 實例"""
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = ConversationSummarizer(memory_manager)
    return _summarizer_instance
