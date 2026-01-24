import json
import os
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

# Add src to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "src"))

# Load .env so GeminiClient can read GEMINI_API_KEY
load_dotenv(dotenv_path=str(ROOT_DIR / ".env"), override=False)

from calculators.astrology import AstrologyCalculator
from calculators.bazi import BaziCalculator
from calculators.name import NameCalculator
from calculators.numerology import NumerologyCalculator
from calculators.tarot import TarotCalculator
from calculators.chart_extractor import ChartExtractor
from utils.gemini_client import GeminiClient


def load_user(user_id: str) -> dict:
    users_path = ROOT_DIR / "data" / "users.json"
    with open(users_path, "r", encoding="utf-8") as f:
        users = json.load(f)
    if user_id not in users:
        raise KeyError(f"user_id not found: {user_id}")
    return users[user_id]


def parse_hhmm(text: str) -> tuple[int, int]:
    parts = str(text).strip().split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    return hour, minute


def run_ziwei_gemini(user: dict) -> dict:
    """紫微斗數：此專案為 LLM-first，使用 Gemini 輸出 + ChartExtractor 結構化。"""

    system_instruction = (
        "你是 Aetheria，精通紫微斗數的 AI 命理顧問。\n\n"
        "重要原則：\n"
        "1. 準確性最重要，不可編造星曜\n"
        "2. 晚子時（23:00-01:00）的判定邏輯要明確說明\n"
        "3. 必須明確說出命宮位置、主星、格局\n"
        "4. 結構清晰，先說命盤結構，再說詳細分析\n\n"
        "輸出風格：專業、溫暖、具啟發性"
    )

    initial_prompt = (
        "請為以下用戶提供完整的紫微斗數命盤分析：\n\n"
        "出生日期：{birth_date}\n"
        "出生時間：{birth_time}\n"
        "出生地點：{birth_location}\n"
        "性別：{gender}\n\n"
        "請按照以下格式輸出（約1500-2000字）：\n\n"
        "### 一、命盤基礎結構\n"
        "1. **時辰判定**：說明如何處理時辰（特別是晚子時）\n"
        "2. **命宮**：請用固定格式輸出：『命宮：X宮；主星：A、B；輔星：C、D（若無請寫無）』\n"
        "3. **核心格局**：屬於什麼格局？（如機月同梁、殺破狼等）\n"
        "4. **關鍵宮位**：\n"
        "   - 官祿宮（事業）：請用固定格式輸出：『官祿宮：X宮；主星：...；四化：...（若無請寫無）』\n"
        "   - 財帛宮（財運）：請用固定格式輸出：『財帛宮：X宮；主星：...；四化：...（若無請寫無）』\n"
        "   - 夫妻宮（感情）：請用固定格式輸出：『夫妻宮：X宮；主星：...；四化：...（若無請寫無）』\n\n"
        "### 二、詳細命盤分析\n"
        "（各宮位深度解讀，約1000字）\n\n"
        "### 三、性格特質與人生建議\n"
        "（日常語言描述，核心關鍵詞至少5個，約500字）\n\n"
        "**注意**：必須明確說出宮位（如「戌宮」「申宮」），不可模糊帶過。"
    ).format(
        birth_date=f"{user['birth_year']}-{user['birth_month']:02d}-{user['birth_day']:02d}",
        birth_time=user.get("birth_time", ""),
        birth_location=user.get("birth_location", ""),
        gender=user.get("gender", ""),
    )

    prompt = system_instruction + "\n\n" + initial_prompt

    client = GeminiClient()
    llm_text = client.generate(prompt)

    # Prefer the fixed-format lines for deterministic extraction
    key_lines = []
    for line in llm_text.splitlines():
        s = line.strip()
        if any(token in s for token in ("命宮：", "夫妻宮：", "官祿宮：", "財帛宮：")):
            key_lines.append(s)
        if "核心格局" in s:
            key_lines.append(s)

    extractor = ChartExtractor()
    chart_structure = extractor.extract_full_structure(llm_text)
    is_valid, errors = extractor.validate_structure(chart_structure)

    return {
        "llm_model": "gemini",
        "valid_structure": is_valid,
        "validation_errors": errors,
        "key_lines": key_lines,
        "chart_structure": chart_structure,
        "llm_text_preview": llm_text[:1500],
    }


