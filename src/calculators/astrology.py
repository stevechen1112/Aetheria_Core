"""
西洋占星術計算引擎
使用 Kerykeion (基於 Swiss Ephemeris GPL v2)
"""

import os

# 避免 kerykeion 在未設定時輸出警告
if not os.getenv("GEONAMES_USERNAME"):
    os.environ["GEONAMES_USERNAME"] = "demo"

from kerykeion import AstrologicalSubject
from datetime import datetime
import pytz
from typing import Dict, Any, List, Tuple, Optional

from src.utils.geonames_cache import get_geonames_cache
from src.utils.logger import get_logger

logger = get_logger()


class AstrologyCalculator:
    """西洋占星術計算器"""
    
    # 行星中文名稱對照
    PLANET_NAMES_ZH = {
        'Sun': '太陽',
        'Moon': '月亮',
        'Mercury': '水星',
        'Venus': '金星',
        'Mars': '火星',
        'Jupiter': '木星',
        'Saturn': '土星',
        'Uranus': '天王星',
        'Neptune': '海王星',
        'Pluto': '冥王星'
    }
    
    # 星座中文名稱對照
    SIGN_NAMES_ZH = {
        'Ari': '白羊座',
        'Tau': '金牛座',
        'Gem': '雙子座',
        'Can': '巨蟹座',
        'Leo': '獅子座',
        'Vir': '處女座',
        'Lib': '天秤座',
        'Sco': '天蠍座',
        'Sag': '射手座',
        'Cap': '摩羯座',
        'Aqu': '水瓶座',
        'Pis': '雙魚座'
    }
    
    # 宮位中文名稱
    HOUSE_NAMES_ZH = {
        'First_House': '第一宮（命宮）',
        'Second_House': '第二宮（財帛宮）',
        'Third_House': '第三宮（兄弟宮）',
        'Fourth_House': '第四宮（田宅宮）',
        'Fifth_House': '第五宮（子女宮）',
        'Sixth_House': '第六宮（奴僕宮）',
        'Seventh_House': '第七宮（夫妻宮）',
        'Eighth_House': '第八宮（疾厄宮）',
        'Ninth_House': '第九宮（遷移宮）',
        'Tenth_House': '第十宮（官祿宮）',
        'Eleventh_House': '第十一宮（福德宮）',
        'Twelfth_House': '第十二宮（玄秘宮）'
    }
    
    # 相位中文名稱
    ASPECT_NAMES_ZH = {
        'conjunction': '合相（0°）',
        'opposition': '對分相（180°）',
        'trine': '三分相（120°）',
        'square': '四分相（90°）',
        'sextile': '六分相（60°）',
        'quincunx': '補十二分相（150°）',
        'semi_sextile': '半六分相（30°）'
    }
    
    def __init__(self):
        """初始化"""
        pass

    # ===== v2.2: 行星廟旺落陷 (Essential Dignity) =====
    # 格式：{sign_abbr: {planet_key: dignity_level}}
    # 層級：Domicile(入廟) > Exaltation(旺) > Detriment(落) > Fall(陷)
    DIGNITY_TABLE = {
        'Ari': {'mars': 'Domicile', 'sun': 'Exaltation', 'venus': 'Detriment', 'saturn': 'Fall'},
        'Tau': {'venus': 'Domicile', 'moon': 'Exaltation', 'mars': 'Detriment', 'uranus': 'Fall'},
        'Gem': {'mercury': 'Domicile', 'jupiter': 'Detriment'},
        'Can': {'moon': 'Domicile', 'jupiter': 'Exaltation', 'saturn': 'Detriment', 'mars': 'Fall'},
        'Leo': {'sun': 'Domicile', 'saturn': 'Detriment', 'uranus': 'Detriment'},
        'Vir': {'mercury': 'Domicile+Exaltation', 'jupiter': 'Detriment', 'venus': 'Fall', 'neptune': 'Detriment'},
        'Lib': {'venus': 'Domicile', 'saturn': 'Exaltation', 'mars': 'Detriment', 'sun': 'Fall'},
        'Sco': {'mars': 'Domicile', 'pluto': 'Domicile', 'venus': 'Detriment', 'moon': 'Fall'},
        'Sag': {'jupiter': 'Domicile', 'mercury': 'Detriment'},
        'Cap': {'saturn': 'Domicile', 'mars': 'Exaltation', 'moon': 'Detriment', 'jupiter': 'Fall'},
        'Aqu': {'saturn': 'Domicile', 'uranus': 'Domicile', 'sun': 'Detriment'},
        'Pis': {'jupiter': 'Domicile', 'neptune': 'Domicile', 'venus': 'Exaltation', 'mercury': 'Detriment+Fall'},
    }

    DIGNITY_ZH = {
        'Domicile': '入廟（守護）',
        'Exaltation': '旺（擢升）',
        'Detriment': '落（不利）',
        'Fall': '陷（衰弱）',
    }

    def _get_planet_dignity(self, planet_key: str, sign_abbr: str) -> Optional[str]:
        """
        查詢行星在特定星座的 Essential Dignity（v2.2 新增，v2.3 支援複合 dignity）

        Args:
            planet_key: 行星鍵（如 'sun', 'moon', 'mars'）
            sign_abbr: 星座縮寫（如 'Ari', 'Leo'）

        Returns:
            Dignity 描述或 None
        """
        sign_data = self.DIGNITY_TABLE.get(sign_abbr, {})
        dignity = sign_data.get(planet_key)
        if dignity:
            # v2.3: 支援複合格式如 'Domicile+Exaltation'
            if '+' in dignity:
                parts = [self.DIGNITY_ZH.get(d.strip(), d.strip()) for d in dignity.split('+')]
                return '／'.join(parts)
            return self.DIGNITY_ZH.get(dignity, dignity)
        return None
    
    def calculate_natal_chart(
        self,
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        city: str = "Taipei",
        nation: str = "TW",
        longitude: float = None,
        latitude: float = None,
        timezone_str: str = "Asia/Taipei"
    ) -> Dict[str, Any]:
        """
        計算本命盤
        
        Args:
            name: 姓名
            year: 出生年
            month: 出生月
            day: 出生日
            hour: 出生時（24小時制）
            minute: 出生分
            city: 城市名稱
            nation: 國家代碼
            longitude: 經度（東經為正）
            latitude: 緯度（北緯為正）
            timezone_str: 時區字串
            
        Returns:
            完整的本命盤數據
        """
        
        # 如果沒有提供經緯度，從緩存或 GeoNames 獲取
        geonames_username = os.getenv("GEONAMES_USERNAME", "demo")
        cached_location = None
        
        if longitude is None or latitude is None:
            # 先查詢緩存
            cache = get_geonames_cache()
            cached_location = cache.get(city, nation)
            
            if cached_location:
                # 使用緩存的經緯度
                logger.info(f"使用緩存的地理資訊: {city} ({nation or 'auto'})")
                subject = AstrologicalSubject(
                    name=name,
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    lng=cached_location['lng'],
                    lat=cached_location['lat'],
                    tz_str=cached_location['timezonestr'],
                    geonames_username=geonames_username
                )
            else:
                # 緩存未命中，查詢 GeoNames API
                logger.info(f"緩存未命中，查詢 GeoNames API: {city} ({nation or 'auto'})")
                subject = AstrologicalSubject(
                    name=name,
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    city=city,
                    nation=nation,
                    tz_str=timezone_str,
                    geonames_username=geonames_username
                )
                
                # 查詢成功後儲存到緩存
                try:
                    if hasattr(subject, 'lat') and hasattr(subject, 'lng'):
                        cache.set(
                            city=city,
                            nation=nation,
                            latitude=subject.lat,
                            longitude=subject.lng,
                            timezone=subject.tz,
                            country_code=getattr(subject, 'nation', None)
                        )
                        logger.info(f"GeoNames 查詢結果已緩存: {city}")
                except Exception as e:
                    logger.warning(f"緩存 GeoNames 結果失敗: {e}")
        else:
            subject = AstrologicalSubject(
                name=name,
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                lng=longitude,
                lat=latitude,
                tz_str=timezone_str,
                geonames_username=geonames_username
            )
        
        # 提取行星位置
        planets = self._extract_planets(subject)
        
        # 提取宮位
        houses = self._extract_houses(subject)
        
        # 提取相位
        aspects = self._extract_aspects(subject)
        
        # 組裝完整數據
        natal_chart = {
            'basic_info': {
                'name': name,
                'birth_date': f"{year}-{month:02d}-{day:02d}",
                'birth_time': f"{hour:02d}:{minute:02d}",
                'location': city,
                'longitude': subject.lng,
                'latitude': subject.lat,
                'timezone': timezone_str
            },
            'planets': planets,
            'houses': houses,
            'aspects': aspects,
            'elements': self._calculate_elements(planets),
            'qualities': self._calculate_qualities(planets),
            'dominant_element': self._get_dominant_element(planets),
            'dominant_quality': self._get_dominant_quality(planets),
            'chart_ruler': self._get_chart_ruler(houses, planets)
        }
        
        # v2.3: 自動偵測相位組型
        natal_chart['aspect_patterns'] = self._detect_aspect_patterns(aspects, planets)
        
        return natal_chart
    
    def _extract_planets(self, subject: AstrologicalSubject) -> Dict[str, Any]:
        """提取行星位置資訊"""
        planets = {}
        
        planet_attrs = [
            'sun', 'moon', 'mercury', 'venus', 'mars',
            'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'
        ]
        
        for planet_attr in planet_attrs:
            planet_data = getattr(subject, planet_attr, None)
            if planet_data:
                planet_name = planet_attr.capitalize()
                planet_name_zh = self.PLANET_NAMES_ZH.get(planet_name, planet_name)
                
                # 獲取星座縮寫（例如 "Ari"）
                sign_abbr = planet_data.get('sign', '')
                sign_name_zh = self.SIGN_NAMES_ZH.get(sign_abbr, sign_abbr)
                
                planets[planet_attr] = {
                    'name': planet_name,
                    'name_zh': planet_name_zh,
                    'sign': sign_abbr,
                    'sign_zh': sign_name_zh,
                    'degree': planet_data.get('abs_pos', 0) % 30,  # 星座內度數
                    'longitude': planet_data.get('abs_pos', 0),    # 黃道經度
                    'latitude': planet_data.get('lat', 0),
                    'house': planet_data.get('house', ''),
                    'retrograde': planet_data.get('retrograde', False),
                    'dignity': self._get_planet_dignity(planet_attr, sign_abbr),  # v2.2
                }
        
        # 添加上升點和天頂
        if hasattr(subject, 'first_house'):
            first_house = subject.first_house
            sign_abbr = first_house.get('sign', '')
            planets['ascendant'] = {
                'name': 'Ascendant',
                'name_zh': '上升點',
                'sign': sign_abbr,
                'sign_zh': self.SIGN_NAMES_ZH.get(sign_abbr, sign_abbr),
                'degree': first_house.get('abs_pos', 0) % 30,
                'longitude': first_house.get('abs_pos', 0),
                'latitude': 0,
                'house': '1',
                'retrograde': False
            }
        
        if hasattr(subject, 'tenth_house'):
            tenth_house = subject.tenth_house
            sign_abbr = tenth_house.get('sign', '')
            planets['midheaven'] = {
                'name': 'Midheaven',
                'name_zh': '天頂',
                'sign': sign_abbr,
                'sign_zh': self.SIGN_NAMES_ZH.get(sign_abbr, sign_abbr),
                'degree': tenth_house.get('abs_pos', 0) % 30,
                'longitude': tenth_house.get('abs_pos', 0),
                'latitude': 0,
                'house': '10',
                'retrograde': False
            }
        
        return planets
    
    def _extract_houses(self, subject: AstrologicalSubject) -> Dict[str, Any]:
        """提取宮位資訊"""
        houses = {}
        
        house_attrs = [
            'first_house', 'second_house', 'third_house', 'fourth_house',
            'fifth_house', 'sixth_house', 'seventh_house', 'eighth_house',
            'ninth_house', 'tenth_house', 'eleventh_house', 'twelfth_house'
        ]
        
        for i, house_attr in enumerate(house_attrs, 1):
            house_data = getattr(subject, house_attr, None)
            if house_data:
                sign_abbr = house_data.get('sign', '')
                houses[f'house_{i}'] = {
                    'number': i,
                    'name_zh': self.HOUSE_NAMES_ZH.get(house_attr.replace('_', ' ').title().replace(' ', '_'), f'第{i}宮'),
                    'sign': sign_abbr,
                    'sign_zh': self.SIGN_NAMES_ZH.get(sign_abbr, sign_abbr),
                    'degree': house_data.get('abs_pos', 0) % 30,
                    'longitude': house_data.get('abs_pos', 0)
                }
        
        return houses
    
    def _extract_aspects(self, subject: AstrologicalSubject) -> List[Dict[str, Any]]:
        """提取相位資訊"""
        aspects = []
        
        # Kerykeion 的相位資料在 aspects_list 屬性中
        if hasattr(subject, 'aspects_list'):
            for aspect in subject.aspects_list:
                aspect_type = aspect.get('aspect', '')
                aspects.append({
                    'planet1': aspect.get('p1_name', ''),
                    'planet1_zh': self.PLANET_NAMES_ZH.get(aspect.get('p1_name', ''), aspect.get('p1_name', '')),
                    'planet2': aspect.get('p2_name', ''),
                    'planet2_zh': self.PLANET_NAMES_ZH.get(aspect.get('p2_name', ''), aspect.get('p2_name', '')),
                    'aspect': aspect_type,
                    'aspect_zh': self.ASPECT_NAMES_ZH.get(aspect_type.lower(), aspect_type),
                    'angle': aspect.get('orbit', 0),
                    'orb': abs(aspect.get('orbit', 0))
                })
        
        return aspects
    
    # ===== v2.3: 相位組型自動偵測 =====

    def _detect_aspect_patterns(self, aspects: List[Dict], planets: Dict) -> List[Dict]:
        """
        自動偵測星盤中的特殊相位組型（v2.3 新增）。
        
        偵測的組型：
        - T-Square（T三角）：三顆行星 A-B 衝(180°) + A-C 刑(90°) + B-C 刑(90°)
        - Grand Trine（大三角）：三顆行星兩兩拱(120°)
        - Grand Cross（大十字）：四顆行星形成兩組衝 + 四組刑
        
        Returns:
            [{"type": "T-Square", "type_zh": "T三角", "planets": ["火星", "土星", "月亮"], "description": "..."}]
        """
        patterns = []
        
        # Build adjacency: {(p1, p2): aspect_type}
        aspect_map = {}
        for a in aspects:
            p1 = a.get('planet1', '')
            p2 = a.get('planet2', '')
            atype = a.get('aspect', '').lower()
            if p1 and p2 and atype:
                aspect_map[(p1, p2)] = atype
                aspect_map[(p2, p1)] = atype
        
        # Get unique planet names involved in aspects
        planet_names = set()
        for a in aspects:
            planet_names.add(a.get('planet1', ''))
            planet_names.add(a.get('planet2', ''))
        planet_names.discard('')
        planet_list = sorted(planet_names)
        
        def _zh(name):
            return self.PLANET_NAMES_ZH.get(name, name)
        
        def _has_aspect(p1, p2, atype):
            return aspect_map.get((p1, p2), '') == atype
        
        # --- T-Square detection ---
        for i, a_planet in enumerate(planet_list):
            for j, b_planet in enumerate(planet_list):
                if j <= i:
                    continue
                if not _has_aspect(a_planet, b_planet, 'opposition'):
                    continue
                for c_planet in planet_list:
                    if c_planet in (a_planet, b_planet):
                        continue
                    if _has_aspect(a_planet, c_planet, 'square') and _has_aspect(b_planet, c_planet, 'square'):
                        trio = tuple(sorted([a_planet, b_planet, c_planet]))
                        entry = {
                            "type": "T-Square",
                            "type_zh": "T三角（T-Square）",
                            "planets": [_zh(a_planet), _zh(b_planet), _zh(c_planet)],
                            "planets_en": list(trio),
                            "description": f"{_zh(a_planet)}與{_zh(b_planet)}對衝(180°)，{_zh(c_planet)}同時刑克(90°)兩者，形成強烈的驅動力與內在張力。{_zh(c_planet)}是此T三角的頂點行星，代表壓力的宣洩口。"
                        }
                        if not any(set(p.get('planets_en', [])) == set(trio) and p['type'] == 'T-Square' for p in patterns):
                            patterns.append(entry)
        
        # --- Grand Trine detection ---
        for i, a_planet in enumerate(planet_list):
            for j, b_planet in enumerate(planet_list):
                if j <= i:
                    continue
                if not _has_aspect(a_planet, b_planet, 'trine'):
                    continue
                for k, c_planet in enumerate(planet_list):
                    if k <= j:
                        continue
                    if _has_aspect(a_planet, c_planet, 'trine') and _has_aspect(b_planet, c_planet, 'trine'):
                        trio = tuple(sorted([a_planet, b_planet, c_planet]))
                        # Determine element
                        signs = []
                        for p_name in trio:
                            p_data = planets.get(p_name.lower(), {})
                            signs.append(p_data.get('sign', ''))
                        element_map = {
                            'Ari': '火', 'Leo': '火', 'Sag': '火',
                            'Tau': '土', 'Vir': '土', 'Cap': '土',
                            'Gem': '風', 'Lib': '風', 'Aqu': '風',
                            'Can': '水', 'Sco': '水', 'Pis': '水'
                        }
                        elems = [element_map.get(s, '') for s in signs]
                        elem_str = elems[0] if elems[0] and all(e == elems[0] for e in elems) else '混合'
                        
                        entry = {
                            "type": "Grand Trine",
                            "type_zh": f"大三角（Grand Trine）— {elem_str}象",
                            "planets": [_zh(a_planet), _zh(b_planet), _zh(c_planet)],
                            "planets_en": list(trio),
                            "description": f"{_zh(a_planet)}、{_zh(b_planet)}、{_zh(c_planet)}兩兩形成拱相(120°)，構成{elem_str}象大三角。代表天賦才能的和諧流動，但也可能因過於安逸而缺乏成長動力。"
                        }
                        if not any(set(p.get('planets_en', [])) == set(trio) and p['type'] == 'Grand Trine' for p in patterns):
                            patterns.append(entry)
        
        # --- Grand Cross detection ---
        for i, a_planet in enumerate(planet_list):
            for j, b_planet in enumerate(planet_list):
                if j <= i:
                    continue
                if not _has_aspect(a_planet, b_planet, 'opposition'):
                    continue
                for k, c_planet in enumerate(planet_list):
                    if k <= i or c_planet in (a_planet, b_planet):
                        continue
                    for l_idx, d_planet in enumerate(planet_list):
                        if l_idx <= k or d_planet in (a_planet, b_planet, c_planet):
                            continue
                        if not _has_aspect(c_planet, d_planet, 'opposition'):
                            continue
                        squares = sum([
                            _has_aspect(a_planet, c_planet, 'square'),
                            _has_aspect(a_planet, d_planet, 'square'),
                            _has_aspect(b_planet, c_planet, 'square'),
                            _has_aspect(b_planet, d_planet, 'square')
                        ])
                        if squares >= 3:
                            quad = tuple(sorted([a_planet, b_planet, c_planet, d_planet]))
                            entry = {
                                "type": "Grand Cross",
                                "type_zh": "大十字（Grand Cross）",
                                "planets": [_zh(a_planet), _zh(b_planet), _zh(c_planet), _zh(d_planet)],
                                "planets_en": list(quad),
                                "description": f"{_zh(a_planet)}、{_zh(b_planet)}、{_zh(c_planet)}、{_zh(d_planet)}形成大十字格局，兩組對衝加四組刑克，代表極大的內在張力與轉化潛能。"
                            }
                            if not any(set(p.get('planets_en', [])) == set(quad) and p['type'] == 'Grand Cross' for p in patterns):
                                patterns.append(entry)
        
        return patterns

    def _calculate_elements(self, planets: Dict[str, Any]) -> Dict[str, int]:
        """計算四元素分佈"""
        elements = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
        
        element_map = {
            'Ari': 'Fire', 'Leo': 'Fire', 'Sag': 'Fire',
            'Tau': 'Earth', 'Vir': 'Earth', 'Cap': 'Earth',
            'Gem': 'Air', 'Lib': 'Air', 'Aqu': 'Air',
            'Can': 'Water', 'Sco': 'Water', 'Pis': 'Water'
        }
        
        # 主要行星（不含上升和天頂）
        for planet_key, planet_data in planets.items():
            if planet_key not in ['ascendant', 'midheaven']:
                sign = planet_data.get('sign', '')
                element = element_map.get(sign, '')
                if element:
                    elements[element] += 1
        
        return elements
    
    def _calculate_qualities(self, planets: Dict[str, Any]) -> Dict[str, int]:
        """計算三態分佈"""
        qualities = {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}
        
        quality_map = {
            'Ari': 'Cardinal', 'Can': 'Cardinal', 'Lib': 'Cardinal', 'Cap': 'Cardinal',
            'Tau': 'Fixed', 'Leo': 'Fixed', 'Sco': 'Fixed', 'Aqu': 'Fixed',
            'Gem': 'Mutable', 'Vir': 'Mutable', 'Sag': 'Mutable', 'Pis': 'Mutable'
        }
        
        for planet_key, planet_data in planets.items():
            if planet_key not in ['ascendant', 'midheaven']:
                sign = planet_data.get('sign', '')
                quality = quality_map.get(sign, '')
                if quality:
                    qualities[quality] += 1
        
        return qualities
    
    def _get_dominant_element(self, planets: Dict[str, Any]) -> str:
        """獲取主導元素"""
        elements = self._calculate_elements(planets)
        dominant = max(elements.items(), key=lambda x: x[1])
        
        element_zh = {
            'Fire': '火',
            'Earth': '土',
            'Air': '風',
            'Water': '水'
        }
        
        return f"{element_zh.get(dominant[0], dominant[0])}（{dominant[1]}顆行星）"
    
    def _get_dominant_quality(self, planets: Dict[str, Any]) -> str:
        """獲取主導型態"""
        qualities = self._calculate_qualities(planets)
        dominant = max(qualities.items(), key=lambda x: x[1])
        
        quality_zh = {
            'Cardinal': '開創',
            'Fixed': '固定',
            'Mutable': '變動'
        }
        
        return f"{quality_zh.get(dominant[0], dominant[0])}（{dominant[1]}顆行星）"
    
    def _get_chart_ruler(self, houses: Dict[str, Any], planets: Dict[str, Any]) -> str:
        """獲取命主星"""
        # 命主星是上升星座的守護星
        if 'house_1' not in houses:
            return "未知"
        
        asc_sign = houses['house_1']['sign']
        
        ruler_map = {
            'Ari': '火星', 'Tau': '金星', 'Gem': '水星',
            'Can': '月亮', 'Leo': '太陽', 'Vir': '水星',
            'Lib': '金星', 'Sco': '冥王星', 'Sag': '木星',
            'Cap': '土星', 'Aqu': '天王星', 'Pis': '海王星'
        }
        
        return ruler_map.get(asc_sign, "未知")
    
    def calculate_transit(self, natal_chart: Dict[str, Any],
                          target_year: int = None,
                          target_month: int = None,
                          target_day: int = None) -> Dict[str, Any]:
        """
        計算行運（Transit）相位（v2.1 新增）
        
        使用 Kerykeion 的 SynastryAspects 計算行運行星與本命行星的相位。
        Transit chart 是指定日期的天體位置，與 natal chart 做交叉相位比對。
        
        Args:
            natal_chart: calculate_natal_chart() 的返回值
            target_year: 行運年份（預設今年）
            target_month: 行運月份（預設當月）
            target_day: 行運日期（預設今天）
            
        Returns:
            {
                'transit_date': '2026-01-25',
                'transit_planets': {...},
                'aspects': [...],
                'summary_text': '...'
            }
        """
        try:
            from kerykeion import SynastryAspects
        except ImportError:
            logger.warning("SynastryAspects 無法匯入，行運計算不可用")
            return {'error': 'SynastryAspects 不可用', 'aspects': []}
        
        now = datetime.now()
        year = target_year or now.year
        month = target_month or now.month
        day = target_day or now.day
        
        # 取得本命盤的基本參數
        birth_info = natal_chart.get('birth_info', {})
        lat = birth_info.get('latitude', 24.08)
        lon = birth_info.get('longitude', 120.52)
        tz = birth_info.get('timezone', 'Asia/Taipei')
        
        # 建立本命盤 subject
        natal_subject = AstrologicalSubject(
            name=birth_info.get('name', 'User'),
            year=birth_info.get('year', 1979),
            month=birth_info.get('month', 1),
            day=birth_info.get('day', 1),
            hour=birth_info.get('hour', 0),
            minute=birth_info.get('minute', 0),
            lat=lat, lng=lon,
            tz_str=tz,
            geonames_username=os.environ.get("GEONAMES_USERNAME", "demo")
        )
        
        # 建立 Transit subject（指定日期正午 12:00）
        transit_subject = AstrologicalSubject(
            name="Transit",
            year=year, month=month, day=day,
            hour=12, minute=0,
            lat=lat, lng=lon,
            tz_str=tz,
            geonames_username=os.environ.get("GEONAMES_USERNAME", "demo")
        )
        
        # 計算交叉相位
        try:
            synastry = SynastryAspects(natal_subject, transit_subject)
            raw_aspects = synastry.all_aspects
        except Exception as e:
            logger.error(f"行運相位計算失敗: {e}")
            return {'error': str(e), 'aspects': []}
        
        # 提取 Transit 行星位置
        transit_planets = self._extract_planets(transit_subject)
        
        # 格式化相位
        aspects = []
        for asp in raw_aspects:
            try:
                natal_planet = asp.get('p1_name', '') if isinstance(asp, dict) else getattr(asp, 'p1_name', '')
                transit_planet = asp.get('p2_name', '') if isinstance(asp, dict) else getattr(asp, 'p2_name', '')
                aspect_type = asp.get('aspect', '') if isinstance(asp, dict) else getattr(asp, 'aspect', '')
                orbit = asp.get('orbit', 0) if isinstance(asp, dict) else getattr(asp, 'orbit', 0)
                
                # 只保留主要行星的相位
                main_planets = {'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                               'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'}
                if natal_planet not in main_planets or transit_planet not in main_planets:
                    continue
                
                natal_zh = self.PLANET_NAMES_ZH.get(natal_planet, natal_planet)
                transit_zh = self.PLANET_NAMES_ZH.get(transit_planet, transit_planet)
                
                aspect_zh_map = {
                    'conjunction': '合相 (0°)',
                    'opposition': '對相 (180°)',
                    'trine': '三分相 (120°)',
                    'square': '四分相 (90°)',
                    'sextile': '六分相 (60°)'
                }
                aspect_zh = aspect_zh_map.get(str(aspect_type).lower(), str(aspect_type))
                
                aspects.append({
                    'natal_planet': natal_planet,
                    'natal_planet_zh': natal_zh,
                    'transit_planet': transit_planet,
                    'transit_planet_zh': transit_zh,
                    'aspect': str(aspect_type),
                    'aspect_zh': aspect_zh,
                    'orbit': round(float(orbit), 2) if orbit else 0
                })
            except Exception:
                continue
        
        # 生成摘要文本
        summary_lines = [f"【行運分析】{year}/{month}/{day}"]
        for a in aspects[:15]:  # 最多 15 條
            summary_lines.append(
                f"  行運{a['transit_planet_zh']} {a['aspect_zh']} 本命{a['natal_planet_zh']}（容許度 {a['orbit']}°）"
            )
        if not aspects:
            summary_lines.append("  當日無顯著行運相位")
        
        return {
            'transit_date': f"{year}-{month:02d}-{day:02d}",
            'transit_planets': transit_planets,
            'aspects': aspects,
            'summary_text': '\n'.join(summary_lines)
        }
    
    def format_for_gemini(self, natal_chart: Dict[str, Any]) -> str:
        """
        將本命盤數據格式化為適合 Gemini 分析的文本
        
        Args:
            natal_chart: 本命盤數據
            
        Returns:
            格式化的文本
        """
        basic = natal_chart['basic_info']
        planets = natal_chart['planets']
        houses = natal_chart['houses']
        aspects = natal_chart['aspects']
        
        output = []
        output.append("=" * 60)
        output.append(f"【本命盤】{basic['name']}")
        output.append("=" * 60)
        
        output.append(f"\n【基本資料】")
        output.append(f"出生日期：{basic['birth_date']}")
        output.append(f"出生時間：{basic['birth_time']}")
        output.append(f"出生地點：{basic['location']}")
        output.append(f"經緯度：{basic['longitude']:.2f}°E, {basic['latitude']:.2f}°N")
        
        output.append(f"\n【行星位置】")
        for planet_key, planet in planets.items():
            if planet_key not in ['ascendant', 'midheaven']:
                retro = " ℞" if planet.get('retrograde') else ""
                dignity = f" [{planet['dignity']}]" if planet.get('dignity') else ""
                output.append(
                    f"{planet['name_zh']:6s} | {planet['sign_zh']:6s} {planet['degree']:.2f}° "
                    f"| 第{planet.get('house', '?')}宮{retro}{dignity}"
                )
        
        # 上升和天頂
        if 'ascendant' in planets:
            asc = planets['ascendant']
            output.append(f"\n上升點：{asc['sign_zh']} {asc['degree']:.2f}°")
        
        if 'midheaven' in planets:
            mc = planets['midheaven']
            output.append(f"天頂：{mc['sign_zh']} {mc['degree']:.2f}°")
        
        output.append(f"\n【宮位】")
        for i in range(1, 13):
            house_key = f'house_{i}'
            if house_key in houses:
                house = houses[house_key]
                output.append(
                    f"第{i:2d}宮 | {house['sign_zh']:6s} {house['degree']:.2f}°"
                )
        
        output.append(f"\n【主要相位】")
        major_aspects = ['conjunction', 'opposition', 'trine', 'square', 'sextile']
        filtered_aspects = [a for a in aspects if a['aspect'].lower() in major_aspects]
        
        if filtered_aspects:
            for aspect in filtered_aspects[:15]:  # 最多顯示15個
                output.append(
                    f"{aspect['planet1_zh']:6s} {aspect['aspect_zh']:12s} {aspect['planet2_zh']:6s} "
                    f"(容許度: {aspect['orb']:.2f}°)"
                )
        else:
            output.append("無主要相位")
        
        # v2.3: 相位組型（T-Square / Grand Trine / Grand Cross）
        aspect_patterns = natal_chart.get('aspect_patterns', [])
        if aspect_patterns:
            output.append(f"\n【⚠ 特殊相位組型】")
            for pat in aspect_patterns:
                planets_str = '、'.join(pat.get('planets', []))
                output.append(f"★ {pat['type_zh']}：{planets_str}")
                output.append(f"  {pat['description']}")
        
        output.append(f"\n【元素分佈】")
        elements = natal_chart['elements']
        output.append(f"火: {elements['Fire']} | 土: {elements['Earth']} | 風: {elements['Air']} | 水: {elements['Water']}")
        output.append(f"主導元素：{natal_chart['dominant_element']}")
        
        output.append(f"\n【型態分佈】")
        qualities = natal_chart['qualities']
        output.append(f"開創: {qualities['Cardinal']} | 固定: {qualities['Fixed']} | 變動: {qualities['Mutable']}")
        output.append(f"主導型態：{natal_chart['dominant_quality']}")
        
        output.append(f"\n【命主星】")
        output.append(f"{natal_chart['chart_ruler']}")
        
        output.append("\n" + "=" * 60)
        
        return "\n".join(output)


if __name__ == '__main__':
    # 測試
    calc = AstrologyCalculator()
    
    # 使用 Steve 的資料測試
    chart = calc.calculate_natal_chart(
        name="Steve",
        year=1979,
        month=11,
        day=12,
        hour=23,
        minute=58,
        longitude=120.52,
        latitude=24.08,
        timezone_str="Asia/Taipei"
    )
    
    print(calc.format_for_gemini(chart))
