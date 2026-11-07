"""한줄 (hanjul) — Streamlit entry point."""
from __future__ import annotations

import streamlit as st

from core import config, db
from views import feed, onboarding, recall, report, settings, today

st.set_page_config(
    page_title="한줄 · 오늘 배운 한 줄",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded",
)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #faf9ff 0%, #ffffff 320px);
}
.block-container {
    max-width: 780px;
    padding-top: 1.6rem;
    padding-bottom: 5rem;
}
footer { visibility: hidden; }

.hj-brand {
    font-size: 1.9rem;
    font-weight: 900;
    letter-spacing: -0.06em;
    color: #4f46e5;
    line-height: 1.1;
}
.hj-hero {
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: -0.07em;
    color: #4f46e5;
    line-height: 1.05;
    margin-top: 1.2rem;
}
.hj-hero-sub {
    font-size: 1.05rem;
    color: #6b7280;
    margin-top: 0.35rem;
    margin-bottom: 1.2rem;
}
.hj-user {
    background: #eef2ff;
    border: 1px solid #e0e7ff;
    border-radius: 14px;
    padding: 0.7rem 0.85rem;
    margin: 0.5rem 0 0.9rem 0;
    font-size: 0.88rem;
    color: #3730a3;
}
.hj-user span { color: #6366f1; }

[data-testid="stSidebar"] {
    background: #fbfbff;
    border-right: 1px solid #eef0f6;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
    border-color: #eceef5;
    background: #ffffff;
}
.stButton > button {
    border-radius: 12px;
    font-weight: 700;
}
.stButton > button[kind="primary"] {
    background: #4f46e5;
    border-color: #4f46e5;
}
.stButton > button[kind="primary"]:hover {
    background: #4338ca;
    border-color: #4338ca;
}
.stTextArea textarea, .stTextInput input {
    border-radius: 12px;
}
.stProgress > div > div > div > div {
    background: #4f46e5;
}
h1, h2, h3, h4 {
    letter-spacing: -0.03em;
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

db.seed_demo_data()

if "user_id" not in st.session_state:
    onboarding.render()
    st.stop()

user = db.get_user(st.session_state["user_id"])
if user is None:
    st.session_state.pop("user_id", None)
    onboarding.render()
    st.stop()

with st.sidebar:
    st.markdown("<div class='hj-brand'>한줄</div>", unsafe_allow_html=True)
    st.caption(config.TAGLINE)
    st.markdown(
        f"<div class='hj-user'><b>{user['nickname']}</b><br>"
        f"<span>고{user['grade']} · {user['class_no']}반 · {user['region']}</span></div>",
        unsafe_allow_html=True,
    )
    nav = st.radio(
        "메뉴",
        ["오늘", "피드", "리포트", "리콜", "설정"],
        key="nav",
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("NEIS 시간표 · 광명시")
    st.caption(f"v{config.APP_VERSION}")

PAGES = {
    "오늘": today.render,
    "피드": feed.render,
    "리포트": report.render,
    "리콜": recall.render,
    "설정": settings.render,
}

PAGES[nav](user)
