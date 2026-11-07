"""Privacy helpers: PII masking, profanity guard, k-anonymity."""
from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"\b0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}\b")
_RRN_RE = re.compile(r"\b\d{6}[-.\s]?[1-4]\d{6}\b")
_URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
_LONG_DIGITS_RE = re.compile(r"\b\d{6,}\b")
_TEACHER_RE = re.compile(r"([가-힣]{2,4})\s*선생님")

_PROFANITY = {
    "씨발",
    "시발",
    "개새끼",
    "병신",
    "지랄",
    "좆",
    "꺼져",
    "죽어라",
    "패드립",
}


def contains_profanity(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text or "").lower()
    return any(word in normalized for word in _PROFANITY)


def mask_school(text: str, school_name: str | None = None) -> str:
    if not school_name:
        return text
    name = school_name.strip()
    if not name:
        return text
    # "진성고등학교" and "진성고" both masked.
    short = re.sub(r"(고등학교|중학교|초등학교)$", "", name)
    result = text.replace(name, "○○고")
    if short and short != name:
        result = result.replace(short, "○○")
    return result


def strip_pii(text: str, school_name: str | None = None) -> str:
    """Remove or mask direct identifiers before a public post or LLM call."""
    if not text:
        return ""
    result = text
    result = mask_school(result, school_name)
    result = _EMAIL_RE.sub("[이메일]", result)
    result = _RRN_RE.sub("[주민번호]", result)
    result = _PHONE_RE.sub("[전화번호]", result)
    result = _URL_RE.sub("[링크]", result)
    result = _TEACHER_RE.sub("선생님", result)
    result = _LONG_DIGITS_RE.sub("[숫자]", result)
    result = re.sub(r"[ \t]+", " ", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def sanitize_for_public(text: str, school_name: str | None = None) -> tuple[str, bool]:
    clean = strip_pii(text, school_name=school_name)
    return clean, clean != (text or "").strip()


def k_anonymized(count: int, k: int = 5) -> bool:
    return count >= k
