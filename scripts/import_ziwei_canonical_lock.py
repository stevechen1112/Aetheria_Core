"""匯入既有紫微盤面作為 canonical lock。

用法（PowerShell）：
    $env:PYTHONPATH="C:/Users/User/Desktop/Aetheria_Core"; python scripts/import_ziwei_canonical_lock.py --user-id <USER_ID> --json "cache/reports_export/.../ziwei_....json" --ruleset no_day_advance

說明：
- 會將指定 JSON 內的 chart_structure 寫入 SQLite 的 chart_locks(ziwei) 作為 confirmed + active。
- 會寫入 provenance.ruleset，避免日後同一人用不同規則漂移。
- 不會自動生成新報告（需要時請用前端或 /api/profile/save-and-analyze 重新產文）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.database import AetheriaDatabase


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_chart_structure(payload: Dict[str, Any]) -> Dict[str, Any]:
    cs = payload.get("chart_structure")
    if isinstance(cs, dict):
        return cs
    raise ValueError("JSON 缺少 chart_structure 或格式不正確")


def _extract_original_analysis(payload: Dict[str, Any], chart_structure: Dict[str, Any]) -> str:
    # 匯出格式可能把原文放在 chart_structure['原始分析'] 或最外層 'analysis'
    raw = None
    if isinstance(chart_structure, dict):
        raw = chart_structure.get("原始分析")
    if not raw:
        raw = payload.get("analysis")
    if not raw:
        raw = payload.get("original_analysis")
    return str(raw or "")


def _normalize_ruleset(value: Optional[str]) -> str:
    if not value:
        return "ziwei.late_zi.no_day_advance"
    v = str(value).strip().lower()
    if v in {"no_day_advance", "no-advance", "noadvance", "ziwei.late_zi.no_day_advance"}:
        return "ziwei.late_zi.no_day_advance"
    if v in {"day_advance", "day-advance", "advance", "ziwei.late_zi.day_advance"}:
        return "ziwei.late_zi.day_advance"
    # 允許直接傳入完整 ruleset id
    return str(value).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="匯入既有紫微盤面作為 canonical lock")
    parser.add_argument("--user-id", required=True, help="要鎖定的 user_id")
    parser.add_argument("--json", required=True, help="匯出 JSON 檔案路徑")
    parser.add_argument(
        "--ruleset",
        default="no_day_advance",
        help="晚子時換日規則：no_day_advance 或 day_advance（預設：no_day_advance）",
    )
    parser.add_argument(
        "--db",
        default="data/aetheria.db",
        help="SQLite DB 路徑（預設：data/aetheria.db）",
    )

    args = parser.parse_args()

    user_id: str = args.user_id
    json_path = Path(args.json)
    if not json_path.exists():
        raise FileNotFoundError(f"找不到檔案：{json_path}")

    payload = _load_json(json_path)
    chart_structure = _extract_chart_structure(payload)

    # 基本欄位檢查（避免匯入錯檔）
    if not isinstance(chart_structure.get("命宮"), dict):
        raise ValueError("chart_structure 缺少 命宮")
    if not isinstance(chart_structure.get("十二宮"), dict):
        raise ValueError("chart_structure 缺少 十二宮")

    ruleset_id = _normalize_ruleset(args.ruleset)
    original_analysis = _extract_original_analysis(payload, chart_structure)

    # 產生可追溯的來源簽章（跟 server 的 source_signature 不同：此處是 import 專用）
    source_signature = _sha256_text(
        json.dumps(
            {
                "import": "ziwei.canonical_lock_import.v1",
                "user_id": user_id,
                "ruleset": ruleset_id,
                "file": str(json_path.as_posix()),
                "chart_structure": chart_structure,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )

    now = datetime.now().isoformat()

    lock_data: Dict[str, Any] = {
        "user_id": user_id,
        "chart_type": "ziwei",
        "chart_structure": chart_structure,
        # 保留原始文字供稽核（但系統產文時會以鎖定盤面重新解讀，避免沿用舊敘事漂移）
        "original_analysis": original_analysis,
        "provenance": {
            "ruleset": ruleset_id,
            "pipeline": "ziwei.canonical_lock_import.v1",
            "source_signature": source_signature,
            "source_file": str(json_path.as_posix()),
            "imported_at": now,
        },
        "source_signature": source_signature,
        "confirmation_status": "confirmed",
        "confirmed_at": now,
        "is_active": True,
    }

    db = AetheriaDatabase(args.db)
    db.save_chart_lock(user_id, "ziwei", lock_data, analysis=original_analysis)

    print("✓ 匯入完成")
    print(f"- user_id: {user_id}")
    print(f"- ruleset: {ruleset_id}")
    ming_gong = chart_structure.get("命宮") or {}
    print(f"- 命宮: {ming_gong.get('宮位')} 宮 / 主星：{', '.join(ming_gong.get('主星') or [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
