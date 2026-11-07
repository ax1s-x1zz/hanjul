"""Small shared utilities."""
from __future__ import annotations

import random
import re
from datetime import date, datetime

_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
_NOUNS = ["기하러", "미적분러", "영어러", "생명러", "데이터러", "화학러", "문학러", "탐구러"]


def make_nickname(grade: int) -> str:
    return f"고{grade}_{random.choice(_NOUNS)}_{random.randint(1000, 9999)}"


def sanitize_nickname(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z가-힣_]", "", value or "")
    return value[:20] or make_nickname(1)


def time_ago(iso_value: str) -> str:
    try:
        then = datetime.fromisoformat(iso_value)
    except (TypeError, ValueError):
        return ""
    delta = datetime.now() - then
    seconds = max(0, int(delta.total_seconds()))
    if seconds < 60:
        return "방금 전"
    if seconds < 3600:
        return f"{seconds // 60}분 전"
    if seconds < 86400:
        return f"{seconds // 3600}시간 전"
    return f"{seconds // 86400}일 전"


def format_kr_date(value: date | str) -> str:
    if isinstance(value, str):
        value = datetime.strptime(value[:10], "%Y-%m-%d").date()
    return f"{value.month}월 {value.day}일 ({_WEEKDAYS[value.weekday()]})"


def format_neis_date(value: str) -> str:
    try:
        return format_kr_date(datetime.strptime(value, "%Y%m%d").date())
    except (TypeError, ValueError):
        return value


def pct(part: int, total: int) -> int:
    if total <= 0:
        return 0
    return round(part / total * 100)
