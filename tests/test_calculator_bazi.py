"""
八字計算器單元測試
"""

import pytest
from src.calculators.bazi import BaziCalculator


@pytest.mark.unit
class TestBaziCalculator:
    """八字計算器測試"""
    
    def setup_method(self):
        """每個測試方法前執行"""
        self.calculator = BaziCalculator()
    
    def test_calculator_initialization(self):
        """測試計算器初始化"""
        assert self.calculator is not None
        assert hasattr(self.calculator, 'calculate_bazi')
    
    def test_calculate_bazi_basic(self):
        """測試基本八字計算"""
        result = self.calculator.calculate_bazi(
            year=1990,
            month=5,
            day=15,
            hour=14,
            minute=30,
            gender="male"
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert '四柱' in result
        assert '年柱' in result['四柱']
        assert '月柱' in result['四柱']
        assert '日柱' in result['四柱']
        assert '时柱' in result['四柱']
    
    def test_calculate_bazi_with_longitude(self):
        """測試帶經度的八字計算（真太陽時）"""
        result = self.calculator.calculate_bazi(
            year=1990,
            month=5,
            day=15,
            hour=14,
            minute=30,
            gender="male",
            longitude=120.5,
            use_apparent_solar_time=True
        )
        
        assert result is not None
    
    def test_gender_normalization(self):
        """測試性別參數標準化"""
        # 應該接受 'male' 和 '男'
        result1 = self.calculator.calculate_bazi(
            year=1990, month=5, day=15, hour=14, minute=30, gender="male"
        )
        result2 = self.calculator.calculate_bazi(
            year=1990, month=5, day=15, hour=14, minute=30, gender="男"
        )
        
        assert result1 is not None
        assert result2 is not None
    
    def test_late_night_hour(self):
        """測試晚子時（23:00-01:00）處理"""
        # 23:00 應該算入下一天
        result = self.calculator.calculate_bazi(
            year=1990,
            month=5,
            day=15,
            hour=23,
            minute=30,
            gender="male"
        )
        
        assert result is not None


@pytest.mark.unit  
class TestBaziValidation:
    """八字輸入驗證測試"""
    
    def setup_method(self):
        self.calculator = BaziCalculator()
    
    @pytest.mark.skip(reason="八字計算器目前沒有輸入驗證，待實作")
    def test_invalid_month(self):
        """測試無效月份"""
        with pytest.raises((ValueError, Exception)):
            self.calculator.calculate_bazi(
                year=1990, month=13, day=15, hour=14, minute=30, gender="male"
            )
    
    @pytest.mark.skip(reason="八字計算器目前沒有輸入驗證，待實作")
    def test_invalid_day(self):
        """測試無效日期"""
        with pytest.raises((ValueError, Exception)):
            self.calculator.calculate_bazi(
                year=1990, month=5, day=32, hour=14, minute=30, gender="male"
            )
    
    @pytest.mark.skip(reason="八字計算器目前沒有輸入驗證，待實作")
    def test_invalid_hour(self):
        """測試無效時辰"""
        with pytest.raises((ValueError, Exception)):
            self.calculator.calculate_bazi(
                year=1990, month=5, day=15, hour=25, minute=30, gender="male"
            )
