from datetime import date

from core import recall


def test_sm2_success_progression():
    interval, ease, reps = recall.sm2(1, 2.5, 0, 5)
    assert (interval, ease, reps) == (1, 2.6, 1)

    interval, ease, reps = recall.sm2(interval, ease, reps, 5)
    assert (interval, ease, reps) == (3, 2.7, 2)

    interval, ease, reps = recall.sm2(interval, ease, reps, 5)
    assert interval == 8
    assert ease == 2.8
    assert reps == 3


def test_sm2_failure_resets():
    interval, ease, reps = recall.sm2(8, 2.8, 3, 2)
    assert interval == 1
    assert ease == 2.6
    assert reps == 0
    assert ease >= 1.3


def test_days_until():
    assert recall.days_until(date(2026, 12, 14), date(2026, 11, 7)) == 37
    assert recall.days_until(date(2026, 11, 7), date(2026, 11, 7)) == 0
