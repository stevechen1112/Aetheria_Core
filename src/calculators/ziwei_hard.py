from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    from iztro_py.astro import by_solar_hour
    from iztro_py.i18n.locales import zh_TW
except Exception:  # pragma: no cover - optional runtime dependency
    by_solar_hour = None
    zh_TW = None


@dataclass(frozen=True)
class ZiweiRuleset:
    # Rule switches (align with teacher reference defaults)
    late_zi_day_advance: bool = False
    split_early_late_zi: bool = False
    use_apparent_solar_time: bool = False


class ZiweiHardCalculator:
    """Hard algorithm Ziwei Dou Shu calculator backed by iztro-py."""

    def __init__(self, ruleset: Optional[ZiweiRuleset] = None):
        self.ruleset = ruleset or ZiweiRuleset()
        if by_solar_hour is None or zh_TW is None:
            raise ImportError("iztro-py is required for ZiweiHardCalculator")

        self._major_map = zh_TW.translations["stars"]["major"]
        self._minor_map = zh_TW.translations["stars"]["minor"]
        self._palace_map = zh_TW.translations["palaces"]
        self._earthly_map = zh_TW.translations["earthlyBranch"]

    def calculate_chart(self, *, birth_date: str, birth_time: str, gender: str, birth_location: str) -> Dict:
        """Return chart_structure for the given birth data."""
        solar_date, hour = self._get_effective_solar_date(birth_date, birth_time)
        g = "男" if gender in ("男", "male", "Male") else "女"

        astro = by_solar_hour(solar_date, hour, g, language="zh-TW")

        structure = {
            "五行局": astro.five_elements_class,
            "命主": self._map_star_name(astro.soul),
            "身主": self._map_star_name(astro.body),
            "十二宮": {},
            "四化": self._extract_mutagen(astro),
        }

        for palace in astro.palaces:
            palace_name = self._palace_map.get(palace.name, palace.name)
            if palace_name == "交友宮":
                palace_name = "僕役宮"
            earthly = self._earthly_map.get(palace.earthly_branch, palace.earthly_branch)
            major = self._map_star_list(palace.major_stars, self._major_map)
            minor = self._map_star_list(palace.minor_stars, self._minor_map)

            structure["十二宮"][palace_name] = {
                "宮位": earthly,
                "主星": major,
                "輔星": minor,
            }

        # Add borrowing info for empty palaces
        self._apply_borrowed_palaces(structure)

        # v2.2: 三方四正分析（命宮、官祿宮、財帛宮、夫妻宮）
        structure["三方四正"] = self._extract_surrounded_palaces(astro)

        # v2.2: 煞星分類
        structure["煞星"] = self._classify_sha_stars(structure)

        # v2.3: 大限/流年（直接計算，不保存非序列化物件）
        try:
            from datetime import date
            today = date.today()
            target_date = f"{today.year}-{today.month}-{today.day}"
            horoscope_data = self.calculate_horoscope(astro, target_date, birth_time)
            if horoscope_data:
                structure["大限流年"] = horoscope_data
        except Exception:
            pass  # 大限流年為附加功能，失敗不影響主排盤

        return structure

    def _get_effective_solar_date(self, birth_date: str, birth_time: str) -> Tuple[str, int]:
        dt = datetime.fromisoformat(birth_date)
        hour, minute = self._parse_time(birth_time)
        if self.ruleset.late_zi_day_advance and hour == 23:
            dt += timedelta(days=1)
        return dt.strftime("%Y-%m-%d"), hour

    @staticmethod
    def _parse_time(birth_time: str) -> Tuple[int, int]:
        parts = str(birth_time).strip().split(":")
        if not parts or not parts[0].isdigit():
            raise ValueError(f"Invalid birth_time: {birth_time}")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return hour, minute

    def _map_star_name(self, star_code: str) -> str:
        return self._major_map.get(star_code) or self._minor_map.get(star_code) or star_code

    @staticmethod
    def _map_star_list(stars, mapping: Dict[str, str]) -> list:
        result = []
        for s in stars:
            data = s.model_dump()
            result.append(mapping.get(data["name"], data["name"]))
        return result

    def _extract_mutagen(self, astro) -> Dict[str, str]:
        result = {}
        for palace in astro.palaces:
            for s in palace.major_stars + palace.minor_stars:
                data = s.model_dump()
                if not data.get("mutagen"):
                    continue
                name = self._map_star_name(data["name"])
                if data["mutagen"] == "禄":
                    result["化祿"] = name
                elif data["mutagen"] == "权":
                    result["化權"] = name
                elif data["mutagen"] == "科":
                    result["化科"] = name
                elif data["mutagen"] == "忌":
                    result["化忌"] = name
        return result

    def _apply_borrowed_palaces(self, structure: Dict) -> None:
        palaces = structure.get("十二宮", {})
        names = list(palaces.keys())
        for palace_name, info in palaces.items():
            if info.get("主星"):
                continue
            # Borrow from opposite palace (對宮)
            if palace_name not in names:
                continue
            idx = names.index(palace_name)
            opposite = names[(idx + 6) % 12]
            opposite_info = palaces.get(opposite, {})
            info["借宮"] = opposite
            info["借宮主星"] = opposite_info.get("主星", [])

    # ===== v2.2: 三方四正 =====

    # iztro_py palace name mapping (API uses English keys)
    _PALACE_KEY_MAP = {
        '命宮': 'soulPalace', '兄弟宮': 'brotherPalace',
        '夫妻宮': 'spousePalace', '子女宮': 'childrenPalace',
        '財帛宮': 'wealthPalace', '疾厄宮': 'healthPalace',
        '遷移宮': 'surfacePalace', '僕役宮': 'friendPalace',
        '官祿宮': 'careerPalace', '田宅宮': 'propertyPalace',
        '福德宮': 'spiritPalace', '父母宮': 'parentPalace',
    }

    def _extract_surrounded_palaces(self, astro) -> Dict:
        """
        使用 iztro_py 的 surrounded_palaces() API 提取關鍵宮位的三方四正。

        Returns:
            {
                "命宮": {"本宮": {...}, "對宮": {...}, "三合1": {...}, "三合2": {...}},
                "官祿宮": {...},
                "財帛宮": {...},
                "夫妻宮": {...},
            }
        """
        result = {}
        key_palaces = ['命宮', '官祿宮', '財帛宮', '夫妻宮']

        for palace_name in key_palaces:
            api_key = self._PALACE_KEY_MAP.get(palace_name)
            if not api_key:
                continue
            try:
                sp = astro.surrounded_palaces(api_key)
                if not sp:
                    continue
                info = {}
                # sp has: target, opposite, wealth, career (or similar structure)
                for attr_name in ['target', 'opposite', 'wealth', 'career']:
                    palace_obj = getattr(sp, attr_name, None)
                    if palace_obj is None:
                        continue
                    data = palace_obj.model_dump() if hasattr(palace_obj, 'model_dump') else {}
                    p_name = self._palace_map.get(data.get('name', ''), data.get('name', ''))
                    if p_name == "交友宮":
                        p_name = "僕役宮"
                    stars = []
                    for s in (data.get('major_stars') or []):
                        s_data = s if isinstance(s, dict) else (s.model_dump() if hasattr(s, 'model_dump') else {})
                        star_name = self._map_star_name(s_data.get('name', ''))
                        brightness = s_data.get('brightness', '')
                        mutagen = s_data.get('mutagen', '')
                        entry = star_name
                        if brightness:
                            entry += f"({brightness})"
                        if mutagen:
                            entry += f"[{mutagen}]"
                        stars.append(entry)

                    label_map = {'target': '本宮', 'opposite': '對宮', 'wealth': '財帛位', 'career': '官祿位'}
                    info[label_map.get(attr_name, attr_name)] = {
                        "宮名": p_name,
                        "主星": stars,
                    }
                result[palace_name] = info
            except Exception:
                continue

        return result

    # ===== v2.2: 煞星分類 =====

    # 四煞星（六煞星中最常見的分法）
    SHA_STARS = {
        "四煞": ["擎羊", "陀羅", "火星", "鈴星"],
        "空劫": ["地空", "地劫"],
        "化忌": [],  # 動態填入
    }

    def _classify_sha_stars(self, structure: Dict) -> Dict:
        """
        分類煞星在各宮的分佈（v2.2 新增）

        Returns:
            {
                "命宮煞星": ["擎羊"],
                "身宮煞星": [],
                "煞星分佈": {"擎羊": "命宮", "火星": "官祿宮", ...}
            }
        """
        all_sha = self.SHA_STARS["四煞"] + self.SHA_STARS["空劫"]
        sha_distribution = {}
        ming_sha = []

        for palace_name, palace_info in structure.get("十二宮", {}).items():
            minor_stars = palace_info.get("輔星", [])
            for star in minor_stars:
                if star in all_sha:
                    sha_distribution[star] = palace_name
                    if palace_name == "命宮":
                        ming_sha.append(star)

        # 化忌所在宮位
        si_hua = structure.get("四化", {})
        hua_ji_palace = None
        hua_ji_star = si_hua.get("化忌", "")
        if hua_ji_star:
            for palace_name, palace_info in structure.get("十二宮", {}).items():
                if hua_ji_star in palace_info.get("主星", []) + palace_info.get("輔星", []):
                    hua_ji_palace = palace_name
                    break

        return {
            "命宮煞星": ming_sha,
            "煞星分佈": sha_distribution,
            "化忌": f"{hua_ji_star}化忌在{hua_ji_palace}" if hua_ji_palace else "",
        }

    # ===== v2.2: 大限流年計算 =====

    def calculate_horoscope(self, astro, target_date: str, birth_time: str) -> Dict:
        """
        使用 iztro_py 的 horoscope() API 計算大限與流年資訊。

        Args:
            astro: FunctionalAstrolabe 物件（由 calculate_chart 內部建立）
            target_date: 目標日期 'YYYY-M-D'
            birth_time: 出生時間 'HH:MM'

        Returns:
            {
                "大限": {"年齡範圍": "23-32歲", "天干地支": "壬辰", "宮位": "夫妻宮", ...},
                "流年": {"年份": "丙午年", "宮位": "命宮", ...}
            }
        """
        try:
            hour, _ = self._parse_time(birth_time)
            horoscope = astro.horoscope(target_date, hour)
            if not horoscope:
                return {}

            result = {}

            # 大限
            decadal = getattr(horoscope, 'decadal', None)
            if decadal:
                d_data = decadal.model_dump() if hasattr(decadal, 'model_dump') else {}
                result["大限"] = {
                    "年齡範圍": d_data.get('age_range', ''),
                    "天干地支": d_data.get('heavenly_stem', '') + d_data.get('earthly_branch', ''),
                    "宮位": self._palace_map.get(d_data.get('palace_name', ''), d_data.get('palace_name', '')),
                }
                # 大限四化
                mutagen = d_data.get('mutagen', [])
                if mutagen:
                    result["大限"]["四化"] = mutagen

            # 流年
            yearly = getattr(horoscope, 'yearly', None)
            if yearly:
                y_data = yearly.model_dump() if hasattr(yearly, 'model_dump') else {}
                result["流年"] = {
                    "年份": y_data.get('heavenly_stem', '') + y_data.get('earthly_branch', '') + '年',
                    "宮位": self._palace_map.get(y_data.get('palace_name', ''), y_data.get('palace_name', '')),
                }
                mutagen = y_data.get('mutagen', [])
                if mutagen:
                    result["流年"]["四化"] = mutagen

            return result
        except Exception:
            return {}
