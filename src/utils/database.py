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
            
            # 命盤鎖定表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chart_locks (
                    user_id TEXT PRIMARY KEY,
                    chart_type TEXT NOT NULL,
                    chart_data TEXT NOT NULL,
                    analysis TEXT,
                    locked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
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
            
            # 索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id 
                ON analysis_history(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at 
                ON analysis_history(created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_member_sessions_user_id
                ON member_sessions(user_id)
            """)
    
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
    
    def get_chart_lock(self, user_id: str) -> Optional[Dict[str, Any]]:
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
                SELECT * FROM chart_locks WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['chart_data'] = json.loads(data['chart_data'])
                return data
            return None
    
    def delete_chart_lock(self, user_id: str) -> bool:
        """
        刪除命盤鎖定
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            是否成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chart_locks WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0
    
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

    def close(self):
        """釋放資源（保留介面相容）"""
        return None


# 全域資料庫實例
_db_instance: Optional[AetheriaDatabase] = None


def get_database(db_path: str = "data/aetheria.db") -> AetheriaDatabase:
    """取得全域資料庫實例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = AetheriaDatabase(db_path)
    return _db_instance
