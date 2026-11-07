"""SQLite data access for 한줄."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from collections import Counter
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from typing import Any, Iterable

from . import config
from .neis import normalize_subject
from .recall import next_due, parse_iso_date, sm2

DEMO_USER_ID = "demo-main"
FRIEND_USER_ID = "demo-friend"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id          TEXT PRIMARY KEY,
  nickname    TEXT NOT NULL UNIQUE,
  school_code TEXT,
  grade       INTEGER NOT NULL,
  class_no    TEXT,
  track       TEXT,
  region      TEXT NOT NULL,
  created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schools (
  code        TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  office_code TEXT NOT NULL,
  region      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS timetable_cache (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  school_code  TEXT NOT NULL,
  date         TEXT NOT NULL,
  grade        INTEGER NOT NULL,
  class_no     TEXT NOT NULL,
  period       INTEGER NOT NULL,
  subject_raw  TEXT,
  subject_norm TEXT,
  room         TEXT,
  is_event     INTEGER NOT NULL DEFAULT 0,
  fetched_at   TEXT NOT NULL,
  UNIQUE(school_code, date, grade, class_no, period)
);

CREATE TABLE IF NOT EXISTS logs (
  id           TEXT PRIMARY KEY,
  user_id      TEXT NOT NULL,
  date         TEXT NOT NULL,
  period       INTEGER NOT NULL,
  subject_raw  TEXT,
  subject_norm TEXT,
  learned      TEXT NOT NULL,
  activity     TEXT,
  stuck        TEXT,
  created_at   TEXT NOT NULL,
  UNIQUE(user_id, date, period)
);

CREATE TABLE IF NOT EXISTS posts (
  id           TEXT PRIMARY KEY,
  log_id       TEXT NOT NULL UNIQUE,
  user_id      TEXT NOT NULL,
  public_text  TEXT NOT NULL,
  subject_norm TEXT,
  concept_tags TEXT,
  grade        INTEGER,
  region       TEXT NOT NULL,
  status       TEXT NOT NULL DEFAULT 'visible',
  created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reactions (
  id         TEXT PRIMARY KEY,
  post_id    TEXT NOT NULL,
  user_id    TEXT NOT NULL,
  type       TEXT NOT NULL DEFAULT 'cheer',
  created_at TEXT NOT NULL,
  UNIQUE(post_id, user_id)
);

CREATE TABLE IF NOT EXISTS reports (
  id          TEXT PRIMARY KEY,
  post_id     TEXT NOT NULL,
  reporter_id TEXT NOT NULL,
  reason      TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'open',
  created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recall_queue (
  id            TEXT PRIMARY KEY,
  user_id       TEXT NOT NULL,
  concept       TEXT NOT NULL,
  concept_id    TEXT,
  due_date      TEXT NOT NULL,
  interval_days INTEGER NOT NULL DEFAULT 1,
  ease          REAL NOT NULL DEFAULT 2.5,
  reps          INTEGER NOT NULL DEFAULT 0,
  last_reviewed TEXT,
  UNIQUE(user_id, concept)
);

CREATE TABLE IF NOT EXISTS events (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id    TEXT,
  name       TEXT NOT NULL,
  props      TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);

CREATE INDEX IF NOT EXISTS idx_logs_user_date ON logs(user_id, date);
CREATE INDEX IF NOT EXISTS idx_posts_region_created ON posts(region, created_at);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_recall_due ON recall_queue(user_id, due_date);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@contextmanager
def get_conn():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# Users / schools
# ---------------------------------------------------------------------------
def get_user(user_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def nickname_exists(nickname: str) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM users WHERE nickname = ?", (nickname,)).fetchone()
    return row is not None


def create_user(
    nickname: str,
    grade: int,
    class_no: str,
    track: str = "",
    school_code: str = config.DEMO_SCHOOL_CODE,
    region: str = config.REGION,
    user_id: str | None = None,
) -> str:
    user_id = user_id or _new_id("user")
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO users
               (id, nickname, school_code, grade, class_no, track, region, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, nickname, school_code, grade, class_no, track, region, _now()),
        )
    return user_id


def _upsert_school(code: str, name: str, office_code: str, region: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO schools (code, name, office_code, region)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(code) DO UPDATE SET
                 name = excluded.name,
                 office_code = excluded.office_code,
                 region = excluded.region""",
            (code, name, office_code, region),
        )


