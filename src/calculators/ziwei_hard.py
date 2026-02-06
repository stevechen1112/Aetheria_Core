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
