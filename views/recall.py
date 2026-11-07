"""Exam D-day and spaced repetition (V2)."""
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
    st.write("")
    exam = _get_exam()
    if exam:
        try:
            exam_date = datetime.strptime(exam["date"], "%Y%m%d").date()
        except (KeyError, ValueError):
            exam_date = date.today()
        st.markdown(
            ui.dday_card(
                exam.get("event", "시험"),
                _dday_label(exam_date),
                exam_date.isoformat(),
                bool(exam.get("is_demo")),
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(ui.helper("예정된 시험이 없습니다."), unsafe_allow_html=True)

    db.build_recall_from_logs(user["id"])
    items = db.get_recall_items(user["id"], due_only=True)
    total = db.count_recall_items(user["id"])

    st.write("")
    st.markdown(
        ui.metrics(
            [
                (len(items), "오늘 복습"),
                (total, "전체 카드"),
                (max(total - len(items), 0), "다음 대기"),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown(ui.section("오늘의 복습"), unsafe_allow_html=True)
    if not items:
        st.markdown(ui.helper("오늘 복습할 카드가 없습니다."), unsafe_allow_html=True)
    else:
        with st.container(key="recall_group"):
            for item in items:
                with st.container(key=f"recall_{item['id']}"):
                    st.markdown(
                        f"<div class='hj-row'><div><div class='hj-row-title'>{ui.esc(item['concept'])}</div>"
                        f"<div class='hj-row-sub'>복습 {item['reps']}회 · 다음 {item['due_date']}</div></div></div>",
                        unsafe_allow_html=True,
                    )
                    c1, c2 = st.columns(2)
                    if c1.button(
                        "기억남",
                        key=f"recall_yes_{item['id']}",
                        use_container_width=True,
                    ):
                        db.review_recall(item["id"], 5)
                        st.toast("다음 복습일을 늘렸습니다.")
                        st.rerun()
                    if c2.button(
                        "헷갈림",
                        key=f"recall_no_{item['id']}",
                        use_container_width=True,
                    ):
                        db.review_recall(item["id"], 2)
                        st.toast("내일 다시 복습합니다.")
                        st.rerun()

    all_items = db.get_recall_items(user["id"], due_only=False)
    if all_items:
        with st.expander("전체 복습 카드 보기"):
            for item in all_items:
                st.markdown(
                    f"<div class='hj-row'><div><div class='hj-row-title'>{ui.esc(item['concept'])}</div>"
                    f"<div class='hj-row-sub'>다음 {item['due_date']} · 간격 {item['interval_days']}일</div></div></div>",
                    unsafe_allow_html=True,
                )
