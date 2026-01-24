"""
八字排盘计算引擎
基于寿星天文历库（sxtwl）
"""

import sxtwl
from datetime import datetime
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
        
        # 计算大运
        dayun = self._calculate_dayun(year_gz, month_gz, gender, lunar_day)
        
        # 分析强弱
        strength_analysis = self._analyze_strength(
            day_master,
            [month_gz[1], day_gz[1], hour_gz[1]],
            lunar_day.getLunarMonth()
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
        获取时柱干支
        时辰划分：
        23-1: 子时, 1-3: 丑时, 3-5: 寅时, 5-7: 卯时
        7-9: 辰时, 9-11: 巳时, 11-13: 午时, 13-15: 未时
        15-17: 申时, 17-19: 酉时, 19-21: 戌时, 21-23: 亥时
        """
        # 使用 sxtwl 的 getShiGz 方法计算时柱
        day_gz = lunar_day.getDayGZ()
        gz = sxtwl.getShiGz(day_gz.dz, hour)
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
    
    def _calculate_dayun(self, year_gz: Tuple, month_gz: Tuple, gender: str, lunar_day) -> List[Dict]:
        """计算大运"""
        dayun_list = []
        
        # 判断顺逆（阳男阴女顺排，阴男阳女逆排）
        year_gan_idx = self.TIANGAN.index(year_gz[0])
        is_yang_year = year_gan_idx % 2 == 0
        is_male = gender == "男"
        
        shun_pai = (is_yang_year and is_male) or (not is_yang_year and not is_male)
        
        # 起运年龄计算（简化版，实际需要根据节气）
        start_age = 2
        
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
                "天干": dayun_gan,
                "地支": dayun_zhi,
                "纳音": self._get_nayin(dayun_gan, dayun_zhi)
            })
        
        return dayun_list

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
    
    def _analyze_strength(self, day_master: str, dizhi_list: List[str], month: int) -> Dict:
        """分析日主强弱"""
        day_wuxing = self.WUXING[day_master]
        
        # 月令（占50%权重）
        month_zhi = dizhi_list[0]
        
        # 简化判断：得令、得地、得势
        score = 0
        factors = []
        
        # 春季（木旺）、夏季（火旺）、秋季（金旺）、冬季（水旺）
        season_map = {
            1: "水", 2: "水", 3: "木", 4: "木", 5: "木",
            6: "火", 7: "火", 8: "土", 9: "金", 10: "金",
            11: "水", 12: "水"
        }
        
        # 使用农历月份
        lunar_month = month  # 这里应该使用传入的农历月份
        season_wuxing = season_map.get(lunar_month, "土")
        
        if day_wuxing == season_wuxing:
            score += 50
            factors.append(f"得月令（{season_wuxing}旺）")
        
        # 地支支持
        for zhi in dizhi_list:
            if self.WUXING[zhi] == day_wuxing:
                score += 10
                factors.append(f"得地支{zhi}支持")
        
        # 判断强弱
        if score >= 60:
            strength = "身旺"
        elif score >= 40:
            strength = "中和"
        else:
            strength = "身弱"
        
        return {
            "结论": strength,
            "评分": score,
            "因素": factors
        }
    
    def _analyze_yongshen(self, day_wuxing: str, strength: Dict) -> Dict:
        """分析用神"""
        strength_level = strength["结论"]
        
        # 简化用神判断
        wuxing_support = {
            "木": ["水", "木"],
            "火": ["木", "火"],
            "土": ["火", "土"],
            "金": ["土", "金"],
            "水": ["金", "水"]
        }
        
        wuxing_restrain = {
            "木": ["金", "土"],
            "火": ["水", "金"],
            "土": ["木", "水"],
            "金": ["火", "木"],
            "水": ["土", "火"]
        }
        
        if strength_level == "身旺":
            # 身旺喜克泄
            yongshen = wuxing_restrain[day_wuxing]
            xishen = []
            jishen = wuxing_support[day_wuxing]
        elif strength_level == "身弱":
            # 身弱喜生扶
            yongshen = wuxing_support[day_wuxing]
            xishen = []
            jishen = wuxing_restrain[day_wuxing]
        else:
            # 中和需具体分析
            yongshen = wuxing_support[day_wuxing][:1]
            xishen = wuxing_restrain[day_wuxing][:1]
            jishen = []
        
        return {
            "用神": yongshen,
            "喜神": xishen if xishen else yongshen,
            "忌神": jishen
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
