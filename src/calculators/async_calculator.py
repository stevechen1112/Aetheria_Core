"""
非同步排盤運算包裝器
將耗時的命盤計算轉為背景任務

版本: v1.0.0
最後更新: 2026-02-05
"""

import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from src.calculators.ziwei_hard import ZiweiHardCalculator, ZiweiRuleset
from src.calculators.bazi import BaziCalculator
from src.calculators.astrology import AstrologyCalculator
from src.calculators.numerology import NumerologyCalculator
from src.calculators.tarot import TarotCalculator
from src.calculators.name import NameCalculator
from src.utils.task_manager import get_task_manager, TaskProgress
from src.utils.logger import get_logger

logger = get_logger()


class AsyncChartCalculator:
    """非同步排盤計算器"""
    
    def __init__(self):
        self.task_manager = get_task_manager()
        self.ziwei_calc = ZiweiHardCalculator()
        self.bazi_calc = BaziCalculator()
        self.astrology_calc = AstrologyCalculator()
        self.numerology_calc = NumerologyCalculator()
        self.tarot_calc = TarotCalculator()
        self.name_calc = NameCalculator()
    
    def calculate_ziwei_async(
        self,
        birth_date: str,
        birth_time: str,
        gender: str,
        birth_location: Optional[str] = None,
        ruleset: Optional[Dict] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        非同步計算紫微斗數命盤
        
        Args:
            birth_date: 出生日期 (YYYY-MM-DD)
            birth_time: 出生時間 (HH:MM)
            gender: 性別
            birth_location: 出生地點
            ruleset: 規則設定
            progress_callback: 進度回調函數
            
        Returns:
            task_id: 任務 ID
        """
        def _calculate():
            start_time = time.time()
            
            try:
                # 解析規則並創建計算器實例
                if ruleset:
                    ziwei_ruleset = ZiweiRuleset(
                        late_zi_day_advance=ruleset.get('late_zi_day_advance', True),
                        split_early_late_zi=ruleset.get('split_early_late_zi', True),
                        use_apparent_solar_time=ruleset.get('use_apparent_solar_time', False)
                    )
                    calc = ZiweiHardCalculator(ziwei_ruleset)
                else:
                    calc = self.ziwei_calc
                
                # 模擬進度更新
                if progress_callback:
                    progress_callback(0.2, "解析生辰資料...")
                
                # 執行計算
                result = calc.calculate_chart(
                    birth_date=birth_date,
                    birth_time=birth_time,
                    gender=gender,
                    birth_location=birth_location
                )
                
                if progress_callback:
                    progress_callback(0.8, "處理命盤結構...")
                
                # 添加元數據
                result['_metadata'] = {
                    'calculation_time_ms': int((time.time() - start_time) * 1000),
                    'calculator': 'ziwei_hard',
                    'version': '1.0.0'
                }
                
                if progress_callback:
                    progress_callback(1.0, "計算完成")
                
                return result
                
            except Exception as e:
                logger.error(f"紫微斗數計算失敗: {e}", exc_info=True)
                raise
        
        # 提交任務
        task_id = self.task_manager.submit_task(
            _calculate,
            task_name="紫微斗數排盤",
            metadata={
                'system': 'ziwei',
                'birth_date': birth_date,
                'birth_time': birth_time
            }
        )
        
        return task_id
    
    def calculate_bazi_async(
        self,
        birth_date: str,
        birth_time: str,
        gender: str,
        birth_location: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """非同步計算八字命盤"""
        def _calculate():
            start_time = time.time()
            
            try:
                if progress_callback:
                    progress_callback(0.3, "計算四柱...")
                
                # 解析日期時間
                from datetime import datetime
                dt_str = f"{birth_date} {birth_time}"
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                
                # BaziCalculator.calculate_bazi 需要分離的年月日時分
                result = self.bazi_calc.calculate_bazi(
                    year=dt.year,
                    month=dt.month,
                    day=dt.day,
                    hour=dt.hour,
                    minute=dt.minute,
                    gender=gender
                )
                
                if progress_callback:
                    progress_callback(0.7, "分析五行...")
                
                result['_metadata'] = {
                    'calculation_time_ms': int((time.time() - start_time) * 1000),
                    'calculator': 'bazi',
                    'version': '1.0.0'
                }
                
                if progress_callback:
                    progress_callback(1.0, "計算完成")
                
                return result
                
            except Exception as e:
                logger.error(f"八字計算失敗: {e}", exc_info=True)
                raise
        
        task_id = self.task_manager.submit_task(
            _calculate,
            task_name="八字排盤",
            metadata={
                'system': 'bazi',
                'birth_date': birth_date,
                'birth_time': birth_time
            }
        )
        
        return task_id
    
    def calculate_astrology_async(
        self,
        birth_date: str,
        birth_time: str,
        birth_location: str,
        timezone: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """非同步計算西洋占星盤"""
        def _calculate():
            start_time = time.time()
            
            try:
                if progress_callback:
                    progress_callback(0.2, "計算行星位置...")
                
                # 解析日期時間
                from datetime import datetime
                dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
                
                result = self.astrology_calc.calculate_natal_chart(
                    name="User",  # 預設名稱
                    year=dt.year,
                    month=dt.month,
                    day=dt.day,
                    hour=dt.hour,
                    minute=dt.minute,
                    city=birth_location or "Taipei",
                    timezone_str=timezone or 'Asia/Taipei'
                )
                
                if progress_callback:
                    progress_callback(0.6, "分析相位...")
                
                result['_metadata'] = {
                    'calculation_time_ms': int((time.time() - start_time) * 1000),
                    'calculator': 'astrology',
                    'version': '1.0.0'
                }
                
                if progress_callback:
                    progress_callback(1.0, "計算完成")
                
                return result
                
            except Exception as e:
                logger.error(f"占星計算失敗: {e}", exc_info=True)
                raise
        
        task_id = self.task_manager.submit_task(
            _calculate,
            task_name="西洋占星排盤",
            metadata={
                'system': 'astrology',
                'birth_date': birth_date,
                'birth_time': birth_time,
                'birth_location': birth_location
            }
        )
        
        return task_id
    
    def calculate_all_systems_async(
        self,
        birth_date: str,
        birth_time: str,
        gender: str,
        birth_location: Optional[str] = None,
        chinese_name: Optional[str] = None,
        timezone: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        非同步計算所有六大系統
        
        Returns:
            task_id: 總任務 ID
        """
        def _calculate():
            start_time = time.time()
            results = {}
            
            try:
                # 紫微斗數 (0-30%)
                if progress_callback:
                    progress_callback(0.05, "正在計算紫微斗數...")
                
                results['ziwei'] = self.ziwei_calc.calculate_chart(
                    birth_date=birth_date,
                    birth_time=birth_time,
                    gender=gender,
                    birth_location=birth_location
                )
                
                if progress_callback:
                    progress_callback(0.30, "紫微斗數完成")
                
                # 八字 (30-50%)
                if progress_callback:
                    progress_callback(0.35, "正在計算八字...")
                
                from datetime import datetime
                dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
                results['bazi'] = self.bazi_calc.calculate_bazi(
                    year=dt.year,
                    month=dt.month,
                    day=dt.day,
                    hour=dt.hour,
                    minute=dt.minute,
                    gender=gender
                )
                
                if progress_callback:
                    progress_callback(0.50, "八字完成")
                
                # 西洋占星 (50-70%)
                if birth_location:
                    if progress_callback:
                        progress_callback(0.55, "正在計算西洋占星...")
                    
                    # 解析日期時間
                    from datetime import datetime
                    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
                    
                    results['astrology'] = self.astrology_calc.calculate_natal_chart(
                        name=chinese_name or "User",
                        year=dt.year,
                        month=dt.month,
                        day=dt.day,
                        hour=dt.hour,
                        minute=dt.minute,
                        city=birth_location,
                        timezone_str=timezone or 'Asia/Taipei'
                    )
                    
                    if progress_callback:
                        progress_callback(0.70, "西洋占星完成")
                
                # 姓名學 (70-85%)
                if chinese_name:
                    if progress_callback:
                        progress_callback(0.75, "正在分析姓名...")
                    
                    name_obj = self.name_calc.analyze(chinese_name)
                    results['name'] = self.name_calc.to_dict(name_obj)
                    
                    if progress_callback:
                        progress_callback(0.85, "姓名學完成")
                
                # 靈數學 (85-95%)
                if progress_callback:
                    progress_callback(0.88, "正在計算靈數...")
                
                from datetime import datetime
                bd = datetime.strptime(birth_date, "%Y-%m-%d").date()
                profile = self.numerology_calc.calculate_full_profile(bd, chinese_name or '')
                results['numerology'] = self.numerology_calc.to_dict(profile)
                
                if progress_callback:
                    progress_callback(0.95, "靈數學完成")
                
                # 完成
                results['_metadata'] = {
                    'calculation_time_ms': int((time.time() - start_time) * 1000),
                    'systems_calculated': list(results.keys()),
                    'total_systems': len(results) - 1  # 扣除 _metadata
                }
                
                if progress_callback:
                    progress_callback(1.0, "所有系統計算完成")
                
                return results
                
            except Exception as e:
                logger.error(f"多系統計算失敗: {e}", exc_info=True)
                raise
        
        task_id = self.task_manager.submit_task(
            _calculate,
            task_name="六大系統排盤",
            metadata={
                'system': 'all',
                'birth_date': birth_date,
                'birth_time': birth_time,
                'systems': ['ziwei', 'bazi', 'astrology', 'numerology', 'name']
            }
        )
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[TaskProgress]:
        """查詢任務狀態"""
        return self.task_manager.get_task_status(task_id)
    
    def wait_for_task(self, task_id: str, timeout: float = 60.0) -> Optional[Any]:
        """
        等待任務完成並返回結果
        
        Args:
            task_id: 任務 ID
            timeout: 超時時間（秒）
            
        Returns:
            任務結果或 None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            progress = self.task_manager.get_task_status(task_id)
            
            if not progress:
                return None
            
            if progress.status.value == "completed":
                return progress.result
            
            if progress.status.value in ["failed", "cancelled"]:
                return None
            
            time.sleep(0.5)
        
        logger.warning(f"等待任務超時: {task_id}")
        return None


# 全局實例
_async_calculator_instance = None

def get_async_calculator() -> AsyncChartCalculator:
    """取得非同步計算器實例（單例）"""
    global _async_calculator_instance
    if _async_calculator_instance is None:
        _async_calculator_instance = AsyncChartCalculator()
    return _async_calculator_instance