def get_school(code: str = config.DEMO_SCHOOL_CODE) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM schools WHERE code = ?", (code,)).fetchone()


# ---------------------------------------------------------------------------
# Timetable cache
# ---------------------------------------------------------------------------
def get_timetable_cache(
    school_code: str,
    day: str,
    grade: int,
    class_no: str,
    ttl_hours: int = 24,
) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM timetable_cache
               WHERE school_code = ? AND date = ? AND grade = ? AND class_no = ?
               ORDER BY period""",
            (school_code, day, grade, class_no),
        ).fetchall()
    if not rows:
        return []
    try:
        fetched = datetime.fromisoformat(rows[0]["fetched_at"])
    except (TypeError, ValueError):
        return []
    if datetime.now() - fetched > timedelta(hours=ttl_hours):
        return []
    return [dict(row) for row in rows]


def save_timetable_cache(
    school_code: str,
    day: str,
    grade: int,
    class_no: str,
    rows: Iterable[Any],
) -> None:
    now = _now()
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM timetable_cache WHERE school_code = ? AND date = ? AND grade = ? AND class_no = ?",
            (school_code, day, grade, class_no),
        )
        for row in rows:
            conn.execute(
                """INSERT OR REPLACE INTO timetable_cache
                   (school_code, date, grade, class_no, period, subject_raw, subject_norm,
                    room, is_event, fetched_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    school_code,
                    day,
                    grade,
                    class_no,
                    row.period,
                    row.subject_raw,
                    row.subject,
                    row.room,
                    1 if row.is_event else 0,
                    now,
                ),
            )


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------
def get_log(user_id: str, day: str, period: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM logs WHERE user_id = ? AND date = ? AND period = ?",
            (user_id, day, period),
        ).fetchone()


def get_logs_for_date(user_id: str, day: str) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM logs WHERE user_id = ? AND date = ? ORDER BY period",
            (user_id, day),
        ).fetchall()


def upsert_log(
    user_id: str,
    day: str,
    period: int,
    subject_raw: str,
    subject_norm: str,
    learned: str,
    activity: str = "",
    stuck: str = "",
) -> str:
    existing = get_log(user_id, day, period)
    if existing:
        with get_conn() as conn:
            conn.execute(
                """UPDATE logs
                   SET subject_raw = ?, subject_norm = ?, learned = ?, activity = ?, stuck = ?
                   WHERE id = ?""",
                (subject_raw, subject_norm, learned, activity, stuck, existing["id"]),
            )
        return existing["id"]

    log_id = _new_id("log")
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO logs
               (id, user_id, date, period, subject_raw, subject_norm, learned, activity, stuck, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (log_id, user_id, day, period, subject_raw, subject_norm, learned, activity, stuck, _now()),
        )
    return log_id


def get_week_logs(user_id: str, days: int = 7) -> list[sqlite3.Row]:
    cutoff = (date.today() - timedelta(days=days - 1)).isoformat()
    with get_conn() as conn:
        return conn.execute(
            """SELECT * FROM logs
               WHERE user_id = ? AND date >= ?
               ORDER BY date DESC, period""",
            (user_id, cutoff),
        ).fetchall()


def count_logs_for_date(user_id: str, day: str) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM logs WHERE user_id = ? AND date = ?",
            (user_id, day),
        ).fetchone()
    return int(row["c"]) if row else 0


