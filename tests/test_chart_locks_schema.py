import sqlite3

import pytest

from src.utils.database import AetheriaDatabase


@pytest.mark.unit
def test_chart_locks_support_multiple_chart_types(tmp_path):
    db_path = tmp_path / "aetheria_test.db"
    db = AetheriaDatabase(str(db_path))

    user_id = "u1"
    ziwei_lock = {"chart_structure": {"命宮": {"地支": "戌", "主星": ["天同"]}}}
    bazi_lock = {"bazi_chart": {"day_pillar": "癸未"}}

    db.save_chart_lock(user_id, "ziwei", ziwei_lock, analysis="ziwei")
    db.save_chart_lock(user_id, "bazi", bazi_lock, analysis="bazi")

    ziwei_row = db.get_chart_lock(user_id, "ziwei")
    bazi_row = db.get_chart_lock(user_id, "bazi")

    assert ziwei_row is not None
    assert bazi_row is not None
    assert ziwei_row["chart_type"] == "ziwei"
    assert bazi_row["chart_type"] == "bazi"
    assert ziwei_row["chart_data"]["chart_structure"]["命宮"]["主星"] == ["天同"]
    assert bazi_row["chart_data"]["bazi_chart"]["day_pillar"] == "癸未"


@pytest.mark.unit
def test_chart_locks_schema_migration_from_legacy_user_id_pk(tmp_path):
    db_path = tmp_path / "legacy.db"

    # Create legacy schema: user_id as the only primary key.
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE chart_locks (
                user_id TEXT PRIMARY KEY,
                chart_type TEXT NOT NULL,
                chart_data TEXT NOT NULL,
                analysis TEXT,
                locked_at TEXT
            )
            """
        )
        cur.execute(
            "INSERT INTO chart_locks (user_id, chart_type, chart_data, analysis, locked_at) VALUES (?, ?, ?, ?, ?)",
            ("u1", "ziwei", '{"chart_structure": {"命宮": {"地支": "戌"}}}', "a", "now"),
        )
        conn.commit()
    finally:
        conn.close()

    # Initialize DB manager; should migrate silently.
    db = AetheriaDatabase(str(db_path))

    # After migration, we must be able to store another chart_type for same user.
    db.save_chart_lock("u1", "bazi", {"bazi_chart": {"day_pillar": "癸未"}}, analysis="b")

    assert db.get_chart_lock("u1", "ziwei") is not None
    assert db.get_chart_lock("u1", "bazi") is not None
