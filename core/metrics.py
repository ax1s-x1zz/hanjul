"""Lightweight product analytics."""
from __future__ import annotations

import json

from . import db


def track(user_id: str | None, name: str, **props) -> None:
    try:
        db.log_event(user_id, name, json.dumps(props, ensure_ascii=False))
    except Exception:
        # Analytics must never break the product.
        pass
