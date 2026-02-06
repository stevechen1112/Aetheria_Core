"""
SQLite 資料庫模組
替代原有的 JSON 檔案存儲
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager


class AetheriaDatabase:
    """Aetheria 核心資料庫管理"""
    
    def __init__(self, db_path: str = "data/aetheria.db"):
        """
        初始化資料庫
        
        Args:
            db_path: 資料庫檔案路徑
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """取得資料庫連線（Context Manager）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 讓結果可以像字典一樣存取
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化資料庫表格"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 用戶表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    gender TEXT,
                    birth_year INTEGER,
                    birth_month INTEGER,
                    birth_day INTEGER,
                    birth_hour INTEGER,
                    birth_minute INTEGER,
                    birth_location TEXT,
                    longitude REAL,
                    latitude REAL,
                    gregorian_birth_date TEXT,
                    full_name TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 命盤鎖定表（治本：以 user_id + chart_type 為鍵，避免不同命盤互相覆蓋）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chart_locks (
                    user_id TEXT NOT NULL,
                    chart_type TEXT NOT NULL,
                    chart_data TEXT NOT NULL,
                    analysis TEXT,
                    locked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, chart_type),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Schema migration: old versions used user_id as the only primary key.
            self._migrate_chart_locks_schema(cursor)
            
            # 分析歷史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    request_data TEXT,
                    response_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # 使用紀錄表（API 使用追蹤）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    path TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER,
                    duration_ms REAL,
                    ip TEXT,
                    user_agent TEXT,
                    request_data TEXT,
                    response_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 會員資料表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    phone TEXT UNIQUE,
                    display_name TEXT,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 會員偏好表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS member_preferences (
                    user_id TEXT PRIMARY KEY,
                    tone TEXT,
                    response_length TEXT,
                    focus_topics TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES members(user_id)
                )
            """)

            # 會員同意紀錄表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS member_consents (
                    user_id TEXT PRIMARY KEY,
                    terms_accepted INTEGER DEFAULT 0,
                    data_usage_accepted INTEGER DEFAULT 0,
                    marketing_accepted INTEGER DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES members(user_id)
                )
            """)

            # 會員登入 Session
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS member_sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES members(user_id)
                )
            """)
            
            # 預計算報告表（新增：儲存各系統的完整分析報告）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    system_type TEXT NOT NULL,
                    report_data TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, system_type),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Fortune Profile（結構化摘要快取，用於「有所本」對話）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fortune_profiles (
                    user_id TEXT PRIMARY KEY,
                    source_signature TEXT,
                    profile_data TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Chat Sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES members(user_id)
                )
            """)

            # Chat Messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    payload TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
                )
            """)

            # ==================== 三層記憶架構表 ====================
            
            # 對話記憶表（包含 system_event）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    summary TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    token_count INTEGER,
                    is_archived INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES members(user_id),
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
                )
            """)

            # 摘要記憶表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodic_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    summary_date TEXT NOT NULL,
                    topic TEXT,
                    key_points TEXT NOT NULL,
                    source_session_ids TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES members(user_id)
                )
            """)

            # 使用者畫像表（核心知識庫）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_persona (
                    user_id TEXT PRIMARY KEY,
                    birth_info TEXT,
                    chart_data TEXT,
                    personality_tags TEXT,
                    preferences TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES members(user_id)
                )
            """)
            
            # ==================== 背景任務系統表 ====================
            
            # 任務狀態表（持久化 TaskManager 狀態）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS background_tasks (
                    task_id TEXT PRIMARY KEY,
                    task_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    progress REAL DEFAULT 0.0,
                    message TEXT,
                    result TEXT,
                    error TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    user_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES members(user_id)
                )
            """)
            
            # 任務索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_background_tasks_status
                ON background_tasks(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_background_tasks_user_id
                ON background_tasks(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_background_tasks_created_at
                ON background_tasks(created_at)
            """)
            
            # 索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id 
                ON analysis_history(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_reports_user_id
                ON system_reports(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id
                ON chat_sessions(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id
                ON chat_messages(session_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at 
                ON analysis_history(created_at DESC)
            """)

            # 記憶表索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_memory_user_id
                ON conversation_memory(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_memory_session_id
                ON conversation_memory(session_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodic_summary_user_id
                ON episodic_summary(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodic_summary_date
                ON episodic_summary(user_id, summary_date DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_member_sessions_user_id
                ON member_sessions(user_id)
            """)

            # ==================== §11.2 用戶回饋表 ====================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    message_id INTEGER,
                    rating TEXT NOT NULL,
                    comment TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES members(user_id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id
                ON user_feedback(user_id)
            """)

            # ==================== §11.4 系統監控指標表 ====================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    labels TEXT,
                    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_metrics_name_time
                ON system_metrics(metric_name, recorded_at DESC)
            """)

    def _migrate_chart_locks_schema(self, cursor: sqlite3.Cursor) -> None:
        """Migrate chart_locks schema to composite primary key (user_id, chart_type).

        Older versions mistakenly used only user_id as the primary key, which caused
        different chart types (ziwei/bazi/astrology/...) to overwrite each other.
        This migration is best-effort and should never block DB initialization.
        """
        try:
            cursor.execute("PRAGMA table_info(chart_locks)")
            cols = cursor.fetchall() or []
            # PRAGMA table_info columns: cid, name, type, notnull, dflt_value, pk
            pk_cols = [row[1] for row in cols if int(row[5] or 0) > 0]

            if pk_cols == ['user_id', 'chart_type']:
                return

            # If we cannot confidently detect the legacy schema, do nothing.
            if pk_cols != ['user_id']:
                return

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chart_locks_v2 (
                    user_id TEXT NOT NULL,
                    chart_type TEXT NOT NULL,
                    chart_data TEXT NOT NULL,
                    analysis TEXT,
                    locked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, chart_type),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO chart_locks_v2 (user_id, chart_type, chart_data, analysis, locked_at)
                SELECT user_id, chart_type, chart_data, analysis, locked_at FROM chart_locks
            """)
            cursor.execute("DROP TABLE chart_locks")
            cursor.execute("ALTER TABLE chart_locks_v2 RENAME TO chart_locks")
        except Exception:
            return
    
    # ==================== 用戶相關 ====================
    
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """
        創建新用戶
        
        Args:
            user_data: 用戶資料字典
            
        Returns:
            是否成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (
                    user_id, name, gender, birth_year, birth_month, birth_day,
                    birth_hour, birth_minute, birth_location, longitude, latitude,
                    gregorian_birth_date, full_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data.get('user_id'),
                user_data.get('name'),
                user_data.get('gender'),
                user_data.get('year'),
                user_data.get('month'),
                user_data.get('day'),
                user_data.get('hour'),
                user_data.get('minute', 0),
                user_data.get('birth_location'),
                user_data.get('longitude'),
                user_data.get('latitude'),
                user_data.get('gregorian_birth_date'),
                user_data.get('full_name')
            ))
            return True
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        取得用戶資料
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            用戶資料字典或 None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_user(self, user_id: str) -> bool:
        """
        刪除用戶資料
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            是否成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        更新用戶資料
        
        Args:
            user_id: 用戶 ID
            user_data: 要更新的資料
            
        Returns:
            是否成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 動態生成 UPDATE 語句
            fields = []
            values = []
            for key, value in user_data.items():
                if key != 'user_id':  # 不更新 primary key
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            values.append(datetime.now().isoformat())
            values.append(user_id)
            
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(fields)}, updated_at = ?
                WHERE user_id = ?
            """, values)
            
            return cursor.rowcount > 0
    
    # ==================== 命盤鎖定相關 ====================
    
    def save_chart_lock(
        self,
        user_id: str,
        chart_type: str,
        chart_data: Dict[str, Any],
        analysis: Optional[str] = None
    ) -> bool:
        """
        保存命盤鎖定
        
        Args:
            user_id: 用戶 ID
            chart_type: 命盤類型（ziwei, bazi, astrology 等）
            chart_data: 命盤資料
            analysis: 分析結果
            
        Returns:
            是否成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO chart_locks 
                (user_id, chart_type, chart_data, analysis, locked_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                chart_type,
                json.dumps(chart_data, ensure_ascii=False),
                analysis,
                datetime.now().isoformat()
            ))
            return True

    def create_chart_lock(
        self,
        user_id: str,
        chart_type: str,
        chart_data: Dict[str, Any],
        analysis: Optional[str] = None
    ) -> bool:
        """
        向後相容的命盤鎖定方法
        """
        return self.save_chart_lock(user_id, chart_type, chart_data, analysis)
    
    def get_chart_lock(self, user_id: str, chart_type: str = 'ziwei') -> Optional[Dict[str, Any]]:
        """
        取得命盤鎖定資料
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            命盤鎖定資料或 None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chart_locks WHERE user_id = ? AND chart_type = ?
            """, (user_id, chart_type))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['chart_data'] = json.loads(data['chart_data'])
                return data
            return None

    def get_all_chart_locks(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """
        取得用戶所有命盤鎖定資料

        Args:
            user_id: 用戶 ID

        Returns:
            以 chart_type 為 key 的命盤鎖定資料
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chart_locks WHERE user_id = ?
            """, (user_id,))
            rows = cursor.fetchall() or []

        locks: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            data = dict(row)
            try:
                data['chart_data'] = json.loads(data.get('chart_data') or '{}')
            except Exception:
                data['chart_data'] = {}
            chart_type = data.get('chart_type') or 'unknown'
            locks[chart_type] = data
        return locks
    
    def delete_chart_lock(self, user_id: str, chart_type: Optional[str] = None) -> bool:
        """
        刪除命盤鎖定
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            是否成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if chart_type:
                cursor.execute(
                    "DELETE FROM chart_locks WHERE user_id = ? AND chart_type = ?",
                    (user_id, chart_type),
                )
            else:
                cursor.execute("DELETE FROM chart_locks WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0

    # ==================== 使用紀錄 ====================

    def save_user_activity(
        self,
        user_id: Optional[str],
        path: str,
        method: str,
        status_code: int,
        duration_ms: float,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        保存 API 使用紀錄

        Returns:
            是否成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_activity
                (user_id, path, method, status_code, duration_ms, ip, user_agent, request_data, response_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                path,
                method,
                status_code,
                duration_ms,
                ip,
                user_agent,
                json.dumps(request_data, ensure_ascii=False) if request_data is not None else None,
                json.dumps(response_data, ensure_ascii=False) if response_data is not None else None,
                datetime.now().isoformat()
            ))
            return True
    
    # ==================== 分析歷史相關 ====================
    
    def save_analysis_history(
        self,
        user_id: str,
        analysis_type: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any]
    ) -> int:
        """
        保存分析歷史
        
        Args:
            user_id: 用戶 ID
            analysis_type: 分析類型
            request_data: 請求資料
            response_data: 回應資料
            
        Returns:
            記錄 ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_history 
                (user_id, analysis_type, request_data, response_data)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                analysis_type,
                json.dumps(request_data, ensure_ascii=False),
                json.dumps(response_data, ensure_ascii=False)
            ))
            return cursor.lastrowid
    
    def get_analysis_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        取得分析歷史
        
        Args:
            user_id: 用戶 ID
            limit: 最多返回幾筆
            
        Returns:
            分析歷史列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM analysis_history 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                data['request_data'] = json.loads(data['request_data'])
                data['response_data'] = json.loads(data['response_data'])
                results.append(data)
            return results

    def list_users(self) -> List[Dict[str, Any]]:
        """
        列出所有用戶
        
        Returns:
            用戶資料列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    # ==================== 會員相關 ====================

    def create_member(self, member_data: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO members (
                    user_id, email, phone, display_name, password_hash, password_salt
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                member_data.get('user_id'),
                member_data.get('email'),
                member_data.get('phone'),
                member_data.get('display_name'),
                member_data.get('password_hash'),
                member_data.get('password_salt')
            ))
            return True

    def get_member_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_member_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_member(self, user_id: str, updates: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            for key, value in updates.items():
                fields.append(f"{key} = ?")
                values.append(value)
            if not fields:
                return False
            values.append(datetime.now().isoformat())
            values.append(user_id)
            cursor.execute(f"""
                UPDATE members
                SET {', '.join(fields)}, updated_at = ?
                WHERE user_id = ?
            """, values)
            return cursor.rowcount > 0

    def save_member_preferences(self, user_id: str, prefs: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO member_preferences
                (user_id, tone, response_length, focus_topics, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                prefs.get('tone'),
                prefs.get('response_length'),
                json.dumps(prefs.get('focus_topics') or [], ensure_ascii=False),
                datetime.now().isoformat()
            ))
            return True

    def get_member_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM member_preferences WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data['focus_topics'] = json.loads(data.get('focus_topics') or '[]')
            return data

    def save_member_consents(self, user_id: str, consents: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO member_consents
                (user_id, terms_accepted, data_usage_accepted, marketing_accepted, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                1 if consents.get('terms_accepted') else 0,
                1 if consents.get('data_usage_accepted') else 0,
                1 if consents.get('marketing_accepted') else 0,
                datetime.now().isoformat()
            ))
            return True

    def get_member_consents(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM member_consents WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_session(self, token: str, user_id: str, expires_at: Optional[str]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO member_sessions (token, user_id, expires_at)
                VALUES (?, ?, ?)
            """, (token, user_id, expires_at))
            return True

    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM member_sessions WHERE token = ?", (token,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_session(self, token: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM member_sessions WHERE token = ?", (token,))
            return cursor.rowcount > 0

    # ==================== 系統報告相關 ====================
    
    def save_system_report(self, user_id: str, system_type: str, report_data: Dict[str, Any]) -> bool:
        """
        儲存或更新系統預計算報告
        
        Args:
            user_id: 用戶 ID
            system_type: 系統類型 (ziwei, bazi, astrology, numerology, name, tarot)
            report_data: 報告資料
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_reports (user_id, system_type, report_data, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, system_type) DO UPDATE SET
                    report_data = excluded.report_data,
                    updated_at = excluded.updated_at
            """, (
                user_id,
                system_type,
                json.dumps(report_data, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            return True
    
    def get_system_report(self, user_id: str, system_type: str) -> Optional[Dict[str, Any]]:
        """取得單一系統的報告"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT report_data, created_at, updated_at FROM system_reports WHERE user_id = ? AND system_type = ?",
                (user_id, system_type)
            )
            row = cursor.fetchone()
            if row:
                try:
                    report_data = json.loads(row[0]) if row[0] else {}
                except json.JSONDecodeError:
                    report_data = {'raw': row[0], 'parse_error': True}
                return {
                    'report': report_data,
                    'created_at': row[1],
                    'updated_at': row[2]
                }
            return None
    
    def get_all_system_reports(self, user_id: str) -> Dict[str, Any]:
        """取得用戶所有系統的報告"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT system_type, report_data, created_at, updated_at FROM system_reports WHERE user_id = ?",
                (user_id,)
            )
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                try:
                    report_data = json.loads(row[1]) if row[1] else {}
                except json.JSONDecodeError:
                    report_data = {'raw': row[1], 'parse_error': True}
                result[row[0]] = {
                    'report': report_data,
                    'created_at': row[2],
                    'updated_at': row[3]
                }
            return result
    
    def delete_system_reports(self, user_id: str) -> bool:
        """刪除用戶所有系統報告"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM system_reports WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0

    # ==================== Fortune Profile（對話用結構化摘要） ====================

    def upsert_fortune_profile(self, user_id: str, source_signature: str, profile_data: Dict[str, Any]) -> bool:
        """寫入 fortune profile 快取"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO fortune_profiles (user_id, source_signature, profile_data, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                source_signature,
                json.dumps(profile_data, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            return True

    def get_fortune_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """讀取 fortune profile 快取"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT source_signature, profile_data, updated_at FROM fortune_profiles WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            try:
                profile_data = json.loads(row[1]) if row[1] else {}
            except json.JSONDecodeError:
                profile_data = {'raw': row[1], 'parse_error': True}
            return {
                'source_signature': row[0],
                'profile': profile_data,
                'updated_at': row[2]
            }

    def delete_fortune_profile(self, user_id: str) -> bool:
        """刪除 fortune profile 快取（重置報告時使用）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fortune_profiles WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0

    # ==================== Chat（對話） ====================

    def create_chat_session(self, user_id: str, session_id: str, title: Optional[str] = None) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_sessions (session_id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                user_id,
                title,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            return True

    def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def touch_chat_session(self, session_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?",
                (datetime.now().isoformat(), session_id)
            )
            return cursor.rowcount > 0

    def get_user_chat_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """獲取用戶的對話列表（按更新時間降序）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, title, created_at, updated_at FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?",
                (user_id, limit)
            )
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                sessions.append({
                    'session_id': row['session_id'],
                    'title': row['title'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            return sessions

    def add_chat_message(self, session_id: str, role: str, content: str, payload: Optional[Dict[str, Any]] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages (session_id, role, content, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                role,
                content,
                json.dumps(payload, ensure_ascii=False) if payload is not None else None,
                datetime.now().isoformat()
            ))
            return int(cursor.lastrowid)

    def get_chat_messages(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, session_id, role, content, payload, created_at FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            messages = []
            for row in reversed(rows):
                payload = None
                if row['payload']:
                    try:
                        payload = json.loads(row['payload'])
                    except json.JSONDecodeError:
                        payload = {'raw': row['payload'], 'parse_error': True}
                messages.append({
                    'id': row['id'],
                    'session_id': row['session_id'],
                    'role': row['role'],
                    'content': row['content'],
                    'payload': payload,
                    'created_at': row['created_at']
                })
            return messages

    def delete_chat_session(self, session_id: str, user_id: str) -> bool:
        """刪除對話（需驗證擁有者）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 先驗證擁有者
            cursor.execute("SELECT user_id FROM chat_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row or row['user_id'] != user_id:
                return False
            # 刪除訊息
            cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            # 刪除 session
            cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
            return True

    def close(self):
        """釋放資源（保留介面相容）"""
        return None

    # ==================== 背景任務管理方法 ====================
    
    def save_task(self, task_data: Dict[str, Any]) -> bool:
        """
        儲存任務狀態到資料庫
        
        Args:
            task_data: 任務資料字典，包含：
                - task_id: 任務 ID
                - task_name: 任務名稱
                - status: 狀態 ('pending', 'running', 'completed', 'failed', 'cancelled')
                - priority: 優先級 (1-10，預設 5)
                - progress: 進度 (0.0-1.0)
                - message: 狀態訊息
                - result: 執行結果 (JSON 字串)
                - error: 錯誤訊息
                - metadata: 元數據 (JSON 字串)
                - created_at: 建立時間
                - started_at: 開始時間
                - completed_at: 完成時間
                - user_id: 用戶 ID (可選)
        
        Returns:
            成功返回 True
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO background_tasks (
                    task_id, task_name, status, priority, progress, message,
                    result, error, metadata, created_at, started_at, completed_at, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_data['task_id'],
                task_data['task_name'],
                task_data['status'],
                task_data.get('priority', 5),
                task_data.get('progress', 0.0),
                task_data.get('message'),
                task_data.get('result'),
                task_data.get('error'),
                task_data.get('metadata'),
                task_data['created_at'],
                task_data.get('started_at'),
                task_data.get('completed_at'),
                task_data.get('user_id')
            ))
            return True
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """取得任務資料"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM background_tasks WHERE task_id = ?
            """, (task_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        result: Optional[str] = None,
        error: Optional[str] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None
    ) -> bool:
        """更新任務狀態"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 動態構建 UPDATE 語句
            update_fields = ["status = ?"]
            params = [status]
            
            if progress is not None:
                update_fields.append("progress = ?")
                params.append(progress)
            
            if message is not None:
                update_fields.append("message = ?")
                params.append(message)
            
            if result is not None:
                update_fields.append("result = ?")
                params.append(result)
            
            if error is not None:
                update_fields.append("error = ?")
                params.append(error)
            
            if started_at is not None:
                update_fields.append("started_at = ?")
                params.append(started_at)
            
            if completed_at is not None:
                update_fields.append("completed_at = ?")
                params.append(completed_at)
            
            params.append(task_id)
            
            cursor.execute(f"""
                UPDATE background_tasks 
                SET {', '.join(update_fields)}
                WHERE task_id = ?
            """, params)
            
            return cursor.rowcount > 0
    
    def get_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得待執行任務（按優先級排序）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM background_tasks 
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """取得用戶的任務列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute("""
                    SELECT * FROM background_tasks 
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, status, limit))
            else:
                cursor.execute("""
                    SELECT * FROM background_tasks 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_old_tasks(self, max_age_hours: int = 24) -> int:
        """刪除舊任務記錄"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM background_tasks
                WHERE status IN ('completed', 'failed', 'cancelled')
                AND datetime(created_at) < datetime('now', '-' || ? || ' hours')
            """, (max_age_hours,))
            
            return cursor.rowcount


# 全域資料庫實例（依路徑快取）
_db_instances: Dict[str, AetheriaDatabase] = {}


def get_database(db_path: str = "data/aetheria.db") -> AetheriaDatabase:
    """取得全域資料庫實例（依 db_path 分開快取）"""
    global _db_instances
    key = str(Path(db_path).resolve())
    if key not in _db_instances:
        _db_instances[key] = AetheriaDatabase(db_path)
    return _db_instances[key]
