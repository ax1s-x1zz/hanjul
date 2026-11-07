"""Today's timetable and the 10-second log editor (V2)."""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from core import config, db, llm, metrics, neis, privacy, ui, utils

_WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]


def _week_days(base: date) -> list[date]:
    monday = base - timedelta(days=base.weekday())
    return [monday + timedelta(days=offset) for offset in range(5)]


def _long_date(day: date) -> str:
    return f"{day.month}월 {day.day}일 {_WEEKDAY_KO[day.weekday()]}요일"


def _load_rows(user, day: str) -> tuple[list[dict], str | None]:
    cached = db.get_timetable_cache(
        user["school_code"] or config.DEMO_SCHOOL_CODE,
        day,
        int(user["grade"]),
        str(user["class_no"] or config.DEMO_CLASS_NO),
    )
    if cached:
        return cached, None

    try:
        api_rows = neis.fetch_timetable(
            config.DEMO_OFFICE_CODE,
            user["school_code"] or config.DEMO_SCHOOL_CODE,
            day,
            int(user["grade"]),
            str(user["class_no"] or config.DEMO_CLASS_NO),
        )
    except neis.NeisError as exc:
        return [], str(exc)

    if not api_rows:
        return [], None

    db.save_timetable_cache(
        user["school_code"] or config.DEMO_SCHOOL_CODE,
        day,
        int(user["grade"]),
        str(user["class_no"] or config.DEMO_CLASS_NO),
        api_rows,
    )
    return [
        {
            "period": row.period,
            "subject_raw": row.subject_raw,
            "subject_norm": row.subject,
            "room": row.room,
            "is_event": 1 if row.is_event else 0,
        }
        for row in api_rows
    ], None


