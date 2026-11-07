"""Safe HTML fragments for the mobile UI (V2)."""
from __future__ import annotations

import html
from textwrap import dedent


def _clean(value: str) -> str:
    return dedent(value).strip()


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def icon(name: str) -> str:
    return f"<span class='hj-icon icon-{esc(name)}'></span>"


def user_initial(nickname: str) -> str:
    nickname = (nickname or "한").strip()
    parts = nickname.split("_")
    if len(parts) > 1 and parts[1]:
        return parts[1][0]
    return nickname[0]


def status_bar() -> str:
    return _clean(
        """
        <div class="hj-statusbar">
          <span>9:41</span>
          <span class="hj-island"></span>
          <span class="hj-status-icons">
            <span class="hj-signal"><i></i><i></i><i></i><i></i></span>
            <span class="hj-battery"></span>
          </span>
        </div>
        """
    )


def app_bar(user, title: str | None = None) -> str:
    initial = esc(user_initial(user["nickname"]))
    region = esc((user["region"] or "광명").replace("경기도 ", ""))
    left = (
        f"<div class='hj-appbar-title'>{esc(title)}</div>"
        if title
        else "<div class='hj-logo'>한줄<span>.</span></div>"
    )
    return _clean(
        f"""
        <div class="hj-appbar">
          {left}
          <div class="hj-appbar-right">
            <span class="hj-region">{region}</span>
            <span class="hj-avatar">{initial}</span>
          </div>
        </div>
        """
    )


def phone_header(user, title: str | None = None) -> str:
    return f"<div class='hj-phone-header'>{status_bar()}{app_bar(user, title)}</div>"


def date_head(title: str, sub: str = "", badge: str = "") -> str:
    badge_html = f"<span class='hj-pill'>{esc(badge)}</span>" if badge else ""
    sub_html = f"<div class='hj-date-sub'>{esc(sub)}</div>" if sub else ""
    return _clean(
        f"""
        <div class="hj-date-head">
          <div class="hj-date-title">{esc(title)}{badge_html}</div>
          {sub_html}
        </div>
        """
    )


def section(label: str) -> str:
    # Native Markdown heading: Streamlit measures its height correctly, unlike
    # a raw HTML block with custom vertical padding.
    return f"#### {esc(label)}"


def helper(text: str) -> str:
    return f"<div class='hj-helper'>{esc(text)}</div>"


def feed_head(nickname, grade, subject, when) -> str:
    initial = esc((nickname or "한")[0])
    sub = f"고{esc(grade)} · {esc(subject or '기타')} · 익명"
    return _clean(
        f"""
        <div class="hj-feed-head">
          <span class="hj-mini-avatar">{initial}</span>
          <div class="hj-feed-meta">
            <span class="hj-feed-name">{esc(nickname)}</span>
            <span class="hj-feed-sub">{sub}</span>
          </div>
          <span class="hj-time">{esc(when)}</span>
        </div>
        """
    )


def post_text(text: str) -> str:
    safe = esc(text).replace("\n", "<br>")
    return f"<div class='hj-post-text'>{safe}</div>"


def tags(items) -> str:
    return "".join(f"<span class='hj-tag'>{esc(item)}</span>" for item in items if item)


def period_row(period, subject, learned=None, is_event=False, is_public=False) -> str:
    event = "<span class='hj-pill-muted'>행사</span>" if is_event else ""
    if learned:
        status = f"<span class='ok'>✓ 기록 완료</span> · {esc(str(learned)[:48])}"
        if is_public:
            status += " · <span class='public'>광명 공개</span>"
    else:
        status = "아직 기록하지 않았습니다"
    return _clean(
        f"""
        <div class="hj-row">
          <span class="hj-row-num">{esc(period)}</span>
          <div>
            <div class="hj-row-title">{esc(subject)}{event}</div>
            <div class="hj-row-sub">{status}</div>
          </div>
        </div>
        """
    )


def metrics(items) -> str:
    cells = "".join(
        f"<div class='hj-metric'><div class='hj-metric-value'>{esc(value)}</div>"
        f"<div class='hj-metric-label'>{esc(label)}</div></div>"
        for value, label in items
    )
    return f"<div class='hj-metrics'>{cells}</div>"


def summary(text: str) -> str:
    return f"<div class='hj-summary'>{esc(text)}</div>"


def bar_row(label, value, max_value, suffix: str = "") -> str:
    pct = 0 if max_value <= 0 else max(0, min(100, round(float(value) / float(max_value) * 100)))
    return _clean(
        f"""
        <div class="hj-bar-row">
          <div class="hj-bar-head">
            <span>{esc(label)}</span><b>{esc(value)}{esc(suffix)}</b>
          </div>
          <div class="hj-bar-track"><div class="hj-bar-fill" style="width:{pct}%"></div></div>
        </div>
        """
    )


def dday_card(name: str, label: str, date_text: str = "", is_demo: bool = False) -> str:
    demo = "<span class='hj-dday-demo'>데모 일정</span>" if is_demo else ""
    date_html = f"<div class='hj-dday-date'>{esc(date_text)}</div>" if date_text else ""
    return _clean(
        f"""
        <div class="hj-dday">
          <div class="hj-dday-label">다음 시험</div>
          <div class="hj-dday-value">{esc(label)}</div>
          <div class="hj-dday-name">{esc(name)}</div>
          {date_html}
          {demo}
        </div>
        """
    )


def feature(icon_name: str, title: str, body: str) -> str:
    return _clean(
        f"""
        <div class="hj-feature">
          <div class="hj-feature-icon">{icon(icon_name)}</div>
          <div><b>{esc(title)}</b><p>{esc(body)}</p></div>
        </div>
        """
    )


def setting_row(title: str, sub: str = "", dot: str = "") -> str:
    dot_html = f"<span class='hj-ai-dot {esc(dot)}'></span>" if dot else ""
    sub_html = f"<div class='hj-row-sub'>{esc(sub)}</div>" if sub else ""
    return _clean(
        f"""
        <div class="hj-row">
          <div>
            <div class="hj-row-title">{dot_html}{esc(title)}</div>
            {sub_html}
          </div>
        </div>
        """
    )
