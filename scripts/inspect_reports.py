
import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional


def connect(db_path: Path) -> sqlite3.Connection:
	conn = sqlite3.connect(str(db_path))
	conn.row_factory = sqlite3.Row
	return conn


def get_latest_user_id(conn: sqlite3.Connection) -> Optional[str]:
	row = conn.execute(
		"""
		SELECT user_id
		FROM system_reports
		ORDER BY datetime(updated_at) DESC, id DESC
		LIMIT 1
		"""
	).fetchone()
	return row["user_id"] if row else None


def get_user_birth_info(conn: sqlite3.Connection, user_id: str) -> Dict[str, Any]:
	row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
	return dict(row) if row else {}


def get_reports(conn: sqlite3.Connection, user_id: str) -> Dict[str, Any]:
	rows = conn.execute(
		"""
		SELECT system_type, report_data, created_at, updated_at
		FROM system_reports
		WHERE user_id = ?
		ORDER BY system_type
		""",
		(user_id,),
	).fetchall()

	reports: Dict[str, Any] = {}
	for r in rows:
		try:
			report_obj = json.loads(r["report_data"]) if r["report_data"] else {}
		except Exception:
			report_obj = {"_raw": r["report_data"], "_parse_error": True}
		reports[r["system_type"]] = {
			"report": report_obj,
			"created_at": r["created_at"],
			"updated_at": r["updated_at"],
		}
	return reports


def main() -> int:
	parser = argparse.ArgumentParser(description="Inspect Aetheria saved system reports")
	parser.add_argument("--db", default="data/aetheria.db")
	parser.add_argument("--user-id", default=None)
	parser.add_argument("--out", default=None, help="Write full JSON to a file")
	args = parser.parse_args()

	db_path = Path(args.db)
	if not db_path.exists():
		print(f"DB not found: {db_path}")
		return 2

	conn = connect(db_path)
	try:
		user_id = args.user_id or get_latest_user_id(conn)
		if not user_id:
			print("No system_reports found in DB.")
			return 0

		birth_info = get_user_birth_info(conn, user_id)
		reports = get_reports(conn, user_id)

		summary = {
			"user_id": user_id,
			"birth_info": {
				"name": birth_info.get("name") or birth_info.get("full_name"),
				"gender": birth_info.get("gender"),
				"gregorian_birth_date": birth_info.get("gregorian_birth_date"),
				"birth_year": birth_info.get("birth_year"),
				"birth_month": birth_info.get("birth_month"),
				"birth_day": birth_info.get("birth_day"),
				"birth_hour": birth_info.get("birth_hour"),
				"birth_minute": birth_info.get("birth_minute"),
				"birth_location": birth_info.get("birth_location"),
				"longitude": birth_info.get("longitude"),
				"latitude": birth_info.get("latitude"),
				"updated_at": birth_info.get("updated_at"),
			},
			"systems": {
				k: {"updated_at": v.get("updated_at"), "created_at": v.get("created_at")}
				for k, v in reports.items()
			},
		}

		print(json.dumps(summary, ensure_ascii=False, indent=2))

		if args.out:
			payload = {"user_id": user_id, "birth_info": birth_info, "reports": reports}
			out_path = Path(args.out)
			out_path.parent.mkdir(parents=True, exist_ok=True)
			out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
			print(f"\nWrote full payload to: {out_path}")

		return 0
	finally:
		conn.close()


if __name__ == "__main__":
	raise SystemExit(main())

