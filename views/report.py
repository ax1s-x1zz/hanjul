"""Private weekly report and anonymous regional stuck concepts."""
from __future__ import annotations

from collections import Counter
from datetime import date

import pandas as pd
import streamlit as st

from core import config, db, llm


def _streak(days: list[str]) -> int:
    unique = sorted({day for day in days if day})
    if not unique:
        return 0
    best = current = 1
    for previous, nxt in zip(unique, unique[1:]):
        try:
            gap = (date.fromisoformat(nxt) - date.fromisoformat(previous)).days
        except ValueError:
            continue
        if gap == 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def _my_report(user) -> None:
    logs = db.get_week_logs(user["id"], days=7)
    if not logs:
        st.info("이번 주 기록이 아직 없습니다. 수업 직후 한 줄부터 남겨보세요.")
        if st.button("오늘 기록하러 가기", type="primary", use_container_width=True):
            st.session_state["nav"] = "오늘"
            st.rerun()
        return

    subject_counts = Counter(log["subject_norm"] or "기타" for log in logs)
    activity_counts = Counter(log["activity"] or "미입력" for log in logs)
    stuck_counts = Counter(
        " ".join((log["stuck"] or "").split())
        for log in logs
        if (log["stuck"] or "").strip()
    )
    stuck_top = stuck_counts.most_common(3)
    days = [log["date"] for log in logs]

    c1, c2, c3 = st.columns(3)
    c1.metric("기록한 수업", f"{len(logs)}개")
    c2.metric("기록한 날", f"{len(set(days))}일")
    c3.metric("최장 연속", f"{_streak(days)}일")

    st.markdown("#### 이번 주 한 줄 요약")
    st.success(llm.weekly_summary(len(logs), len(subject_counts), stuck_top))

    left, right = st.columns(2)
    with left:
        st.markdown("##### 과목 분포")
        df = pd.DataFrame(
            {"기록 수": [subject_counts[name] for name in subject_counts]},
            index=list(subject_counts.keys()),
        )
        st.bar_chart(df)
    with right:
        st.markdown("##### 활동 분포")
        df = pd.DataFrame(
            {"기록 수": [activity_counts[name] for name in activity_counts]},
            index=list(activity_counts.keys()),
        )
        st.bar_chart(df)

    st.markdown("#### 막힌 개념 TOP 3")
    if stuck_top:
        for rank, (concept, count) in enumerate(stuck_top, start=1):
            st.markdown(f"**{rank}. {concept}** · {count}회")
        st.caption("시험 전에 이 개념부터 다시 확인해보세요.")
    else:
        st.caption("막힌 개념을 기록하면 여기에 모입니다.")


def _region_stuck() -> None:
    rows = db.get_region_stuck(config.REGION, days=7, k=config.STUCK_MIN_K)
    st.caption(
        "공개 글의 개념 태그를 익명 집계합니다. "
        f"{config.STUCK_MIN_K}명 이상일 때만 표시합니다."
    )
    if not rows:
        st.info("아직 충분히 쌓인 개념이 없습니다.")
        return

    df = pd.DataFrame(
        {"막힌 학생 수": [row["count"] for row in rows]},
        index=[row["concept"] for row in rows],
    )
    st.bar_chart(df)
    st.markdown("#### 이번 주 광명의 막힘")
    for rank, row in enumerate(rows[:10], start=1):
        st.markdown(f"**{rank}. {row['concept']}** · {row['count']}명")


def render(user) -> None:
    st.markdown("### 📊 리포트")
    st.caption("내 리포트는 나만 볼 수 있습니다. 지역 막힘은 익명 집계입니다.")
    tab_mine, tab_region = st.tabs(["내 리포트", "지역 막힘"])
    with tab_mine:
        _my_report(user)
    with tab_region:
        _region_stuck()
