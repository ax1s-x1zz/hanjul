"""Safe HTML fragments for the mobile UI."""
from __future__ import annotations

import html
from textwrap import dedent


def _clean(value: str) -> str:
    """Dedent + strip so Markdown never turns indented HTML into a code block."""
    return dedent(value).strip()


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


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


def app_bar(user) -> str:
    initial = esc((user["nickname"] or "한")[0])
    region = esc((user["region"] or "광명").replace("경기도 ", ""))
    return _clean(
        f"""
        <div class="hj-appbar">
          <div class="hj-logo">한줄<span>.</span></div>
          <div class="hj-appbar-right">
            <span class="hj-region">{region}</span>
            <span class="hj-avatar">{initial}</span>
          </div>
        </div>
        """
    )


def phone_header(user) -> str:
    return f"<div class='hj-phone-header'>{status_bar()}{app_bar(user)}</div>"


def page_header(title: str, subtitle: str = "", badge: str = "") -> str:
    badge_html = f"<span class='hj-pill'>{esc(badge)}</span>" if badge else ""
    sub_html = f"<div class='hj-page-sub'>{esc(subtitle)}</div>" if subtitle else ""
    return (
        f"<div class='hj-page-head'>"
        f"<div class='hj-page-title'>{esc(title)}{badge_html}</div>"
        f"{sub_html}</div>"
    )


def feed_head(nickname, grade, subject, when) -> str:
    initial = esc((nickname or "한")[0])
    return _clean(
        f"""
        <div class="hj-feed-head">
          <span class="hj-mini-avatar">{initial}</span>
          <div class="hj-feed-meta">
            <span class="hj-feed-name">{esc(nickname)}</span>
            <span class="hj-feed-sub">고{esc(grade)} · {esc(subject or '기타')}</span>
          </div>
          <span class="hj-time">{esc(when)}</span>
        </div>
        """
    )


def post_text(text: str) -> str:
    safe = esc(text).replace("\n", "<br>")
    return f"<div class='hj-post-text'>{safe}</div>"


def tags(items) -> str:
    return "".join(
        f"<span class='hj-tag'>{esc(item)}</span>"
        for item in items
        if item
    )


def period_row(period, subject, learned=None, is_event=False, is_public=False) -> str:
    event = "<span class='hj-tag'>행사</span>" if is_event else ""
    if learned:
        status = f"<span class='ok'>✓ 기록 완료</span> · {esc(str(learned)[:52])}"
        if is_public:
            status += " · <span class='public'>광명 공개</span>"
    else:
        status = "아직 기록하지 않았습니다"
    return _clean(
        f"""
        <div class="hj-period-row">
          <span class="hj-period">{esc(period)}</span>
          <div>
            <div class="hj-period-subject">{esc(subject)} {event}</div>
            <div class="hj-period-status">{status}</div>
          </div>
        </div>
        """
    )


def dday_card(name: str, label: str, date_text: str = "", is_demo: bool = False) -> str:
    demo = "<span class='hj-dday-demo'>DEMO 일정</span>" if is_demo else ""
    date_html = f"<div class='hj-dday-date'>{esc(date_text)}</div>" if date_text else ""
    return _clean(
        f"""
        <div class="hj-dday">
          <div class="hj-dday-label">NEXT EXAM</div>
          <div class="hj-dday-value">{esc(label)}</div>
          <div class="hj-dday-name">{esc(name)}</div>
          {date_html}
          {demo}
        </div>
        """
    )


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


def feature(icon: str, title: str, body: str) -> str:
    return _clean(
        f"""
        <div class="hj-feature">
          <div class="hj-feature-icon">{icon}</div>
          <div><b>{esc(title)}</b><p>{esc(body)}</p></div>
        </div>
        """
    )
