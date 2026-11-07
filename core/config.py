"""Application configuration and environment loading."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def _load_env_file(path: Path) -> dict[str, str]:
    """Parse KEY=VALUE lines, tolerating spaces around '=' and BOM."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


_FILE_ENV = _load_env_file(ENV_PATH)

try:  # optional: python-dotenv
    from dotenv import load_dotenv

    load_dotenv(ENV_PATH, override=False)
except Exception:  # pragma: no cover - optional dependency
    pass


def env(key: str, default: str = "") -> str:
    value = os.getenv(key)
    if value is None or value == "":
        value = _FILE_ENV.get(key, default)
    return str(value).strip()


APP_NAME = "한줄"
APP_VERSION = "0.1.0"
TAGLINE = "오늘 배운 한 줄, 광명의 배움 피드"

REGION = env("DEMO_REGION", "경기도 광명시")

DEMO_MODE = env("DEMO_MODE", "1") == "1"
DEMO_OFFICE_CODE = env("DEMO_ATPT_OFCDC_SC_CODE", "J10")
DEMO_SCHOOL_CODE = env("DEMO_SD_SCHUL_CODE", "7530207")
DEMO_SCHOOL_NAME = env("DEMO_SCHOOL_NAME", "진성고등학교")
DEMO_GRADE = int(env("DEMO_GRADE", "2"))
DEMO_CLASS_NO = env("DEMO_CLASS_NO", "5")

# 2026-11-03 (Tue) is a real school day with 7 periods for grade 2 class 5.
DEMO_DATE = env("DEMO_DATE", "2026-11-03")
# The school schedule has no exam in Nov-Dec, so the recall screen marks this as a demo event.
DEMO_EXAM_DATE = env("DEMO_EXAM_DATE", "2026-12-14")
DEMO_EXAM_NAME = env("DEMO_EXAM_NAME", "2학기 기말고사")

NEIS_KEY = env("NEIS_KEY")
OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_MODEL = env("OPENAI_MODEL", "gpt-4o-mini")

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(env("HANJUL_DB", str(DATA_DIR / "hanjul.db")))

SUBJECTS = [
    "국어",
    "수학",
    "영어",
    "한국사",
    "사회",
    "과학",
    "기타",
]

ACTIVITIES = ["들음", "필기", "문제풀이", "질문", "이해못함"]

STUCK_MIN_K = 5
