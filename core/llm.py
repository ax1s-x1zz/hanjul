"""AI assist with strict guardrails and deterministic fallbacks.

The AI is allowed to organize and ask questions.
It is NOT allowed to write the student's entry or give exam answers.
"""
from __future__ import annotations

import hashlib
import re

from . import config, privacy

_CACHE: dict[str, str] = {}

_KEYWORDS = {
    "판별식": ["판별식", "이차방정식", "근의 개수"],
    "미분": ["미분", "도함수", "연쇄법칙"],
    "적분": ["적분", "부정적분", "정적분"],
    "관계대명사": ["관계대명사", "whose", "of which"],
    "세포호흡": ["세포호흡", "ATP", "미토콘드리아"],
    "이상기체": ["이상기체", "PV=nRT", "상태방정식"],
    "판다스": ["판다스", "groupby", "데이터프레임"],
    "이차곡선": ["이차곡선", "타원", "포물선"],
}


def _client():
    if not config.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        return OpenAI(api_key=config.OPENAI_API_KEY, timeout=5.0)
    except Exception:
        return None


def _call(system: str, user: str, max_tokens: int = 80) -> str | None:
    cache_key = hashlib.sha256((system + "\n" + user).encode("utf-8")).hexdigest()
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    client = _client()
    if client is None:
        return None
    try:
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        text = (response.choices[0].message.content or "").strip()
        if text:
            _CACHE[cache_key] = text
            return text
    except Exception:
        return None
    return None


def rule_based_tags(text: str, subject: str) -> list[str]:
    tags: list[str] = []
    lowered = (text or "").lower()
    for tag, words in _KEYWORDS.items():
        if any(word.lower() in lowered for word in words):
            tags.append(tag)
    if not tags and subject:
        tags.append(subject)
    return tags[:3]


def suggest_tags(text: str, subject: str) -> list[str]:
    """Return 1-3 concept tags. Falls back to keywords when AI is unavailable."""
    clean = privacy.strip_pii(text, school_name=config.DEMO_SCHOOL_NAME)
    if not clean:
        return rule_based_tags(text, subject)
    result = _call(
        "너는 고등학생의 수업 기록에서 개념 태그만 뽑는 도구다. "
        "정답이나 설명을 쓰지 말고, 쉼표로 구분된 개념 태그 1~3개만 출력해라. "
        "예: 판별식,이차방정식",
        f"과목: {subject}\n기록: {clean}",
        max_tokens=40,
    )
    if not result:
        return rule_based_tags(text, subject)
    tags = [re.sub(r"[^0-9A-Za-z가-힣 ]", "", tag).strip() for tag in re.split(r"[,\n]", result)]
    tags = [tag for tag in tags if tag][:3]
    return tags or rule_based_tags(text, subject)


def weekly_summary(total_logs: int, subjects: int, stuck_top: list[tuple[str, int]]) -> str:
    """Return a 3-sentence private weekly summary."""
    if total_logs <= 0:
        return "이번 주 기록이 아직 없습니다. 수업 직후 한 줄부터 남겨보세요."
    result = _call(
        "너는 학생의 주간 학습 기록을 3문장 이내로 정리하는 도우미다. "
        "칭찬은 1문장만, 나머지는 관찰과 다음 행동 제안에 써라. "
        "성적이나 등수를 언급하지 마라.",
        (
            f"기록 수: {total_logs}\n과목 수: {subjects}\n"
            f"막힘 상위: {', '.join(f'{name}({count})' for name, count in stuck_top[:3])}"
        ),
        max_tokens=160,
    )
    if result:
        return result
    top = ", ".join(name for name, _ in stuck_top[:3]) or "아직 없음"
    return (
        f"이번 주 {total_logs}개의 수업을 기록했습니다. "
        f"가장 자주 막힌 개념은 {top}입니다. "
        "시험 전에 이 개념부터 다시 확인해보세요."
    )


def question_card(stuck: str) -> str:
    """Turn a stuck note into a polite question for the teacher."""
    clean = privacy.strip_pii(stuck, school_name=config.DEMO_SCHOOL_NAME)
    if not clean:
        return ""
    result = _call(
        "너는 학생이 선생님께 물어볼 질문을 다듬는 도우미다. "
        "정답을 주지 말고, 질문 한 문장만 만들어라.",
        f"막힌 내용: {clean}",
        max_tokens=80,
    )
    return result or f"선생님, {clean} 부분이 아직 헷갈립니다. 조금 더 설명해주실 수 있나요?"
