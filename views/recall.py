"""Exam D-day and spaced repetition recall."""
from __future__ import annotations

from datetime import date, datetime, timedelta

import streamlit as st

from core import config, db, neis, ui


def _get_exam() -> dict | None:
    if "exam_cache" not in st.session_state:
        exams: list[dict] = []
        try:
            events = neis.fetch_schedule(
                config.DEMO_OFFICE_CODE,
                config.DEMO_SCHOOL_CODE,
                date.today(),
                date.today() + timedelta(days=120),
            )
            exams = neis.find_exams(events)
        except Exception:
            exams = []
        if not exams and config.DEMO_MODE:
            exams = [neis.demo_exam()]
        st.session_state["exam_cache"] = exams
    exams = st.session_state.get("exam_cache", [])
    return neis.next_exam(exams, date.today())


def _dday_label(exam_date: date) -> str:
    delta = (exam_date - date.today()).days
    if delta == 0:
        return "D-DAY"
    if delta > 0:
        return f"D-{delta}"
    return f"D+{abs(delta)}"


def render(user) -> None:
    st.markdown(
        ui.page_header("시험 리콜", "막힌 개념만 다시 꺼내봅니다.", "SM-2"),
        unsafe_allow_html=True,
    )

    exam = _get_exam()
    if exam:
        exam_date = datetime.strptime(exam["date"], "%Y%m%d").date()
        st.markdown(
            ui.dday_card(
                exam["event"],
                _dday_label(exam_date),
                exam_date.isoformat(),
                bool(exam.get("is_demo")),
            ),
            unsafe_allow_html=True,
        )
        if exam.get("is_demo"):
            st.caption("데모 일정입니다. 실제 학사일정이 등록되면 자동으로 대체됩니다.")
    else:
        st.info("예정된 시험이 없습니다. 그래도 오늘의 복습 카드는 사용할 수 있습니다.")

    db.build_recall_from_logs(user["id"])
    due_items = db.get_recall_items(user["id"], due_only=True)
    total = db.count_recall_items(user["id"])

    if total == 0:
        st.info("막힌 개념을 기록하면 복습 카드가 자동으로 만들어집니다.")
        if st.button("오늘 기록하러 가기", type="primary", use_container_width=True):
            st.session_state["nav"] = "오늘"
            st.rerun()
        return

    c1, c2 = st.columns(2)
    c1.metric("오늘 복습", f"{len(due_items)}개")
    c2.metric("전체 카드", f"{total}개")
    st.progress(
        (total - len(due_items)) / total if total else 0,
        text=f"오늘 {len(due_items)}개 · 다음 복습 대기 {total - len(due_items)}개",
    )

    if not due_items:
        st.success("오늘 복습할 카드가 없습니다. 다음 복습일을 기다려주세요.")
        return

    st.markdown("#### 오늘의 복습 카드")
    for item in due_items:
        with st.container(border=True):
            st.markdown(f"**{item['concept']}**")
            st.caption(
                f"복습 {item['reps']}회 · 다음 복습 {item['due_date']} "
                f"· 간격 {item['interval_days']}일"
            )
            c1, c2 = st.columns(2)
            if c1.button(
                "기억남",
                key=f"recall-yes-{item['id']}",
                type="primary",
                use_container_width=True,
            ):
                db.review_recall(item["id"], 5)
                st.toast("다음 복습일을 늘렸습니다.")
                st.rerun()
            if c2.button(
                "헷갈림",
                key=f"recall-no-{item['id']}",
                use_container_width=True,
            ):
                db.review_recall(item["id"], 2)
                st.toast("내일 다시 복습합니다.")
                st.rerun()

    with st.expander("전체 복습 카드 보기"):
        for item in db.get_recall_items(user["id"], due_only=False):
            st.markdown(
                f"- **{item['concept']}** · 다음 복습 {item['due_date']} "
                f"(간격 {item['interval_days']}일)"
            )
