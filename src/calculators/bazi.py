"""
八字排盘计算引擎
基于寿星天文历库（sxtwl）

v2.1 升級：
- 大運起運歲數：使用節氣精算（取代寫死 2 歲）
- 身強弱分析：四維度評分（得令/得地/得生/得助）
- 用神分析：增加調候用神概念
"""

import sxtwl
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class BaziCalculator:
    """八字计算器"""
    
    # 天干
    TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 地支
    DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 五行
    WUXING = {
        '甲': '木', '乙': '木',
        '丙': '火', '丁': '火',
        '戊': '土', '己': '土',
        '庚': '金', '辛': '金',
        '壬': '水', '癸': '水',
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }
    
    # 十神（以日干为主）
    SHISHEN = {
        '同性比': '比肩', '异性比': '劫财',
        '同性食': '食神', '异性食': '伤官',
        '同性财': '偏财', '异性财': '正财',
        '同性官': '偏官', '异性官': '正官',
        '同性印': '偏印', '异性印': '正印'
    }
    
    # 藏干（地支所藏天干）
    CANGGAN = {
        '子': ['癸'],
        '丑': ['己', '癸', '辛'],
        '寅': ['甲', '丙', '戊'],
        '卯': ['乙'],
        '辰': ['戊', '乙', '癸'],
        '巳': ['丙', '戊', '庚'],
        '午': ['丁', '己'],
        '未': ['己', '丁', '乙'],
        '申': ['庚', '壬', '戊'],
        '酉': ['辛'],
        '戌': ['戊', '辛', '丁'],
        '亥': ['壬', '甲']
    }
    
    def __init__(self):
        """初始化寿星天文历对象"""
        # sxtwl 使用函数式 API，不需要初始化对象
        pass
    
    def calculate_bazi(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        gender: str = "男",
        longitude: float = 120.0,
        use_apparent_solar_time: bool = True
    ) -> Dict:
        """
        计算八字
        
        Args:
            year: 公历年
            month: 公历月
            day: 公历日
            hour: 公历时（24小时制）
            minute: 公历分
            gender: 性别（"男"或"女"）
            longitude: 出生地经度（用于真太阳时校正）
            use_apparent_solar_time: 是否使用真太阳时
        
        Returns:
            八字数据字典
        """
        
        # 性別統一
        gender = self._normalize_gender(gender)

        # 真太阳时校正
        if use_apparent_solar_time:
            time_correction = (longitude - 120) * 4  # 分钟
            corrected_minute = minute + time_correction
            
            # 处理分钟溢出
            if corrected_minute >= 60:
                hour += int(corrected_minute // 60)
                corrected_minute = int(corrected_minute % 60)
            elif corrected_minute < 0:
                hour -= int((-corrected_minute // 60) + 1)
                corrected_minute = int(60 + (corrected_minute % 60))
            
            # 处理小时溢出
            if hour >= 24:
                day += 1
                hour = hour % 24
            elif hour < 0:
                day -= 1
                hour = 24 + (hour % 24)
        else:
            corrected_minute = minute
        
        # 获取农历日期
        lunar_day = sxtwl.fromSolar(year, month, day)
        
        # 计算四柱
        year_gz = self._get_year_ganzhi(lunar_day)
        month_gz = self._get_month_ganzhi(year, month, day, lunar_day)
        day_gz = self._get_day_ganzhi(lunar_day)
        hour_gz = self._get_hour_ganzhi(lunar_day, hour)
        
        # 日主（日干）
        day_master = day_gz[0]
        day_master_wuxing = self.WUXING[day_master]
        
        # 计算十神
        year_shishen = self._calculate_shishen(day_master, year_gz[0], year_gz[1])
        month_shishen = self._calculate_shishen(day_master, month_gz[0], month_gz[1])
        day_shishen = self._calculate_shishen(day_master, day_gz[0], day_gz[1])
        hour_shishen = self._calculate_shishen(day_master, hour_gz[0], hour_gz[1])
        
        # 计算大运（v2.1：傳入出生日期以精算起運歲數）
        dayun = self._calculate_dayun(
            year_gz, month_gz, gender, lunar_day,
            year=year, month=month, day=day,
            hour=hour, minute=corrected_minute if use_apparent_solar_time else minute
        )
        
        # 分析强弱（v2.1：四維度評分 + 天干分析）
        strength_analysis = self._analyze_strength(
            day_master,
            [month_gz[1], day_gz[1], hour_gz[1]],
            lunar_day.getLunarMonth(),
            all_tiangan=[year_gz[0], month_gz[0], day_gz[0], hour_gz[0]]
        )
        
        # 用神分析
        yongshen_analysis = self._analyze_yongshen(
            day_master_wuxing,
            strength_analysis
        )
        
        result = {
            "四柱": {
                "年柱": {
                    "天干": year_gz[0],
                    "地支": year_gz[1],
                    "纳音": self._get_nayin(year_gz[0], year_gz[1]),
                    "十神": year_shishen
                },
                "月柱": {
                    "天干": month_gz[0],
                    "地支": month_gz[1],
                    "纳音": self._get_nayin(month_gz[0], month_gz[1]),
                    "十神": month_shishen
                },
                "日柱": {
                    "天干": day_gz[0],
                    "地支": day_gz[1],
                    "纳音": self._get_nayin(day_gz[0], day_gz[1]),
                    "十神": day_shishen
                },
                "时柱": {
                    "天干": hour_gz[0],
                    "地支": hour_gz[1],
                    "纳音": self._get_nayin(hour_gz[0], hour_gz[1]),
                    "十神": hour_shishen
                }
            },
            "日主": {
                "天干": day_master,
                "五行": day_master_wuxing
            },
            "强弱": strength_analysis,
            "用神": yongshen_analysis,
            "大运": dayun,
            "农历": {
                "年": lunar_day.getLunarYear(),
                "月": lunar_day.getLunarMonth(),
                "日": lunar_day.getLunarDay(),
                "是否闰月": lunar_day.isLunarLeap()
            },
            "计算参数": {
                "真太阳时": use_apparent_solar_time,
                "经度": longitude if use_apparent_solar_time else None,
                "时间校正": f"{time_correction:.1f}分钟" if use_apparent_solar_time else "未使用"
            }
        }

        # 合沖刑害分析（v2.2 新增）
        all_zhi = [year_gz[1], month_gz[1], day_gz[1], hour_gz[1]]
        result["合冲刑害"] = self._analyze_dizhi_interactions(all_zhi)

        # 格局分析（v2.2 新增）
        result["格局"] = self._analyze_pattern(
            day_master,
            strength_analysis,
            [year_gz[0], month_gz[0], day_gz[0], hour_gz[0]],
            all_zhi,
            month_gz[1]
        )

        # 兼容繁體鍵名
        result["四柱"]["時柱"] = result["四柱"]["时柱"]
        result["強弱"] = result["强弱"]
        
        return result
    
    def _get_year_ganzhi(self, lunar_day) -> Tuple[str, str]:
        """获取年柱干支"""
        gz = lunar_day.getYearGZ()
        return (self.TIANGAN[gz.tg], self.DIZHI[gz.dz])
    
    def _get_month_ganzhi(self, year: int, month: int, day: int, lunar_day) -> Tuple[str, str]:
        """获取月柱干支（以节气为准）"""
        gz = lunar_day.getMonthGZ()
        return (self.TIANGAN[gz.tg], self.DIZHI[gz.dz])
    
    def _get_day_ganzhi(self, lunar_day) -> Tuple[str, str]:
        """获取日柱干支"""
        gz = lunar_day.getDayGZ()
        return (self.TIANGAN[gz.tg], self.DIZHI[gz.dz])
    
    def _get_hour_ganzhi(self, lunar_day, hour: int) -> Tuple[str, str]:
        """
        獲取時柱干支
        時辰劃分：
        23-1: 子時, 1-3: 丑時, 3-5: 寅時, 5-7: 卯時
        7-9: 辰時, 9-11: 巳時, 11-13: 午時, 13-15: 未時
        15-17: 申時, 17-19: 酉時, 19-21: 戌時, 21-23: 亥時
        
        Aetheria 修正：處理晚子時 (23:00-00:00) 的日柱不變邏輯。
        """
        # 獲取日柱干支索引
        day_gz = lunar_day.getDayGZ()
        
        # 處理晚子時：sxtwl.getShiGz 在 23 點會自動跳到下一天（早子時邏輯）
        # 為了實現「日柱不變」的晚子時，對於 23 點，我們取該日的子時（index 0）之干支，
        # 這樣時干就是基於當日日干計算出的「壬子」（以癸日為例），而非下一日的「甲子」。
        lookup_hour = hour
        if hour >= 23:
            lookup_hour = 0
            
        # sxtwl.getShiGz 需要 (日干索引, 小時)
        gz = sxtwl.getShiGz(day_gz.tg, lookup_hour)
        return (self.TIANGAN[gz.tg], self.DIZHI[gz.dz])
    
    def _calculate_shishen(self, day_gan: str, target_gan: str, target_zhi: str) -> Dict[str, str]:
        """计算十神"""
        result = {}
        
        # 天干十神
        if target_gan:
            result["天干"] = self._get_shishen_relation(day_gan, target_gan)
        
        # 地支藏干十神
        if target_zhi:
            canggan = self.CANGGAN[target_zhi]
            result["地支藏干"] = {
                gan: self._get_shishen_relation(day_gan, gan)
                for gan in canggan
            }
        
        return result
    
    def _get_shishen_relation(self, day_gan: str, target_gan: str) -> str:
        """获取天干之间的十神关系"""
        if day_gan == target_gan:
            return "比肩"
        
        day_idx = self.TIANGAN.index(day_gan)
        target_idx = self.TIANGAN.index(target_gan)
        
        day_wuxing = self.WUXING[day_gan]
        target_wuxing = self.WUXING[target_gan]
        
        # 判断阴阳（偶数为阳，奇数为阴）
        day_yinyang = "阳" if day_idx % 2 == 0 else "阴"
        target_yinyang = "阳" if target_idx % 2 == 0 else "阴"
        same_yinyang = day_yinyang == target_yinyang
        
        # 五行生克关系
        wuxing_relation = self._get_wuxing_relation(day_wuxing, target_wuxing)
        
        # 十神映射
        shishen_map = {
            "比": "比肩" if same_yinyang else "劫财",
            "食": "食神" if same_yinyang else "伤官",
            "财": "偏财" if same_yinyang else "正财",
            "官": "七杀" if same_yinyang else "正官",
            "印": "偏印" if same_yinyang else "正印"
        }
        
        return shishen_map.get(wuxing_relation, "未知")
    
    def _get_wuxing_relation(self, from_wuxing: str, to_wuxing: str) -> str:
        """获取五行生克关系"""
        if from_wuxing == to_wuxing:
            return "比"
        
        sheng_map = {
            "木": "火", "火": "土", "土": "金", "金": "水", "水": "木"
        }
        ke_map = {
            "木": "土", "土": "水", "水": "火", "火": "金", "金": "木"
        }
        
        if sheng_map[from_wuxing] == to_wuxing:
            return "食"  # 我生者为食伤
        elif sheng_map[to_wuxing] == from_wuxing:
            return "印"  # 生我者为印
        elif ke_map[from_wuxing] == to_wuxing:
            return "财"  # 我克者为财
        elif ke_map[to_wuxing] == from_wuxing:
            return "官"  # 克我者为官杀
        
        return "未知"
    
    def _calculate_dayun(self, year_gz: Tuple, month_gz: Tuple, gender: str,
                         lunar_day, year: int = None, month: int = None,
                         day: int = None, hour: int = 0, minute: int = 0) -> List[Dict]:
        """
        计算大运（v2.1 升級：節氣精算起運歲數）
        
        起運歲數計算：
        1. 陽年男 / 陰年女 → 順排 → 出生日到「下一個節」的天數 ÷ 3
        2. 陰年男 / 陽年女 → 逆排 → 出生日到「上一個節」的天數 ÷ 3
        """
        dayun_list = []
        
        # 判断顺逆（阳男阴女顺排，阴男阳女逆排）
        year_gan_idx = self.TIANGAN.index(year_gz[0])
        is_yang_year = year_gan_idx % 2 == 0
        is_male = gender == "男"
        
        shun_pai = (is_yang_year and is_male) or (not is_yang_year and not is_male)
        
        # ===== v2.1: 節氣精算起運歲數 =====
        start_age = self._calculate_start_age(year, month, day, hour, minute, shun_pai)
        
        # 月柱干支索引
        month_gan_idx = self.TIANGAN.index(month_gz[0])
        month_zhi_idx = self.DIZHI.index(month_gz[1])
        
        # 生成10步大运
        for i in range(10):
            age_start = start_age + i * 10
            age_end = age_start + 9
            
            if shun_pai:
                gan_idx = (month_gan_idx + i + 1) % 10
                zhi_idx = (month_zhi_idx + i + 1) % 12
            else:
                gan_idx = (month_gan_idx - i - 1) % 10
                zhi_idx = (month_zhi_idx - i - 1) % 12
            
            dayun_gan = self.TIANGAN[gan_idx]
            dayun_zhi = self.DIZHI[zhi_idx]
            
            dayun_list.append({
                "序号": i + 1,
                "年龄": f"{age_start}-{age_end}岁",
                "起运岁数": start_age,
                "天干": dayun_gan,
                "地支": dayun_zhi,
                "纳音": self._get_nayin(dayun_gan, dayun_zhi)
            })
        
        return dayun_list
    
    # 24 節氣名稱（與 sxtwl 的 index 對應）
    JIE_QI_NAMES = [
        "小寒", "大寒", "立春", "雨水", "驚蟄", "春分",
        "清明", "穀雨", "立夏", "小滿", "芒種", "夏至",
        "小暑", "大暑", "立秋", "處暑", "白露", "秋分",
        "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
    ]
    
    def _calculate_start_age(self, year: int, month: int, day: int,
                             hour: int, minute: int, shun_pai: bool) -> int:
        """
        根據節氣精算大運起運歲數
        
        算法：
        - 順排：出生日到下一個「節」的天數 ÷ 3 = 起運虛歲
        - 逆排：出生日到上一個「節」的天數 ÷ 3 = 起運虛歲
        - 「節」= 偶數索引的節氣（小寒、立春、驚蟄、清明、立夏、芒種、小暑、立秋、白露、寒露、立冬、大雪）
        - 餘數按四捨五入取整，最小 1 歲
        
        Args:
            year, month, day, hour, minute: 出生時間（公曆）
            shun_pai: True=順排, False=逆排
            
        Returns:
            起運歲數（虛歲）
        """
        if year is None or month is None or day is None:
            return 2  # fallback: 無法計算時返回安全預設值
        
        # 出生日的 Julian Day（精確到小時分鐘）
        try:
            birth_time = sxtwl.Time()
            birth_time.setYear(int(year))
            birth_time.setMonth(int(month))
            birth_time.setDay(int(day))
            birth_time.setHour(float(hour))
            birth_time.setMour(float(minute))
            birth_time.setSec(0.0)
            birth_jd = sxtwl.toJD(birth_time)
        except Exception:
            return 2  # fallback
        
        # 取得出生年和前後一年的所有節氣
        all_jie = []  # 只收集「節」（偶數索引）
        for y in [year - 1, year, year + 1]:
            try:
                jq_list = sxtwl.getJieQiByYear(y)
                for jq in jq_list:
                    # 偶數索引才是「節」（月令分界）
                    if jq.jqIndex % 2 == 0:
                        all_jie.append(jq.jd)
            except Exception:
                continue
        
        if not all_jie:
            return 2  # fallback
        
        all_jie.sort()
        
        if shun_pai:
            # 順排：找出生日之後最近的「節」
            next_jie = None
            for jd in all_jie:
                if jd > birth_jd:
                    next_jie = jd
                    break
            if next_jie is None:
                return 2
            diff_days = next_jie - birth_jd
        else:
            # 逆排：找出生日之前最近的「節」
            prev_jie = None
            for jd in reversed(all_jie):
                if jd < birth_jd:
                    prev_jie = jd
                    break
            if prev_jie is None:
                return 2
            diff_days = birth_jd - prev_jie
        
        # 天數 ÷ 3 = 起運歲數，四捨五入，最小 1 歲
        start_age = max(1, round(diff_days / 3))
        return start_age

    def _normalize_gender(self, value: str) -> str:
        """統一性別格式為「男/女/未指定」"""
        if not value:
            return "未指定"
        value = str(value).strip().lower()
        if value in ["男", "male", "m", "man", "男性", "boy"]:
            return "男"
        if value in ["女", "female", "f", "woman", "女性", "girl"]:
            return "女"
        return "未指定"
    
    def _analyze_strength(self, day_master: str, dizhi_list: List[str],
                          month: int, all_tiangan: List[str] = None) -> Dict:
        """
        分析日主强弱（v2.1 四維度評分）
        
        四維度：
        1. 得令（月令旺相休囚死）：30 分
        2. 得地（地支藏干生扶）：20 分
        3. 得生（天干生助日主）：15 分
        4. 得助（天干同行五行）：15 分
        5. 剋泄（天干剋泄日主）：扣分
        
        Args:
            day_master: 日干
            dizhi_list: [月支, 日支, 時支]
            month: 農曆月份
            all_tiangan: [年干, 月干, 日干, 時干]（可選，用於天干分析）
        """
        day_wuxing = self.WUXING[day_master]
        score = 0
        factors = []
        
        # ===== 維度 1: 得令（月令旺相休囚死）=====
        # 月支藏干中的本氣（第一個元素）決定月令
        month_zhi = dizhi_list[0]
        month_canggan = self.CANGGAN[month_zhi]
        month_benqi = month_canggan[0]  # 本氣
        month_benqi_wuxing = self.WUXING[month_benqi]
        
        # 月令旺相休囚死判定
        # 旺（同行）= 30, 相（生我）= 20, 休（我生）= 5, 囚（剋我）= 0, 死（我剋）= 0
        relation = self._get_wuxing_relation(day_wuxing, month_benqi_wuxing)
        if day_wuxing == month_benqi_wuxing:
            score += 30
            factors.append(f"得月令（月支{month_zhi}本氣{month_benqi}={month_benqi_wuxing}，旺 +30）")
        elif relation == "印":
            # 月令五行生我
            score += 20
            factors.append(f"月令相生（月支{month_zhi}本氣{month_benqi}={month_benqi_wuxing}生{day_wuxing}，相 +20）")
        elif relation == "食":
            # 我生月令五行
            score += 5
            factors.append(f"月令洩氣（{day_wuxing}生{month_benqi_wuxing}，休 +5）")
        elif relation == "官":
            factors.append(f"月令剋我（{month_benqi_wuxing}剋{day_wuxing}，囚）")
        elif relation == "财":
            factors.append(f"月令被我剋（{day_wuxing}剋{month_benqi_wuxing}，死）")
        
        # ===== 維度 2: 得地（所有地支藏干生扶日主）=====
        support_count = 0
        drain_count = 0
        for zhi in dizhi_list:
            canggan = self.CANGGAN[zhi]
            for i, gan in enumerate(canggan):
                gan_wuxing = self.WUXING[gan]
                # 本氣權重最高，中氣次之，餘氣最低
                weight = [7, 3, 1][min(i, 2)]
                if gan_wuxing == day_wuxing:
                    # 同行 = 得助
                    score += weight
                    support_count += 1
                    factors.append(f"得地支{zhi}藏{gan}（{gan_wuxing}同行 +{weight}）")
                elif self._get_wuxing_relation(day_wuxing, gan_wuxing) == "印":
                    # 藏干生我 = 得生
                    score += weight
                    support_count += 1
                    factors.append(f"得地支{zhi}藏{gan}（{gan_wuxing}生{day_wuxing} +{weight}）")
                elif self._get_wuxing_relation(day_wuxing, gan_wuxing) in ("官", "财"):
                    drain_count += 1
        
        # ===== 維度 3 & 4: 天干得生 / 得助 / 被剋泄 =====
        if all_tiangan:
            for i, gan in enumerate(all_tiangan):
                if i == 2:  # 跳過日干自己
                    continue
                gan_wuxing = self.WUXING[gan]
                position = ["年干", "月干", "日干", "時干"][i]
                
                if gan_wuxing == day_wuxing:
                    # 得助（天干同行）
                    score += 8
                    factors.append(f"得{position}{gan}助力（{gan_wuxing}同行 +8）")
                elif self._get_wuxing_relation(day_wuxing, gan_wuxing) == "印":
                    # 得生（天干生我）
                    score += 10
                    factors.append(f"得{position}{gan}生扶（{gan_wuxing}生{day_wuxing} +10）")
                elif self._get_wuxing_relation(day_wuxing, gan_wuxing) == "食":
                    # 我生 = 泄氣
                    score -= 5
                    factors.append(f"{position}{gan}洩氣（{day_wuxing}生{gan_wuxing} -5）")
                elif self._get_wuxing_relation(day_wuxing, gan_wuxing) == "官":
                    # 剋我
                    score -= 8
                    factors.append(f"{position}{gan}剋制（{gan_wuxing}剋{day_wuxing} -8）")
                elif self._get_wuxing_relation(day_wuxing, gan_wuxing) == "财":
                    # 我剋 = 耗氣
                    score -= 3
                    factors.append(f"{position}{gan}耗氣（{day_wuxing}剋{gan_wuxing} -3）")
        
        # ===== 綜合判斷 =====
        # 分數區間：理論最高約 100+，最低可能為負
        # 標準化到 0-100 區間
        normalized_score = max(0, min(100, score))
        
        if normalized_score >= 60:
            strength = "身旺"
        elif normalized_score >= 40:
            strength = "中和偏旺"
        elif normalized_score >= 25:
            strength = "中和"
        elif normalized_score >= 15:
            strength = "中和偏弱"
        else:
            strength = "身弱"
        
        return {
            "结论": strength,
            "评分": normalized_score,
            "原始分": score,
            "因素": factors
        }
    
    def _analyze_yongshen(self, day_wuxing: str, strength: Dict) -> Dict:
        """
        分析用神（v2.1：加入調候用神概念）
        
        用神選取邏輯：
        1. 身旺 → 用泄、用剋、用耗（食傷 > 官殺 > 財）
        2. 身弱 → 用生、用助（印 > 比劫）
        3. 中和 → 維持平衡，取最缺之五行
        4. 調候用神：夏季火土日主喜水，冬季水木日主喜火
        """
        strength_level = strength["结论"]
        
        # 五行相生相剋映射
        sheng_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        ke_map = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
        
        # 生我者
        sheng_wo = {v: k for k, v in sheng_map.items()}[day_wuxing]
        # 我生者
        wo_sheng = sheng_map[day_wuxing]
        # 剋我者
        ke_wo = {v: k for k, v in ke_map.items()}[day_wuxing]
        # 我剋者
        wo_ke = ke_map[day_wuxing]
        
        if strength_level in ("身旺", "中和偏旺"):
            # 身旺：用食傷泄秀，官殺制身，財星耗氣
            yongshen = [wo_sheng]  # 食傷泄秀為第一用神
            xishen = [wo_ke, ke_wo]  # 財星耗氣 + 官殺制身
            jishen = [sheng_wo, day_wuxing]  # 忌印生、比劫助
        elif strength_level in ("身弱", "中和偏弱"):
            # 身弱：用印綬生身，比劫助力
            yongshen = [sheng_wo]  # 印綬生身為第一用神
            xishen = [day_wuxing]  # 比劫助力
            jishen = [ke_wo, wo_sheng, wo_ke]  # 忌官殺、食傷、財星
        else:
            # 中和：維持平衡
            yongshen = [sheng_wo]
            xishen = [day_wuxing]
            jishen = [ke_wo]
        
        # 調候用神修正提示（提供給 AI 做 Prompt 參考）
        tiao_hou_note = ""
        score = strength.get("评分", 50)
        factors = strength.get("因素", [])
        
        # 檢查月令特徵（從因素中提取）
        month_info = ""
        for f in factors:
            if "月令" in f or "月支" in f or "得月令" in f:
                month_info = f
                break
        
        # 夏月火土日主 → 調候用水
        if "火旺" in month_info or "巳" in month_info or "午" in month_info or "未" in month_info:
            if day_wuxing in ("火", "土"):
                tiao_hou_note = f"調候：夏月{day_wuxing}日主，宜取水為調候用神"
        # 冬月水木日主 → 調候用火
        if "水旺" in month_info or "亥" in month_info or "子" in month_info or "丑" in month_info:
            if day_wuxing in ("水", "木"):
                tiao_hou_note = f"調候：冬月{day_wuxing}日主，宜取火為調候用神"
        
        result = {
            "用神": yongshen,
            "喜神": xishen,
            "忌神": jishen,
            "身强弱": strength_level,
            "评分": score
        }
        
        if tiao_hou_note:
            result["调候"] = tiao_hou_note
        
        return result
    
    # ===== v2.2: 合沖刑害分析 =====

    # 六合
    LIUHE = {
        ('子', '丑'): '土', ('丑', '子'): '土',
        ('寅', '亥'): '木', ('亥', '寅'): '木',
        ('卯', '戌'): '火', ('戌', '卯'): '火',
        ('辰', '酉'): '金', ('酉', '辰'): '金',
        ('巳', '申'): '水', ('申', '巳'): '水',
        ('午', '未'): '土', ('未', '午'): '土',
    }

    # 六沖
    LIUCHONG = [
        ('子', '午'), ('午', '子'),
        ('丑', '未'), ('未', '丑'),
        ('寅', '申'), ('申', '寅'),
        ('卯', '酉'), ('酉', '卯'),
        ('辰', '戌'), ('戌', '辰'),
        ('巳', '亥'), ('亥', '巳'),
    ]

    # 三合局
    SANHE = {
        ('申', '子', '辰'): '水局',
        ('寅', '午', '戌'): '火局',
        ('巳', '酉', '丑'): '金局',
        ('亥', '卯', '未'): '木局',
    }

    # 三刑
    SANXING = [
        (('寅', '巳'), '恃勢之刑'),
        (('巳', '申'), '恃勢之刑'),
        (('寅', '申'), '恃勢之刑'),
        (('丑', '戌'), '無恩之刑'),
        (('戌', '未'), '無恩之刑'),
        (('丑', '未'), '無恩之刑'),
        (('子', '卯'), '無禮之刑'),
        (('卯', '子'), '無禮之刑'),
        (('辰', '辰'), '自刑'),
        (('午', '午'), '自刑'),
        (('酉', '酉'), '自刑'),
        (('亥', '亥'), '自刑'),
    ]

    # 六害
    LIUHAI = [
        (('子', '未'), '子未相害'),
        (('未', '子'), '子未相害'),
        (('丑', '午'), '丑午相害'),
        (('午', '丑'), '丑午相害'),
        (('寅', '巳'), '寅巳相害'),
        (('巳', '寅'), '寅巳相害'),
        (('卯', '辰'), '卯辰相害'),
        (('辰', '卯'), '卯辰相害'),
        (('申', '亥'), '申亥相害'),
        (('亥', '申'), '申亥相害'),
        (('酉', '戌'), '酉戌相害'),
        (('戌', '酉'), '酉戌相害'),
    ]

    PILLAR_NAMES = ['年支', '月支', '日支', '時支']

    def _analyze_dizhi_interactions(self, all_zhi: List[str]) -> Dict:
        """
        分析四柱地支間的合沖刑害（v2.2 新增）

        Args:
            all_zhi: [年支, 月支, 日支, 時支]

        Returns:
            {"六合": [...], "六沖": [...], "三合": [...], "三刑": [...], "六害": [...]}
        """
        results = {"六合": [], "六沖": [], "三合": [], "三刑": [], "六害": []}

        # 所有兩兩組合
        pairs = []
        for i in range(len(all_zhi)):
            for j in range(i + 1, len(all_zhi)):
                pairs.append((i, j))

        # 六合
        for i, j in pairs:
            key = (all_zhi[i], all_zhi[j])
            if key in self.LIUHE:
                results["六合"].append(
                    f"{self.PILLAR_NAMES[i]}{all_zhi[i]}與{self.PILLAR_NAMES[j]}{all_zhi[j]}合化{self.LIUHE[key]}"
                )

        # 六沖
        for i, j in pairs:
            if (all_zhi[i], all_zhi[j]) in self.LIUCHONG:
                results["六沖"].append(
                    f"{self.PILLAR_NAMES[i]}{all_zhi[i]}沖{self.PILLAR_NAMES[j]}{all_zhi[j]}"
                )

        # 三合
        zhi_set = set(all_zhi)
        for combo, ju_name in self.SANHE.items():
            matches = [z for z in combo if z in zhi_set]
            if len(matches) >= 2:
                # 半合也列出
                if len(matches) == 3:
                    results["三合"].append(f"{''.join(matches)}三合{ju_name}")
                else:
                    results["三合"].append(f"{''.join(matches)}半合{ju_name}")

        # 三刑
        for i, j in pairs:
            for (a, b), desc in self.SANXING:
                if all_zhi[i] == a and all_zhi[j] == b:
                    results["三刑"].append(
                        f"{self.PILLAR_NAMES[i]}{all_zhi[i]}刑{self.PILLAR_NAMES[j]}{all_zhi[j]}（{desc}）"
                    )

        # 自刑
        from collections import Counter
        zhi_count = Counter(all_zhi)
        for z, cnt in zhi_count.items():
            if cnt >= 2 and (z, z) in [(a, b) for (a, b), d in self.SANXING if d == '自刑']:
                results["三刑"].append(f"{z}自刑（見{cnt}次）")

        # 六害
        for i, j in pairs:
            for (a, b), desc in self.LIUHAI:
                if all_zhi[i] == a and all_zhi[j] == b:
                    results["六害"].append(
                        f"{self.PILLAR_NAMES[i]}{all_zhi[i]}害{self.PILLAR_NAMES[j]}{all_zhi[j]}（{desc}）"
                    )

        return results

    # ===== v2.2: 格局分析 =====

    def _analyze_pattern(self, day_master: str, strength: Dict,
                         all_gan: List[str], all_zhi: List[str],
                         month_zhi: str) -> Dict:
        """
        分析八字格局（v2.2 新增）

        八大正格判定（以月支透干為主）：
        正官格、偏官格(七殺格)、正印格、偏印格、
        正財格、偏財格、食神格、傷官格

        特殊格局：
        建祿格、月刃格（羊刃格）

        Args:
            day_master: 日干
            strength: 強弱分析結果
            all_gan: [年干, 月干, 日干, 時干]
            all_zhi: [年支, 月支, 日支, 時支]
            month_zhi: 月支

        Returns:
            {"格局名稱": "...", "判定依據": "...", "格局特點": "..."}
        """
        day_wuxing = self.WUXING[day_master]

        # 月支藏干（取得本氣、中氣、餘氣）
        month_canggan = self.CANGGAN[month_zhi]

        # 檢查月支藏干是否透出天干（年、月、時干）
        transparent_gan = [all_gan[0], all_gan[1], all_gan[3]]  # 年月時干

        # 取月令本氣的十神
        month_benqi = month_canggan[0]
        benqi_relation = self._get_shishen_relation(day_master, month_benqi)

        # 先檢查特殊格局
        # 建祿格：月支為日主的祿位
        lu_map = {'甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
                  '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
                  '壬': '亥', '癸': '子'}
        # 羊刃：月支為日主的刃位
        ren_map = {'甲': '卯', '乙': '寅', '丙': '午', '丁': '巳',
                   '戊': '午', '己': '巳', '庚': '酉', '辛': '申',
                   '壬': '子', '癸': '亥'}

        if month_zhi == lu_map.get(day_master):
            return {
                "格局名稱": "建祿格",
                "判定依據": f"月支{month_zhi}為日主{day_master}之祿位",
                "格局特點": "日主在月令得祿，先天根基穩固，宜看透干何神決定用神方向"
            }

        if month_zhi == ren_map.get(day_master):
            return {
                "格局名稱": "月刃格（羊刃格）",
                "判定依據": f"月支{month_zhi}為日主{day_master}之刃位",
                "格局特點": "日主得刃，身旺性剛，宜見官殺制刃，忌再見比劫助旺"
            }

        # 八大正格：月支藏干透出為準
        detected = None
        for cg in month_canggan:
            if cg == day_master:
                continue  # 比肩不成格
            if cg in transparent_gan:
                ss = self._get_shishen_relation(day_master, cg)
                detected = (ss, cg)
                break

        # 若無透干，以月支本氣定格
        if not detected and month_benqi != day_master:
            detected = (benqi_relation, month_benqi)

        if detected:
            ss, gan = detected
            pattern_names = {
                '正官': ('正官格', '性情端正，重視規範，適合體制內發展，宜配財印'),
                '七杀': ('七殺格（偏官格）', '魄力十足，敢闖敢拼，適合開創性事業，宜食制或印化'),
                '正印': ('正印格', '重視學識修養，心性仁慈，適合學術教育領域'),
                '偏印': ('偏印格（梟神格）', '思維獨特，具研究精神，需留意偏印奪食'),
                '正财': ('正財格', '踏實穩健，理財有方，適合穩定性的財務工作'),
                '偏财': ('偏財格', '交際廣闊，善抓機會，適合商貿流通領域'),
                '食神': ('食神格', '性情溫和，才藝出眾，適合文藝或服務業'),
                '伤官': ('傷官格', '聰明伶俐，不拘一格，適合技藝創新領域，需注意人際'),
            }
            # 統一十神名稱（簡體→繁體映射）
            ss_normalized = ss.replace('杀', '殺').replace('财', '財').replace('伤', '傷')
            found = pattern_names.get(ss) or pattern_names.get(ss_normalized)
            if found:
                return {
                    "格局名稱": found[0],
                    "判定依據": f"月支{month_zhi}藏{gan}透出，{gan}與日主{day_master}為{ss}關係",
                    "格局特點": found[1]
                }

        # 兜底
        return {
            "格局名稱": f"雜氣格（以{benqi_relation}取用）",
            "判定依據": f"月支{month_zhi}本氣{month_benqi}為{benqi_relation}，未明確透干成格",
            "格局特點": "需綜合全局天干地支配合判定用神方向"
        }

    def _get_nayin(self, gan: str, zhi: str) -> str:
        """获取纳音五行"""
        nayin_map = {
            ('甲', '子'): '海中金', ('乙', '丑'): '海中金',
            ('丙', '寅'): '炉中火', ('丁', '卯'): '炉中火',
            ('戊', '辰'): '大林木', ('己', '巳'): '大林木',
            ('庚', '午'): '路旁土', ('辛', '未'): '路旁土',
            ('壬', '申'): '剑锋金', ('癸', '酉'): '剑锋金',
            ('甲', '戌'): '山头火', ('乙', '亥'): '山头火',
            ('丙', '子'): '涧下水', ('丁', '丑'): '涧下水',
            ('戊', '寅'): '城头土', ('己', '卯'): '城头土',
            ('庚', '辰'): '白蜡金', ('辛', '巳'): '白蜡金',
            ('壬', '午'): '杨柳木', ('癸', '未'): '杨柳木',
            ('甲', '申'): '泉中水', ('乙', '酉'): '泉中水',
            ('丙', '戌'): '屋上土', ('丁', '亥'): '屋上土',
            ('戊', '子'): '霹雳火', ('己', '丑'): '霹雳火',
            ('庚', '寅'): '松柏木', ('辛', '卯'): '松柏木',
            ('壬', '辰'): '长流水', ('癸', '巳'): '长流水',
            ('甲', '午'): '砂中金', ('乙', '未'): '砂中金',
            ('丙', '申'): '山下火', ('丁', '酉'): '山下火',
            ('戊', '戌'): '平地木', ('己', '亥'): '平地木',
            ('庚', '子'): '壁上土', ('辛', '丑'): '壁上土',
            ('壬', '寅'): '金箔金', ('癸', '卯'): '金箔金',
            ('甲', '辰'): '覆灯火', ('乙', '巳'): '覆灯火',
            ('丙', '午'): '天河水', ('丁', '未'): '天河水',
            ('戊', '申'): '大驿土', ('己', '酉'): '大驿土',
            ('庚', '戌'): '钗钏金', ('辛', '亥'): '钗钏金',
            ('壬', '子'): '桑柘木', ('癸', '丑'): '桑柘木',
            ('甲', '寅'): '大溪水', ('乙', '卯'): '大溪水',
            ('丙', '辰'): '沙中土', ('丁', '巳'): '沙中土',
            ('戊', '午'): '天上火', ('己', '未'): '天上火',
            ('庚', '申'): '石榴木', ('辛', '酉'): '石榴木',
            ('壬', '戌'): '大海水', ('癸', '亥'): '大海水'
        }
        
        return nayin_map.get((gan, zhi), '未知')


# 测试代码
if __name__ == "__main__":
    calculator = BaziCalculator()
    
    # 测试案例：1979年10月11日 23:58（对应农历68年9月23日）
    result = calculator.calculate_bazi(
        year=1979,
        month=10,
        day=11,
        hour=23,
        minute=58,
        gender="男",
        longitude=120.52,  # 彰化市经度
        use_apparent_solar_time=True
    )
    
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
