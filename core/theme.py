"""Design system V2: native-feeling mobile app inside a phone frame."""
from __future__ import annotations

from urllib.parse import quote

_ICONS = {
    "home": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M3 10.5 12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z'/></svg>"
    ),
    "feed": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.7' stroke-linecap='round'>"
        "<path d='M4 6h16M4 12h16M4 18h10'/></svg>"
    ),
    "chart": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='2' stroke-linecap='round'>"
        "<path d='M5 20V10M12 20V4M19 20v-7'/></svg>"
    ),
    "clock": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.8' stroke-linecap='round'>"
        "<circle cx='12' cy='12' r='8.5'/><path d='M12 7.5V12l3 2'/></svg>"
    ),
    "settings": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.8' stroke-linecap='round'>"
        "<path d='M4 7h5M13 7h7M4 17h7M15 17h5'/>"
        "<circle cx='11' cy='7' r='2.2' fill='black'/><circle cx='13' cy='17' r='2.2' fill='black'/></svg>"
    ),
    "lock": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.7' stroke-linejoin='round'>"
        "<rect x='5' y='10' width='14' height='10' rx='2.5'/>"
        "<path d='M8.5 10V7.5a3.5 3.5 0 0 1 7 0V10'/></svg>"
    ),
    "pin": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.7' stroke-linejoin='round'>"
        "<path d='M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11z'/>"
        "<circle cx='12' cy='10' r='2.5'/></svg>"
    ),
    "heart": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.7' stroke-linejoin='round'>"
        "<path d='M20.8 8.6a5 5 0 0 0-8.8-3.2A5 5 0 0 0 3.2 8.6c0 5.4 8.8 10.4 8.8 10.4s8.8-5 8.8-10.4z'/></svg>"
    ),
    "spark": (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='black' stroke-width='1.6' stroke-linejoin='round'>"
        "<path d='M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z'/></svg>"
    ),
}

_MASKS = {
    name: f'url("data:image/svg+xml,{quote(svg)}") center / contain no-repeat'
    for name, svg in _ICONS.items()
}

