# DESIGN.md — 한줄 디자인 시스템

> **“인스타에는 노는 것이, 여기에는 배운 것이.”**
> 텍스트 중심 · 단일 액센트 · 폰 프레임 · 하단 탭.

---

## 1. 레퍼런스 (무엇을 가져왔는가)

| # | 레퍼런스 | 가져온 것 | 링크 |
|---|---|---|---|
| 1 | **Threads** | 텍스트 중심 피드, 1px 헤어라인, 그림자 없는 카드, pill 태그, 5개 하단 탭, frosted glass | [Refero Styles](https://styles.refero.design/style/182f8743-fe22-45d3-98bc-9fd29d058602) · [Banani](https://www.banani.co/references/apps/threads) |
| 2 | **Toss** | 360–430px 모바일 캔버스, 4px 그리드, 단일 액센트, 56px 하단 탭, 큰 터치 타깃 | [Toss Design Reference](https://github.com/rohitg00/awesome-claude-design/blob/main/design-md/playful/toss.md) |
| 3 | **BeReal** | “한 번, 정직하게” 컨셉, 시간순 피드, 미니멀 크롬, 과시 없는 공유 | [BeReal redesign case](https://medium.com/@rynmnfrd/redesigning-bereal-5271fe87a984) |
| 4 | **당근** | 지역 필(pill), 동네 정체성, 따뜻한 뉴트럴, 신뢰 중심 카피 | [daangn.com](https://www.daangn.com) |
| 5 | **Duolingo** | 스트릭·진행률의 가벼운 게이미피케이션 (과하지 않게) | [duolingo.com](https://www.duolingo.com) |
| 6 | **GitHub 잔디** | “쌓인다”는 시각적 은유 — 지식의 축적을 보여주는 방향 | [github.com](https://github.com) |
| 7 | **Linear / Notion** | 차분한 타이포, 높은 대비, 조용한 UI, 정보 위계 | [linear.app](https://linear.app) · [notion.so](https://notion.so) |
| 8 | **Apple HIG / Material 3** | 44px 터치 타깃, 안전 영역, 모바일 우선, 8pt 리듬 | [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/) · [Material 3](https://m3.material.io) |

### 레퍼런스에서 의도적으로 **버린** 것

- 인스타식 **좋아요 수 경쟁** → 응원은 있지만 랭킹·팔로워 수 없음
- 틱톡식 **무한 자동재생** → “더 보기” 명시적 페이지네이션
- 공부 인증샷 · 성적 자랑 → **과정·막힘** 중심
- 화려한 그라데이션·다중 액센트 → **단일 액센트**
- 이모지 아이콘 남발 → **텍스트 탭 + 점 표시**

---

## 2. 디자인 토큰

### Color

| 토큰 | 값 | 용도 |
|---|---|---|
| `--hj-accent` | `#5B4DFF` | 단일 액센트, 활성 탭, CTA |
| `--hj-accent-soft` | `#EFECFF` | pill, 선택 배경 |
| `--hj-text` | `#17171D` | 본문·제목 |
| `--hj-muted` | `#85858F` | 보조 텍스트 |
| `--hj-line` | `#EEEEF4` | 1px 구분선 |
| `--hj-surface` | `#FFFFFF` | 카드·폰 화면 |
| `--hj-surface-2` | `#F7F7FB` | 입력·메트릭 배경 |
| `--hj-bg` | `#ECECF4` | 데스크톱 배경 |
| `--hj-success` | `#12B76A` | 기록 완료 |
| `--hj-danger` | `#F04438` | 오류·신고 |

> Streamlit 기본 primary(빨강)는 `.streamlit/config.toml`에서 `#5B4DFF`로 교체.

### Typography

| 역할 | 크기 | 무게 | 자간 |
|---|---|---|---|
| Hero | 2.85rem | 900 | -0.08em |
| Page title | 1.42rem | 900 | -0.055em |
| Section | 1.0rem | 800 | -0.03em |
| Body | 0.92rem | 400 | -0.01em |
| Caption | 0.75rem | 500 | 0 |
| Bottom nav | 0.67rem | 800 | 0 |

- 폰트: `Pretendard` → `-apple-system` → `Noto Sans KR` → `Apple SD Gothic Neo`
- 원격 폰트 의존 없이 시스템 폰트로 폴백 (해커톤 네트워크 대비)

### Spacing / Radius / Shadow

- Spacing: **4 / 8 / 12 / 16 / 20 / 24 / 32**
- Radius: **14** (버튼) · **16** (입력) · **18** (메트릭) · **20** (카드) · **22** (D-day) · **50** (폰 프레임)
- Shadow: 카드 `0 6px 18px rgba(23,23,29,.035)` / 프레임 `0 40px 100px rgba(17,17,22,.30)`
- Motion: `150ms ease`

---

## 3. 폰 프레임 (Phone Shell)

| 항목 | 값 |
|---|---|
| 외곽 | **430 × 886px**, 9px 베젤, 50px 라운드 |
| 내부 | 868px (베젤 제외), 내부 스크롤 |
| 상단 | 상태바(9:41 · 다이나믹 아일랜드 · 신호/배터리) + 앱바 |
| 하단 | **412px 고정 탭**, 63px 높이, 5개 텍스트 탭 |
| 데스크톱 | 중앙 정렬, `#ECECF4` 배경, 큰 그림자 |
| 모바일 | `max-width: 640px`에서 **풀블리드**, 프레임 제거, `100dvh` |
| 스크롤 | 페이지만 내부 스크롤, 하단 탭은 `position: fixed` |

### 하단 탭 규칙

- 활성: **보라색 텍스트 + 4px 점**, 배경 없음
- 비활성: 회색 텍스트
- hover/focus/active에서도 **절대 채워진 버튼 금지**
- 탭 전환 시 내부 스크롤 **맨 위로 리셋** (`st.components.v1.html`)

---

## 4. 화면별 원칙

| 화면 | 핵심 | 금지 |
|---|---|---|
| 온보딩 | 1문장 가치 제안 + 데모 CTA | 기능 나열 과다 |
| 오늘 | 교시 카드 · 진행률 · 10초 입력 | 표 형태 |
| 피드 | 아바타+닉네임+과목+한 줄+태그 | 좋아요 순 정렬 |
| 리포트 | 메트릭 3개 + CSS 바 + 막힘 TOP3 | 차트 라이브러리 남용 |
| 리콜 | 큰 D-day 카드 + 복습 카드 | 시험 없는 빈 화면 |
| 설정 | 프로필 · 계정 전환 · 데이터 권리 | 숨겨진 위험 버튼 |

---

## 5. 접근성

- 터치 타깃 **최소 40px** (주요 CTA 44px)
- 텍스트 대비 **4.5:1 이상**
- 색만으로 상태를 구분하지 않음 (`✓`, 점, 텍스트 병기)
- 모바일 세로 화면 우선, `env(safe-area-inset-bottom)` 대응

---

## 6. 구현 위치

| 파일 | 역할 |
|---|---|
| `core/theme.py` | 전체 CSS (토큰·폰 프레임·탭·카드·차트 바) |
| `core/ui.py` | 안전한 HTML 조각 (상태바·앱바·피드 헤드·D-day) |
| `.streamlit/config.toml` | Streamlit primary color = `#5B4DFF` |
| `app.py` | 폰 셸, 하단 탭, 스크롤 리셋 |

---

## 7. 다음 단계 (Post-Hackathon)

- 다크 모드 토큰
- 실제 Pretendard 셀프호스팅
- 피드 카드 등장 모션 (120ms fade/slide)
- 하단 탭 아이콘 (Material Symbols) + 텍스트 병기
- 접근성 자동 검사(axe)
