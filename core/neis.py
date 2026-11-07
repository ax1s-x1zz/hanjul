"""NEIS Open API client and parsers."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

import requests

from . import config

BASE_URL = "https://open.neis.go.kr/hub"

_EVENT_KEYWORDS = ("현장체험", "휴업", "재량", "행사", "축제", "체육대회", "수련")
_EXAM_KEYWORDS = ("중간고사", "기말고사", "모의고사", "학력평가", "수행평가", "지필평가", "고사")

_SUBJECT_MAP = {
    "수학Ⅰ": "수학1",
    "수학Ⅱ": "수학2",
    "수학1": "수학1",
    "수학2": "수학2",
    "미적분Ⅰ": "미적분1",
    "미적분Ⅱ": "미적분2",
    "미적분1": "미적분1",
    "미적분2": "미적분2",
    "화학Ⅰ": "화학1",
    "화학Ⅱ": "화학2",
    "화학1": "화학1",
    "화학2": "화학2",
    "물리학Ⅰ": "물리학1",
    "물리학Ⅱ": "물리학2",
    "생명과학Ⅰ": "생명과학1",
    "생명과학Ⅱ": "생명과학2",
    "지구과학Ⅰ": "지구과학1",
    "지구과학Ⅱ": "지구과학2",
    "영어Ⅰ": "영어1",
    "영어Ⅱ": "영어2",
    "영어1": "영어1",
    "영어2": "영어2",
    "국어Ⅰ": "국어1",
    "국어Ⅱ": "국어2",
    "독서와 작문": "독서와작문",
    "영어 독해와 작문": "영어독해와작문",
    "물질과 에너지": "물질과에너지",
    "역학과 에너지": "역학과에너지",
    "세포와 물질대사": "세포와물질대사",
    "데이터 과학": "데이터과학",
    "스포츠 생활1": "스포츠생활1",
    "스포츠 생활": "스포츠생활",
    "윤리와 사상": "윤리와사상",
}


class NeisError(RuntimeError):
    """Raised when the NEIS API cannot be used."""


@dataclass(frozen=True)
class TimetableRow:
    period: int
    subject_raw: str
    subject: str
    room: str
    is_event: bool


def normalize_subject(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return "미지정"
    return _SUBJECT_MAP.get(text, re.sub(r"\s+", "", text))


def is_event_subject(raw: str) -> bool:
    return any(keyword in (raw or "") for keyword in _EVENT_KEYWORDS)


def parse_rows(payload: Any, service: str) -> list[dict]:
    """Extract rows from a NEIS JSON payload.

    Success shape:
      {"hisTimetable": [{"head": [...]}, {"row": [...]}]}
    Failure shape:
      {"RESULT": {"CODE": "INFO-200", "MESSAGE": "..."}}
    """
    if not isinstance(payload, dict):
        return []
    block = payload.get(service)
    if isinstance(block, list):
        for item in block:
            if isinstance(item, dict) and isinstance(item.get("row"), list):
                return item["row"]
    return []


def _request(service: str, params: dict[str, Any]) -> dict:
    if not config.NEIS_KEY:
        raise NeisError("NEIS_KEY가 설정되지 않았습니다. .env를 확인하세요.")
    query = {
        "KEY": config.NEIS_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        **params,
    }
    try:
        response = requests.get(f"{BASE_URL}/{service}", params=query, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        # Never include the request URL here: it contains the API key.
        raise NeisError(f"NEIS 응답 오류({status})") from exc
    except requests.RequestException:
        raise NeisError("NEIS 연결에 실패했습니다. 잠시 후 다시 시도해주세요.") from None
    except ValueError:
        raise NeisError("NEIS 응답을 해석할 수 없습니다.") from None


def fetch_schools(name: str, office_code: str | None = None) -> list[dict]:
    params: dict[str, Any] = {"SCHUL_NM": name}
    if office_code:
        params["ATPT_OFCDC_SC_CODE"] = office_code
    payload = _request("schoolInfo", params)
    rows = parse_rows(payload, "schoolInfo")
    result = []
    for row in rows:
        result.append(
            {
                "office_code": row.get("ATPT_OFCDC_SC_CODE", ""),
                "school_code": row.get("SD_SCHUL_CODE", ""),
                "name": row.get("SCHUL_NM", ""),
                "address": row.get("ORG_RDNMA", ""),
                "region": row.get("LCTN_SC_NM", ""),
                "kind": row.get("SCHUL_KND_SC_NM", ""),
            }
        )
    return result


def fetch_timetable(
    office_code: str,
    school_code: str,
    day: date | str,
    grade: int,
    class_no: str,
) -> list[TimetableRow]:
    ymd = day.strftime("%Y%m%d") if isinstance(day, date) else str(day).replace("-", "")
    payload = _request(
        "hisTimetable",
        {
            "ATPT_OFCDC_SC_CODE": office_code,
            "SD_SCHUL_CODE": school_code,
            "ALL_TI_YMD": ymd,
            "GRADE": str(grade),
            "CLASS_NM": str(class_no),
        },
    )
    rows = parse_rows(payload, "hisTimetable")
    result: list[TimetableRow] = []
    for row in rows:
        raw = (row.get("ITRT_CNTNT") or "").strip()
        try:
            period = int(row.get("PERIO"))
        except (TypeError, ValueError):
            continue
        result.append(
            TimetableRow(
                period=period,
                subject_raw=raw,
                subject=normalize_subject(raw),
                room=(row.get("CLRM_NM") or "").strip(),
                is_event=is_event_subject(raw),
            )
        )
    return sorted(result, key=lambda item: item.period)


def fetch_schedule(
    office_code: str,
    school_code: str,
    start: date | str,
    end: date | str,
) -> list[dict]:
    def fmt(value: date | str) -> str:
        return value.strftime("%Y%m%d") if isinstance(value, date) else str(value).replace("-", "")

    payload = _request(
        "SchoolSchedule",
        {
            "ATPT_OFCDC_SC_CODE": office_code,
            "SD_SCHUL_CODE": school_code,
            "AA_FROM_YMD": fmt(start),
            "AA_TO_YMD": fmt(end),
        },
    )
    rows = parse_rows(payload, "SchoolSchedule")
    result = []
    for row in rows:
        result.append(
            {
                "date": row.get("AA_YMD", ""),
                "event": (row.get("EVENT_NM") or "").strip(),
                "detail": (row.get("EVENT_CNTNT") or "").strip(),
                "holiday": (row.get("SBTR_DD_SC_NM") or "").strip(),
            }
        )
    return result


def find_exams(events: list[dict]) -> list[dict]:
    exams = []
    for event in events:
        name = event.get("event", "")
        if not name or "휴업" in name:
            continue
        if any(keyword in name for keyword in _EXAM_KEYWORDS):
            exams.append(event)
    return exams


def demo_exam() -> dict:
    return {
        "date": config.DEMO_EXAM_DATE.replace("-", ""),
        "event": config.DEMO_EXAM_NAME,
        "detail": "",
        "holiday": "",
        "is_demo": True,
    }


def next_exam(events: list[dict], today: date | None = None) -> dict | None:
    today = today or date.today()
    candidates = []
    for event in find_exams(events):
        try:
            event_date = datetime.strptime(event["date"], "%Y%m%d").date()
        except (KeyError, ValueError):
            continue
        if event_date >= today:
            candidates.append((event_date, event))
    if not candidates:
        return None
    candidates.sort(key=lambda pair: pair[0])
    return candidates[0][1]


def date_range(days: int, start: date | None = None) -> tuple[date, date]:
    start = start or date.today()
    return start, start + timedelta(days=days)
