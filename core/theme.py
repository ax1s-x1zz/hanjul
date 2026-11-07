"""Design system: mobile-first phone frame, typography, cards, nav."""
from __future__ import annotations

CSS = r"""
:root {
  --hj-bg: #ECECF4;
  --hj-surface: #FFFFFF;
  --hj-surface-2: #F7F7FB;
  --hj-text: #17171D;
  --hj-muted: #85858F;
  --hj-line: #EEEEF4;
  --hj-accent: #5B4DFF;
  --hj-accent-2: #7C6CFF;
  --hj-accent-soft: #EFECFF;
  --hj-success: #12B76A;
  --hj-danger: #F04438;
  --hj-radius: 20px;
}

html, body, [class*="css"] {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR',
    'Apple SD Gothic Neo', sans-serif;
  -webkit-font-smoothing: antialiased;
  word-break: keep-all;
}

.stApp {
  background:
    radial-gradient(1100px 600px at 50% -10%, #F7F6FF 0%, rgba(247,246,255,0) 62%),
    var(--hj-bg);
  overflow: hidden;
}

footer { visibility: hidden; }
header[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

.block-container {
  max-width: none !important;
  padding: 0 !important;
}

/* ------------------------------------------------------------------ */
/* Phone frame                                                         */
/* ------------------------------------------------------------------ */
.st-key-phone_screen {
  box-sizing: border-box;
  width: min(430px, calc(100vw - 32px));
  height: min(886px, calc(100vh - 32px)) !important;
  min-height: min(886px, calc(100vh - 32px)) !important;
  max-height: min(886px, calc(100vh - 32px)) !important;
  flex: 0 0 auto !important;
  margin: 16px auto;
  padding: 0 18px 84px;
  background: var(--hj-surface);
  border: 9px solid #111116;
  border-radius: 50px;
  box-shadow:
    0 40px 100px rgba(17, 17, 22, 0.30),
    0 8px 24px rgba(17, 17, 22, 0.12);
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
  gap: 0.55rem;
  padding-bottom: 0;
}
.st-key-page_content::-webkit-scrollbar { display: none; }

/* ------------------------------------------------------------------ */
/* Sticky phone header                                                 */
/* ------------------------------------------------------------------ */
.hj-phone-header {
  position: sticky;
  top: 0;
  z-index: 80;
  margin: 0 -18px;
  padding: 0 18px 9px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom: 1px solid var(--hj-line);
}

.hj-statusbar {
  position: relative;
  height: 31px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 800;
  color: var(--hj-text);
  letter-spacing: -0.01em;
}
.hj-island {
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 84px;
  height: 23px;
  background: #111116;
  border-radius: 999px;
}
.hj-status-icons {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.hj-signal {
  display: inline-flex;
  align-items: flex-end;
  gap: 1.5px;
  height: 10px;
}
.hj-signal i {
  display: block;
  width: 2.5px;
  background: var(--hj-text);
  border-radius: 2px;
}
.hj-signal i:nth-child(1) { height: 4px; }
.hj-signal i:nth-child(2) { height: 6px; }
.hj-signal i:nth-child(3) { height: 8px; }
.hj-signal i:nth-child(4) { height: 10px; }
.hj-battery {
  width: 18px;
  height: 9px;
  border: 1.5px solid var(--hj-text);
  border-radius: 3px;
  position: relative;
}
.hj-battery::after {
  content: "";
  position: absolute;
  right: -4px;
  top: 2px;
  width: 2px;
  height: 4px;
  background: var(--hj-text);
  border-radius: 0 2px 2px 0;
}

.hj-appbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 0;
}
.hj-logo {
  font-size: 1.42rem;
  font-weight: 900;
  letter-spacing: -0.07em;
  color: var(--hj-text);
  line-height: 1;
}
.hj-logo span { color: var(--hj-accent); }
.hj-appbar-right { display: flex; align-items: center; gap: 8px; }
.hj-region {
  font-size: 0.66rem;
  font-weight: 800;
  color: var(--hj-accent);
  background: var(--hj-accent-soft);
  padding: 5px 9px;
  border-radius: 999px;
}
.hj-avatar {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  background: linear-gradient(135deg, #5B4DFF 0%, #9C8BFF 100%);
  color: #fff;
  font-weight: 800;
  font-size: 0.76rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(91, 77, 255, 0.25);
}

/* ------------------------------------------------------------------ */
/* Page header                                                         */
/* ------------------------------------------------------------------ */
.hj-page-head { padding: 11px 0 5px; }
.hj-page-title {
  font-size: 1.42rem;
  font-weight: 900;
  letter-spacing: -0.055em;
  color: var(--hj-text);
  line-height: 1.2;
}
.hj-page-sub {
  font-size: 0.8rem;
  color: var(--hj-muted);
  margin-top: 4px;
  line-height: 1.45;
}
.hj-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.63rem;
  font-weight: 800;
  color: var(--hj-accent);
  background: var(--hj-accent-soft);
  padding: 4px 8px;
  border-radius: 999px;
  margin-left: 6px;
  vertical-align: 3px;
  letter-spacing: 0;
}

/* ------------------------------------------------------------------ */
/* Cards                                                               */
/* ------------------------------------------------------------------ */
div[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--hj-line) !important;
  border-radius: var(--hj-radius) !important;
  background: var(--hj-surface) !important;
  box-shadow: 0 6px 18px rgba(23, 23, 29, 0.035);
  padding: 14px !important;
}

/* ------------------------------------------------------------------ */
/* Feed                                                                */
/* ------------------------------------------------------------------ */
.hj-feed-head { display: flex; align-items: center; gap: 10px; }
.hj-mini-avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: linear-gradient(135deg, #EFECFF 0%, #DCD6FF 100%);
  color: var(--hj-accent);
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.82rem;
  flex: 0 0 auto;
}
.hj-feed-meta { display: flex; flex-direction: column; line-height: 1.25; }
.hj-feed-name { font-weight: 800; font-size: 0.85rem; color: var(--hj-text); }
.hj-feed-sub { font-size: 0.71rem; color: var(--hj-muted); }
.hj-time { margin-left: auto; font-size: 0.66rem; color: var(--hj-muted); white-space: nowrap; }
.hj-post-text {
  font-size: 0.92rem;
  line-height: 1.62;
  color: var(--hj-text);
  margin: 11px 0 9px;
}
.hj-tag {
  display: inline-flex;
  font-size: 0.64rem;
  font-weight: 700;
  color: #6B6B78;
  background: #F5F5FA;
  border: 1px solid var(--hj-line);
  padding: 3px 8px;
  border-radius: 999px;
  margin: 0 4px 0 0;
}

/* ------------------------------------------------------------------ */
/* Today period row                                                    */
/* ------------------------------------------------------------------ */
.hj-period-row { display: flex; gap: 12px; align-items: flex-start; }
.hj-period {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: var(--hj-accent-soft);
  color: var(--hj-accent);
  font-weight: 900;
  font-size: 0.77rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}
.hj-period-subject {
  font-weight: 800;
  font-size: 0.93rem;
  color: var(--hj-text);
  line-height: 1.3;
}
.hj-period-status {
  font-size: 0.75rem;
  color: var(--hj-muted);
  margin-top: 3px;
  line-height: 1.42;
}
.hj-period-status .ok { color: var(--hj-success); font-weight: 800; }
.hj-period-status .public { color: var(--hj-accent); font-weight: 800; }

/* ------------------------------------------------------------------ */
/* Simple CSS bars (no chart library)                                  */
/* ------------------------------------------------------------------ */
.hj-bar-row { margin: 8px 0 10px; }
.hj-bar-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 0.76rem;
  margin-bottom: 4px;
}
.hj-bar-head span { color: #5F5F6B; font-weight: 700; }
.hj-bar-head b { color: var(--hj-text); font-weight: 800; }
.hj-bar-track {
  height: 8px;
  background: #F0F0F6;
  border-radius: 999px;
  overflow: hidden;
}
.hj-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #5B4DFF 0%, #9C8BFF 100%);
  border-radius: 999px;
}

/* ------------------------------------------------------------------ */
/* D-day                                                               */
/* ------------------------------------------------------------------ */
.hj-dday {
  border-radius: 22px;
  padding: 19px;
  background: linear-gradient(135deg, #5B4DFF 0%, #8B7BFF 100%);
  color: #fff;
  box-shadow: 0 16px 34px rgba(91, 77, 255, 0.26);
  margin: 6px 0 5px;
}
.hj-dday-label { font-size: 0.66rem; font-weight: 800; opacity: 0.78; letter-spacing: 0.08em; }
.hj-dday-value { font-size: 2.15rem; font-weight: 900; letter-spacing: -0.06em; line-height: 1.08; margin-top: 3px; }
.hj-dday-name { font-size: 0.84rem; font-weight: 700; opacity: 0.96; margin-top: 3px; }
.hj-dday-date { font-size: 0.72rem; opacity: 0.75; margin-top: 2px; }
.hj-dday-demo {
  display: inline-block;
  margin-top: 10px;
  font-size: 0.62rem;
  font-weight: 800;
  background: rgba(255, 255, 255, 0.18);
  padding: 3px 8px;
  border-radius: 999px;
}

/* ------------------------------------------------------------------ */
/* Onboarding                                                          */
/* ------------------------------------------------------------------ */
.hj-hero {
  font-size: 2.85rem;
  font-weight: 900;
  letter-spacing: -0.08em;
  color: var(--hj-text);
  line-height: 1.02;
  margin-top: 25px;
}
.hj-hero span { color: var(--hj-accent); }
.hj-hero-sub {
  font-size: 0.93rem;
  color: var(--hj-muted);
  margin-top: 9px;
  line-height: 1.5;
}
.hj-feature {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--hj-line);
  border-radius: 16px;
  background: #fff;
  margin-bottom: 8px;
}
.hj-feature-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: var(--hj-accent-soft);
  color: var(--hj-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex: 0 0 auto;
}
.hj-feature b { font-size: 0.84rem; color: var(--hj-text); }
.hj-feature p { font-size: 0.75rem; color: var(--hj-muted); margin: 2px 0 0; line-height: 1.42; }

/* ------------------------------------------------------------------ */
/* Bottom nav                                                          */
/* ------------------------------------------------------------------ */
.st-key-bottom_nav {
  position: fixed;
  left: 50%;
  bottom: calc(100vh - 16px - min(886px, calc(100vh - 32px)));
  transform: translateX(-50%);
  width: min(412px, calc(100vw - 48px));
  z-index: 120;
  margin: 0;
  padding: 8px 10px 14px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-top: 1px solid var(--hj-line);
  border-radius: 0 0 40px 40px;
}
.st-key-bottom_nav [data-testid="stHorizontalBlock"] { gap: 0 !important; }
.st-key-bottom_nav .stButton > button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--hj-muted) !important;
  font-size: 0.67rem !important;
  font-weight: 800 !important;
  padding: 2px 0 !important;
  min-height: 40px !important;
}
.st-key-bottom_nav .stButton > button[kind="primary"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--hj-accent) !important;
}
.st-key-bottom_nav .stButton > button[kind="primary"]::before {
  content: "";
  display: block;
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: var(--hj-accent);
  margin: 0 auto 3px;
}
.st-key-bottom_nav .stButton > button:hover {
  color: var(--hj-accent) !important;
  background: transparent !important;
}

/* ------------------------------------------------------------------ */
/* Buttons / inputs                                                    */
/* ------------------------------------------------------------------ */
.stButton > button {
  border-radius: 14px !important;
  font-weight: 800 !important;
  font-size: 0.83rem !important;
  min-height: 44px;
  border: 1px solid var(--hj-line) !important;
  background: var(--hj-surface-2) !important;
  color: var(--hj-text) !important;
  box-shadow: none !important;
  transition: all 0.15s ease;
}
.stButton > button[kind="primary"] {
  background: var(--hj-accent) !important;
  border-color: var(--hj-accent) !important;
  color: #fff !important;
  box-shadow: 0 8px 18px rgba(91, 77, 255, 0.22) !important;
}
.stButton > button[kind="primary"]:hover {
  background: #4B3DF0 !important;
  border-color: #4B3DF0 !important;
}
.stButton > button:hover {
  border-color: #DAD6FF !important;
  background: #F3F1FF !important;
}

[class*="st-key-report-"] button {
  background: transparent !important;
  border: none !important;
  color: #A6A6B3 !important;
  font-size: 0.68rem !important;
  min-height: 28px !important;
  padding: 0 !important;
  box-shadow: none !important;
}
[class*="st-key-cheer-"] button {
  background: var(--hj-accent-soft) !important;
  border: 1px solid #E4DFFF !important;
  color: var(--hj-accent) !important;
  font-size: 0.71rem !important;
  min-height: 32px !important;
  border-radius: 999px !important;
  padding: 0 12px !important;
  box-shadow: none !important;
}

.stTextInput input, .stTextArea textarea {
  border-radius: 14px !important;
  border: 1px solid var(--hj-line) !important;
  background: var(--hj-surface-2) !important;
  font-size: 0.87rem !important;
  color: var(--hj-text) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--hj-accent) !important;
  box-shadow: 0 0 0 3px rgba(91, 77, 255, 0.12) !important;
}
label, .stTextInput label, .stTextArea label {
  font-size: 0.75rem !important;
  font-weight: 800 !important;
  color: #5F5F6B !important;
}

/* ------------------------------------------------------------------ */
/* Metrics / tabs / progress / misc                                    */
/* ------------------------------------------------------------------ */
[data-testid="stMetric"] {
  background: var(--hj-surface-2);
  border: 1px solid var(--hj-line);
  border-radius: 18px;
  padding: 14px 14px 10px;
}
[data-testid="stMetricValue"] {
  font-size: 1.42rem;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: var(--hj-text);
}
[data-testid="stMetricLabel"] {
  color: var(--hj-muted);
  font-size: 0.71rem;
  font-weight: 700;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: var(--hj-surface-2);
  padding: 4px;
  border-radius: 14px;
}
.stTabs [data-baseweb="tab"] {
  height: 36px;
  border-radius: 10px;
  padding: 0 14px;
  font-size: 0.79rem;
  font-weight: 800;
  color: var(--hj-muted);
}
.stTabs [aria-selected="true"] {
  background: #fff !important;
  color: var(--hj-text) !important;
  box-shadow: 0 1px 4px rgba(23, 23, 29, 0.06);
}
.stTabs [data-baseweb="tab-highlight"] {
  background-color: var(--hj-accent) !important;
  height: 2px !important;
}
.stTabs [data-baseweb="tab-border"] { background: transparent !important; }

.stProgress > div > div {
  background: #F0F0F6 !important;
  border-radius: 999px !important;
}
.stProgress > div > div > div > div {
  background: var(--hj-accent) !important;
  border-radius: 999px !important;
}

[data-testid="stExpander"] {
  border: 1px solid var(--hj-line);
  border-radius: 16px;
  background: #fff;
}
[data-testid="stAlert"] {
  border-radius: 14px;
  border: 1px solid var(--hj-line);
  font-size: 0.81rem;
}
[data-testid="stCaptionContainer"] { font-size: 0.74rem !important; }

/* ------------------------------------------------------------------ */
/* Mobile: remove the frame, go full-bleed                             */
/* ------------------------------------------------------------------ */
@media (max-width: 640px) {
  .stApp { overflow: auto; background: #fff; }
  .st-key-phone_screen {
    width: 100%;
    height: 100dvh !important;
    min-height: 100dvh !important;
    max-height: 100dvh !important;
    flex: 1 1 auto !important;
    margin: 0;
    padding: 0 16px 76px;
    border: none;
    border-radius: 0;
    box-shadow: none;
    overflow-y: auto !important;
  }
  .hj-phone-header { margin: 0 -16px; padding: 8px 16px 8px; }
  .hj-statusbar { display: none; }
  .hj-island { display: none; }
  .st-key-bottom_nav {
    left: 0;
    bottom: 0;
    transform: none;
    width: 100%;
    margin: 0;
    border-radius: 0;
    padding-bottom: calc(12px + env(safe-area-inset-bottom));
  }
}

/* Final bottom-nav overrides: keep text tabs in every interaction state. */
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
  color: var(--hj-muted) !important;
  font-size: 0.67rem !important;
  font-weight: 800 !important;
  min-height: 40px !important;
  padding: 2px 0 !important;
}
.st-key-bottom_nav .stButton > button[kind="primary"] {
  color: var(--hj-accent) !important;
}

"""
