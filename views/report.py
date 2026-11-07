"""Private weekly report and anonymous regional stuck concepts (V2)."""
from __future__ import annotations

from collections import Counter
from datetime import date

import streamlit as st

from core import config, db, llm, ui


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
        st.markdown(ui.helper("이번 주 기록이 아직 없습니다."), unsafe_allow_html=True)
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

    st.write("")
    st.markdown(
        ui.metrics(
            [
                (len(logs), "기록한 수업"),
                (len(set(days)), "기록한 날"),
                (_streak(days), "최장 연속"),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown(ui.section("이번 주 요약"), unsafe_allow_html=True)
    st.markdown(
        ui.summary(llm.weekly_summary(len(logs), len(subject_counts), stuck_top)),
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.markdown(ui.section("과목"), unsafe_allow_html=True)
        subject_max = max(subject_counts.values(), default=1)
        for name, count in subject_counts.most_common():
            st.markdown(ui.bar_row(name, count, subject_max, "회"), unsafe_allow_html=True)
    with right:
        st.markdown(ui.section("활동"), unsafe_allow_html=True)
        activity_max = max(activity_counts.values(), default=1)
        for name, count in activity_counts.most_common():
            st.markdown(ui.bar_row(name, count, activity_max, "회"), unsafe_allow_html=True)

    st.markdown(ui.section("막힌 개념"), unsafe_allow_html=True)
    if stuck_top:
        with st.container(key="stuck_group"):
            for rank, (concept, count) in enumerate(stuck_top, start=1):
                with st.container(key=f"stuck_{rank}"):
                    st.markdown(
                        f"<div class='hj-row'><span class='hj-row-num'>{rank}</span>"
                        f"<div><div class='hj-row-title'>{ui.esc(concept)}</div>"
                        f"<div class='hj-row-sub'>{count}회 막힘</div></div></div>",
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown(ui.helper("막힌 개념을 기록하면 여기에 모입니다."), unsafe_allow_html=True)


def _region_stuck() -> None:
    rows = db.get_region_stuck(config.REGION, days=7, k=config.STUCK_MIN_K)
    st.markdown(
        ui.helper(
            "공개 글의 개념 태그를 익명 집계합니다. "
            f"{config.STUCK_MIN_K}명 이상일 때만 표시합니다."
        ),
        unsafe_allow_html=True,
    )
    if not rows:
        st.markdown(ui.helper("아직 충분히 쌓인 개념이 없습니다."), unsafe_allow_html=True)
        return

    max_count = max((row["count"] for row in rows), default=1)
    st.markdown(ui.section("이번 주 광명의 막힘"), unsafe_allow_html=True)
    for row in rows[:10]:
        st.markdown(
            ui.bar_row(row["concept"], row["count"], max_count, "명"),
            unsafe_allow_html=True,
        )


def render(user) -> None:
    tab = st.session_state.get("report_tab", "mine")
    with st.container(key="report_tabs"):
        c1, c2 = st.columns(2)
        if c1.button(
            "내 기록",
            key="tab_mine",
            type="primary" if tab == "mine" else "secondary",
            use_container_width=True,
        ):
            st.session_state["report_tab"] = "mine"
            st.rerun()
        if c2.button(
            "지역 막힘",
            key="tab_region",
            type="primary" if tab == "region" else "secondary",
            use_container_width=True,
        ):
            st.session_state["report_tab"] = "region"
            st.rerun()

    if tab == "mine":
        _my_report(user)
    else:
        _region_stuck()
