"""Profile, account switching, data rights, AI status (V2)."""
from __future__ import annotations

import json

import streamlit as st

from core import config, db, ui


def render(user) -> None:
    initial = ui.esc(ui.user_initial(user["nickname"]))
    with st.container(key="profile_group"):
        st.markdown(
            f"""
            <div class="hj-profile">
              <span class="hj-avatar hj-avatar-lg">{initial}</span>
              <div>
                <div class="hj-profile-name">{ui.esc(user['nickname'])}</div>
                <div class="hj-profile-sub">고{user['grade']} · {ui.esc(user['class_no'])}반 · {ui.esc(user['track'] or '계열 미설정')}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(ui.section("계정"), unsafe_allow_html=True)
    with st.container(key="settings_group"):
        if st.button("나 · 2학년 5반", key="switch_me", use_container_width=True):
            st.session_state["user_id"] = db.DEMO_USER_ID
            st.rerun()
        if st.button("친구 · 2학년 2반", key="switch_friend", use_container_width=True):
            st.session_state["user_id"] = db.FRIEND_USER_ID
            st.rerun()

    st.markdown(ui.section("데이터"), unsafe_allow_html=True)
    payload = json.dumps(
        db.export_user_data(user["id"]),
        ensure_ascii=False,
        indent=2,
        default=str,
    )
    st.download_button(
        "내 기록 내보내기",
        data=payload,
        file_name=f"hanjul-{user['id']}.json",
        mime="application/json",
        key="export",
        use_container_width=True,
    )

    with st.expander("내 데이터 모두 삭제"):
        st.warning("기록·공개 글·응원·복습 카드가 모두 삭제됩니다.")
        confirmed = st.checkbox("정말 삭제합니다", key="delete-confirm")
        if st.button(
            "삭제 실행",
            type="primary",
            disabled=not confirmed,
            use_container_width=True,
        ):
            db.delete_all_user_data(user["id"])
            st.session_state.pop("user_id", None)
            st.toast("데이터를 삭제했습니다.")
            st.rerun()

    with st.expander("데모 데이터 초기화"):
        st.warning("로컬 DB를 삭제하고 시드부터 다시 시작합니다.")
        reset_confirmed = st.checkbox("초기화합니다", key="reset-confirm")
        if st.button(
            "초기화",
            type="primary",
            disabled=not reset_confirmed,
            use_container_width=True,
        ):
            db.reset_database()
            st.session_state.clear()
            st.rerun()

    st.markdown(ui.section("정보"), unsafe_allow_html=True)
    ai_status = (
        f"사용 가능 · {config.OPENAI_MODEL}"
        if config.OPENAI_API_KEY
        else "규칙 기반으로 동작 중"
    )
    st.markdown(f"**AI 보조** · {ai_status}")
    st.caption("AI는 태그·요약만 만들고, 기록 문장은 학생이 작성합니다.")

    st.caption(f"v{config.APP_VERSION} · {config.REGION}")
    st.caption("한줄은 학교 공식 서비스가 아닙니다. NEIS·공공데이터 출처 표시 조건을 따릅니다.")
