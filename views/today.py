"""Today's timetable and the 10-second log editor."""
from __future__ import annotations

from datetime import date

import streamlit as st

from core import config, db, llm, metrics, neis, privacy, utils


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

    with st.container(border=True):
        st.markdown("#### 🌿 공개 미리보기")
        st.info(pending["text"])
        if pending.get("tags"):
            st.caption("개념 태그 · " + ", ".join(pending["tags"]))
        if pending.get("changed"):
            st.warning("개인정보로 보이는 부분을 자동으로 가렸습니다.")
        st.caption("이 내용은 광명시 피드에 공개됩니다. 학교명·실명은 포함되지 않습니다.")

        col1, col2 = st.columns(2)
        if col1.button("광명 피드에 게시", type="primary", use_container_width=True):
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
        if col2.button("취소 (비공개 유지)", use_container_width=True):
            st.session_state.pop("pending_publish", None)
            st.session_state.pop("editing", None)
            st.toast("비공개로 저장했습니다.")
            st.rerun()


def _render_editor(user, day: str, row: dict) -> None:
    existing = db.get_log(user["id"], day, row["period"])
    post = db.get_post_by_log(existing["id"]) if existing else None

    with st.form(key=f"editor-{day}-{row['period']}"):
        st.caption(
            f"{row['period']}교시 · {row['subject_raw'] or '수업 정보 없음'}"
            + (f" · {row['room']}실" if row.get("room") else "")
        )
        learned = st.text_area(
            "배운 것 한 줄",
            value=existing["learned"] if existing else "",
            max_chars=120,
            height=80,
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
            "이 한 줄을 광명 피드에 공개",
            value=bool(post and post["status"] == "visible"),
        )
        submitted = st.form_submit_button("저장", type="primary", use_container_width=True)

    if not submitted:
        if st.button("닫기", key=f"close-{day}-{row['period']}"):
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
    st.markdown("### 📝 오늘의 수업")
    st.caption(
        f"{user['nickname']} · 고{user['grade']} · {user['class_no']}반 · {user['region']}"
    )

    _render_pending(user)

    today = date.today()
    default_date = date.fromisoformat(config.DEMO_DATE) if config.DEMO_MODE else today
    selected = st.date_input("날짜", value=default_date, key="today_date")
    day = selected.isoformat()
    rows, error = _load_rows(user, day)

    using_demo_date = False
    if not rows and not error and selected == today and config.DEMO_MODE:
        day = config.DEMO_DATE
        rows, error = _load_rows(user, day)
        using_demo_date = True

    if using_demo_date:
        st.info(
            f"오늘은 수업이 없어 **{utils.format_kr_date(day)}** 데모 수업일을 표시합니다."
        )
    elif config.DEMO_MODE and day == config.DEMO_DATE:
        st.caption(f"데모 모드 · {utils.format_kr_date(day)} 실제 수업일")
    elif not rows and not error:
        st.info("이 날은 시간표가 없습니다. 다른 날짜를 선택해보세요.")

    if error:
        st.error(f"NEIS 시간표를 불러오지 못했습니다. ({error})")
        with st.expander("수업 정보 직접 입력", expanded=True):
            c1, c2 = st.columns([1, 3])
            manual_period = c1.number_input("교시", 1, 10, 1, key=f"manual-p-{day}")
            manual_subject = c2.text_input("과목", key=f"manual-s-{day}")
            if st.button("이 교시 추가", key=f"manual-add-{day}"):
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
                    st.session_state.setdefault("manual_rows", {})[day] = rows
                    st.rerun()

    manual_rows = st.session_state.get("manual_rows", {}).get(day, [])
    if manual_rows:
        known = {row["period"] for row in rows}
        rows.extend(row for row in manual_rows if row["period"] not in known)
    rows = sorted(rows, key=lambda row: row["period"])

    if not rows:
        return

    logged = sum(
        1 for row in rows if db.get_log(user["id"], day, int(row["period"])) is not None
    )
    st.progress(
        logged / len(rows),
        text=f"{utils.format_kr_date(day)} · {logged}/{len(rows)}교시 기록",
    )

    editing = st.session_state.get("editing")
    if editing and editing.get("date") != day:
        st.session_state.pop("editing", None)
        editing = None

    if editing:
        row = next((item for item in rows if item["period"] == editing["period"]), None)
        if row:
            st.markdown(f"#### {row['period']}교시 기록")
            _render_editor(user, day, row)
            st.divider()

    for row in rows:
        period = int(row["period"])
        existing = db.get_log(user["id"], day, period)
        post = db.get_post_by_log(existing["id"]) if existing else None
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            subject = row.get("subject_raw") or "수업 정보 없음"
            badge = " `행사`" if row.get("is_event") else ""
            col1.markdown(f"**{period}교시 · {subject}**{badge}")
            if existing:
                col1.caption(f"✓ {existing['learned'][:60]}")
                if post and post["status"] == "visible":
                    col1.caption("🌿 광명 피드에 공개됨")
            else:
                col1.caption("아직 기록하지 않았습니다.")
            if col2.button(
                "수정" if existing else "기록",
                key=f"edit-{day}-{period}",
                use_container_width=True,
            ):
                st.session_state["editing"] = {"date": day, "period": period}
                st.rerun()
