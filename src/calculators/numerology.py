"""
靈數學計算器
Aetheria Core v1.6.0

基於畢達哥拉斯靈數學系統，計算各種核心數字：
- 生命靈數 (Life Path Number)
- 天賦數 (Expression Number)
- 靈魂渴望數 (Soul Urge Number)
- 人格數 (Personality Number)
- 生日數 (Birthday Number)
- 流年數 (Personal Year)
- 流月數 (Personal Month)
- 流日數 (Personal Day)
- 高峰期 (Pinnacle Cycles)
- 挑戰數 (Challenge Numbers)
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, date
import re


@dataclass
class NumerologyProfile:
    """靈數學完整檔案"""
    # 基本資料
    birth_date: date
    full_name: str = ""
    
    # 核心數字
    life_path: int = 0
    life_path_master: bool = False
    expression: int = 0
    expression_master: bool = False
    soul_urge: int = 0
    soul_urge_master: bool = False
    personality: int = 0
    personality_master: bool = False
    birthday: int = 0

    # 姓名靈數可用性（避免中文姓名產生 0 的誤導結果）
    name_numbers_available: bool = False
    
    # 流年資訊
    personal_year: int = 0
    personal_month: int = 0
    personal_day: int = 0
    
    # 高峰期與挑戰
    pinnacles: List[Dict] = field(default_factory=list)
    challenges: List[Dict] = field(default_factory=list)
    
    # 業力債
    karmic_debts: List[int] = field(default_factory=list)
    
    # 計算用中間值
    calculation_details: Dict = field(default_factory=dict)


class NumerologyCalculator:
    """靈數學計算器"""
    
    # 畢達哥拉斯字母數值對照表
    LETTER_VALUES = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
        'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
    }
    
    VOWELS = set('AEIOU')
    MASTER_NUMBERS = {11, 22, 33}
    KARMIC_DEBT_NUMBERS = {13, 14, 16, 19}
    
    # v2.1: 標準母音集合（不含 Y）
    STRICT_VOWELS = set('AEIOU')
    
    def __init__(self):
        """初始化計算器，載入資料庫"""
        root_dir = Path(__file__).parent.parent.parent
        data_file = root_dir / "data" / "numerology_data.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def _classify_y(self, name_upper: str, position: int) -> str:
        """
        根據上下文判斷 Y 是母音還是子音（v2.1 新增）
        
        畢達哥拉斯靈數學規則：
        - Y 在名字開頭且後接母音 → 子音（例：Yolanda 的 Y）
        - Y 在兩個子音之間 → 母音（例：Lynn 的 Y）
        - Y 在母音之後 → 子音（例：Day 的 Y，按發音仍可為母音—看門派）
        - Y 是名字中唯一的「母音發音」 → 母音（例：Glynis, Bryn）
        - 否則 → 子音
        
        Returns:
            'vowel' 或 'consonant'
        """
        if position < 0 or position >= len(name_upper):
            return 'consonant'
        
        char = name_upper[position]
        if char != 'Y':
            return 'vowel' if char in self.STRICT_VOWELS else 'consonant'
        
        # 取得前後字元（僅看字母）
        prev_char = None
        next_char = None
        
        for i in range(position - 1, -1, -1):
            if name_upper[i].isalpha():
                prev_char = name_upper[i]
                break
        
        for i in range(position + 1, len(name_upper)):
            if name_upper[i].isalpha():
                next_char = name_upper[i]
                break
        
        # 規則 1：開頭 + 後面是母音 → 子音
        if prev_char is None and next_char in self.STRICT_VOWELS:
            return 'consonant'
        
        # 規則 2：前後都是子音（或邊界） → 母音
        prev_is_consonant = prev_char is not None and prev_char not in self.STRICT_VOWELS
        next_is_consonant = next_char is not None and next_char not in self.STRICT_VOWELS
        
        if prev_is_consonant and (next_is_consonant or next_char is None):
            return 'vowel'
        
        # 規則 3：名字中沒有其他母音 → 母音
        # 找到當前名字片段（以空格分隔）
        words = name_upper.split()
        cum = 0
        for word in words:
            if cum <= position < cum + len(word):
                # 這個 word 中除了 Y 以外有沒有母音
                other_vowels = [c for i, c in enumerate(word) if c in self.STRICT_VOWELS]
                if not other_vowels:
                    return 'vowel'
                break
            cum += len(word) + 1  # +1 for space
        
        # 預設：子音
        return 'consonant'
    
    def reduce_number(self, num: int, keep_master: bool = True) -> Tuple[int, bool]:
        """
        化約數字至單一位數，可選擇保留主數
        
        Args:
            num: 要化約的數字
            keep_master: 是否保留主數 (11, 22, 33)
            
        Returns:
            (化約後的數字, 是否為主數)
        """
        # 檢查業力債數字（在化約前記錄）
        original = num
        
        while num > 9:
            if keep_master and num in self.MASTER_NUMBERS:
                return num, True
            num = sum(int(d) for d in str(num))
        
        return num, False
    
    def calculate_life_path(self, birth_date: date) -> Tuple[int, bool, Dict]:
        """
        計算生命靈數
        
        生命靈數是最重要的數字，揭示人生使命與核心特質
        計算方式：將出生年月日所有數字相加，化約至 1-9 或主數
        """
        year = birth_date.year
        month = birth_date.month
        day = birth_date.day
        
        # 分別化約年、月、日
        year_sum = sum(int(d) for d in str(year))
        month_sum = month
        day_sum = day
        
        # 化約各部分
        year_reduced, _ = self.reduce_number(year_sum, keep_master=True)
        month_reduced, _ = self.reduce_number(month_sum, keep_master=True)
        day_reduced, _ = self.reduce_number(day_sum, keep_master=True)
        
        # 總和
        total = year_reduced + month_reduced + day_reduced
        life_path, is_master = self.reduce_number(total, keep_master=True)
        
        details = {
            "year": year,
            "month": month,
            "day": day,
            "year_reduced": year_reduced,
            "month_reduced": month_reduced,
            "day_reduced": day_reduced,
            "total_before_reduction": total,
            "life_path": life_path,
            "is_master": is_master
        }
        
        return life_path, is_master, details
    
    def calculate_expression(self, full_name: str) -> Tuple[int, bool, Dict]:
        """
        計算天賦數/表達數
        
        天賦數揭示天生才能與潛力
        計算方式：將姓名中所有字母對應的數字相加
        """
        name_upper = full_name.upper()
        letter_values = []
        total = 0
        
        for char in name_upper:
            if char in self.LETTER_VALUES:
                value = self.LETTER_VALUES[char]
                letter_values.append((char, value))
                total += value
        
        expression, is_master = self.reduce_number(total, keep_master=True)
        
        details = {
            "name": full_name,
            "letter_values": letter_values,
            "total_before_reduction": total,
            "expression": expression,
            "is_master": is_master
        }
        
        return expression, is_master, details
    
    def calculate_soul_urge(self, full_name: str) -> Tuple[int, bool, Dict]:
        """
        計算靈魂渴望數/心靈數
        
        靈魂渴望數揭示內心深處的渴望
        計算方式：將姓名中所有元音（A, E, I, O, U + 視情境的 Y）對應的數字相加
        v2.1: Y 的分類現在依據上下文判定
        """
        name_upper = full_name.upper()
        vowel_values = []
        total = 0
        
        for i, char in enumerate(name_upper):
            if char in self.LETTER_VALUES:
                if char in self.STRICT_VOWELS:
                    value = self.LETTER_VALUES[char]
                    vowel_values.append((char, value))
                    total += value
                elif char == 'Y' and self._classify_y(name_upper, i) == 'vowel':
                    value = self.LETTER_VALUES[char]
                    vowel_values.append((char, value, 'Y作母音'))
                    total += value
        
        soul_urge, is_master = self.reduce_number(total, keep_master=True)
        
        details = {
            "name": full_name,
            "vowel_values": vowel_values,
            "total_before_reduction": total,
            "soul_urge": soul_urge,
            "is_master": is_master
        }
        
        return soul_urge, is_master, details
    
    def calculate_personality(self, full_name: str) -> Tuple[int, bool, Dict]:
        """
        計算人格數/外在數
        
        人格數揭示外在形象與他人的第一印象
        計算方式：將姓名中所有輔音對應的數字相加
        v2.1: Y 的分類現在依據上下文判定
        """
        name_upper = full_name.upper()
        consonant_values = []
        total = 0
        
        for i, char in enumerate(name_upper):
            if char in self.LETTER_VALUES:
                if char in self.STRICT_VOWELS:
                    continue  # 跳過標準母音
                elif char == 'Y':
                    if self._classify_y(name_upper, i) == 'consonant':
                        value = self.LETTER_VALUES[char]
                        consonant_values.append((char, value))
                        total += value
                    # Y 作母音時跳過
                else:
                    value = self.LETTER_VALUES[char]
                    consonant_values.append((char, value))
                    total += value
        
        personality, is_master = self.reduce_number(total, keep_master=True)
        
        details = {
            "name": full_name,
            "consonant_values": consonant_values,
            "total_before_reduction": total,
            "personality": personality,
            "is_master": is_master
        }
        
        return personality, is_master, details
    
    def calculate_birthday(self, birth_date: date) -> Tuple[int, bool, Dict]:
        """
        計算生日數
        
        生日數揭示特殊才能
        計算方式：取出生日的日數，化約至 1-9 或保留 11、22
        """
        day = birth_date.day
        birthday, is_master = self.reduce_number(day, keep_master=True)
        
        details = {
            "day": day,
            "birthday": birthday,
            "is_master": is_master
        }
        
        return birthday, is_master, details
    
    def calculate_personal_year(self, birth_date: date, target_year: int = None) -> Tuple[int, bool, Dict]:
        """
        計算流年數
        
        流年數揭示當年的主題與能量
        計算方式：將出生月日與目標年份相加
        """
        if target_year is None:
            target_year = datetime.now().year
        
        month = birth_date.month
        day = birth_date.day
        
        # 計算總和
        year_sum = sum(int(d) for d in str(target_year))
        total = month + day + year_sum
        
        personal_year, is_master = self.reduce_number(total, keep_master=True)
        
        details = {
            "birth_month": month,
            "birth_day": day,
            "target_year": target_year,
            "year_sum": year_sum,
            "total_before_reduction": total,
            "personal_year": personal_year,
            "is_master": is_master
        }
        
        return personal_year, is_master, details
    
    def calculate_personal_month(self, birth_date: date, target_year: int = None, target_month: int = None) -> Tuple[int, bool, Dict]:
        """
        計算流月數
        
        計算方式：流年數 + 目標月份
        """
        if target_year is None:
            target_year = datetime.now().year
        if target_month is None:
            target_month = datetime.now().month
        
        personal_year, _, _ = self.calculate_personal_year(birth_date, target_year)
        total = personal_year + target_month
        
        personal_month, is_master = self.reduce_number(total, keep_master=True)
        
        details = {
            "personal_year": personal_year,
            "target_month": target_month,
            "total_before_reduction": total,
            "personal_month": personal_month,
            "is_master": is_master
        }
        
        return personal_month, is_master, details
    
    def calculate_personal_day(self, birth_date: date, target_date: date = None) -> Tuple[int, bool, Dict]:
        """
        計算流日數
        
        計算方式：流月數 + 目標日期
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        personal_month, _, _ = self.calculate_personal_month(
            birth_date, target_date.year, target_date.month
        )
        total = personal_month + target_date.day
        
        personal_day, is_master = self.reduce_number(total, keep_master=True)
        
        details = {
            "personal_month": personal_month,
            "target_day": target_date.day,
            "total_before_reduction": total,
            "personal_day": personal_day,
            "is_master": is_master
        }
        
        return personal_day, is_master, details
    
    def calculate_pinnacles(self, birth_date: date) -> List[Dict]:
        """
        計算人生高峰期
        
        人生分為四個高峰期，每個高峰期都有其主題
        """
        life_path, _, _ = self.calculate_life_path(birth_date)
        
        month = birth_date.month
        day = birth_date.day
        year = birth_date.year
        year_reduced, _ = self.reduce_number(sum(int(d) for d in str(year)))
        
        # 第一高峰期結束年齡
        first_pinnacle_end = 36 - life_path
        
        pinnacles = []
        
        # 第一高峰期: 月 + 日
        p1_total = month + day
        p1, p1_master = self.reduce_number(p1_total)
        pinnacles.append({
            "number": 1,
            "name": "第一高峰期",
            "pinnacle": p1,
            "is_master": p1_master,
            "age_start": 0,
            "age_end": first_pinnacle_end,
            "description": "早年的成長與學習階段"
        })
        
        # 第二高峰期: 日 + 年
        p2_total = day + year_reduced
        p2, p2_master = self.reduce_number(p2_total)
        pinnacles.append({
            "number": 2,
            "name": "第二高峰期",
            "pinnacle": p2,
            "is_master": p2_master,
            "age_start": first_pinnacle_end + 1,
            "age_end": first_pinnacle_end + 9,
            "description": "建立事業與家庭的階段"
        })
        
        # 第三高峰期: P1 + P2
        p3_total = p1 + p2
        p3, p3_master = self.reduce_number(p3_total)
        pinnacles.append({
            "number": 3,
            "name": "第三高峰期",
            "pinnacle": p3,
            "is_master": p3_master,
            "age_start": first_pinnacle_end + 10,
            "age_end": first_pinnacle_end + 18,
            "description": "收穫與傳承的階段"
        })
        
        # 第四高峰期: 月 + 年
        p4_total = month + year_reduced
        p4, p4_master = self.reduce_number(p4_total)
        pinnacles.append({
            "number": 4,
            "name": "第四高峰期",
            "pinnacle": p4,
            "is_master": p4_master,
            "age_start": first_pinnacle_end + 19,
            "age_end": None,  # 終生
            "description": "智慧與完成的階段"
        })
        
        return pinnacles
    
    def calculate_challenges(self, birth_date: date) -> List[Dict]:
        """
        計算挑戰數
        
        人生有四個主要挑戰，需要克服才能成長
        """
        month = birth_date.month
        day = birth_date.day
        year = birth_date.year
        year_reduced, _ = self.reduce_number(sum(int(d) for d in str(year)))
        
        month_reduced, _ = self.reduce_number(month, keep_master=False)
        day_reduced, _ = self.reduce_number(day, keep_master=False)
        
        challenges = []
        
        # 第一挑戰: |月 - 日|
        c1 = abs(month_reduced - day_reduced)
        challenges.append({
            "number": 1,
            "name": "第一挑戰",
            "challenge": c1,
            "description": "早年的主要挑戰"
        })
        
        # 第二挑戰: |日 - 年|
        c2 = abs(day_reduced - year_reduced)
        challenges.append({
            "number": 2,
            "name": "第二挑戰",
            "challenge": c2,
            "description": "中年的主要挑戰"
        })
        
        # 第三挑戰: |C1 - C2|
        c3 = abs(c1 - c2)
        challenges.append({
            "number": 3,
            "name": "第三挑戰",
            "challenge": c3,
            "description": "人生的核心挑戰"
        })
        
        # 第四挑戰: |月 - 年|
        c4 = abs(month_reduced - year_reduced)
        challenges.append({
            "number": 4,
            "name": "第四挑戰",
            "challenge": c4,
            "description": "晚年的主要挑戰"
        })
        
        return challenges
    
    def check_karmic_debts(self, birth_date: date, full_name: str = "") -> List[Dict]:
        """
        檢查業力債數字
        
        業力債數字（13, 14, 16, 19）表示前世帶來的功課
        """
        debts = []
        
        # 檢查生日
        day = birth_date.day
        if day in self.KARMIC_DEBT_NUMBERS:
            debt_info = self.data["karmic_debt_numbers"]["numbers"].get(str(day), {})
            debts.append({
                "number": day,
                "source": "生日",
                "debt": debt_info.get("debt", ""),
                "lesson": debt_info.get("lesson", ""),
                "description": debt_info.get("description", "")
            })
        
        # 檢查姓名計算過程中是否出現業力債數字
        if full_name:
            name_upper = full_name.upper()
            total = sum(self.LETTER_VALUES.get(c, 0) for c in name_upper if c in self.LETTER_VALUES)
            
            # 檢查化約過程
            while total > 9:
                if total in self.KARMIC_DEBT_NUMBERS:
                    debt_info = self.data["karmic_debt_numbers"]["numbers"].get(str(total), {})
                    debts.append({
                        "number": total,
                        "source": "姓名天賦數",
                        "debt": debt_info.get("debt", ""),
                        "lesson": debt_info.get("lesson", ""),
                        "description": debt_info.get("description", "")
                    })
                total = sum(int(d) for d in str(total))
        
        return debts
    
    def calculate_compatibility(self, life_path1: int, life_path2: int) -> Dict:
        """
        計算兩個生命靈數的相容性
        """
        # 處理主數
        base1 = life_path1 if life_path1 <= 9 else (life_path1 % 10 if life_path1 % 10 != 0 else life_path1 // 10)
        base2 = life_path2 if life_path2 <= 9 else (life_path2 % 10 if life_path2 % 10 != 0 else life_path2 // 10)
        
        # 修正：11 -> 2, 22 -> 4, 33 -> 6
        if life_path1 == 11:
            base1 = 2
        elif life_path1 == 22:
            base1 = 4
        elif life_path1 == 33:
            base1 = 6
            
        if life_path2 == 11:
            base2 = 2
        elif life_path2 == 22:
            base2 = 4
        elif life_path2 == 33:
            base2 = 6
        
        compatibility_data = self.data["number_compatibility"]["compatibility_matrix"].get(str(base1), {})
        
        if base2 in compatibility_data.get("best", []):
            level = "excellent"
            description = "極佳的相容性，彼此能夠自然地理解和支持對方"
        elif base2 in compatibility_data.get("good", []):
            level = "good"
            description = "良好的相容性，有共同點但也需要一些調適"
        else:
            level = "challenging"
            description = "具有挑戰性的組合，需要更多理解和包容"
        
        return {
            "life_path_1": life_path1,
            "life_path_2": life_path2,
            "compatibility_level": level,
            "description": description
        }
    
    def calculate_full_profile(self, birth_date: date, full_name: str = "", 
                               target_date: date = None) -> NumerologyProfile:
        """
        計算完整的靈數學檔案
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        profile = NumerologyProfile(
            birth_date=birth_date,
            full_name=full_name
        )

        # 判斷是否可計算「姓名靈數」：只對含拉丁字母 (A-Z) 的姓名啟用
        # （中文/非拉丁字母姓名若硬算，會得到 0 等不具意義的結果）
        name_has_latin = bool(re.search(r"[A-Za-z]", full_name or ""))
        
        # 計算生命靈數
        profile.life_path, profile.life_path_master, lp_details = self.calculate_life_path(birth_date)
        
        # 計算生日數
        profile.birthday, _, bd_details = self.calculate_birthday(birth_date)
        
        # 如果有姓名，計算姓名相關數字
        if full_name and name_has_latin:
            profile.expression, profile.expression_master, exp_details = self.calculate_expression(full_name)
            profile.soul_urge, profile.soul_urge_master, su_details = self.calculate_soul_urge(full_name)
            profile.personality, profile.personality_master, pers_details = self.calculate_personality(full_name)
            profile.name_numbers_available = True
        elif full_name and not name_has_latin:
            profile.name_numbers_available = False
        
        # 計算流年相關
        profile.personal_year, _, py_details = self.calculate_personal_year(birth_date, target_date.year)
        profile.personal_month, _, pm_details = self.calculate_personal_month(birth_date, target_date.year, target_date.month)
        profile.personal_day, _, pd_details = self.calculate_personal_day(birth_date, target_date)
        
        # 計算高峰期與挑戰
        profile.pinnacles = self.calculate_pinnacles(birth_date)
        profile.challenges = self.calculate_challenges(birth_date)
        
        # 檢查業力債
        profile.karmic_debts = self.check_karmic_debts(birth_date, full_name if name_has_latin else "")
        
        # 儲存計算細節
        profile.calculation_details = {
            "life_path": lp_details,
            "birthday": bd_details,
            "personal_year": py_details,
            "personal_month": pm_details,
            "personal_day": pd_details
        }
        
        if full_name:
            profile.calculation_details["name_numbers"] = {
                "available": bool(profile.name_numbers_available),
                "reason": "" if name_has_latin else "姓名未包含拉丁字母；姓名靈數需英文/拼音輸入",
            }

        if full_name and name_has_latin:
            profile.calculation_details.update({
                "expression": exp_details,
                "soul_urge": su_details,
                "personality": pers_details
            })
        
        return profile
    
    def get_number_meaning(self, number: int, number_type: str = "life_path") -> Dict:
        """
        取得數字的詳細含義
        
        Args:
            number: 要查詢的數字
            number_type: 數字類型 (life_path, personal_year, birthday, etc.)
        """
        if number_type == "life_path":
            meanings = self.data["life_path_numbers"]["numbers"]
        elif number_type == "personal_year":
            meanings = self.data["personal_year"]["numbers"]
        elif number_type == "birthday":
            meanings = self.data["birthday_number"]["numbers"]
        else:
            meanings = self.data["life_path_numbers"]["numbers"]
        
        return meanings.get(str(number), {})
    
    def format_profile_for_prompt(self, profile: NumerologyProfile, context: str = "general") -> str:
        """
        將靈數學檔案格式化為 Prompt 文字
        """
        lines = []
        lines.append(f"【靈數學分析資料】")
        lines.append(f"出生日期：{profile.birth_date.strftime('%Y年%m月%d日')}")
        
        if profile.full_name:
            lines.append(f"姓名：{profile.full_name}")
        
        lines.append("")
        lines.append("【核心數字】")
        
        # 生命靈數
        lp_meaning = self.get_number_meaning(profile.life_path, "life_path")
        master_note = "（主數）" if profile.life_path_master else ""
        lines.append(f"• 生命靈數：{profile.life_path}{master_note} - {lp_meaning.get('name', '')}")
        
        # 生日數
        bd_meaning = self.get_number_meaning(profile.birthday, "birthday")
        lines.append(f"• 生日數：{profile.birthday} - {bd_meaning if isinstance(bd_meaning, str) else ''}")
        
        # 姓名相關數字
        if profile.full_name and profile.name_numbers_available:
            exp_meaning = self.get_number_meaning(profile.expression, "life_path")
            lines.append(f"• 天賦數：{profile.expression} - {exp_meaning.get('name', '')}")
            
            su_meaning = self.get_number_meaning(profile.soul_urge, "life_path")
            lines.append(f"• 靈魂渴望數：{profile.soul_urge} - {su_meaning.get('name', '')}")
            
            pers_meaning = self.get_number_meaning(profile.personality, "life_path")
            lines.append(f"• 人格數：{profile.personality} - {pers_meaning.get('name', '')}")
        elif profile.full_name and not profile.name_numbers_available:
            lines.append("• 姓名靈數：略（姓名需英文/拼音，才能計算天賦數/靈魂渴望數/人格數）")
        
        lines.append("")
        lines.append("【流年運勢】")
        py_meaning = self.get_number_meaning(profile.personal_year, "personal_year")
        lines.append(f"• 流年數：{profile.personal_year} - {py_meaning.get('theme', '')}")
        lines.append(f"• 流月數：{profile.personal_month}")
        lines.append(f"• 流日數：{profile.personal_day}")
        
        # 高峰期
        lines.append("")
        lines.append("【人生高峰期】")
        for p in profile.pinnacles:
            age_range = f"{p['age_start']}-{p['age_end']}歲" if p['age_end'] else f"{p['age_start']}歲至終生"
            master_note = "（主數）" if p.get('is_master') else ""
            lines.append(f"• {p['name']}（{age_range}）：{p['pinnacle']}{master_note}")
        
        # 挑戰數
        lines.append("")
        lines.append("【人生挑戰】")
        for c in profile.challenges:
            lines.append(f"• {c['name']}：{c['challenge']}")
        
        # 業力債
        if profile.karmic_debts:
            lines.append("")
            lines.append("【業力債功課】")
            for debt in profile.karmic_debts:
                lines.append(f"• {debt['number']}（來源：{debt['source']}）：{debt['lesson']}")
        
        # 情境說明
        lines.append("")
        if context == "love":
            lines.append("【分析重點】：感情關係、伴侶相容性、情感模式")
        elif context == "career":
            lines.append("【分析重點】：職業發展、工作風格、事業潛力")
        elif context == "finance":
            lines.append("【分析重點】：財富觀念、理財傾向、金錢課題")
        elif context == "health":
            lines.append("【分析重點】：身心健康、能量平衡、自我照顧")
        else:
            lines.append("【分析重點】：整體人生藍圖與核心特質")
        
        return "\n".join(lines)
    
    def to_dict(self, profile: NumerologyProfile) -> Dict:
        """
        將靈數學檔案轉換為字典格式
        """
        return {
            "birth_date": profile.birth_date.isoformat(),
            "full_name": profile.full_name,
            "core_numbers": {
                "life_path": {
                    "number": profile.life_path,
                    "is_master": profile.life_path_master,
                    "meaning": self.get_number_meaning(profile.life_path, "life_path")
                },
                "birthday": {
                    "number": profile.birthday,
                    "meaning": self.get_number_meaning(profile.birthday, "birthday")
                },
                "expression": {
                    "number": profile.expression,
                    "is_master": profile.expression_master,
                    "meaning": self.get_number_meaning(profile.expression, "life_path")
                } if (profile.full_name and profile.name_numbers_available) else None,
                "soul_urge": {
                    "number": profile.soul_urge,
                    "is_master": profile.soul_urge_master,
                    "meaning": self.get_number_meaning(profile.soul_urge, "life_path")
                } if (profile.full_name and profile.name_numbers_available) else None,
                "personality": {
                    "number": profile.personality,
                    "is_master": profile.personality_master,
                    "meaning": self.get_number_meaning(profile.personality, "life_path")
                } if (profile.full_name and profile.name_numbers_available) else None
            },
            "cycles": {
                "personal_year": {
                    "number": profile.personal_year,
                    "meaning": self.get_number_meaning(profile.personal_year, "personal_year")
                },
                "personal_month": profile.personal_month,
                "personal_day": profile.personal_day
            },
            "pinnacles": profile.pinnacles,
            "challenges": profile.challenges,
            "karmic_debts": profile.karmic_debts,
            "calculation_details": profile.calculation_details
        }


# 測試程式
if __name__ == "__main__":
    print("=" * 60)
    print("靈數學計算器測試")
    print("=" * 60)
    
    calc = NumerologyCalculator()
    
    # 測試用例：1979 年 11 月 12 日
    test_date = date(1979, 11, 12)
    test_name = "CHEN YU CHU"
    
    print(f"\n測試資料：")
    print(f"  出生日期：{test_date}")
    print(f"  英文姓名：{test_name}")
    
    # 計算完整檔案
    profile = calc.calculate_full_profile(test_date, test_name)
    
    print(f"\n【核心數字】")
    print(f"  生命靈數：{profile.life_path}{'（主數）' if profile.life_path_master else ''}")
    print(f"  天賦數：{profile.expression}{'（主數）' if profile.expression_master else ''}")
    print(f"  靈魂渴望數：{profile.soul_urge}{'（主數）' if profile.soul_urge_master else ''}")
    print(f"  人格數：{profile.personality}{'（主數）' if profile.personality_master else ''}")
    print(f"  生日數：{profile.birthday}")
    
    print(f"\n【流年運勢】（{datetime.now().year}年）")
    print(f"  流年數：{profile.personal_year}")
    print(f"  流月數：{profile.personal_month}")
    print(f"  流日數：{profile.personal_day}")
    
    print(f"\n【人生高峰期】")
    for p in profile.pinnacles:
        age_range = f"{p['age_start']}-{p['age_end']}歲" if p['age_end'] else f"{p['age_start']}歲至終生"
        print(f"  {p['name']}：{p['pinnacle']}（{age_range}）")
    
    print(f"\n【人生挑戰】")
    for c in profile.challenges:
        print(f"  {c['name']}：{c['challenge']}")
    
    if profile.karmic_debts:
        print(f"\n【業力債】")
        for debt in profile.karmic_debts:
            print(f"  {debt['number']}：{debt['lesson']}")
    
    # 測試相容性
    print(f"\n【相容性測試】")
    compat = calc.calculate_compatibility(profile.life_path, 5)
    print(f"  生命靈數 {compat['life_path_1']} 與 {compat['life_path_2']}：{compat['compatibility_level']}")
    print(f"  {compat['description']}")
    
    # 測試 Prompt 格式化
    print(f"\n【Prompt 格式化輸出】")
    print("-" * 40)
    print(calc.format_profile_for_prompt(profile, "general"))
    
    print("\n" + "=" * 60)
    print("✅ 靈數學計算器測試完成！")
    print("=" * 60)
