"""한줄 (hanjul) — Streamlit entry point with a mobile phone shell."""
from __future__ import annotations

import streamlit as st

from core import config, db, theme, ui
from views import feed, onboarding, recall, report, settings, today

st.set_page_config(
    page_title="한줄 · 오늘 배운 한 줄",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(f"<style>{theme.CSS}</style>", unsafe_allow_html=True)

db.seed_demo_data()

NAV = ["오늘", "피드", "리포트", "리콜", "설정"]
PAGES = {
    "오늘": today.render,
    "피드": feed.render,
    "리포트": report.render,
    "리콜": recall.render,
    "설정": settings.render,
}
TITLES = {
    "오늘": None,
    "피드": "광명 피드",
    "리포트": "리포트",
    "리콜": "시험 리콜",
    "설정": "설정",
}


def _scroll_screen_top() -> None:
    """Reset the page scroll when the page changes (not on every rerun)."""
    st.iframe(
        """
        <script>
        const el = window.parent.document.querySelector('.st-key-phone_screen');
        if (el) { el.scrollTop = 0; }
        </script>
        """,
        height=1,
    )


def _bottom_nav(active: str) -> None:
    with st.container(key="bottom_nav"):
        cols = st.columns(5, gap="small")
        for col, page in zip(cols, NAV):
            with col:
                if st.button(
                    page,
                    key=f"nav-{page}",
                    use_container_width=True,
                    type="primary" if page == active else "secondary",
                ):
                    st.session_state["nav"] = page
                    st.rerun()


# One stable container for both onboarding and the main app. Keeping it at the
# same delta path prevents the previous screen from lingering after a rerun.
with st.container(key="phone_screen"):
    user = None
    if "user_id" in st.session_state:
        user = db.get_user(st.session_state["user_id"])
        if user is None:
            st.session_state.pop("user_id", None)

    if user is None:
        st.markdown(ui.status_bar(), unsafe_allow_html=True)
        with st.container(key="page_content"):
            onboarding.render()
    else:
        nav = st.session_state.get("nav", "오늘")
        if nav not in NAV:
            nav = "오늘"
            st.session_state["nav"] = nav

        if st.session_state.get("_last_nav") != nav:
            st.session_state["_last_nav"] = nav
            _scroll_screen_top()

        st.markdown(ui.phone_header(user, TITLES.get(nav)), unsafe_allow_html=True)
        with st.container(key="page_content"):
            PAGES[nav](user)
        _bottom_nav(nav)
