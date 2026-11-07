from pathlib import Path

import pytest

from core import config, db


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", Path(tmp_path) / "test.db")
    db.seed_demo_data()
    return db


def test_seed_creates_feed_and_users(temp_db):
    assert db.get_user(db.DEMO_USER_ID) is not None
    feed = db.get_feed(limit=100)
    assert len(feed) >= 20


def test_region_stuck_respects_k_anonymity(temp_db):
    rows = db.get_region_stuck(days=7, k=5)
    assert any(row["concept"] == "판별식" for row in rows)
    assert all(row["count"] >= 5 for row in rows)


def test_log_and_post_roundtrip(temp_db):
    log_id = db.upsert_log(
        db.DEMO_USER_ID,
        "2026-11-03",
        3,
        "영어Ⅱ",
        "영어2",
        "관계대명사 whose를 배웠다.",
        "필기",
        "whose vs of which",
    )
    assert db.get_log(db.DEMO_USER_ID, "2026-11-03", 3)["learned"].startswith("관계대명사")

    post_id = db.create_post(
        log_id,
        db.DEMO_USER_ID,
        "관계대명사 whose를 배웠다.",
        "영어2",
        ["관계대명사"],
        2,
    )
    post = db.get_post(post_id)
    assert post is not None
    assert post["status"] == "visible"

    assert db.toggle_cheer(post_id, db.FRIEND_USER_ID) is True
    assert db.cheer_count(post_id) == 1
    assert db.toggle_cheer(post_id, db.FRIEND_USER_ID) is False
    assert db.cheer_count(post_id) == 0


def test_three_reports_hide_post(temp_db):
    feed = db.get_feed(limit=1)
    post_id = feed[0]["id"]
    assert db.report_post(post_id, "seed-01") == 1
    assert db.report_post(post_id, "seed-02") == 2
    assert db.report_post(post_id, "seed-03") == 3
    assert db.get_post(post_id)["status"] == "hidden"


def test_recall_built_from_logs(temp_db):
    db.build_recall_from_logs(db.DEMO_USER_ID)
    assert db.count_recall_items(db.DEMO_USER_ID) > 0
    items = db.get_recall_items(db.DEMO_USER_ID, due_only=False)
    db.review_recall(items[0]["id"], 5)
    with db.get_conn() as conn:
        updated = conn.execute(
            "SELECT * FROM recall_queue WHERE id = ?", (items[0]["id"],)
        ).fetchone()
    assert updated["reps"] >= 1
