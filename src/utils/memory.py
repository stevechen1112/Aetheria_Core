"""
Aetheria 三層記憶管理模組
實作 Agent-first 架構所需的記憶系統
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from src.utils.database import AetheriaDatabase
from src.utils.logger import get_logger

logger = get_logger()


class MemoryManager:
    """三層記憶管理器
    
    Layer 1: 短期工作記憶 (Short-term Buffer) - 滑動視窗，保留最近對話
    Layer 2: 摘要記憶 (Episodic Memory) - 重要事件與結論的摘要
    Layer 3: 核心知識庫 (Semantic Memory) - 使用者不變屬性與深層畫像
    """
    
    def __init__(self, db: AetheriaDatabase, window_size: int = 20):
        """
        Args:
            db: 資料庫實例
            window_size: 短期記憶視窗大小（對話輪數）
        """
        self.db = db
        self.window_size = window_size
    
    # ==================== Layer 1: 短期工作記憶 ====================
    
    def add_conversation_turn(
        self, 
        user_id: str, 
        session_id: str, 
        role: str, 
        content: str,
        token_count: Optional[int] = None
    ) -> int:
        """新增對話輪次到短期記憶
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            role: 'user' | 'assistant' | 'system_event'
            content: 對話內容或事件描述
            token_count: Token 數量（用於控制視窗大小）
        
        Returns:
            記憶 ID
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_memory 
                (user_id, session_id, role, content, timestamp, token_count, is_archived)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (
                user_id,
                session_id,
                role,
                content,
                datetime.now().isoformat(),
                token_count
            ))
            memory_id = cursor.lastrowid
            
        logger.info(f"[Memory Layer 1] 新增對話記憶: user={user_id}, role={role}, id={memory_id}")
        return memory_id
    
    def get_recent_conversation(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """取得最近對話（短期記憶視窗）
        
        Args:
            session_id: 對話 session ID
            limit: 取得數量（預設使用 window_size）
        
        Returns:
            對話列表，按時間升序
        """
        limit = limit or self.window_size
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, user_id, session_id, role, content, summary, 
                       timestamp, token_count, is_archived
                FROM conversation_memory
                WHERE session_id = ? AND is_archived = 0
                ORDER BY id DESC
                LIMIT ?
            """, (session_id, limit))
            
            rows = cursor.fetchall()
            
        # 反轉為升序（時間由舊到新）
        memories = []
        for row in reversed(rows):
            memories.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'session_id': row['session_id'],
                'role': row['role'],
                'content': row['content'],
                'summary': row['summary'],
                'timestamp': row['timestamp'],
                'token_count': row['token_count'],
                'is_archived': bool(row['is_archived'])
            })
        
        return memories
    
    def inject_system_event(
        self, 
        user_id: str, 
        session_id: str, 
        event_type: str,
        event_data: Dict[str, Any]
    ) -> int:
        """注入系統事件（如：排盤完成、報告生成）
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            event_type: 事件類型（如 'chart.completed', 'task.progress'）
            event_data: 事件資料
        
        Returns:
            事件記憶 ID
        """
        event_content = json.dumps({
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat()
        }, ensure_ascii=False)
        
        memory_id = self.add_conversation_turn(
            user_id=user_id,
            session_id=session_id,
            role='system_event',
            content=event_content
        )
        
        logger.info(f"[Memory Layer 1] 注入系統事件: {event_type}, id={memory_id}")
        return memory_id
    
    # ==================== Layer 2: 摘要記憶 ====================
    
    def create_episodic_summary(
        self,
        user_id: str,
        topic: str,
        key_points: str,
        source_session_ids: Optional[List[str]] = None,
        summary_date: Optional[str] = None
    ) -> int:
        """建立摘要記憶
        
        Args:
            user_id: 使用者 ID
            topic: 主題分類（如 'career', 'relationship', 'health', 'general'）
            key_points: AI 生成的重點摘要
            source_session_ids: 來源對話 session 列表
            summary_date: 摘要日期（預設今天）
        
        Returns:
            摘要 ID
        """
        summary_date = summary_date or datetime.now().strftime('%Y-%m-%d')
        source_json = json.dumps(source_session_ids or [], ensure_ascii=False)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO episodic_summary 
                (user_id, summary_date, topic, key_points, source_session_ids, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                summary_date,
                topic,
                key_points,
                source_json,
                datetime.now().isoformat()
            ))
            summary_id = cursor.lastrowid
        
        logger.info(f"[Memory Layer 2] 建立摘要記憶: user={user_id}, topic={topic}, id={summary_id}")
        return summary_id
    
    def get_episodic_summaries(
        self,
        user_id: str,
        topic: Optional[str] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """取得摘要記憶
        
        Args:
            user_id: 使用者 ID
            topic: 主題過濾（可選）
            days: 取得幾天內的摘要
            limit: 最大數量
        
        Returns:
            摘要列表
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if topic:
                cursor.execute("""
                    SELECT id, user_id, summary_date, topic, key_points, 
                           source_session_ids, created_at
                    FROM episodic_summary
                    WHERE user_id = ? AND topic = ? AND summary_date >= ?
                    ORDER BY summary_date DESC, id DESC
                    LIMIT ?
                """, (user_id, topic, cutoff_date, limit))
            else:
                cursor.execute("""
                    SELECT id, user_id, summary_date, topic, key_points, 
                           source_session_ids, created_at
                    FROM episodic_summary
                    WHERE user_id = ? AND summary_date >= ?
                    ORDER BY summary_date DESC, id DESC
                    LIMIT ?
                """, (user_id, cutoff_date, limit))
            
            rows = cursor.fetchall()
        
        summaries = []
        for row in rows:
            try:
                source_sessions = json.loads(row['source_session_ids']) if row['source_session_ids'] else []
            except Exception as e:
                logger.warning(f"[Memory Layer 2] source_session_ids 解析失敗: {e}")
                source_sessions = []
            
            summaries.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'summary_date': row['summary_date'],
                'topic': row['topic'],
                'key_points': row['key_points'],
                'source_session_ids': source_sessions,
                'created_at': row['created_at']
            })
        
        return summaries
    
    # ==================== Layer 3: 核心知識庫 ====================
    
    def upsert_user_persona(
        self,
        user_id: str,
        birth_info: Optional[Dict[str, Any]] = None,
        chart_data: Optional[Dict[str, Any]] = None,
        personality_tags: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """更新或建立使用者畫像（核心知識庫）
        
        Args:
            user_id: 使用者 ID
            birth_info: 生辰資料
            chart_data: 命盤資料
            personality_tags: 人格特質標籤
            preferences: 使用者偏好
        
        Returns:
            是否成功
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 先查詢是否已存在
            cursor.execute("SELECT user_id FROM user_persona WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone() is not None
            
            birth_json = json.dumps(birth_info, ensure_ascii=False) if birth_info else None
            chart_json = json.dumps(chart_data, ensure_ascii=False) if chart_data else None
            tags_json = json.dumps(personality_tags, ensure_ascii=False) if personality_tags else None
            pref_json = json.dumps(preferences, ensure_ascii=False) if preferences else None
            
            if exists:
                # 更新：只更新非 None 的欄位
                updates = []
                params = []
                if birth_info is not None:
                    updates.append("birth_info = ?")
                    params.append(birth_json)
                if chart_data is not None:
                    updates.append("chart_data = ?")
                    params.append(chart_json)
                if personality_tags is not None:
                    updates.append("personality_tags = ?")
                    params.append(tags_json)
                if preferences is not None:
                    updates.append("preferences = ?")
                    params.append(pref_json)
                
                if updates:
                    updates.append("updated_at = ?")
                    params.append(datetime.now().isoformat())
                    params.append(user_id)
                    
                    query = f"UPDATE user_persona SET {', '.join(updates)} WHERE user_id = ?"
                    cursor.execute(query, params)
                    
                logger.info(f"[Memory Layer 3] 更新使用者畫像: user={user_id}")
            else:
                # 新增
                cursor.execute("""
                    INSERT INTO user_persona 
                    (user_id, birth_info, chart_data, personality_tags, preferences, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    birth_json,
                    chart_json,
                    tags_json,
                    pref_json,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                logger.info(f"[Memory Layer 3] 建立使用者畫像: user={user_id}")
        
        return True
    
    def get_user_persona(self, user_id: str) -> Optional[Dict[str, Any]]:
        """取得使用者畫像（核心知識庫）
        
        Args:
            user_id: 使用者 ID
        
        Returns:
            畫像資料，若不存在則回傳 None
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, birth_info, chart_data, personality_tags, 
                       preferences, created_at, updated_at
                FROM user_persona
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
        
        if not row:
            return None
        
        def safe_json_load(text: Optional[str]) -> Any:
            if not text:
                return None
            try:
                return json.loads(text)
            except Exception as e:
                logger.warning(f"[Memory Layer 3] JSON 解析失敗: {e}")
                return None
        
        return {
            'user_id': row['user_id'],
            'birth_info': safe_json_load(row['birth_info']),
            'chart_data': safe_json_load(row['chart_data']),
            'personality_tags': safe_json_load(row['personality_tags']) or [],
            'preferences': safe_json_load(row['preferences']) or {},
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    # ==================== 輔助方法 ====================
    
    def build_context_for_ai(
        self,
        user_id: str,
        session_id: str,
        include_episodic: bool = True,
        include_persona: bool = True
    ) -> Dict[str, Any]:
        """為 AI 對話建構完整的記憶上下文
        
        Args:
            user_id: 使用者 ID
            session_id: 對話 session ID
            include_episodic: 是否包含摘要記憶
            include_persona: 是否包含使用者畫像
        
        Returns:
            包含三層記憶的上下文字典
        """
        context = {
            'short_term': [],
            'episodic': [],
            'persona': None
        }
        
        # Layer 1: 短期記憶
        context['short_term'] = self.get_recent_conversation(session_id)
        
        # Layer 2: 摘要記憶
        if include_episodic:
            context['episodic'] = self.get_episodic_summaries(user_id, days=30, limit=5)
        
        # Layer 3: 核心知識庫
        if include_persona:
            context['persona'] = self.get_user_persona(user_id)
        
        return context
    
    def archive_old_conversations(
        self,
        session_id: str,
        keep_recent: int = 50
    ) -> int:
        """封存舊對話（超出視窗的對話標記為已封存）
        
        Args:
            session_id: 對話 session ID
            keep_recent: 保留最近幾筆
        
        Returns:
            封存數量
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 找出要封存的 ID
            cursor.execute("""
                SELECT id FROM conversation_memory
                WHERE session_id = ? AND is_archived = 0
                ORDER BY id DESC
                LIMIT -1 OFFSET ?
            """, (session_id, keep_recent))
            
            rows = cursor.fetchall()
            ids_to_archive = [row['id'] for row in rows]
            
            if not ids_to_archive:
                return 0
            
            # 批次更新
            placeholders = ','.join('?' * len(ids_to_archive))
            cursor.execute(f"""
                UPDATE conversation_memory
                SET is_archived = 1
                WHERE id IN ({placeholders})
            """, ids_to_archive)
            
            archived_count = cursor.rowcount
        
        logger.info(f"[Memory] 封存 {archived_count} 筆舊對話: session={session_id}")
        return archived_count


# 全域實例（可選）
_memory_manager_instance: Optional[MemoryManager] = None


def get_memory_manager(db: AetheriaDatabase) -> MemoryManager:
    """取得 MemoryManager 實例"""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager(db)
    return _memory_manager_instance