def main():
    user = load_user("zhang_naiwen")

    hour, minute = parse_hhmm(user.get("birth_time", "06:00"))
    year, month, day = user["birth_year"], user["birth_month"], user["birth_day"]

    print("=" * 72)
    print("張小姐（zhang_naiwen）六大系統輸出（系統原始字段/結構）")
    print("=" * 72)
    print(f"姓名：{user.get('name', '')}  性別：{user.get('gender', '')}")
    print(f"出生：{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}  地點：{user.get('birth_location', '')}")

    # 1) 紫微斗數（LLM-first）
    print("\n" + "-" * 72)
    print("[1] 紫微斗數（Gemini + ChartExtractor 結構化）")
    print("-" * 72)
    ziwei = run_ziwei_gemini(user)
    print(f"結構有效：{ziwei['valid_structure']}")
    if ziwei["validation_errors"]:
        print("結構缺漏：" + "、".join(ziwei["validation_errors"]))
    if ziwei.get("key_lines"):
        print("LLM 固定格式行：")
        for s in ziwei["key_lines"]:
            print("- " + s)
    else:
        cs = ziwei["chart_structure"]
        print("命宮：", cs.get("命宮"))
        print("格局：", cs.get("格局"))
        print("五行局：", cs.get("五行局"))
        print("四化：", cs.get("四化"))
        twelve = cs.get("十二宮", {})
        for palace in ["夫妻宮", "官祿宮", "財帛宮", "遷移宮", "奴僕宮", "福德宮", "父母宮", "子女宮"]:
            if palace in twelve:
                print(f"{palace}：{twelve[palace]}")

    # 2) 八字
    print("\n" + "-" * 72)
    print("[2] 八字命理（sxtwl）")
    print("-" * 72)
    bazi_calc = BaziCalculator()
    bazi = bazi_calc.calculate_bazi(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        gender=user.get("gender", "女"),
        longitude=float(user.get("longitude", 121.5654)),
        use_apparent_solar_time=True,
    )
    print("四柱：", bazi.get("四柱"))
    print("日主：", bazi.get("日主"))
    print("強弱：", bazi.get("強弱") or bazi.get("強弱"))
    print("用神：", bazi.get("用神"))
    print("大運（前3步）：", (bazi.get("大运") or [])[:3])

    # 3) 西洋占星
    print("\n" + "-" * 72)
    print("[3] 西洋占星術（Kerykeion / Swiss Ephemeris）")
    print("-" * 72)
    astro_calc = AstrologyCalculator()
    natal = astro_calc.calculate_natal_chart(
        name=user.get("name", "Zhang Naiwen"),
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city="Taipei",
        nation="TW",
        longitude=float(user.get("longitude", 121.5654)),
        latitude=float(user.get("latitude", 25.033)),
        timezone_str="Asia/Taipei",
    )
    core = {
        "sun": natal["planets"].get("sun"),
        "moon": natal["planets"].get("moon"),
        "asc": natal["planets"].get("ascendant"),
        "midheaven": natal["planets"].get("midheaven"),
        "venus": natal["planets"].get("venus"),
        "mars": natal["planets"].get("mars"),
        "house_7": natal["houses"].get("house_7"),
        "house_10": natal["houses"].get("house_10"),
        "dominant_element": natal.get("dominant_element"),
        "dominant_quality": natal.get("dominant_quality"),
        "chart_ruler": natal.get("chart_ruler"),
    }
    print(json.dumps(core, ensure_ascii=False, indent=2))

    # 4) 靈數學
    print("\n" + "-" * 72)
    print("[4] 靈數學（Pythagorean）")
    print("-" * 72)
    numerology_calc = NumerologyCalculator()
    prof = numerology_calc.calculate_full_profile(
        birth_date=date(year, month, day),
        full_name="",  # 未提供羅馬拼音姓名，僅計算出生日期相關核心數
        target_date=date(2026, 1, 25),
    )
    numerology_dict = numerology_calc.to_dict(prof)
    # 只輸出核心欄位，避免過長
    print(json.dumps({
        "core_numbers": numerology_dict.get("core_numbers"),
        "cycles": numerology_dict.get("cycles"),
        "pinnacles": numerology_dict.get("pinnacles"),
        "challenges": numerology_dict.get("challenges"),
        "karmic_debts": numerology_dict.get("karmic_debts"),
    }, ensure_ascii=False, indent=2))

    # 5) 姓名學
    print("\n" + "-" * 72)
    print("[5] 姓名學（五格剖象法）")
    print("-" * 72)
    name_calc = NameCalculator()
    name_result = name_calc.analyze(
        full_name=user.get("name", ""),
        bazi_element=bazi.get("用神", {}).get("用神") if isinstance(bazi.get("用神"), dict) else None,
    )
    name_dict = asdict(name_result)
    # 精簡輸出
    print(json.dumps({
        "full_name": name_dict.get("full_name"),
        "five_grids": name_dict.get("five_grids"),
        "three_talents": name_dict.get("three_talents"),
        "overall_fortune": name_dict.get("overall_fortune"),
        "recommendations": name_dict.get("recommendations"),
    }, ensure_ascii=False, indent=2))

    # 6) 塔羅牌（可重現：seed 固定）
    print("\n" + "-" * 72)
    print("[6] 塔羅牌（RWS；seed 固定以便重現）")
    print("-" * 72)
    tarot_calc = TarotCalculator()
    seed = int(f"{year:04d}{month:02d}{day:02d}")
    reading = tarot_calc.draw_cards(
        spread_type="celtic_cross",
        question="張乃文：人格/內在/外在人際與關係模式",
        allow_reversed=True,
        seed=seed,
    )
    print(tarot_calc.format_reading_for_prompt(reading, context="general"))


if __name__ == "__main__":
    main()
