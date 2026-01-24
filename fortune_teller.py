"""
Aetheria 流年運勢分析模組
計算並分析大限、流年、流月運勢
"""

from datetime import datetime
from typing import Dict, List, Tuple, Optional


class FortuneTeller:
    """
    流年運勢計算器
    """
    
    # 十二地支
    EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 十二宮位
    PALACES = [
        '命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮',
        '遷移宮', '奴僕宮', '官祿宮', '田宅宮', '福德宮', '父母宮'
    ]
    
    def __init__(self, birth_year: int, birth_month: int, birth_day: int, 
                 gender: str, ming_gong_branch: str):
        """
        初始化
        
        Args:
            birth_year: 出生年份（西元年）
            birth_month: 出生月份
            birth_day: 出生日
            gender: 性別（'男' 或 '女'）
            ming_gong_branch: 命宮地支（如 '戌'）
        """
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_day
        self.gender = gender
        self.ming_gong_branch = ming_gong_branch
        self.ming_gong_index = self.EARTHLY_BRANCHES.index(ming_gong_branch)
        
    def calculate_current_age(self, target_year: Optional[int] = None) -> int:
        """計算虛歲"""
        if target_year is None:
            target_year = datetime.now().year
        return target_year - self.birth_year + 1
    
    def calculate_da_xian(self, target_year: Optional[int] = None) -> Dict:
        """
        計算大限
        
        Returns:
            {
                'age_range': (30, 39),
                'start_year': 1997,
                'end_year': 2006,
                'palace_name': '財帛宮',
                'palace_branch': '午'
            }
        """
        age = self.calculate_current_age(target_year)
        
        # 大限起始年齡（依命宮和五行局決定）
        # 簡化版：假設水二局（每宮10年，從命宮起2歲）
        # 實際應該根據五行局決定起始歲數
        da_xian_start_age = 2  # 水二局
        
        # 計算在第幾個大限
        da_xian_number = (age - da_xian_start_age) // 10
        
        # 大限年齡範圍
        start_age = da_xian_start_age + (da_xian_number * 10)
        end_age = start_age + 9
        
        # 大限宮位（順行或逆行取決於性別和陰陽局）
        # 陽男陰女順行，陰男陽女逆行
        # 簡化版：男順女逆
        direction = 1 if self.gender == '男' else -1
        
        palace_index = (self.ming_gong_index + (da_xian_number * direction)) % 12
        palace_name = self.PALACES[palace_index]
        palace_branch = self.EARTHLY_BRANCHES[palace_index]
        
        return {
            'age_range': (start_age, end_age),
            'start_year': self.birth_year + start_age - 1,
            'end_year': self.birth_year + end_age - 1,
            'palace_name': palace_name,
            'palace_branch': palace_branch,
            'da_xian_number': da_xian_number + 1
        }
    
    def calculate_liu_nian(self, target_year: Optional[int] = None) -> Dict:
        """
        計算流年
        
        Returns:
            {
                'year': 2026,
                'age': 58,
                'heavenly_stem': '丙',
                'earthly_branch': '午',
                'palace_name': '官祿宮',
                'palace_branch': '寅'
            }
        """
        if target_year is None:
            target_year = datetime.now().year
        
        age = self.calculate_current_age(target_year)
        
        # 天干地支
        gan_index = (target_year - 4) % 10  # 甲子年是西元1984年
        zhi_index = (target_year - 4) % 12
        
        heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        heavenly_stem = heavenly_stems[gan_index]
        earthly_branch = self.EARTHLY_BRANCHES[zhi_index]
        
        # 流年宮位（從命宮起，依地支順行）
        liu_nian_index = (self.ming_gong_index + zhi_index) % 12
        palace_name = self.PALACES[liu_nian_index]
        palace_branch = self.EARTHLY_BRANCHES[liu_nian_index]
        
        return {
            'year': target_year,
            'age': age,
            'heavenly_stem': heavenly_stem,
            'earthly_branch': earthly_branch,
            'gan_zhi': f'{heavenly_stem}{earthly_branch}',
            'palace_name': palace_name,
            'palace_branch': palace_branch
        }
    
    def calculate_liu_yue(self, target_year: Optional[int] = None, 
                          target_month: Optional[int] = None) -> Dict:
        """
        計算流月
        
        Returns:
            {
                'year': 2026,
                'month': 1,
                'palace_name': '夫妻宮',
                'palace_branch': '申'
            }
        """
        if target_year is None:
            target_year = datetime.now().year
        if target_month is None:
            target_month = datetime.now().month
        
        # 流月從流年的正月宮起算
        # 正月宮位 = 流年地支對應的宮位
        liu_nian = self.calculate_liu_nian(target_year)
        liu_nian_index = self.EARTHLY_BRANCHES.index(liu_nian['earthly_branch'])
        
        # 從正月宮順行
        liu_yue_index = (liu_nian_index + target_month - 1) % 12
        palace_name = self.PALACES[liu_yue_index]
        palace_branch = self.EARTHLY_BRANCHES[liu_yue_index]
        
        return {
            'year': target_year,
            'month': target_month,
            'palace_name': palace_name,
            'palace_branch': palace_branch
        }
    
    def get_fortune_summary(self, target_year: Optional[int] = None, 
                           target_month: Optional[int] = None) -> Dict:
        """
        獲取完整運勢摘要
        
        Returns:
            {
                'current_age': 58,
                'da_xian': {...},
                'liu_nian': {...},
                'liu_yue': {...}
            }
        """
        da_xian = self.calculate_da_xian(target_year)
        liu_nian = self.calculate_liu_nian(target_year)
        liu_yue = self.calculate_liu_yue(target_year, target_month)
        
        return {
            'current_age': self.calculate_current_age(target_year),
            'da_xian': da_xian,
            'liu_nian': liu_nian,
            'liu_yue': liu_yue
        }
    
    def format_fortune_text(self, fortune: Dict) -> str:
        """
        格式化運勢資訊為文字
        """
        da_xian = fortune['da_xian']
        liu_nian = fortune['liu_nian']
        liu_yue = fortune['liu_yue']
        
        text = f"""
【大限】第 {da_xian['da_xian_number']} 大限（{da_xian['age_range'][0]}-{da_xian['age_range'][1]} 歲）
  宮位：{da_xian['palace_name']}（{da_xian['palace_branch']}宮）
  年份：{da_xian['start_year']}-{da_xian['end_year']} 年

【流年】{liu_nian['year']} 年（{liu_nian['gan_zhi']}年，{fortune['current_age']} 歲）
  宮位：{liu_nian['palace_name']}（{liu_nian['palace_branch']}宮）
  
【流月】{liu_yue['year']} 年 {liu_yue['month']} 月
  宮位：{liu_yue['palace_name']}（{liu_yue['palace_branch']}宮）
"""
        return text


# 使用範例
if __name__ == '__main__':
    # 測試用戶：農曆68年（西元1979年）9月23日出生，男性，命宮戌宮
    teller = FortuneTeller(
        birth_year=1979,
        birth_month=9,
        birth_day=23,
        gender='男',
        ming_gong_branch='戌'
    )
    
    # 計算 2026 年運勢
    fortune = teller.get_fortune_summary(2026, 1)
    
    print('='*60)
    print('流年運勢計算範例')
    print('='*60)
    print(teller.format_fortune_text(fortune))
    
    print('\n原始資料:')
    import json
    print(json.dumps(fortune, ensure_ascii=False, indent=2))
