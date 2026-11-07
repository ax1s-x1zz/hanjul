"""Gwangmyeong learning feed."""
from __future__ import annotations

import streamlit as st

from core import config, db, metrics, utils


def render(user) -> None:
    st.markdown("### 🌿 광명 피드")
    st.caption("공개를 선택한 한 줄만 보입니다. 학교명·실명은 표시되지 않습니다.")

    subjects = ["전체"] + db.get_feed_subjects(config.REGION)
    subject = st.selectbox("과목", subjects, key="feed_subject")
    if st.session_state.get("last_feed_subject") != subject:
        st.session_state["feed_limit"] = 20
        st.session_state["last_feed_subject"] = subject
    limit = int(st.session_state.setdefault("feed_limit", 20))

    posts = db.get_feed(
        region=config.REGION,
        subject=None if subject == "전체" else subject,
        limit=limit,
    )

    if not posts:
        st.info("아직 공개 글이 없습니다. 오늘 첫 배움을 남겨보세요.")
        if st.button("오늘 기록하러 가기", type="primary", use_container_width=True):
            st.session_state["nav"] = "오늘"
            st.rerun()
        return

    for post in posts:
        with st.container(border=True):
            header, stamp = st.columns([4, 1])
            header.markdown(
                f"**{post['nickname']}** · 고{post['grade']} · "
                f"{post['subject_norm'] or '기타'}"
            )
            stamp.caption(utils.time_ago(post["created_at"]))

            st.write(post["public_text"])

            cheer_col, report_col, meta_col = st.columns([1.2, 0.5, 2.3])
            cheer_count = int(post["cheer_count"])
            if post["user_id"] == user["id"]:
                cheer_col.caption("내 글")
            else:
                cheered = db.has_cheered(post["id"], user["id"])
                label = f"👏 응원함 {cheer_count}" if cheered else f"👏 응원 {cheer_count}"
                if cheer_col.button(label, key=f"cheer-{post['id']}", use_container_width=True):
                    db.toggle_cheer(post["id"], user["id"])
                    metrics.track(user["id"], "cheer_given", post_id=post["id"])
                    st.rerun()

            if report_col.button("🚩", key=f"report-{post['id']}", help="신고"):
                count = db.report_post(post["id"], user["id"])
                metrics.track(user["id"], "report_submit", post_id=post["id"])
                if count >= 3:
                    st.toast("신고가 누적되어 이 글을 숨겼습니다.")
                else:
                    st.toast("신고가 접수되었습니다.")
                st.rerun()

            meta_col.caption(
                f"{post['subject_norm'] or '기타'} · {post['created_at'][:10]}"
            )

    if len(posts) >= limit:
        if st.button("더 보기", use_container_width=True):
            st.session_state["feed_limit"] = limit + 10
            st.rerun()
