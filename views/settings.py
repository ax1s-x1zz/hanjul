"""Profile, demo account switching, data rights, AI status."""
from __future__ import annotations

import json

import streamlit as st

from core import config, db


def render(user) -> None:
    st.markdown("### ⚙️ 설정")
    st.caption("프로필과 데이터 권리를 관리합니다.")

    with st.container(border=True):
        st.markdown(f"**{user['nickname']}**")
        st.caption(
            f"고{user['grade']} · {user['class_no']}반 · {user['track'] or '계열 미설정'} "
            f"· {user['region']}"
        )
        st.caption("실명·전화번호·주소·사진은 저장하지 않습니다.")

    st.markdown("#### 데모 계정 전환")
    st.caption("피드 응원을 양쪽에서 확인할 때 사용하세요.")
    c1, c2 = st.columns(2)
    if c1.button("나 · 2학년 5반", use_container_width=True):
        st.session_state["user_id"] = db.DEMO_USER_ID
        st.rerun()
    if c2.button("친구 · 2학년 2반", use_container_width=True):
        st.session_state["user_id"] = db.FRIEND_USER_ID
        st.rerun()

    st.markdown("#### 내 데이터")
    payload = json.dumps(
        db.export_user_data(user["id"]),
        ensure_ascii=False,
        indent=2,
        default=str,
    )
    st.download_button(
        "내 기록 JSON으로 내보내기",
        data=payload,
        file_name=f"hanjul-{user['id']}.json",
        mime="application/json",
        use_container_width=True,
    )

    with st.expander("내 데이터 모두 삭제"):
        st.warning("기록·공개 글·응원·복습 카드가 모두 삭제됩니다. 되돌릴 수 없습니다.")
        confirmed = st.checkbox("정말 삭제합니다", key="delete-confirm")
        if st.button("삭제 실행", type="primary", disabled=not confirmed, use_container_width=True):
            db.delete_all_user_data(user["id"])
            st.session_state.pop("user_id", None)
            st.toast("데이터를 삭제했습니다.")
            st.rerun()

    st.markdown("#### AI 상태")
    if config.OPENAI_API_KEY:
        st.success(f"AI 보조 사용 가능 · {config.OPENAI_MODEL}")
        st.caption("AI는 태그·요약·질문만 만들고, 기록 문장은 학생이 작성합니다.")
    else:
        st.info("AI 키가 없어 규칙 기반 태그로 동작합니다.")
        st.caption(".env에 OPENAI_API_KEY를 추가하면 주간 요약과 태그 품질이 올라갑니다.")

    st.divider()
    st.caption(
        "한줄은 학교 공식 서비스가 아닙니다. "
        "NEIS 교육정보 개방 포털과 공공데이터를 활용하며, "
        "각 데이터의 출처 표시 조건을 따릅니다."
    )
    st.caption(f"v{config.APP_VERSION} · {config.REGION}")
