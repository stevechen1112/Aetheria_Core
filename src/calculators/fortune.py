"""
Aetheria 流年運勢分析模組（v2.1 升級版）
計算並分析大限、流年、流月運勢

v2.1 修正：
- P0-2: 大限五行局不再硬編碼，改為動態讀取 iztro 排盤結果
- P0-3: 流年宮位改用「太歲入宮」（流年地支直接對應宮位）
- 大限順逆修正：陽男陰女順行，陰男陽女逆行（以出生年天干判斷）
- 流月修正：以流年命宮為起點順行
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class FortuneTeller:
    """
    流年運勢計算器（v2.1）
    """
    
    # 十天干
    HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 十二地支
    EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 十二宮位
    PALACES = [
        '命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮',
        '遷移宮', '奴僕宮', '官祿宮', '田宅宮', '福德宮', '父母宮'
    ]
    
    # 五行局起運歲數映射
    WUXING_JU_AGE = {
        '水二局': 2, '木三局': 3, '金四局': 4, '土五局': 5, '火六局': 6
    }
    
    def __init__(self, birth_year: int, birth_month: int, birth_day: int, 
                 gender: str, ming_gong_branch: str,
                 five_elements_class: str = None,
                 palace_branch_map: Dict[str, str] = None):
        """
        初始化
        
        Args:
            birth_year: 出生年份（西元年）
            birth_month: 出生月份
            birth_day: 出生日
            gender: 性別（'男' 或 '女'）
            ming_gong_branch: 命宮地支（如 '戌'）
            five_elements_class: 五行局名稱（如 '火六局'），
                                 None 時回退到水二局（相容舊行為）
            palace_branch_map: 宮位地支映射表（dict），
                               key = 地支, value = 宮名
                               用於太歲入宮的流年命宮查找
        """
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.birth_day = birth_day
        self.gender = gender
        self.ming_gong_branch = ming_gong_branch
        self.ming_gong_index = self.EARTHLY_BRANCHES.index(ming_gong_branch)
        
        # v2.1: 動態五行局
        self.five_elements_class = five_elements_class
        self.da_xian_start_age = self._parse_five_elements_age(five_elements_class)
        
        # v2.1: 宮位地支映射（太歲入宮用）
        self.palace_branch_map = palace_branch_map or {}
        
        # v2.1: 出生年天干陰陽判定
        birth_gan_idx = (self.birth_year - 4) % 10
        self.is_yang_year = birth_gan_idx % 2 == 0  # 甲丙戊庚壬 = 陽
        
    def _parse_five_elements_age(self, five_elements_class: str) -> int:
        """
        從五行局名稱解析起運歲數
        
        '水二局' → 2, '木三局' → 3, '金四局' → 4,
        '土五局' → 5, '火六局' → 6
        
        找不到時回退到 2（水二局，相容舊行為）
        """
        if not five_elements_class:
            return 2  # 向後相容
        
        # 先查完整匹配
        if five_elements_class in self.WUXING_JU_AGE:
            return self.WUXING_JU_AGE[five_elements_class]
        
        # 嘗試正則解析數字
        match = re.search(r'[二三四五六]', five_elements_class)
        if match:
            cn_num = {'二': 2, '三': 3, '四': 4, '五': 5, '六': 6}
            return cn_num.get(match.group(), 2)
        
        # 嘗試阿拉伯數字
        match = re.search(r'(\d)', five_elements_class)
        if match:
            return int(match.group(1))
        
        return 2  # 最終回退
    
    def _get_branch_for_palace(self, palace_name: str) -> str:
        """
        反查宮位名稱對應的地支
        
        利用 palace_branch_map（地支→宮名）的反向映射。
        若無映射則回退到命宮地支做偏移計算。
        """
        # 反查：palace_branch_map 是 {地支: 宮名}，反轉為 {宮名: 地支}
        if self.palace_branch_map:
            for branch, pname in self.palace_branch_map.items():
                if pname == palace_name:
                    return branch
        
        # 回退：以命宮地支 index 為基準，加上宮名在 PALACES 中的偏移
        if palace_name in self.PALACES:
            palace_offset = self.PALACES.index(palace_name)
            # 紫微斗數宮位按地支逆時針排列（命宮之後地支 index 遞減）
            branch_index = (self.ming_gong_index - palace_offset) % 12
            return self.EARTHLY_BRANCHES[branch_index]
        
        return self.ming_gong_branch  # 最終回退
        
    def calculate_current_age(self, target_year: Optional[int] = None) -> int:
        """計算虛歲"""
        if target_year is None:
            target_year = datetime.now().year
        return target_year - self.birth_year + 1
    
    def calculate_da_xian(self, target_year: Optional[int] = None) -> Dict:
        """
        計算大限（v2.1 修正）
        
        修正內容：
        - 起運歲數由五行局動態決定
        - 順逆行以出生年天干陰陽 + 性別判定：
          陽男陰女 → 順行（宮位 index 增加）
          陰男陽女 → 逆行（宮位 index 減少）
        
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
        
        # v2.1: 動態五行局起運歲數
        da_xian_start_age = self.da_xian_start_age
        
        # 防範 edge case：age 還沒到起運歲數
        if age < da_xian_start_age:
            da_xian_number = 0
        else:
            da_xian_number = (age - da_xian_start_age) // 10
        
        # 大限年齡範圍
        start_age = da_xian_start_age + (da_xian_number * 10)
        end_age = start_age + 9
        
        # v2.1: 修正順逆行判定
        # 陽男陰女 → 順行，陰男陽女 → 逆行
        is_male = self.gender == '男'
        shun_xing = (self.is_yang_year and is_male) or (not self.is_yang_year and not is_male)
        direction = 1 if shun_xing else -1
        
        # v2.1 fix: 大限在「宮名序列」上移動，從命宮(index=0)出發
        # 順行: 命宮→兄弟宮→夫妻宮→...
        # 逆行: 命宮→父母宮→福德宮→...
        palace_index = (0 + da_xian_number * direction) % 12
        palace_name = self.PALACES[palace_index]
        
        # 反查該宮位對應的地支（利用 palace_branch_map 的反向映射）
        palace_branch = self._get_branch_for_palace(palace_name)
        
        return {
            'age_range': (start_age, end_age),
            'start_year': self.birth_year + start_age - 1,
            'end_year': self.birth_year + end_age - 1,
            'palace_name': palace_name,
            'palace_branch': palace_branch,
            'da_xian_number': da_xian_number + 1,
            'five_elements_class': self.five_elements_class or '水二局（預設）'
        }
    
    def calculate_liu_nian(self, target_year: Optional[int] = None) -> Dict:
        """
        計算流年（v2.1 修正）
        
        v2.1 修正：太歲入宮法
        - 流年命宮 = 流年地支所在的宮位
        - 例：2026 丙午年 → 午在哪個宮，那個宮就是流年命宮
        - 需要 palace_branch_map（地支→宮名映射表）
        - 若無映射表則回退到舊邏輯
        
        Returns:
            {
                'year': 2026,
                'age': 48,
                'heavenly_stem': '丙',
                'earthly_branch': '午',
                'palace_name': '官祿宮',
                'palace_branch': '午',
                'liu_nian_ming_gong': '遷移宮'
            }
        """
        if target_year is None:
            target_year = datetime.now().year
        
        age = self.calculate_current_age(target_year)
        
        # 天干地支
        gan_index = (target_year - 4) % 10
        zhi_index = (target_year - 4) % 12
        
        heavenly_stem = self.HEAVENLY_STEMS[gan_index]
        earthly_branch = self.EARTHLY_BRANCHES[zhi_index]
        
        # v2.1: 太歲入宮法
        if self.palace_branch_map and earthly_branch in self.palace_branch_map:
            # 流年地支直接對應到宮位
            liu_nian_ming_gong = self.palace_branch_map[earthly_branch]
            palace_branch = earthly_branch
            palace_name = liu_nian_ming_gong
        else:
            # 回退邏輯：以命宮為序列起點，再按流年地支序號順行推算宮位
            # 注意：不再混用地支 index 與宮位 index
            liu_nian_index = (0 + zhi_index) % 12
            palace_name = self.PALACES[liu_nian_index]
            palace_branch = self._get_branch_for_palace(palace_name)
            liu_nian_ming_gong = palace_name
        
        return {
            'year': target_year,
            'age': age,
            'heavenly_stem': heavenly_stem,
            'earthly_branch': earthly_branch,
            'gan_zhi': f'{heavenly_stem}{earthly_branch}',
            'palace_name': palace_name,
            'palace_branch': palace_branch,
            'liu_nian_ming_gong': liu_nian_ming_gong
        }
    
    def calculate_liu_yue(self, target_year: Optional[int] = None, 
                          target_month: Optional[int] = None) -> Dict:
        """
        計算流月（v2.1 修正）
        
        v2.1 修正：
        - 流月以流年命宮為起點
        - 正月（1月）= 流年命宮
        - 二月 = 流年命宮順數一位（依宮位）
        
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
        
        # v2.1: 取流年命宮作為起點
        liu_nian = self.calculate_liu_nian(target_year)
        liu_nian_palace = liu_nian['liu_nian_ming_gong']
        
        # 找到流年命宮在 PALACES 中的 index
        if liu_nian_palace in self.PALACES:
            base_index = self.PALACES.index(liu_nian_palace)
        else:
            # 回退：以命宮為序列起點
            base_index = 0
        
        # 流月：從流年命宮起，正月占流年命宮，二月順行一宮...
        liu_yue_index = (base_index + target_month - 1) % 12
        palace_name = self.PALACES[liu_yue_index]
        palace_branch = self._get_branch_for_palace(palace_name)
        
        return {
            'year': target_year,
            'month': target_month,
            'palace_name': palace_name,
            'palace_branch': palace_branch,
            'liu_nian_ming_gong': liu_nian_palace
        }
    
    def get_fortune_summary(self, target_year: Optional[int] = None, 
                           target_month: Optional[int] = None) -> Dict:
        """
        獲取完整運勢摘要
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
        
        five_elements_info = da_xian.get('five_elements_class', '')
        
        text = f"""
【大限】第 {da_xian['da_xian_number']} 大限（{da_xian['age_range'][0]}-{da_xian['age_range'][1]} 歲）
  宮位：{da_xian['palace_name']}（{da_xian['palace_branch']}宮）
  年份：{da_xian['start_year']}-{da_xian['end_year']} 年
  五行局：{five_elements_info}

【流年】{liu_nian['year']} 年（{liu_nian['gan_zhi']}年，{fortune['current_age']} 歲）
  流年命宮：{liu_nian.get('liu_nian_ming_gong', liu_nian['palace_name'])}（{liu_nian['palace_branch']}宮）
  
【流月】{liu_yue['year']} 年 {liu_yue['month']} 月
  宮位：{liu_yue['palace_name']}（{liu_yue['palace_branch']}宮）
  基準：{liu_yue.get('liu_nian_ming_gong', '')}
"""
        return text


# 使用範例
if __name__ == '__main__':
    # 測試用戶：農曆68年（西元1979年）9月23日出生，男性，命宮戌宮
    # v2.1: 傳入五行局和宮位映射
    palace_branch_map = {
        '戌': '命宮', '酉': '兄弟宮', '申': '夫妻宮', '未': '子女宮',
        '午': '財帛宮', '巳': '疾厄宮', '辰': '遷移宮', '卯': '奴僕宮',
        '寅': '官祿宮', '丑': '田宅宮', '子': '福德宮', '亥': '父母宮'
    }
    
    teller = FortuneTeller(
        birth_year=1979,
        birth_month=9,
        birth_day=23,
        gender='男',
        ming_gong_branch='戌',
        five_elements_class='火六局',
        palace_branch_map=palace_branch_map
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