def _render_pending(user) -> None:
    pending = st.session_state.get("pending_publish")
    if not pending:
        return

    st.markdown(ui.section("공개 미리보기"), unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(ui.summary(pending["text"]), unsafe_allow_html=True)
        if pending.get("tags"):
            st.markdown(ui.tags(pending["tags"]), unsafe_allow_html=True)
        if pending.get("changed"):
            st.caption("개인정보로 보이는 부분을 자동으로 가렸습니다.")
        st.caption("학교명·실명은 포함되지 않습니다.")

        col1, col2 = st.columns(2)
        if col1.button("게시", type="primary", use_container_width=True):
            db.replace_post_for_log(
                pending["log_id"],
                user["id"],
                pending["text"],
                pending["subject_norm"],
                pending["tags"],
                int(user["grade"]),
            )
            metrics.track(user["id"], "post_publish", subject=pending["subject_norm"])
            st.session_state.pop("pending_publish", None)
            st.session_state.pop("editing", None)
            st.toast("광명 피드에 게시했습니다.")
            st.rerun()
        if col2.button("취소", use_container_width=True):
            st.session_state.pop("pending_publish", None)
            st.session_state.pop("editing", None)
            st.toast("비공개로 저장했습니다.")
            st.rerun()


def _render_editor(user, day: str, row: dict) -> None:
    existing = db.get_log(user["id"], day, row["period"])
    post = db.get_post_by_log(existing["id"]) if existing else None

    with st.container(border=True):
        st.markdown(
            "<div class='hj-sheet-handle'></div>"
            f"<div class='hj-sheet-title'>{row['period']}교시 · {ui.esc(row['subject_raw'] or '수업 정보 없음')}</div>",
            unsafe_allow_html=True,
        )

        with st.form(key=f"editor-{day}-{row['period']}"):
            learned = st.text_area(
                "배운 것 한 줄",
                value=existing["learned"] if existing else "",
                max_chars=120,
                height=84,
                placeholder="예: 관계대명사 whose가 소유격이라는 걸 배웠다.",
            )
            activity_index = 0
            if existing and existing["activity"] in config.ACTIVITIES:
                activity_index = config.ACTIVITIES.index(existing["activity"])
            activity = st.radio(
                "내가 한 것",
                config.ACTIVITIES,
                index=activity_index,
                horizontal=True,
            )
            stuck = st.text_input(
                "막힌 것 (선택)",
                value=existing["stuck"] if existing else "",
                max_chars=80,
                placeholder="예: whose vs of which",
            )
            is_public = st.toggle(
                "광명 피드에 공개",
                value=bool(post and post["status"] == "visible"),
            )
            submitted = st.form_submit_button("저장", type="primary", use_container_width=True)

        if not submitted:
            if st.button("닫기", key=f"close-{day}-{row['period']}", use_container_width=True):
                st.session_state.pop("editing", None)
                st.rerun()
            return

        text = learned.strip()
        if not text:
            st.error("배운 것 한 줄은 비워둘 수 없습니다.")
            return
        if privacy.contains_profanity(text) or privacy.contains_profanity(stuck):
            st.error("부적절한 표현이 포함되어 저장할 수 없습니다.")
            return

        log_id = db.upsert_log(
            user["id"],
            day,
            row["period"],
            row["subject_raw"],
            row["subject_norm"],
            text,
            activity,
            stuck.strip(),
        )
        metrics.track(
            user["id"],
            "log_save",
            subject=row["subject_norm"],
            has_stuck=bool(stuck.strip()),
            public=bool(is_public),
        )

        if is_public:
            clean, changed = privacy.sanitize_for_public(text, school_name=config.DEMO_SCHOOL_NAME)
            if not clean:
                st.error("공개할 수 있는 내용이 없습니다. 표현을 수정해주세요.")
                return
            if post:
                db.delete_post_by_log(log_id)
            tags = llm.suggest_tags(text, row["subject_norm"])
            st.session_state["pending_publish"] = {
                "log_id": log_id,
                "date": day,
                "period": row["period"],
                "text": clean,
                "tags": tags,
                "subject_norm": row["subject_norm"],
                "changed": changed,
            }
        else:
            if post:
                db.delete_post_by_log(log_id)
            st.session_state.pop("editing", None)
            st.toast("저장했습니다. 상세 기록은 나만 볼 수 있습니다.")

        st.session_state.pop("editing", None)
        st.rerun()


def render(user) -> None:
    if "selected_day" not in st.session_state:
        st.session_state["selected_day"] = (
            config.DEMO_DATE if config.DEMO_MODE else date.today().isoformat()
        )
    selected_day = date.fromisoformat(st.session_state["selected_day"])
    week = _week_days(selected_day)

    st.markdown(
        ui.date_head(
            _long_date(selected_day),
            f"고{user['grade']} · {user['class_no']}반 · {config.DEMO_SCHOOL_NAME}",
            "DEMO" if config.DEMO_MODE else "",
        ),
        unsafe_allow_html=True,
    )

    with st.container(key="week_strip"):
        cols = st.columns(5, gap="small")
        for col, day in zip(cols, week):
            with col:
                if st.button(
                    f"{_WEEKDAY_KO[day.weekday()]} {day.day}",
                    key=f"day_{day.isoformat()}",
                    type="primary" if day == selected_day else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["selected_day"] = day.isoformat()
                    st.rerun()

    _render_pending(user)

    day_str = selected_day.isoformat()
    rows, error = _load_rows(user, day_str)

    if error:
        st.error("시간표를 불러오지 못했습니다.")
        with st.expander("수업 정보 직접 입력", expanded=True):
            c1, c2 = st.columns([1, 3])
            manual_period = c1.number_input("교시", 1, 10, 1, key=f"manual-p-{day_str}")
            manual_subject = c2.text_input("과목", key=f"manual-s-{day_str}")
            if st.button("이 교시 추가", key=f"manual-add-{day_str}"):
                if manual_subject.strip():
                    rows.append(
                        {
                            "period": int(manual_period),
                            "subject_raw": manual_subject.strip(),
                            "subject_norm": neis.normalize_subject(manual_subject),
                            "room": "",
                            "is_event": 0,
                        }
                    )
                    st.session_state.setdefault("manual_rows", {})[day_str] = rows
                    st.rerun()

    manual_rows = st.session_state.get("manual_rows", {}).get(day_str, [])
    if manual_rows:
        known = {row["period"] for row in rows}
        rows.extend(row for row in manual_rows if row["period"] not in known)
    rows = sorted(rows, key=lambda row: row["period"])

    if not rows:
        st.markdown(ui.helper("이 날은 시간표가 없습니다."), unsafe_allow_html=True)
        return

    logged = sum(
        1 for row in rows if db.get_log(user["id"], day_str, int(row["period"])) is not None
    )
    pct = round(logged / len(rows) * 100)
    st.markdown(
        f"<div class='hj-progress-head'><span>오늘의 기록</span><b>{logged}/{len(rows)}</b></div>"
        f"<div class='hj-progress'><div style='width:{pct}%'></div></div>",
        unsafe_allow_html=True,
    )

    editing = st.session_state.get("editing")
    if editing and editing.get("date") != day_str:
        st.session_state.pop("editing", None)
        editing = None

    if editing:
        row = next((item for item in rows if item["period"] == editing["period"]), None)
        if row:
            _render_editor(user, day_str, row)

    with st.container(key="period_group"):
        for row in rows:
            period = int(row["period"])
            existing = db.get_log(user["id"], day_str, period)
            post = db.get_post_by_log(existing["id"]) if existing else None
            with st.container(key=f"prow_{period}"):
                c1, c2 = st.columns([9, 1])
                c1.markdown(
                    ui.period_row(
                        period,
                        row.get("subject_raw") or "수업 정보 없음",
                        existing["learned"] if existing else None,
                        bool(row.get("is_event")),
                        bool(post and post["status"] == "visible"),
                    ),
                    unsafe_allow_html=True,
                )
                if c2.button(
                    "›" if existing else "＋",
                    key=f"pact_{period}",
                    use_container_width=True,
                ):
                    st.session_state["editing"] = {"date": day_str, "period": period}
                    st.rerun()
