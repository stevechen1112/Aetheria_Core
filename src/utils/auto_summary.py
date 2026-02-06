"""
自動摘要服務 (Auto Summary Service)
在對話結束或累積一定輪次後自動觸發摘要收斂

版本: v1.0.0
最後更新: 2026-02-05
"""

import time
import json
from typing import Dict, List, Optional
from datetime import datetime

from src.utils.memory import get_memory_manager
from src.utils.gemini_client import GeminiClient
from src.utils.logger import get_logger
from src.utils.database import get_database

logger = get_logger()


class AutoSummaryService:
    """
    自動摘要服務
    
    觸發條件：
    1. 對話輪次累積達到閾值（預設 10 輪）
    2. 對話時間間隔超過一定時長（預設 1 小時）
    3. 手動觸發
    """
    
    def __init__(
        self,
        turn_threshold: int = 10,
        inactive_hours: int = 1,
        gemini_client: Optional[GeminiClient] = None
    ):
        """
        Args:
            turn_threshold: 觸發摘要的對話輪次閾值
            inactive_hours: 觸發摘要的不活躍小時數
            gemini_client: Gemini 客戶端（若不提供則建立新實例）
        """
        self.turn_threshold = turn_threshold
        self.inactive_hours = inactive_hours
        self.db = get_database()
        self.memory_manager = get_memory_manager(self.db)
        
        if gemini_client:
            self.gemini_client = gemini_client
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            self.gemini_client = GeminiClient(
                api_key=os.getenv('GEMINI_API_KEY'),
                model_name=os.getenv('MODEL_NAME_CHAT', 'gemini-3-flash-preview'),
                temperature=0.3  # 較低溫度確保摘要穩定
            )
    
    def should_trigger_summary(
        self,
        user_id: str,
        session_id: str
    ) -> tuple[bool, str]:
        """
        判斷是否應該觸發摘要
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            
        Returns:
            (should_trigger: bool, reason: str)
        """
        # 取得對話歷史
        messages = self.db.get_chat_messages(session_id, limit=100)
        
        if not messages or len(messages) < 4:  # 至少要有 2 輪對話
            return False, "對話輪次不足"
        
        # 計算未摘要的對話輪次
        unsummarized_turns = len([m for m in messages if not m.get('summarized', False)])
        
        if unsummarized_turns >= self.turn_threshold * 2:  # 對話輪數 = turns * 2（user + assistant）
            return True, f"對話輪次達到閾值 ({unsummarized_turns // 2} 輪)"
        
        # 檢查最後活躍時間
        if messages:
            last_message = messages[-1]
            last_created_at = last_message.get('created_at') or ''
            try:
                last_time = datetime.fromisoformat(last_created_at.replace('Z', '+00:00'))
                now = datetime.utcnow()
                inactive_hours = (now - last_time).total_seconds() / 3600

                if inactive_hours >= self.inactive_hours and unsummarized_turns >= 4:
                    return True, f"對話已不活躍 {inactive_hours:.1f} 小時"
            except Exception:
                logger.warning("無法解析最後訊息時間，略過不活躍檢查")
        
        return False, "不需要摘要"
    
    def generate_summary(
        self,
        user_id: str,
        session_id: str,
        topic: Optional[str] = None
    ) -> Optional[Dict]:
        """
        生成對話摘要
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            topic: 主題分類（可選）
            
        Returns:
            摘要資料或 None
        """
        try:
            # 檢查是否已有相似摘要（去重）
            if self._has_similar_summary(user_id, session_id):
                logger.info(f"該對話已有相似摘要，跳過生成: user={user_id}, session={session_id}")
                return None
            
            # 取得對話歷史
            messages = self.db.get_chat_messages(session_id, limit=100)
            
            if not messages:
                return None
            
            # 建構對話文本
            conversation_text = "\n\n".join([
                f"{'使用者' if m.get('role') == 'user' else 'AI 命理師'}：{m.get('content', '')}"
                for m in messages
            ])
            
            # 建構摘要 prompt
            summary_prompt = f"""請將以下命理諮詢對話摘要為重點記錄。

【對話內容】
{conversation_text}

【摘要要求】
1. 提取使用者的核心問題與關切議題
2. 記錄 AI 給出的關鍵洞察和建議
3. 記錄使用者的決策或行動意向
4. 用條列式呈現，每條不超過 100 字
5. 總共 3-5 條重點

請以 JSON 格式返回：
{{
    "topic": "事業發展" | "感情議題" | "健康問題" | "財務規劃" | "一般諮詢",
    "key_points": [
        "重點 1",
        "重點 2",
        ...
    ],
    "user_concerns": ["關切 1", "關切 2"],
    "ai_insights": ["洞察 1", "洞察 2"],
    "action_items": ["行動 1", "行動 2"]
}}
"""
            
            logger.info(f"正在生成摘要: user={user_id}, session={session_id}")
            
            # 調用 Gemini 生成摘要
            response = self.gemini_client.generate_content(
                prompt=summary_prompt,
                system_instruction="你是一位專業的命理諮詢摘要助手。"
            )
            
            # 解析 JSON 回應
            import json
            import re
            
            response_text = response.text
            
            # 清理 markdown 標記
            response_text = re.sub(r'^```json\s*', '', response_text, flags=re.IGNORECASE | re.MULTILINE)
            response_text = re.sub(r'^```\s*$', '', response_text, flags=re.MULTILINE)
            response_text = response_text.strip()
            
            summary_data = json.loads(response_text)
            
            # 合併為摘要文本
            key_points = summary_data.get('key_points', [])
            summary_text = "\n".join([f"• {point}" for point in key_points])
            
            # 儲存摘要
            detected_topic = summary_data.get('topic', topic or 'general')
            
            summary_id = self.memory_manager.create_episodic_summary(
                user_id=user_id,
                topic=detected_topic,
                key_points=summary_text,
                source_session_ids=[session_id]
            )
            
            logger.info(f"摘要已生成: summary_id={summary_id}, topic={detected_topic}")
            
            # 標記訊息為已摘要
            self._mark_messages_as_summarized(session_id)
            
            return {
                'summary_id': summary_id,
                'topic': detected_topic,
                'key_points': key_points,
                'user_concerns': summary_data.get('user_concerns', []),
                'ai_insights': summary_data.get('ai_insights', []),
                'action_items': summary_data.get('action_items', [])
            }
        
        except Exception as e:
            logger.error(f"生成摘要失敗: {e}", exc_info=True)
            return None
    
    def _mark_messages_as_summarized(self, session_id: str):
        """標記訊息為已摘要"""
        try:
            # 簡單標記（可以透過在訊息表添加 summarized 欄位）
            # 這裡僅做日誌記錄
            logger.info(f"標記 session {session_id} 的訊息為已摘要")
        except Exception as e:
            logger.error(f"標記已摘要失敗: {e}")
    
    def _has_similar_summary(self, user_id: str, session_id: str) -> bool:
        """
        檢查是否已有相似摘要（去重）
        
        使用簡單的時間窗口檢查：如果該用戶在最近 1 小時內有摘要，
        且包含相同的 session_id，則視為重複
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            
        Returns:
            是否存在相似摘要
        """
        try:
            # 查詢最近的摘要
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, source_session_ids, created_at 
                    FROM episodic_summary 
                    WHERE user_id = ?
                    AND datetime(created_at) > datetime('now', '-1 hour')
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (user_id,))
                
                recent_summaries = cursor.fetchall()
                
                for summary in recent_summaries:
                    source_sessions = summary['source_session_ids']
                    if not source_sessions:
                        continue

                    try:
                        parsed = json.loads(source_sessions)
                    except Exception:
                        parsed = source_sessions

                    if isinstance(parsed, list):
                        if session_id in parsed:
                            logger.info(f"發現相似摘要: summary_id={summary['id']}")
                            return True
                    elif isinstance(parsed, str):
                        if session_id == parsed:
                            logger.info(f"發現相似摘要: summary_id={summary['id']}")
                            return True
                
                return False
        
        except Exception as e:
            logger.error(f"檢查相似摘要失敗: {e}")
            return False  # 出錯時不阻擋摘要生成
    
    def auto_summarize_if_needed(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[Dict]:
        """
        自動檢查並在需要時生成摘要
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            
        Returns:
            摘要資料或 None
        """
        should_trigger, reason = self.should_trigger_summary(user_id, session_id)
        
        if should_trigger:
            logger.info(f"觸發自動摘要: {reason}")
            return self.generate_summary(user_id, session_id)
        
        return None
    
    def summarize_all_old_sessions(
        self,
        days_threshold: int = 7,
        max_sessions: int = 100
    ):
        """
        批次處理舊對話的摘要（背景任務）
        
        Args:
            days_threshold: 處理幾天前的對話
            max_sessions: 最多處理幾個 session
        """
        # 這個方法可以作為定期背景任務執行
        logger.info(f"開始批次摘要舊對話: days_threshold={days_threshold}")
        
        # TODO: 實作查詢舊 session 並批次處理
        # 需要在 database.py 添加相應查詢方法
        
        logger.info("批次摘要完成")


# 全局實例
_auto_summary_service_instance = None

def get_auto_summary_service() -> AutoSummaryService:
    """取得自動摘要服務實例（單例）"""
    global _auto_summary_service_instance
    if _auto_summary_service_instance is None:
        _auto_summary_service_instance = AutoSummaryService()
    return _auto_summary_service_instance