# ---------------------------------------------------------------------------
# Posts / feed
# ---------------------------------------------------------------------------
def get_post_by_log(log_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM posts WHERE log_id = ?", (log_id,)).fetchone()


def get_post(post_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            """SELECT p.*, u.nickname, u.grade, u.track
               FROM posts p JOIN users u ON u.id = p.user_id
               WHERE p.id = ?""",
            (post_id,),
        ).fetchone()


def delete_post_by_log(log_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM posts WHERE log_id = ?", (log_id,))


def create_post(
    log_id: str,
    user_id: str,
    text: str,
    subject_norm: str,
    tags: list[str],
    grade: int,
    region: str | None = None,
) -> str:
    post_id = _new_id("post")
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO posts
               (id, log_id, user_id, public_text, subject_norm, concept_tags, grade, region, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'visible', ?)""",
            (
                post_id,
                log_id,
                user_id,
                text,
                subject_norm,
                ",".join(tags),
                grade,
                region or config.REGION,
                _now(),
            ),
        )
    return post_id


def replace_post_for_log(
    log_id: str,
    user_id: str,
    text: str,
    subject_norm: str,
    tags: list[str],
    grade: int,
    region: str | None = None,
) -> str:
    delete_post_by_log(log_id)
    return create_post(log_id, user_id, text, subject_norm, tags, grade, region)


def get_feed(
    region: str = config.REGION,
    subject: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[sqlite3.Row]:
    sql = """
        SELECT p.*, u.nickname, u.grade, u.track,
               (SELECT COUNT(*) FROM reactions r WHERE r.post_id = p.id) AS cheer_count
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.region = ? AND p.status = 'visible'
    """
    params: list[Any] = [region]
    if subject:
        sql += " AND p.subject_norm = ?"
        params.append(subject)
    sql += " ORDER BY p.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_conn() as conn:
        return conn.execute(sql, params).fetchall()


def get_feed_subjects(region: str = config.REGION) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT DISTINCT subject_norm FROM posts
               WHERE region = ? AND status = 'visible' AND subject_norm IS NOT NULL
               ORDER BY subject_norm""",
            (region,),
        ).fetchall()
    return [row["subject_norm"] for row in rows]


def cheer_count(post_id: str) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM reactions WHERE post_id = ?", (post_id,)
        ).fetchone()
    return int(row["c"]) if row else 0


def has_cheered(post_id: str, user_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM reactions WHERE post_id = ? AND user_id = ?",
            (post_id, user_id),
        ).fetchone()
    return row is not None


def toggle_cheer(post_id: str, user_id: str) -> bool:
    """Return True when the user now cheers."""
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM reactions WHERE post_id = ? AND user_id = ?",
            (post_id, user_id),
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM reactions WHERE id = ?", (existing["id"],))
            return False
        conn.execute(
            "INSERT INTO reactions (id, post_id, user_id, type, created_at) VALUES (?, ?, ?, 'cheer', ?)",
            (_new_id("reaction"), post_id, user_id, _now()),
        )
        return True


def report_post(post_id: str, reporter_id: str, reason: str = "신고") -> int:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO reports (id, post_id, reporter_id, reason, status, created_at)
               VALUES (?, ?, ?, ?, 'open', ?)""",
            (_new_id("report"), post_id, reporter_id, reason, _now()),
        )
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM reports WHERE post_id = ? AND status = 'open'",
            (post_id,),
        ).fetchone()
        count = int(row["c"]) if row else 0
        if count >= 3:
            conn.execute("UPDATE posts SET status = 'hidden' WHERE id = ?", (post_id,))
    return count


def get_region_stuck(
    region: str = config.REGION,
    days: int = 7,
    k: int = config.STUCK_MIN_K,
) -> list[dict]:
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT concept_tags FROM posts
               WHERE region = ? AND status = 'visible' AND created_at >= ?""",
            (region, cutoff),
        ).fetchall()
    counter: Counter[str] = Counter()
    for row in rows:
        for tag in (row["concept_tags"] or "").split(","):
            tag = tag.strip()
            if tag:
                counter[tag] += 1
    return [
        {"concept": concept, "count": count}
        for concept, count in counter.most_common()
        if count >= k
    ]


