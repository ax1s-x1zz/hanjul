"""Gwangmyeong learning feed (V2)."""
from __future__ import annotations

import streamlit as st

from core import config, db, metrics, ui, utils

_SHORT = {
    "데이터과학": "데이터",
    "독서와작문": "독서",
    "물질과에너지": "물질",
    "미적분1": "미적분",
    "세포와물질대사": "세포",
    "영어독해와작문": "영독작",
    "스포츠생활1": "스포츠",
    "윤리와사상": "윤리",
}


def render(user) -> None:
    st.markdown(ui.helper("공개한 한 줄만 보입니다. 학교명·실명은 표시되지 않습니다."), unsafe_allow_html=True)

    subjects = ["전체"] + db.get_feed_subjects(config.REGION)
    selected = st.session_state.get("feed_subject", "전체")
    if selected not in subjects:
        selected = "전체"

    with st.container(key="subject_chips"):
        cols = st.columns(len(subjects), gap="small")
        for col, subject in zip(cols, subjects):
            with col:
                if st.button(
                    _SHORT.get(subject, subject),
                    key=f"subject_{subject}",
                    type="primary" if subject == selected else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["feed_subject"] = subject
                    st.session_state["feed_limit"] = 20
                    st.rerun()

    limit = int(st.session_state.setdefault("feed_limit", 20))
    posts = db.get_feed(
        region=config.REGION,
        subject=None if selected == "전체" else selected,
        limit=limit,
    )

    if not posts:
        st.write("")
        st.markdown(ui.helper("아직 공개 글이 없습니다."), unsafe_allow_html=True)
        if st.button("오늘 기록하러 가기", type="primary", use_container_width=True):
            st.session_state["nav"] = "오늘"
            st.rerun()
        return

    for post in posts:
        with st.container(key=f"post_{post['id']}"):
            st.markdown(
                ui.feed_head(
                    post["nickname"],
                    post["grade"],
                    post["subject_norm"],
                    utils.time_ago(post["created_at"]),
                ),
                unsafe_allow_html=True,
            )
            st.markdown(ui.post_text(post["public_text"]), unsafe_allow_html=True)

            tag_html = ui.tags(
                [
                    tag.strip()
                    for tag in (post["concept_tags"] or "").split(",")
                    if tag.strip()
                ][:3]
            )
            if tag_html:
                st.markdown(tag_html, unsafe_allow_html=True)

            cheer_col, report_col, _ = st.columns([1.2, 0.5, 4.3])
            cheer_count = int(post["cheer_count"])
            if post["user_id"] == user["id"]:
                cheer_col.caption("내 글")
            else:
                cheered = db.has_cheered(post["id"], user["id"])
                key = f"cheer_active_{post['id']}" if cheered else f"cheer_{post['id']}"
                if cheer_col.button(
                    f"응원 {cheer_count}",
                    key=key,
                    use_container_width=True,
                ):
                    db.toggle_cheer(post["id"], user["id"])
                    metrics.track(user["id"], "cheer_given", post_id=post["id"])
                    st.rerun()

            if report_col.button("···", key=f"report_{post['id']}", help="신고"):
                count = db.report_post(post["id"], user["id"])
                metrics.track(user["id"], "report_submit", post_id=post["id"])
                if count >= 3:
                    st.toast("신고가 누적되어 이 글을 숨겼습니다.")
                else:
                    st.toast("신고가 접수되었습니다.")
                st.rerun()

    st.write("")
    if len(posts) >= limit:
        if st.button("더 보기", use_container_width=True):
            st.session_state["feed_limit"] = limit + 10
            st.rerun()
