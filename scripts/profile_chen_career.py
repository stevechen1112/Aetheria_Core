import json
import idna
import os
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

# Add src to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "src"))

# Load .env
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
    """紫微斗數：LLM-first + ChartExtractor"""

    # 特別備註：已定盤為 Chart B (甲申日)
    ziwei_note = "【定盤確認】：此命盤已確認為『B盤』，即視為隔日（11月13日）早子時排盤。日支必須是『申』(夫妻宮)，命宮在『戌』，太陰坐命。"

    system_instruction = (
        "你是 Aetheria，精通紫微斗數的 AI 命理顧問。\n\n"
        "重要原則：\n"
        "1. 準確性最重要，不可編造星曜\n"
        "2. 用戶是晚子時出生，且已定盤為『視為隔日早子時』。\n"
        "3. 必須明確說出命宮位置、主星、格局\n"
        "4. 針對『事業運』（官祿宮/整體格局）做深入分析\n"
        "輸出風格：專業、一針見血、宏觀"
    )

    initial_prompt = (
        "請為以下用戶（陳宥竹）提供完整的紫微斗數事業運專項分析：\n\n"
        "出生日期：{birth_date}\n"
        "出生時間：{birth_time}（晚子時，視為隔日）\n"
        "出生地點：{birth_location}\n"
        "性別：{gender}\n"
        "{ziwei_note}\n\n"
        "請按照以下格式輸出（約1500字）：\n\n"
        "### 一、命盤事業格局\n"
        "1. **命宮配置**：請用固定格式輸出：『命宮：X宮；主星：A、B；輔星：C、D』\n"
        "2. **官祿宮配置**：請用固定格式輸出：『官祿宮：X宮；主星：...；四化：...』\n"
        "3. **財帛宮配置**：請用固定格式輸出：『財帛宮：X宮；主星：...；四化：...』\n"
        "4. **夫/遷/福配置**：請用固定格式輸出：『夫妻宮：X宮；...』『遷移宮：X宮；...』『福德宮：X宮；...』\n\n"
        "### 二、事業特質深度解析\n"
        "（分析太陰在戌、機月同梁或相關格局對事業的影響，適合的產業屬性）\n\n"
        "### 三、人生事業大運走勢\n"
        "（分析中晚年運勢，以及目前的流年事業氣象）\n\n"
    ).format(
        birth_date=f"{user['birth_year']}-{user['birth_month']:02d}-{user['birth_day']:02d}",
        birth_time=user.get("birth_time", ""),
        birth_location=user.get("birth_location", ""),
        gender=user.get("gender", ""),
        ziwei_note=ziwei_note
    )

    prompt = system_instruction + "\n\n" + initial_prompt

    client = GeminiClient()
    llm_text = client.generate(prompt)

    # Prefer the fixed-format lines for deterministic extraction
    key_lines = []
    for line in llm_text.splitlines():
        s = line.strip()
        if any(token in s for token in ("命宮：", "夫妻宮：", "官祿宮：", "財帛宮：", "遷移宮：", "福德宮：")):
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
    user = load_user("chen_youzhu")

    # Time parsing
    hour, minute = parse_hhmm(user.get("birth_time", "23:58"))
    year, month, day = user["birth_year"], user["birth_month"], user["birth_day"]

    print("=" * 72)
    print("陳宥竹（chen_youzhu）六大系統事業運輸出")
    print("=" * 72)
    print(f"姓名：{user.get('name', '')}  性別：{user.get('gender', '')}")
    print(f"出生：{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} (Solar)")

    # 1) 紫微斗數
    print("\n" + "-" * 72)
    print("[1] 紫微斗數（事業專注）")
    print("-" * 72)
    ziwei = run_ziwei_gemini(user)
    if ziwei.get("key_lines"):
        print("LLM 固定格式行：")
        for s in ziwei["key_lines"]:
            print("- " + s)
    else:
        # Fallback
        print("結構化提取如下：")
        print(json.dumps(ziwei["chart_structure"], ensure_ascii=False, indent=2))

    # 2) 八字
    print("\n" + "-" * 72)
    print("[2] 八字命理（Sxtwl）")
    print("-" * 72)
    bazi_calc = BaziCalculator()
    # 這裡必須注意：User 是 23:58 出生，BaziCalculator 預設會根據 user_apparent_solar_time 調整
    # 若要強制符合「隔日早子」的定盤結果（甲申日），我們讓程式自己算算看是否轉過去了
    # 若沒轉過去，可能需要手動傳隔日日期。
    # 先試跑原時間。
    bazi = bazi_calc.calculate_bazi(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        gender=user.get("gender", "男"),
        longitude=float(user.get("longitude", 120.54)),
        use_apparent_solar_time=True,
    )
    print("四柱：", bazi.get("四柱"))
    print("日主：", bazi.get("日主"))
    print("格局與強弱：", bazi.get("強弱"))
    print("喜用神：", bazi.get("用神"))
    print("大運（目前40-50歲）：")
    # 找出當前大運
    current_age = 2026 - 1979
    dy_list = bazi.get("大運", [])
    for dy in dy_list:
        # 大運格式可能是 "4-13歲" string parsing needed if structured well
        # Sxtwl output usually has structured data
        print(dy)

    # 3) 西洋占星
    print("\n" + "-" * 72)
    print("[3] 西洋占星（事業：10宮/6宮/2宮）")
    print("-" * 72)
    astro_calc = AstrologyCalculator()
    natal = astro_calc.calculate_natal_chart(
        name=user.get("name", "Chen Youzhu"),
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city="Changhua",
        nation="TW",
        longitude=float(user.get("longitude", 120.54)),
        latitude=float(user.get("latitude", 24.08)),
        timezone_str="Asia/Taipei",
    )
    core_career = {
        "sun": natal["planets"].get("sun"),
        "mars": natal["planets"].get("mars"),
        "jupiter": natal["planets"].get("jupiter"), # 擴張
        "saturn": natal["planets"].get("saturn"),   # 壓力/結構
        "midheaven": natal["planets"].get("midheaven"),
        "house_10": natal["houses"].get("house_10"), # MC
        "house_6": natal["houses"].get("house_6"),   # 工作日常
        "house_2": natal["houses"].get("house_2"),   # 正財
    }
    print(json.dumps(core_career, ensure_ascii=False, indent=2))

    # 4) 靈數學
    print("\n" + "-" * 72)
    print("[4] 靈數學（流年/天賦）")
    print("-" * 72)
    numerology_calc = NumerologyCalculator()
    # 英文名用拼音
    prof = numerology_calc.calculate_full_profile(
        birth_date=date(year, month, day),
        full_name="CHEN YOU ZHU",
        target_date=date(2026, 1, 26),
    )
    nd = numerology_calc.to_dict(prof)
    print(json.dumps({
        "life_path": nd["core_numbers"]["life_path"],
        "personal_year_2026": nd["cycles"]["personal_year"],
        "pinnacles": nd["pinnacles"],
    }, ensure_ascii=False, indent=2))

    # 5) 姓名學
    print("\n" + "-" * 72)
    print("[5] 姓名學（事業運）")
    print("-" * 72)
    name_calc = NameCalculator()
    name_res = name_calc.analyze(
        full_name=user.get("name", "陳宥竹"),
        bazi_element=bazi.get("用神", {}).get("用神") if isinstance(bazi.get("用神"), dict) else None,
    )
    nr = asdict(name_res)
    print(f"人格（主運）：{nr['five_grids']['人格']}")
    print(f"總格（後運）：{nr['five_grids']['總格']}")
    # 找人格、總格的分析
    print("人格分析：", nr['grid_analyses'].get('人格'))
    print("總格分析：", nr['grid_analyses'].get('總格'))

    # 6) 塔羅牌
    print("\n" + "-" * 72)
    print("[6] 塔羅牌（事業現況與展望）")
    print("-" * 72)
    tarot_calc = TarotCalculator()
    seed = int(f"{year}{month}{day}") + 999 
    reading = tarot_calc.draw_cards(
        spread_type="three_card", # 過去/現在/未來
        question="陳宥竹的事業發展與核心方向",
        allow_reversed=True,
        seed=seed,
    )
    print(tarot_calc.format_reading_for_prompt(reading, context="career"))

if __name__ == "__main__":
    main()
