"""First-run onboarding."""
from __future__ import annotations

import streamlit as st

from core import config, db, metrics, neis, utils


def render() -> None:
    st.markdown("<div class='hj-hero'>한줄</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='hj-hero-sub'>{config.TAGLINE}</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        "수업 시간표는 학교가 알려주고, **배운 것은 당신이 한 줄로 남깁니다.** "
        "상세 기록은 나만 보고, 공개를 선택한 한 줄만 광명 친구들과 나눕니다."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### ⏱️ 10초")
        st.caption("시간표가 자동으로 채워줍니다.")
    with col2:
        st.markdown("#### 🔒 나만")
        st.caption("리포트와 막힘 분석은 비공개.")
    with col3:
        st.markdown("#### 🌿 광명")
        st.caption("공개한 한 줄만 지역 피드로.")

    st.write("")
    if st.button("데모로 시작하기 · 2학년 5반", type="primary", use_container_width=True):
        db.seed_demo_data()
        st.session_state["user_id"] = db.DEMO_USER_ID
        metrics.track(db.DEMO_USER_ID, "onboarding_complete", mode="demo")
        st.rerun()

    if st.button("친구 계정으로 체험하기", use_container_width=True):
        db.seed_demo_data()
        st.session_state["user_id"] = db.FRIEND_USER_ID
        metrics.track(db.FRIEND_USER_ID, "onboarding_complete", mode="friend")
        st.rerun()

    st.caption("데모는 진성고등학교 2학년 5반 시간표를 사용합니다.")

    with st.expander("직접 학교를 설정할게요"):
        school_name = st.text_input("학교 이름", value=config.DEMO_SCHOOL_NAME)
        if st.button("학교 검색", use_container_width=True):
            try:
                st.session_state["school_results"] = neis.fetch_schools(
                    school_name, config.DEMO_OFFICE_CODE
                )
            except neis.NeisError as exc:
                st.error(str(exc))
                st.session_state["school_results"] = []

        results = st.session_state.get("school_results", [])
        selected: dict | None = None
        if results:
            labels = {f"{item['name']} · {item['address']}": item for item in results}
            label = st.selectbox("검색 결과", list(labels))
            selected = labels[label]
        else:
            st.caption("검색하지 않으면 데모 학교(진성고등학교)로 시작합니다.")

        grade = st.selectbox("학년", [1, 2, 3], index=1)
        class_no = st.text_input("반", value=config.DEMO_CLASS_NO)
        track = st.selectbox("계열", ["이과", "문과", "예체능", "기타"])
        nickname = st.text_input("닉네임", value=utils.make_nickname(grade))

        if st.button("이 설정으로 시작", use_container_width=True):
            school = selected or {
                "school_code": config.DEMO_SCHOOL_CODE,
                "name": config.DEMO_SCHOOL_NAME,
                "region": config.REGION,
            }
            final_nickname = utils.sanitize_nickname(nickname)
            if db.nickname_exists(final_nickname):
                final_nickname = utils.make_nickname(grade)
            user_id = db.create_user(
                nickname=final_nickname,
                grade=grade,
                class_no=class_no,
                track=track,
                school_code=school.get("school_code", config.DEMO_SCHOOL_CODE),
            )
            st.session_state["user_id"] = user_id
            metrics.track(user_id, "onboarding_complete", mode="custom")
            st.rerun()

    st.divider()
    st.caption(
        "실명·전화번호·주소·사진은 수집하지 않습니다. "
        "공개 글은 게시 전 개인정보를 자동으로 가립니다."
    )