CSS = r"""
@font-face {
  font-family: 'Pretendard';
  src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/woff2/PretendardVariable.woff2') format('woff2-variations');
  font-weight: 45 920;
  font-display: swap;
}

:root {
  --bg: #E7E7ED;
  --screen: #F7F7FA;
  --surface: #FFFFFF;
  --text: #111114;
  --muted: #6E6E78;
  --tertiary: #9A9AA5;
  --line: #E9E9EF;
  --accent: #5546F5;
  --accent-soft: #EFEDFF;
  --accent-line: #E1DCFF;
  --success: #0E9F6E;
  --danger: #E5484D;
}

html, body, [class*="css"] {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR',
    'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
  -webkit-font-smoothing: antialiased;
  word-break: keep-all;
}

.stApp {
  background: var(--bg);
  overflow: hidden;
}

footer, header[data-testid="stHeader"], [data-testid="stSidebar"],
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }

.block-container { max-width: none !important; padding: 0 !important; }

/* ------------------------------------------------------------------ */
/* Phone frame                                                         */
/* ------------------------------------------------------------------ */
.st-key-phone_screen {
  box-sizing: border-box;
  width: 390px;
  height: min(844px, calc(100vh - 48px)) !important;
  min-height: min(844px, calc(100vh - 48px)) !important;
  max-height: min(844px, calc(100vh - 48px)) !important;
  flex: 0 0 auto !important;
  margin: 24px auto;
  padding: 0 16px 88px;
  background: var(--screen);
  border: 8px solid #111116;
  border-radius: 44px;
  box-shadow:
    0 38px 90px rgba(17, 17, 22, 0.30),
    0 6px 18px rgba(17, 17, 22, 0.10);
  overflow-y: auto !important;
  overflow-x: hidden !important;
  position: relative;
  scrollbar-width: none;
  gap: 0;
}
.st-key-phone_screen::-webkit-scrollbar { display: none; }

.st-key-page_content {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding-top: 16px;
  padding-bottom: 0;
}

/* ------------------------------------------------------------------ */
/* Header                                                              */
/* ------------------------------------------------------------------ */
.hj-phone-header {
  position: sticky;
  top: 0;
  z-index: 80;
  margin: 0 -16px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom: 1px solid var(--line);
}

.hj-statusbar {
  position: relative;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 10.5px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.01em;
}
.hj-island {
  position: absolute;
  top: 5px;
  left: 50%;
  transform: translateX(-50%);
  width: 76px;
  height: 20px;
  background: #111116;
  border-radius: 999px;
}
.hj-status-icons { display: inline-flex; align-items: center; gap: 4px; }
.hj-signal { display: inline-flex; align-items: flex-end; gap: 1.4px; height: 9px; }
.hj-signal i { display: block; width: 2.3px; background: var(--text); border-radius: 2px; }
.hj-signal i:nth-child(1) { height: 3.5px; }
.hj-signal i:nth-child(2) { height: 5.5px; }
.hj-signal i:nth-child(3) { height: 7.5px; }
.hj-signal i:nth-child(4) { height: 9px; }
.hj-battery {
  width: 17px;
  height: 8.5px;
  border: 1.4px solid var(--text);
  border-radius: 3px;
  position: relative;
}
.hj-battery::after {
  content: "";
  position: absolute;
  right: -3.5px;
  top: 2px;
  width: 2px;
  height: 4px;
  background: var(--text);
  border-radius: 0 2px 2px 0;
}

.hj-appbar {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.hj-logo {
  font-size: 1.18rem;
  font-weight: 900;
  letter-spacing: -0.07em;
  color: var(--text);
  line-height: 1;
}
.hj-logo span { color: var(--accent); }
.hj-appbar-title {
  font-size: 1.02rem;
  font-weight: 800;
  letter-spacing: -0.035em;
  color: var(--text);
}
.hj-appbar-right { display: flex; align-items: center; gap: 8px; }
.hj-region {
  font-size: 0.63rem;
  font-weight: 700;
  color: var(--muted);
  background: #F1F1F5;
  padding: 4px 8px;
  border-radius: 999px;
}
.hj-avatar {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 800;
  font-size: 0.72rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* ------------------------------------------------------------------ */
/* Typography / sections                                               */
/* ------------------------------------------------------------------ */
.hj-section {
  font-size: 0.68rem;
  font-weight: 800;
  color: var(--tertiary);
  letter-spacing: 0.05em;
  margin: 0;
}
h4 {
  font-size: 0.68rem !important;
  font-weight: 800 !important;
  color: var(--tertiary) !important;
  letter-spacing: 0.05em !important;
  line-height: 1.45 !important;
  margin: 18px 0 7px !important;
}
.hj-helper {
  font-size: 0.73rem;
  color: var(--muted);
  line-height: 1.5;
  margin: 2px 0 10px;
}
.hj-progress-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 0.69rem;
  color: var(--muted);
  margin: 14px 0 5px;
}
.hj-progress-head b { color: var(--text); font-weight: 800; font-size: 0.72rem; }
.hj-progress {
  height: 5px;
  background: #ECECF2;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 8px;
}
.hj-progress > div { height: 100%; background: var(--accent); border-radius: 999px; }
.hj-sheet-handle {
  width: 34px;
  height: 4px;
  background: #D9D9E3;
  border-radius: 999px;
  margin: 0 auto 12px;
}
.hj-sheet-title {
  font-size: 0.98rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text);
  margin-bottom: 8px;
}
.hj-date-head { padding: 14px 0 10px; }
.hj-date-title {
  font-size: 1.42rem;
  font-weight: 800;
  letter-spacing: -0.055em;
  color: var(--text);
  line-height: 1.18;
}
.hj-date-sub {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 4px;
}
.hj-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.62rem;
  font-weight: 800;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 3px 7px;
  border-radius: 999px;
  margin-left: 6px;
  vertical-align: 2px;
  letter-spacing: 0;
}
.hj-pill-muted {
  display: inline-flex;
  font-size: 0.62rem;
  font-weight: 700;
  color: var(--muted);
  background: #F1F1F5;
  padding: 3px 7px;
  border-radius: 999px;
  margin-left: 6px;
  vertical-align: 2px;
}

.hj-profile { display: flex; align-items: center; gap: 12px; padding: 16px 14px; }
.hj-avatar-lg {
  width: 46px;
  height: 46px;
  font-size: 1rem;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  flex: 0 0 auto;
}
.hj-profile-name { font-size: 1rem; font-weight: 800; letter-spacing: -0.03em; }
.hj-profile-sub { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }

.st-key-report_tabs {
  background: #F1F1F5;
  border-radius: 12px;
  padding: 3px;
  gap: 0;
}

/* ------------------------------------------------------------------ */
/* Grouped list / rows                                                 */
/* ------------------------------------------------------------------ */
.st-key-period_group,
.st-key-recall_group,
.st-key-stuck_group,
[class*="st-key-settings_group"],
.st-key-profile_group {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  overflow: hidden;
  gap: 0 !important;
  padding: 0 !important;
}

[class*="st-key-prow_"],
[class*="st-key-recall_"],
[class*="st-key-stuck_"],
[class*="st-key-setting_"] {
  padding: 13px 14px !important;
  border-bottom: 1px solid var(--line);
}
[class*="st-key-prow_"]:last-child,
[class*="st-key-recall_"]:last-child,
[class*="st-key-stuck_"]:last-child,
[class*="st-key-setting_"]:last-child {
  border-bottom: none;
}

.hj-row { display: flex; align-items: center; gap: 11px; }
.hj-row-num {
  width: 26px;
  height: 26px;
  border-radius: 9px;
  background: #F2F2F7;
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}
.hj-row-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.32;
  letter-spacing: -0.02em;
}
.hj-row-sub {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 3px;
  line-height: 1.42;
}
.hj-row-sub .ok { color: var(--success); font-weight: 700; }
.hj-row-sub .public { color: var(--accent); font-weight: 700; }
.hj-row-chevron { color: #B8B8C2; font-size: 1.12rem; line-height: 1; }

/* ------------------------------------------------------------------ */
/* Feed                                                                */
/* ------------------------------------------------------------------ */
[class*="st-key-post_"] {
  padding: 15px 0 13px !important;
  border-bottom: 1px solid var(--line);
}
.hj-feed-head { display: flex; align-items: center; gap: 9px; }
.hj-mini-avatar {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  background: #F1F1F5;
  color: var(--muted);
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  flex: 0 0 auto;
}
.hj-feed-meta { display: flex; flex-direction: column; line-height: 1.22; min-width: 0; }
.hj-feed-name { font-weight: 700; font-size: 0.82rem; color: var(--text); }
.hj-feed-sub { font-size: 0.68rem; color: var(--muted); }
.hj-time { margin-left: auto; font-size: 0.64rem; color: var(--tertiary); white-space: nowrap; }
.hj-post-text {
  font-size: 0.91rem;
  line-height: 1.62;
  color: var(--text);
  margin: 10px 0 8px;
  letter-spacing: -0.01em;
}
.hj-tag {
  display: inline-flex;
  font-size: 0.61rem;
  font-weight: 700;
  color: var(--muted);
  background: #F5F5F8;
  border: 1px solid var(--line);
  padding: 2px 7px;
  border-radius: 999px;
  margin: 0 4px 0 0;
}

[class*="st-key-cheer_"] button,
[class*="st-key-cheer_active_"] button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--tertiary) !important;
  font-size: 0.71rem !important;
  font-weight: 700 !important;
  min-height: 28px !important;
  padding: 0 !important;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
[class*="st-key-cheer_"] button::before,
[class*="st-key-cheer_active_"] button::before {
  content: "";
  width: 15px;
  height: 15px;
  background-color: currentColor;
  -webkit-mask: __ICON_HEART__;
  mask: __ICON_HEART__;
}
[class*="st-key-cheer_active_"] button { color: var(--accent) !important; }
[class*="st-key-report_"] button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--tertiary) !important;
  font-size: 0.9rem !important;
  min-height: 24px !important;
  padding: 0 !important;
}

/* ------------------------------------------------------------------ */
/* Metrics / summary / bars                                            */
/* ------------------------------------------------------------------ */
.hj-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  overflow: hidden;
}
.hj-metric {
  padding: 13px 8px 11px;
  text-align: center;
  border-right: 1px solid var(--line);
}
.hj-metric:last-child { border-right: none; }
.hj-metric-value {
  font-size: 1.3rem;
  font-weight: 800;
  letter-spacing: -0.05em;
  color: var(--text);
}
.hj-metric-label { font-size: 0.65rem; color: var(--muted); margin-top: 2px; }

.hj-summary {
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
  border-radius: 18px;
  padding: 15px 16px;
  font-size: 0.84rem;
  line-height: 1.62;
  color: #302A63;
  letter-spacing: -0.01em;
}
.hj-summary b { color: var(--accent); }

.hj-bar-row { margin: 7px 0 9px; }
.hj-bar-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 0.72rem;
  margin-bottom: 4px;
}
.hj-bar-head span { color: var(--muted); font-weight: 600; }
.hj-bar-head b { color: var(--text); font-weight: 700; }
.hj-bar-track { height: 6px; background: #F0F0F5; border-radius: 999px; overflow: hidden; }
.hj-bar-fill { height: 100%; background: var(--accent); border-radius: 999px; }

/* ------------------------------------------------------------------ */
/* D-day                                                               */
/* ------------------------------------------------------------------ */
.hj-dday {
  background: #F1EEFF;
  border: 1px solid var(--accent-line);
  border-radius: 20px;
  padding: 17px 18px 15px;
}
.hj-dday-label {
  font-size: 0.62rem;
  font-weight: 800;
  color: var(--accent);
  letter-spacing: 0.08em;
}
.hj-dday-value {
  font-size: 2.25rem;
  font-weight: 900;
  letter-spacing: -0.07em;
  color: var(--accent);
  line-height: 1.06;
  margin-top: 2px;
}
.hj-dday-name { font-size: 0.82rem; font-weight: 700; color: var(--text); margin-top: 2px; }
.hj-dday-date { font-size: 0.7rem; color: var(--muted); margin-top: 2px; }
.hj-dday-demo {
  display: inline-block;
  margin-top: 9px;
  font-size: 0.6rem;
  font-weight: 800;
  color: var(--accent);
  background: #FFFFFF;
  border: 1px solid var(--accent-line);
  padding: 3px 8px;
  border-radius: 999px;
}

/* ------------------------------------------------------------------ */
/* Chips / segmented                                                   */
/* ------------------------------------------------------------------ */
.st-key-week_strip [data-testid="stHorizontalBlock"] { gap: 5px !important; }
.st-key-week_strip .stButton > button {
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--muted) !important;
  border-radius: 12px !important;
  min-height: 44px !important;
  padding: 3px 0 !important;
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  box-shadow: none !important;
}
.st-key-week_strip .stButton > button[kind="primary"] {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
}

.st-key-subject_chips [data-testid="stHorizontalBlock"] {
  gap: 6px !important;
  flex-wrap: nowrap !important;
  overflow-x: auto !important;
  padding-bottom: 3px;
  scrollbar-width: none;
}
.st-key-subject_chips [data-testid="stHorizontalBlock"]::-webkit-scrollbar { display: none; }
.st-key-subject_chips [data-testid="stHorizontalBlock"] > div {
  flex: 0 0 auto !important;
  min-width: 58px;
}
.st-key-subject_chips .stButton > button {
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--muted) !important;
  border-radius: 999px !important;
  min-height: 32px !important;
  padding: 0 4px !important;
  font-size: 0.66rem !important;
  font-weight: 700 !important;
  box-shadow: none !important;
}
.st-key-subject_chips .stButton > button[kind="primary"] {
  background: var(--accent-soft) !important;
  border-color: var(--accent-line) !important;
  color: var(--accent) !important;
}

.st-key-report_tabs [data-testid="stHorizontalBlock"] { gap: 4px !important; }
.st-key-report_tabs .stButton > button {
  background: #F1F1F5 !important;
  border: none !important;
  color: var(--muted) !important;
  border-radius: 11px !important;
  min-height: 36px !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  box-shadow: none !important;
}
.st-key-report_tabs .stButton > button[kind="primary"] {
  background: var(--surface) !important;
  color: var(--text) !important;
  box-shadow: 0 1px 4px rgba(17, 17, 20, 0.08) !important;
}

/* ------------------------------------------------------------------ */
/* Bottom nav                                                          */
/* ------------------------------------------------------------------ */
.st-key-bottom_nav {
  position: fixed;
  left: 50%;
  bottom: calc(100vh - 24px - min(844px, calc(100vh - 48px)));
  transform: translateX(-50%);
  width: min(374px, calc(100vw - 48px));
  z-index: 120;
  padding: 7px 10px 9px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-top: 1px solid var(--line);
  border-radius: 0 0 36px 36px;
}
.st-key-bottom_nav::after {
  content: "";
  display: block;
  width: 118px;
  height: 4px;
  margin: 7px auto 0;
  background: #111116;
  border-radius: 999px;
  opacity: 0.9;
}
.st-key-bottom_nav [data-testid="stHorizontalBlock"] { gap: 0 !important; }

.st-key-bottom_nav .stButton,
.st-key-bottom_nav .stButton > button,
.st-key-bottom_nav .stButton > button:hover,
.st-key-bottom_nav .stButton > button:focus,
.st-key-bottom_nav .stButton > button:focus-visible,
.st-key-bottom_nav .stButton > button:active,
.st-key-bottom_nav .stButton > button[kind="primary"],
.st-key-bottom_nav .stButton > button[kind="primary"]:hover,
.st-key-bottom_nav .stButton > button[kind="primary"]:focus,
.st-key-bottom_nav .stButton > button[kind="primary"]:active {
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}
.st-key-bottom_nav .stButton > button {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 1px !important;
  color: var(--tertiary) !important;
  font-size: 0.6rem !important;
  font-weight: 700 !important;
  min-height: 44px !important;
  padding: 0 !important;
}
.st-key-bottom_nav .stButton > button[kind="primary"] { color: var(--accent) !important; }
.st-key-bottom_nav .stButton > button::before {
  content: "";
  display: block;
  width: 22px;
  height: 22px;
  background-color: currentColor;
}
.st-key-bottom_nav [data-testid="stHorizontalBlock"] > div:nth-child(1) button::before { -webkit-mask: __ICON_HOME__; mask: __ICON_HOME__; }
.st-key-bottom_nav [data-testid="stHorizontalBlock"] > div:nth-child(2) button::before { -webkit-mask: __ICON_FEED__; mask: __ICON_FEED__; }
.st-key-bottom_nav [data-testid="stHorizontalBlock"] > div:nth-child(3) button::before { -webkit-mask: __ICON_CHART__; mask: __ICON_CHART__; }
.st-key-bottom_nav [data-testid="stHorizontalBlock"] > div:nth-child(4) button::before { -webkit-mask: __ICON_CLOCK__; mask: __ICON_CLOCK__; }
.st-key-bottom_nav [data-testid="stHorizontalBlock"] > div:nth-child(5) button::before { -webkit-mask: __ICON_SETTINGS__; mask: __ICON_SETTINGS__; }

/* ------------------------------------------------------------------ */
/* Buttons / inputs                                                    */
/* ------------------------------------------------------------------ */
.stButton > button {
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-size: 0.82rem !important;
  min-height: 44px;
  border: 1px solid var(--line) !important;
  background: var(--surface) !important;
  color: var(--text) !important;
  box-shadow: none !important;
  transition: all 0.15s ease;
}
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
  box-shadow: 0 8px 18px rgba(85, 70, 245, 0.20) !important;
}
.stButton > button[kind="primary"]:hover {
  background: #4335E8 !important;
  border-color: #4335E8 !important;
}
.stButton > button:hover { background: #F5F5F8 !important; }

[class*="st-key-pact_"] button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #B8B8C2 !important;
  font-size: 1.1rem !important;
  min-height: 28px !important;
  padding: 0 !important;
}
[class*="st-key-pact_"] button:hover { color: var(--accent) !important; }

[class*="st-key-recall_yes_"] button {
  background: var(--accent-soft) !important;
  border: 1px solid var(--accent-line) !important;
  color: var(--accent) !important;
  border-radius: 999px !important;
  min-height: 32px !important;
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  box-shadow: none !important;
  padding: 0 10px !important;
}
[class*="st-key-recall_no_"] button {
  background: #F5F5F8 !important;
  border: 1px solid var(--line) !important;
  color: var(--muted) !important;
  border-radius: 999px !important;
  min-height: 32px !important;
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  box-shadow: none !important;
  padding: 0 10px !important;
}

.stTextInput input, .stTextArea textarea {
  border-radius: 12px !important;
  border: 1px solid var(--line) !important;
  background: #F7F7FA !important;
  font-size: 0.86rem !important;
  color: var(--text) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(85, 70, 245, 0.10) !important;
}
label, .stTextInput label, .stTextArea label {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  color: var(--muted) !important;
}

div[role="radiogroup"] { display: flex; gap: 6px; flex-wrap: wrap; }
div[role="radiogroup"] label {
  background: #F2F2F7;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 5px 10px !important;
  margin: 0 !important;
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  color: var(--muted) !important;
  transition: all 0.15s ease;
}
div[role="radiogroup"] label:has(input:checked) {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent) !important;
}
div[role="radiogroup"] label > div:first-child { display: none; }

/* ------------------------------------------------------------------ */
/* Onboarding                                                          */
/* ------------------------------------------------------------------ */
.hj-onboarding-hero {
  margin: 0 -16px;
  padding: 42px 24px 26px;
  background: #F1EEFF;
  border-radius: 0 0 26px 26px;
}
.hj-onboarding-brand {
  font-size: 1.9rem;
  font-weight: 900;
  letter-spacing: -0.08em;
  color: var(--accent);
  line-height: 1;
}
.hj-onboarding-title {
  font-size: 1.68rem;
  font-weight: 800;
  letter-spacing: -0.06em;
  color: var(--text);
  line-height: 1.28;
  margin-top: 18px;
}
.hj-onboarding-sub {
  font-size: 0.82rem;
  color: var(--muted);
  margin-top: 8px;
  line-height: 1.5;
}
.hj-feature {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 0;
  border-bottom: 1px solid var(--line);
}
.hj-feature:last-child { border-bottom: none; }
.hj-feature-icon {
  width: 34px;
  height: 34px;
  border-radius: 11px;
  background: var(--accent-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}
.hj-feature-icon .hj-icon {
  width: 18px;
  height: 18px;
  background-color: var(--accent);
}
.hj-feature b { font-size: 0.84rem; color: var(--text); font-weight: 700; }
.hj-feature p { font-size: 0.72rem; color: var(--muted); margin: 2px 0 0; line-height: 1.4; }

.hj-icon { display: inline-block; -webkit-mask: center / contain no-repeat; mask: center / contain no-repeat; }
.hj-icon.icon-clock { -webkit-mask: __ICON_CLOCK__; mask: __ICON_CLOCK__; }
.hj-icon.icon-lock { -webkit-mask: __ICON_LOCK__; mask: __ICON_LOCK__; }
.hj-icon.icon-pin { -webkit-mask: __ICON_PIN__; mask: __ICON_PIN__; }
.hj-icon.icon-spark { -webkit-mask: __ICON_SPARK__; mask: __ICON_SPARK__; }

/* ------------------------------------------------------------------ */
/* Misc                                                               */
/* ------------------------------------------------------------------ */
[data-testid="stExpander"] {
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  background: var(--surface) !important;
}
[data-testid="stExpander"] summary {
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  color: var(--text) !important;
}
[data-testid="stAlert"] {
  border-radius: 14px !important;
  border: 1px solid var(--line) !important;
  font-size: 0.8rem !important;
  background: #F7F7FA !important;
  color: var(--text) !important;
}
[data-testid="stCaptionContainer"] { font-size: 0.72rem !important; }
div[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--line) !important;
  border-radius: 18px !important;
  background: var(--surface) !important;
  padding: 14px !important;
}

/* settings rows */
[class*="st-key-export"] { background: transparent !important; }
[class*="st-key-switch_"] button,
[class*="st-key-export"] button {
  display: flex !important;
  justify-content: flex-start !important;
  align-items: center !important;
  width: 100% !important;
  text-align: left !important;
  background: var(--surface) !important;
  border: none !important;
  border-bottom: 1px solid var(--line) !important;
  border-radius: 0 !important;
  min-height: 50px !important;
  padding: 0 14px !important;
  font-size: 0.84rem !important;
  font-weight: 600 !important;
  color: var(--text) !important;
  box-shadow: none !important;
}
[class*="st-key-switch_"] button > div,
[class*="st-key-export"] button > div {
  justify-content: flex-start !important;
  text-align: left !important;
}
[class*="st-key-switch_"] button p,
[class*="st-key-export"] button p { text-align: left !important; }
[class*="st-key-switch_"] button::after,
[class*="st-key-export"] button::after {
  content: "›";
  color: #B8B8C2;
  font-size: 1.1rem;
  font-weight: 400;
  margin-left: auto;
}
.hj-ai-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--tertiary);
  display: inline-block;
  margin-right: 7px;
}
.hj-ai-dot.on { background: var(--success); }

/* ------------------------------------------------------------------ */
/* Mobile                                                              */
/* ------------------------------------------------------------------ */
@media (max-width: 640px) {
  .stApp { overflow: auto; background: var(--surface); }
  .st-key-phone_screen {
    width: 100%;
    height: 100dvh !important;
    min-height: 100dvh !important;
    max-height: 100dvh !important;
    margin: 0;
    padding: 0 16px 84px;
    border: none;
    border-radius: 0;
    box-shadow: none;
    overflow-y: auto !important;
  }
  .hj-phone-header { margin: 0 -16px; padding: 8px 16px 0; }
  .hj-statusbar { display: none; }
  .hj-island { display: none; }
  .st-key-bottom_nav {
    left: 0;
    bottom: 0;
    transform: none;
    width: 100%;
    margin: 0;
    border-radius: 0;
    padding-bottom: calc(9px + env(safe-area-inset-bottom));
  }
  .st-key-bottom_nav::after { display: none; }
}
"""

for _name, _mask in _MASKS.items():
    CSS = CSS.replace(f"__ICON_{_name.upper()}__", _mask)
