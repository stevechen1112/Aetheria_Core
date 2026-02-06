import json
from pathlib import Path

from src.calculators.ziwei_hard import ZiweiHardCalculator, ZiweiRuleset


def test_ziwei_hard_matches_teacher_reference():
    ref_path = Path("data/ziwei_reference_chen.json")
    ref = json.loads(ref_path.read_text(encoding="utf-8"))

    calc = ZiweiHardCalculator(
        ruleset=ZiweiRuleset(
            late_zi_day_advance=False,
            split_early_late_zi=False,
            use_apparent_solar_time=False,
        )
    )

    chart = calc.calculate_chart(
        birth_date="1979-11-12",
        birth_time="23:58",
        gender="男",
        birth_location="台灣彰化市",
    )

    ref_chart = ref["chart_structure"]
    assert chart["五行局"] == ref_chart["五行局"]
    assert chart["命主"] == ref_chart["命主"]
    assert chart["身主"] == ref_chart["身主"]
    assert chart["四化"] == ref_chart["四化"]

    ref_palaces = ref_chart["十二宮"]
    got_palaces = chart["十二宮"]
    for palace, ref_info in ref_palaces.items():
        got_info = got_palaces.get(palace)
        assert got_info is not None
        assert got_info["主星"] == ref_info["主星"]
