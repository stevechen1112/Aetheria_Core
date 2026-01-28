import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, Tuple


def safe_get(d: Any, *path: str) -> Any:
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def summarize_text(text: Any) -> Tuple[int, int]:
    if not isinstance(text, str):
        return (0, 0)
    stripped = text.strip()
    return (len(stripped), stripped.count("\n") + 1 if stripped else 0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify saved reports vs calculators")
    parser.add_argument("--in", dest="input_path", default="cache/latest_reports_dump.json")
    args = parser.parse_args()

    payload = json.loads(Path(args.input_path).read_text(encoding="utf-8"))
    user_id = payload.get("user_id")
    birth = payload.get("birth_info") or {}
    reports = payload.get("reports") or {}

    print(f"user_id: {user_id}")
    print("birth:", {
        "name": birth.get("name"),
        "gender": birth.get("gender"),
        "date": birth.get("gregorian_birth_date") or f"{birth.get('birth_year')}-{birth.get('birth_month')}-{birth.get('birth_day')}",
        "time": f"{birth.get('birth_hour'):02d}:{birth.get('birth_minute'):02d}" if birth.get('birth_hour') is not None else None,
        "location": birth.get("birth_location"),
    })

    # --- Presence / size checks ---
    for sys_name in ["ziwei", "bazi", "astrology", "numerology", "name"]:
        rep = (reports.get(sys_name) or {}).get("report")
        analysis = safe_get(rep, "analysis")
        n_chars, n_lines = summarize_text(analysis)
        print(f"\n[{sys_name}] keys={list(rep.keys()) if isinstance(rep, dict) else type(rep)}")
        print(f"[{sys_name}] analysis chars={n_chars}, lines={n_lines}")

    # --- Calculator cross-checks (best-effort) ---
    try:
        from src.calculators.bazi import BaziCalculator

        bd = birth.get("gregorian_birth_date")
        if bd and birth.get("birth_hour") is not None:
            y, m, d = map(int, bd.split("-"))
            bazi_calc = BaziCalculator()
            bazi_calc_out = bazi_calc.calculate_bazi(
                year=y,
                month=m,
                day=d,
                hour=int(birth.get("birth_hour")),
                minute=int(birth.get("birth_minute") or 0),
                gender=birth.get("gender") or "男",
            )

            saved_bazi = safe_get(reports.get("bazi"), "report", "bazi_chart") or safe_get(reports.get("bazi"), "report", "四柱")
            print("\n[bazi] recompute day master:", safe_get(bazi_calc_out, "日主", "天干"))
            print("[bazi] recompute pillars:", {
                "年": safe_get(bazi_calc_out, "四柱", "年柱", "天干") + safe_get(bazi_calc_out, "四柱", "年柱", "地支"),
                "月": safe_get(bazi_calc_out, "四柱", "月柱", "天干") + safe_get(bazi_calc_out, "四柱", "月柱", "地支"),
                "日": safe_get(bazi_calc_out, "四柱", "日柱", "天干") + safe_get(bazi_calc_out, "四柱", "日柱", "地支"),
                "時": safe_get(bazi_calc_out, "四柱", "時柱", "天干") + safe_get(bazi_calc_out, "四柱", "時柱", "地支"),
            })

            if isinstance(saved_bazi, dict):
                # Saved schema in this project usually uses traditional keys.
                print("[bazi] saved keys:", list(saved_bazi.keys())[:20])
    except Exception as e:
        print("\n[bazi] recompute skipped:", e)

    try:
        from src.calculators.numerology import NumerologyCalculator

        bd = birth.get("gregorian_birth_date")
        nm = birth.get("name") or ""
        if bd:
            y, m, d = map(int, bd.split("-"))
            ncalc = NumerologyCalculator()
            prof = ncalc.calculate_full_profile(date(y, m, d), nm)
            nd = ncalc.to_dict(prof)
            recompute_lp = safe_get(nd, "core_numbers", "life_path", "number")
            saved_prof = safe_get(reports.get("numerology"), "report", "profile")
            saved_lp = safe_get(saved_prof, "core_numbers", "life_path", "number")
            print("\n[numerology] recompute life_path:", recompute_lp)
            print("[numerology] saved life_path:", saved_lp)
    except Exception as e:
        print("\n[numerology] recompute skipped:", e)

    try:
        from src.calculators.name import NameCalculator

        nm = birth.get("name") or ""
        if nm:
            ncalc = NameCalculator()
            analysis = ncalc.analyze(nm)
            nd = ncalc.to_dict(analysis)
            recompute_total = safe_get(nd, "name_info", "total_strokes")
            saved_name = safe_get(reports.get("name"), "report", "five_grids")
            saved_total = safe_get(saved_name, "name_info", "total_strokes") if isinstance(saved_name, dict) else None
            print("\n[name] recompute total_strokes:", recompute_total)
            print("[name] saved total_strokes:", saved_total)
    except Exception as e:
        print("\n[name] recompute skipped:", e)

    try:
        # Astrology calculator is optional; only check if available.
        from src.calculators.astrology import AstrologyCalculator

        bd = birth.get("gregorian_birth_date")
        loc = birth.get("birth_location") or ""
        if bd and birth.get("birth_hour") is not None:
            y, m, d = map(int, bd.split("-"))
            # Mirror server's Taiwan city lookup, with Taipei fallback.
            taiwan_cities = {
                '台北': (25.0330, 121.5654), '台北市': (25.0330, 121.5654),
                '新北': (25.0169, 121.4628), '新北市': (25.0169, 121.4628),
                '桃園': (24.9936, 121.3010), '桃園市': (24.9936, 121.3010),
                '台中': (24.1477, 120.6736), '台中市': (24.1477, 120.6736),
                '台南': (22.9998, 120.2270), '台南市': (22.9998, 120.2270),
                '高雄': (22.6273, 120.3014), '高雄市': (22.6273, 120.3014),
                '基隆': (25.1276, 121.7392), '基隆市': (25.1276, 121.7392),
                '新竹': (24.8138, 120.9675), '新竹市': (24.8138, 120.9675),
                '嘉義': (23.4801, 120.4491), '嘉義市': (23.4801, 120.4491),
                '彰化': (24.0518, 120.5161), '彰化市': (24.0518, 120.5161), '彰化縣': (24.0518, 120.5161),
                '南投': (23.9609, 120.9719), '南投市': (23.9609, 120.9719), '南投縣': (23.9609, 120.9719),
                '雲林': (23.7092, 120.4313), '雲林縣': (23.7092, 120.4313),
                '苗栗': (24.5602, 120.8214), '苗栗市': (24.5602, 120.8214), '苗栗縣': (24.5602, 120.8214),
                '屏東': (22.6727, 120.4871), '屏東市': (22.6727, 120.4871), '屏東縣': (22.6727, 120.4871),
                '宜蘭': (24.7570, 121.7533), '宜蘭市': (24.7570, 121.7533), '宜蘭縣': (24.7570, 121.7533),
                '花蓮': (23.9910, 121.6114), '花蓮市': (23.9910, 121.6114), '花蓮縣': (23.9910, 121.6114),
                '台東': (22.7583, 121.1444), '台東市': (22.7583, 121.1444), '台東縣': (22.7583, 121.1444),
                '澎湖': (23.5711, 119.5793), '澎湖縣': (23.5711, 119.5793),
                '金門': (24.4493, 118.3767), '金門縣': (24.4493, 118.3767),
                '連江': (26.1505, 119.9499), '連江縣': (26.1505, 119.9499), '馬祖': (26.1505, 119.9499),
            }
            city_name = loc.replace('台灣', '').replace('臺灣', '').strip()
            lat, lng = 25.0330, 121.5654
            for city_key, (city_lat, city_lng) in taiwan_cities.items():
                if city_key in city_name:
                    lat, lng = city_lat, city_lng
                    break

            acalc = AstrologyCalculator()
            natal = acalc.calculate_natal_chart(
                name=birth.get("name") or "用戶",
                year=y,
                month=m,
                day=d,
                hour=int(birth.get("birth_hour")),
                minute=int(birth.get("birth_minute") or 0),
                city="Taiwan",
                longitude=lng,
                latitude=lat,
                timezone_str="Asia/Taipei",
            )

            rs = safe_get(reports.get("astrology"), "report", "natal_chart")
            recompute = {
                "sun": safe_get(natal, "sun", "sign"),
                "moon": safe_get(natal, "moon", "sign"),
                "asc": safe_get(natal, "ascendant", "sign"),
            }
            saved = {
                "sun": safe_get(rs, "sun", "sign"),
                "moon": safe_get(rs, "moon", "sign"),
                "asc": safe_get(rs, "ascendant", "sign"),
            }
            print("\n[astrology] recompute signs:", recompute)
            print("[astrology] saved signs:", saved)
    except Exception as e:
        print("\n[astrology] recompute skipped:", e)

    # --- Ziwei structure sanity ---
    try:
        z = safe_get(reports.get("ziwei"), "report", "chart_structure")
        if isinstance(z, dict):
            palaces = z.get("十二宮") if isinstance(z.get("十二宮"), dict) else None
            palace_count = len(palaces.keys()) if palaces else 0
            print(f"\n[ziwei] has 十二宮: {bool(palaces)} count={palace_count}")
            missing = [p for p in [
                '命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮', '遷移宮', '交友宮', '官祿宮', '田宅宮', '福德宮', '父母宮'
            ] if palaces and p not in palaces]
            if missing:
                print("[ziwei] missing palaces:", missing)
    except Exception as e:
        print("\n[ziwei] sanity skipped:", e)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
