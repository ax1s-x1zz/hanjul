"""First-run onboarding (V2)."""
from __future__ import annotations

import streamlit as st

from core import config, db, metrics, neis, ui, utils


def render() -> None:
    st.markdown(
        """
        <div class="hj-onboarding-hero">
          <div class="hj-onboarding-brand">한줄.</div>
          <div class="hj-onboarding-title">오늘 배운 한 줄,<br>여기 남기세요.</div>
          <div class="hj-onboarding-sub">시간표는 학교가, 기록은 당신이.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown(
        ui.feature("clock", "10초 기록", "시간표가 과목과 교시를 자동으로 채웁니다.")
        + ui.feature("lock", "나만 보는 기록", "상세 리포트와 막힘 분석은 나만 봅니다.")
        + ui.feature("pin", "광명 피드", "공개한 한 줄만 지역 친구들과 나눕니다.")
        + "<div style='height:18px'></div>",
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("데모로 시작하기", type="primary", use_container_width=True):
        db.seed_demo_data()
        st.session_state["user_id"] = db.DEMO_USER_ID
        metrics.track(db.DEMO_USER_ID, "onboarding_complete", mode="demo")
        st.rerun()

    if st.button("친구 계정으로 체험하기", use_container_width=True):
        db.seed_demo_data()
        st.session_state["user_id"] = db.FRIEND_USER_ID
        metrics.track(db.FRIEND_USER_ID, "onboarding_complete", mode="friend")
        st.rerun()

    st.caption("진성고등학교 2학년 5반 · 경기 광명시")

    with st.expander("직접 학교 설정"):
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
            st.caption("검색하지 않으면 데모 학교로 시작합니다.")

        grade = st.selectbox("학년", [1, 2, 3], index=1)
        class_no = st.text_input("반", value=config.DEMO_CLASS_NO)
        track = st.selectbox("계열", ["이과", "문과", "예체능", "기타"])
        nickname = st.text_input("닉네임", value=utils.make_nickname(grade))

        if st.button("이 설정으로 시작", use_container_width=True):
            school = selected or {
                "school_code": config.DEMO_SCHOOL_CODE,
                "name": config.DEMO_SCHOOL_NAME,
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

    st.write("")
    st.caption("실명·전화번호·주소·사진은 저장하지 않습니다.")