# ---------------------------------------------------------------------------
# Recall queue
# ---------------------------------------------------------------------------
def build_recall_from_logs(user_id: str) -> int:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT stuck FROM logs
               WHERE user_id = ? AND stuck IS NOT NULL AND TRIM(stuck) <> ''""",
            (user_id,),
        ).fetchall()
    concepts = []
    seen = set()
    for row in rows:
        concept = " ".join((row["stuck"] or "").split())
        if concept and concept not in seen:
            seen.add(concept)
            concepts.append(concept)
    if not concepts:
        return 0
    created = 0
    today = date.today().isoformat()
    with get_conn() as conn:
        for concept in concepts:
            concept_id = hashlib.md5(concept.encode("utf-8")).hexdigest()[:12]
            cursor = conn.execute(
                """INSERT OR IGNORE INTO recall_queue
                   (id, user_id, concept, concept_id, due_date, interval_days, ease, reps)
                   VALUES (?, ?, ?, ?, ?, 1, 2.5, 0)""",
                (_new_id("recall"), user_id, concept, concept_id, today),
            )
            created += cursor.rowcount
    return created


def get_recall_items(user_id: str, due_only: bool = True) -> list[sqlite3.Row]:
    today = date.today().isoformat()
    sql = "SELECT * FROM recall_queue WHERE user_id = ?"
    params: list[Any] = [user_id]
    if due_only:
        sql += " AND due_date <= ?"
        params.append(today)
    sql += " ORDER BY due_date, concept"
    with get_conn() as conn:
        return conn.execute(sql, params).fetchall()


def count_recall_items(user_id: str) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM recall_queue WHERE user_id = ?", (user_id,)
        ).fetchone()
    return int(row["c"]) if row else 0


def review_recall(item_id: str, quality: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        item = conn.execute("SELECT * FROM recall_queue WHERE id = ?", (item_id,)).fetchone()
        if not item:
            return None
        interval, ease, reps = sm2(
            item["interval_days"], item["ease"], item["reps"], quality
        )
        due = next_due(date.today(), interval).isoformat()
        conn.execute(
            """UPDATE recall_queue
               SET interval_days = ?, ease = ?, reps = ?, due_date = ?, last_reviewed = ?
               WHERE id = ?""",
            (interval, ease, reps, due, _now(), item_id),
        )
    return item


# ---------------------------------------------------------------------------
# Events / data rights
# ---------------------------------------------------------------------------
def log_event(user_id: str | None, name: str, props: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO events (user_id, name, props, created_at) VALUES (?, ?, ?, ?)",
            (user_id, name, props, _now()),
        )


def export_user_data(user_id: str) -> dict:
    with get_conn() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        logs = conn.execute("SELECT * FROM logs WHERE user_id = ?", (user_id,)).fetchall()
        posts = conn.execute("SELECT * FROM posts WHERE user_id = ?", (user_id,)).fetchall()
        reactions = conn.execute("SELECT * FROM reactions WHERE user_id = ?", (user_id,)).fetchall()
        recall = conn.execute("SELECT * FROM recall_queue WHERE user_id = ?", (user_id,)).fetchall()
    return {
        "user": dict(user) if user else None,
        "logs": [dict(row) for row in logs],
        "posts": [dict(row) for row in posts],
        "reactions": [dict(row) for row in reactions],
        "recall": [dict(row) for row in recall],
    }


def delete_all_user_data(user_id: str) -> None:
    with get_conn() as conn:
        post_ids = [
            row["id"] for row in conn.execute("SELECT id FROM posts WHERE user_id = ?", (user_id,))
        ]
        for post_id in post_ids:
            conn.execute("DELETE FROM reactions WHERE post_id = ?", (post_id,))
            conn.execute("DELETE FROM reports WHERE post_id = ?", (post_id,))
        conn.execute("DELETE FROM reactions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM reports WHERE reporter_id = ?", (user_id,))
        conn.execute("DELETE FROM posts WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM logs WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM recall_queue WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM events WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


# ---------------------------------------------------------------------------
# Demo seed
# ---------------------------------------------------------------------------
_SEED_USERS = [
    ("seed-01", "고2_미적분러_1102", 2, "5", "이과"),
    ("seed-02", "고2_영어러_0421", 2, "2", "이과"),
    ("seed-03", "고2_생명러_0731", 2, "3", "이과"),
    ("seed-04", "고1_국어러_0210", 1, "4", "문과"),
    ("seed-05", "고2_데이터러_0515", 2, "5", "이과"),
    ("seed-06", "고2_화학러_0908", 2, "6", "이과"),
]

_SEED_POSTS = [
    ("seed-01", "미적분1", "판별식,이차방정식", "오늘 미적분에서 판별식으로 근의 개수를 판별하는 법을 배웠다. 이차방정식이랑 연결되는 게 신기했다.", 1, 2),
    ("seed-02", "영어2", "관계대명사,소유격", "영어Ⅱ에서 관계대명사 whose가 소유격이라는 걸 이제 알았다. of which랑 헷갈렸는데 예문으로 이해됨.", 2, 5),
    ("seed-03", "세포와물질대사", "세포호흡,ATP", "세포호흡에서 ATP가 왜 중요한지 질문했다. 미토콘드리아가 에너지 공장이라는 말이 이제 이해된다.", 3, 1),
    ("seed-01", "기하", "이차곡선,타원,판별식", "기하 시간에 타원의 접선의 방정식을 유도했다. 계산이 길어서 중간에 부호를 놓쳤다.", 4, 2),
    ("seed-05", "데이터과학", "판다스,groupby", "데이터 과학에서 groupby로 반별 평균을 냈다. 인덱스를 다시 정렬하는 게 아직 어색하다.", 5, 4),
    ("seed-06", "물질과에너지", "이상기체,상태방정식", "물질과 에너지에서 이상기체 상태방정식을 배웠다. PV=nRT에서 단위 환산이 헷갈린다.", 6, 7),
    ("seed-01", "미적분1", "판별식,근의개수", "판별식 문제를 10개 풀었다. D=0일 때 중근이라는 걸 이제 안 틀린다.", 8, 6),
    ("seed-02", "영어2", "관계대명사,whose", "whose 예문을 직접 만들어봤다. 내가 만든 문장이 맞는지 선생님께 물어봐야겠다.", 10, 3),
    ("seed-03", "세포와물질대사", "세포호흡,미토콘드리아", "세포호흡 단계를 그림으로 정리했다. 해당과정이 어디서 일어나는지 다시 봐야 한다.", 12, 1),
    ("seed-04", "독서와작문", "설득전략,논증", "설득하는 글에서 통계 자료를 쓰는 이유를 배웠다. 근거의 신뢰도가 중요하다는 걸 알았다.", 14, 5),
    ("seed-01", "미적분1", "판별식,이차함수", "이차함수 그래프와 판별식의 관계를 연결해서 이해했다.", 16, 6),
    ("seed-02", "영어2", "관계대명사,문법", "관계대명사 계속적 용법을 배웠다. 콤마 하나로 의미가 달라지는 게 신기하다.", 18, 3),
    ("seed-03", "세포와물질대사", "세포호흡,ATP", "ATP 합성 효소의 역할을 정리했다. 아직 세부 단계는 헷갈린다.", 20, 1),
    ("seed-05", "데이터과학", "판다스,데이터정제", "결측치를 채우는 방법을 배웠다. 평균으로 채우는 게 항상 좋은 건 아니라는 걸 알았다.", 22, 4),
    ("seed-06", "물질과에너지", "이상기체,몰", "몰과 부피의 관계를 계산했다. 단위 맞추는 연습이 더 필요하다.", 24, 7),
    ("seed-01", "기하", "판별식,이차곡선", "이차곡선 단원에서 판별식이 다시 나왔다. 수학은 결국 연결되어 있다.", 26, 2),
    ("seed-02", "영어2", "관계대명사,독해", "긴 문장에서 관계대명사가 생략된 경우를 찾았다. 해석이 빨라졌다.", 28, 5),
    ("seed-04", "독서와작문", "주장,근거", "주장과 근거를 구분하는 연습을 했다. 내 글은 근거가 부족했다.", 30, 5),
    ("seed-03", "세포와물질대사", "세포호흡,발효", "발효와 세포호흡의 차이를 배웠다. 산소가 있을 때와 없을 때를 비교했다.", 32, 1),
    ("seed-06", "물질과에너지", "이상기체,기체법칙", "보일 법칙과 샤를 법칙을 하나의 식으로 합치는 과정을 이해했다.", 34, 7),
    ("seed-02", "영어2", "관계대명사,전치사", "관계대명사 앞에 전치사가 오는 문장을 해석했다. in which가 특히 어려웠다.", 36, 3),
    ("seed-03", "세포와물질대사", "세포호흡,해당과정", "해당과정이 세포질에서 일어난다는 걸 그림으로 확인했다.", 38, 1),
]

_SEED_LOGS = [
    ("2026-11-03", 1, "세포와 물질대사", "세포 호흡과 물질대사의 관계를 배웠다.", "질문", "ATP 생성 과정"),
    ("2026-11-03", 2, "기하", "이차곡선의 접선의 방정식을 유도했다.", "문제풀이", "타원 접선의 기울기"),
    ("2026-11-03", 3, "독서와 작문", "설득하는 글의 논증 구조를 분석했다.", "필기", ""),
    ("2026-11-03", 4, "데이터 과학", "pandas groupby로 반별 평균을 계산했다.", "문제풀이", "인덱스 재설정"),
    # 5교시(영어Ⅱ)는 데모에서 직접 기록하는 장면을 위해 비워둔다.
    ("2026-11-03", 6, "미적분Ⅰ", "합성함수의 미분법을 배웠다.", "문제풀이", "연쇄법칙"),
    ("2026-11-03", 7, "물질과 에너지", "이상기체 상태방정식을 배웠다.", "필기", ""),
    ("2026-11-02", 1, "세포와 물질대사", "세포막의 선택적 투과성을 배웠다.", "들음", "능동 수송"),
    ("2026-11-02", 2, "미적분Ⅰ", "판별식으로 근의 개수를 판별했다.", "문제풀이", "판별식"),
    ("2026-11-02", 3, "스포츠 생활1", "배드민턴 복식 규칙을 익혔다.", "들음", ""),
    ("2026-11-02", 4, "윤리와 사상", "공리주의의 기본 원리를 배웠다.", "필기", "최대 행복 원칙"),
    ("2026-11-01", 1, "미적분Ⅰ", "미분계수의 정의를 복습했다.", "문제풀이", "극한"),
    ("2026-11-01", 2, "영어Ⅱ", "본문에서 관계대명사를 찾아 해석했다.", "문제풀이", "관계대명사"),
]


def seed_demo_data() -> None:
    init_db()
    with get_conn() as conn:
        already = conn.execute("SELECT 1 FROM meta WHERE key = 'demo_seeded'").fetchone()
    if already:
        return

    _upsert_school(
        config.DEMO_SCHOOL_CODE,
        config.DEMO_SCHOOL_NAME,
        config.DEMO_OFFICE_CODE,
        config.REGION,
    )
    create_user(
        "고2_기하러_0503",
        config.DEMO_GRADE,
        config.DEMO_CLASS_NO,
        "이과",
        user_id=DEMO_USER_ID,
    )
    create_user("고2_미분러_0217", 2, "2", "이과", user_id=FRIEND_USER_ID)
    for user_id, nickname, grade, class_no, track in _SEED_USERS:
        create_user(nickname, grade, class_no, track, user_id=user_id)

    with get_conn() as conn:
        post_count = conn.execute("SELECT COUNT(*) AS c FROM posts").fetchone()["c"]
    if post_count == 0:
        _seed_posts()
        _seed_reactions()

    with get_conn() as conn:
        log_count = conn.execute(
            "SELECT COUNT(*) AS c FROM logs WHERE user_id = ?", (DEMO_USER_ID,)
        ).fetchone()["c"]
    if log_count == 0:
        _seed_logs()

    build_recall_from_logs(DEMO_USER_ID)
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('demo_seeded', '1')")


def _seed_posts() -> None:
    now = datetime.now()
    with get_conn() as conn:
        for index, (user_id, subject, tags, text, hours_ago, period) in enumerate(_SEED_POSTS, start=1):
            created = (now - timedelta(hours=hours_ago)).isoformat(timespec="seconds")
            conn.execute(
                """INSERT OR IGNORE INTO posts
                   (id, log_id, user_id, public_text, subject_norm, concept_tags,
                    grade, region, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'visible', ?)""",
                (
                    f"seed-post-{index:02d}",
                    f"seed-post-log-{index:02d}",
                    user_id,
                    text,
                    subject,
                    tags,
                    config.DEMO_GRADE,
                    config.REGION,
                    created,
                ),
            )


def _seed_reactions() -> None:
    with get_conn() as conn:
        for index in range(1, len(_SEED_POSTS) + 1):
            post_id = f"seed-post-{index:02d}"
            for offset in range(index % 3):
                user = _SEED_USERS[(index + offset) % len(_SEED_USERS)][0]
                conn.execute(
                    """INSERT OR IGNORE INTO reactions (id, post_id, user_id, type, created_at)
                       VALUES (?, ?, ?, 'cheer', ?)""",
                    (f"seed-reaction-{index:02d}-{offset}", post_id, user, _now()),
                )


def _seed_logs() -> None:
    with get_conn() as conn:
        for index, (day, period, subject_raw, learned, activity, stuck) in enumerate(_SEED_LOGS, start=1):
            conn.execute(
                """INSERT OR IGNORE INTO logs
                   (id, user_id, date, period, subject_raw, subject_norm, learned, activity, stuck, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"seed-log-{index:02d}",
                    DEMO_USER_ID,
                    day,
                    period,
                    subject_raw,
                    normalize_subject(subject_raw),
                    learned,
                    activity,
                    stuck,
                    f"{day}T18:00:00",
                ),
            )
