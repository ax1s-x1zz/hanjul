"""Spaced repetition (SM-2) and date helpers."""
from __future__ import annotations

from datetime import date, datetime, timedelta


def sm2(interval_days: int, ease: float, reps: int, quality: int) -> tuple[int, float, int]:
    """Return (next_interval, next_ease, next_reps).

    quality: 0-5. We use 5 for "remembered" and 2 for "confused".
    """
    interval_days = max(1, int(interval_days or 1))
    ease = float(ease or 2.5)
    reps = max(0, int(reps or 0))

    if quality < 3:
        reps = 0
        interval_days = 1
        ease = max(1.3, ease - 0.2)
    else:
        if reps == 0:
            interval_days = 1
        elif reps == 1:
            interval_days = 3
        else:
            interval_days = max(1, round(interval_days * ease))
        reps += 1
        ease = min(2.8, ease + 0.1)

    return interval_days, round(ease, 2), reps


def next_due(today: date, interval_days: int) -> date:
    return today + timedelta(days=max(1, int(interval_days)))


def days_until(target: date, today: date | None = None) -> int:
    today = today or date.today()
    return (target - today).days


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


def iso_today() -> str:
    return date.today().isoformat()
