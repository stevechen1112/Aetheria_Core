"""
GeoNames 本地緩存
減少網路請求，提升占星計算速度

版本: v1.0.0
最後更新: 2026-02-05
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager
from datetime import datetime, timedelta

from src.utils.logger import get_logger

logger = get_logger()


class GeoNamesCache:
    """GeoNames 查詢結果緩存"""
    
    def __init__(self, db_path: str = "data/geonames_cache.db", cache_days: int = 90):
        """
        Args:
            db_path: 緩存資料庫路徑
            cache_days: 緩存有效天數
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_days = cache_days
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """取得資料庫連線"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化緩存表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 地名查詢緩存表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS geonames_cache (
                    query_key TEXT PRIMARY KEY,
                    city TEXT NOT NULL,
                    nation TEXT,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    timezone TEXT NOT NULL,
                    country_code TEXT,
                    response_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 1
                )
            """)
            
            # 索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_geonames_city 
                ON geonames_cache(city, nation)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_geonames_accessed_at
                ON geonames_cache(accessed_at)
            """)
    
    def _make_query_key(self, city: str, nation: Optional[str] = None) -> str:
        """生成查詢鍵"""
        if nation:
            return f"{city.lower()}:{nation.upper()}"
        return city.lower()
    
    def get(self, city: str, nation: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        從緩存中查詢地名資料
        
        Args:
            city: 城市名稱
            nation: 國家代碼 (可選)
            
        Returns:
            緩存資料或 None
        """
        query_key = self._make_query_key(city, nation)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 查詢並檢查過期
            cursor.execute("""
                SELECT * FROM geonames_cache 
                WHERE query_key = ?
                AND datetime(accessed_at) > datetime('now', '-' || ? || ' days')
            """, (query_key, self.cache_days))
            
            row = cursor.fetchone()
            
            if row:
                # 更新訪問時間和計數
                cursor.execute("""
                    UPDATE geonames_cache 
                    SET accessed_at = CURRENT_TIMESTAMP, access_count = access_count + 1
                    WHERE query_key = ?
                """, (query_key,))
                
                logger.info(f"GeoNames 緩存命中: {city} ({nation or 'auto'})")
                
                return {
                    'city': row['city'],
                    'nation': row['nation'],
                    'lat': row['latitude'],
                    'lng': row['longitude'],
                    'timezonestr': row['timezone'],
                    'countryCode': row['country_code'],
                    'cached': True
                }
            
            return None
    
    def set(
        self,
        city: str,
        nation: Optional[str],
        latitude: float,
        longitude: float,
        timezone: str,
        country_code: Optional[str] = None,
        response_data: Optional[Dict] = None
    ):
        """
        儲存地名資料到緩存
        
        Args:
            city: 城市名稱
            nation: 國家代碼
            latitude: 緯度
            longitude: 經度
            timezone: 時區字串
            country_code: 國家代碼
            response_data: 原始回應數據 (可選，用於調試)
        """
        query_key = self._make_query_key(city, nation)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO geonames_cache (
                    query_key, city, nation, latitude, longitude, 
                    timezone, country_code, response_data,
                    created_at, accessed_at, access_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
            """, (
                query_key,
                city,
                nation,
                latitude,
                longitude,
                timezone,
                country_code,
                json.dumps(response_data) if response_data else None
            ))
            
            logger.info(f"GeoNames 緩存已儲存: {city} ({nation or 'auto'})")
    
    def cleanup_old_entries(self, days: Optional[int] = None) -> int:
        """
        清理過期緩存
        
        Args:
            days: 保留天數（預設使用 cache_days）
            
        Returns:
            刪除的記錄數
        """
        days = days or self.cache_days
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM geonames_cache
                WHERE datetime(accessed_at) < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            deleted = cursor.rowcount
            
            if deleted > 0:
                logger.info(f"已清理 {deleted} 個過期的 GeoNames 緩存")
            
            return deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """取得緩存統計資訊"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total FROM geonames_cache")
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT SUM(access_count) as total_accesses FROM geonames_cache")
            total_accesses = cursor.fetchone()['total_accesses'] or 0
            
            cursor.execute("""
                SELECT city, access_count 
                FROM geonames_cache 
                ORDER BY access_count DESC 
                LIMIT 10
            """)
            top_cities = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_entries': total,
                'total_accesses': total_accesses,
                'top_cities': top_cities,
                'cache_days': self.cache_days,
                'hit_rate': (total_accesses / (total_accesses + 1)) if total_accesses > 0 else 0.0
            }
    
    def preload_common_cities(self):
        """預載常用城市資料"""
        common_cities = [
            # 台灣主要城市
            ("Taipei", "TW", 25.0330, 121.5654, "Asia/Taipei", "TW"),
            ("Taichung", "TW", 24.1477, 120.6736, "Asia/Taipei", "TW"),
            ("Kaohsiung", "TW", 22.6273, 120.3014, "Asia/Taipei", "TW"),
            ("Tainan", "TW", 22.9999, 120.2269, "Asia/Taipei", "TW"),
            ("Hsinchu", "TW", 24.8138, 120.9675, "Asia/Taipei", "TW"),
            
            # 中國主要城市
            ("Beijing", "CN", 39.9042, 116.4074, "Asia/Shanghai", "CN"),
            ("Shanghai", "CN", 31.2304, 121.4737, "Asia/Shanghai", "CN"),
            ("Guangzhou", "CN", 23.1291, 113.2644, "Asia/Shanghai", "CN"),
            ("Shenzhen", "CN", 22.5431, 114.0579, "Asia/Shanghai", "CN"),
            
            # 香港、澳門
            ("Hong Kong", "HK", 22.3193, 114.1694, "Asia/Hong_Kong", "HK"),
            ("Macau", "MO", 22.1987, 113.5439, "Asia/Macau", "MO"),
            
            # 其他亞洲城市
            ("Tokyo", "JP", 35.6762, 139.6503, "Asia/Tokyo", "JP"),
            ("Seoul", "KR", 37.5665, 126.9780, "Asia/Seoul", "KR"),
            ("Singapore", "SG", 1.3521, 103.8198, "Asia/Singapore", "SG"),
            
            # 歐美城市
            ("London", "GB", 51.5074, -0.1278, "Europe/London", "GB"),
            ("New York", "US", 40.7128, -74.0060, "America/New_York", "US"),
            ("Los Angeles", "US", 34.0522, -118.2437, "America/Los_Angeles", "US"),
        ]
        
        loaded_count = 0
        
        for city, nation, lat, lng, tz, country in common_cities:
            # 只有當緩存中沒有時才添加
            if not self.get(city, nation):
                self.set(city, nation, lat, lng, tz, country)
                loaded_count += 1
        
        if loaded_count > 0:
            logger.info(f"已預載 {loaded_count} 個常用城市到 GeoNames 緩存")


# 全局實例
_geonames_cache_instance = None


def get_geonames_cache() -> GeoNamesCache:
    """取得 GeoNames 緩存實例（單例）"""
    global _geonames_cache_instance
    if _geonames_cache_instance is None:
        _geonames_cache_instance = GeoNamesCache()
        _geonames_cache_instance.preload_common_cities()  # 自動預載
    return _geonames_cache_instance
