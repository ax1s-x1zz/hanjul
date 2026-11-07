# DESIGN.md — 한줄 디자인 시스템 V2

> **“웹 대시보드가 아니라, 손에 쥔 기록 앱.”**
> 390×844 폰 셸 · 아이콘 탭 바 · inset grouped list · 단일 액센트.

---

## 0. 진단 — V1이 “바이브 코딩”처럼 보인 이유

| 문제 | V1 | V2 |
|---|---|---|
| Streamlit 위젯 노출 | date input, selectbox, tabs, expander, info box | **주간 스트립·칩·세그먼트·그룹 리스트**로 교체 |
| 카드 남발 | 교시 7개 = 카드 7개, 피드 = 카드 | **inset grouped list 1개**, 피드는 **헤어라인 리스트** |
| 웹 랜딩 문법 | 큰 페이지 타이틀 + 메타데이터 | **컴팩트 앱바 타이틀** + 날짜 헤더 |
| 반복 액션 | “수정” 버튼 7개 | **작은 chevron 1개** per row |
| AI 흔적 | 이모지 아이콘, 보라색 그라데이션, 과한 그림자 | **라인 SVG 아이콘**, 단일 액센트, 그림자 최소 |
| 정보 위계 | 모든 텍스트가 비슷한 크기/굵기 | 28/17/15/13/11px **5단 위계** |
| 하단 탭 | 텍스트만 | **아이콘 + 라벨 + 홈 인디케이터** |
| 레이아웃 | 겹침·잘림·스크롤 튐 | 고정 셸 + 내부 스크롤 + 전환 시 top reset |

---

## 1. 레퍼런스 (무엇을 가져왔는가)

| # | 레퍼런스 | 가져온 것 | 링크 |
|---|---|---|---|
| 1 | **Threads** | 텍스트 중심 피드, 1px 헤어라인, 그림자 없는 리스트, 5탭 | [Refero](https://styles.refero.design/style/182f8743-fe22-45d3-98bc-9fd29d058602) |
| 2 | **Toss** | 390px 모바일 캔버스, 4px 그리드, **단일 액센트**, 큰 터치 타깃 | [Toss design ref](https://github.com/rohitg00/awesome-claude-design/blob/main/design-md/playful/toss.md) |
| 3 | **BeReal** | “한 번, 정직하게”, 시간순 피드, 과시 없는 공유 | [Case study](https://medium.com/@rynmnfrd/redesigning-bereal-5271fe87a984) |
| 4 | **당근** | 지역 필(`광명시`), 동네 정체성, 따뜻한 뉴트럴 | [daangn.com](https://www.daangn.com) |
| 5 | **Duolingo** | 스트릭·진행률의 가벼운 게이미피케이션 | [duolingo.com](https://www.duolingo.com) |
| 6 | **Things 3** | **inset grouped list**, chevron 행, 조용한 타이포 | [culturedcode.com/things](https://culturedcode.com/things/) |
| 7 | **Day One** | 사적인 기록, 차분한 저널 UI | [dayoneapp.com](https://dayoneapp.com) |
| 8 | **Linear / Notion** | 높은 대비, 낮은 채도, 정보 위계 | [linear.app](https://linear.app) · [notion.so](https://notion.so) |
| 9 | **GitHub 잔디** | “쌓인다”는 축적의 시각적 은유 | [github.com](https://github.com) |
| 10 | **Apple HIG** | 44pt 터치, 탭 바, inset grouped list, safe area | [HIG](https://developer.apple.com/design/human-interface-guidelines/) |
| 11 | **Material 3** | segmented button, navigation bar, 8pt 리듬 | [m3.material.io](https://m3.material.io) |
| 12 | **Mobbin** | 실제 앱 화면 패턴 라이브러리 | [mobbin.com](https://mobbin.com) |

### 의도적으로 버린 것

- 좋아요 수 경쟁·팔로워 수·랭킹
- 공부 인증샷·성적 자랑
- 이모지 아이콘 남발
- 다중 액센트·과한 그라데이션·모든 카드에 그림자
- 무한 자동재생

---

## 2. 토큰

### Color

| 토큰 | 값 | 용도 |
|---|---|---|
| `--accent` | `#5546F5` | 단일 액센트, 활성 탭, CTA |
| `--accent-soft` | `#EFEDFF` | pill, 선택 배경, D-day |
| `--accent-line` | `#E1DCFF` | 선택 테두리 |
| `--text` | `#111114` | 제목·본문 |
| `--muted` | `#6E6E78` | 보조 텍스트 |
| `--tertiary` | `#9A9AA5` | 캡션·비활성 |
| `--line` | `#E9E9EF` | 1px 헤어라인 |
| `--screen` | `#F7F7FA` | 폰 화면 배경 |
| `--surface` | `#FFFFFF` | 카드·그룹 |
| `--bg` | `#E7E7ED` | 데스크톱 배경 |
| `--success` | `#0E9F6E` | 기록 완료 |
| `--danger` | `#E5484D` | 오류 |

> Streamlit 기본 primary(빨강)는 `.streamlit/config.toml`에서 `#5546F5`로 교체.

### Type

| 역할 | 크기 | 무게 | 자간 |
|---|---|---|---|
| 날짜/대제목 | 1.42rem | 800 | -0.055em |
| 온보딩 헤드라인 | 1.68rem | 800 | -0.06em |
| 행 제목 | 0.90rem | 700 | -0.02em |
| 본문 | 0.91rem | 400 | -0.01em |
| 보조 | 0.72rem | 400 | 0 |
| 섹션 라벨 | 0.68rem | 800 | 0.05em |
| 탭 라벨 | 0.60rem | 700 | 0 |

- 폰트: Pretendard(variable, `font-display: swap`) → 시스템 폰트.
- **섹션 라벨은 네이티브 Markdown `####`** 사용 (Streamlit이 높이를 정확히 측정).

### Space / Radius

- 4 / 8 / 12 / 16 / 20 / 24
- 버튼 12 · 입력 12 · 그룹 18 · D-day 20 · 폰 44
- 그림자: 카드 없음, D-day 없음, 폰 프레임만 `0 38px 90px`

---

## 3. 폰 셸

| 항목 | 값 |
|---|---|
| 외곽 | **390 × 844px**, 8px 베젤, 44px 라운드 |
| 내부 | 374px, 내부 스크롤 |
| 상단 | 상태바(9:41·아일랜드·신호/배터리) + **44px 앱바** |
| 하단 | **374px 고정 탭**, 아이콘 22px + 라벨 10px, 홈 인디케이터 |
| 데스크톱 | 중앙 정렬, `#E7E7ED` 배경 |
| 모바일 | `max-width: 640px` → 풀블리드, `100dvh` |
| 전환 | 페이지 변경 시 내부 스크롤 **top reset** |

### 탭 바

- 5개: 오늘(집) · 피드(리스트) · 리포트(차트) · 리콜(시계) · 설정(슬라이더)
- 아이콘은 **SVG mask** + `currentColor` → 활성/비활성 색 자동
- 활성: 보라색, 비활성: 회색
- hover/focus/active에서도 **채워진 버튼 금지**

---

## 4. 컴포넌트

### Inset grouped list (오늘/리콜/리포트/설정)

- 바깥: 1px `--line`, 18px 라운드, 흰 배경
- 행: 13–15px 패딩, 행 사이 1px 헤어라인
- 왼쪽: 26px 숫자 배지 / 오른쪽: **작은 chevron**
- 큰 “수정” 버튼 금지

### Hairline feed

- 카드/그림자 없음, 행 사이 1px 헤어라인
- 아바타 30px, 이름 0.82rem, 서브 0.68rem
- 본문 0.91rem / 1.62
- 태그는 작은 pill, 액션은 하트 아이콘 + count, 신고는 `···`

### Chips / segmented

- 주간 스트립: 5칸, 선택 시 **solid accent**
- 과목 필터: **짧은 라벨 + 가로 스크롤**
- 리포트 탭: **segmented control** (회색 트랙 + 흰 활성 pill)
- 활동 선택: radio를 chip 스타일로 (`:has(input:checked)`)

### D-day

- `#F1EEFF` 표면 + `#E1DCFF` 테두리 (그라데이션 금지)
- `다음 시험` eyebrow → **D-37** 2.25rem accent → 시험명 → 날짜 → 데모 chip

---

## 5. 화면 원칙

| 화면 | 핵심 | 금지 |
|---|---|---|
| 온보딩 | 라벤더 히어로 + 라인 아이콘 3개 + CTA | 이모지, 기능 나열 과다 |
| 오늘 | 날짜 + 주간 스트립 + 진행률 + 그룹 리스트 | 큰 페이지 타이틀, 카드 7개 |
| 피드 | 헤어라인 리스트 + 짧은 칩 | 카드 테두리, 좋아요 순 정렬 |
| 리포트 | 세그먼트 + 메트릭 3 + 요약 + CSS 바 | 차트 라이브러리, 큰 제목 |
| 리콜 | D-day + 메트릭 + 행별 2버튼 | 작은 원형 버튼 |
| 설정 | 프로필 + 그룹 행 + chevron | 큰 섹션 제목, 기본 info box |

---

## 6. 접근성

- 터치 타깃 **최소 40px** (주요 CTA 44px)
- 텍스트 대비 4.5:1 이상
- 색만으로 상태를 구분하지 않음 (`✓`, 텍스트 병기)
- `env(safe-area-inset-bottom)` 대응

---

## 7. 구현

| 파일 | 역할 |
|---|---|
| `core/theme.py` | 토큰·폰 셸·컴포넌트 CSS, SVG mask 아이콘 |
| `core/ui.py` | 안전한 HTML 조각 (앱바·행·피드·D-day·메트릭) |
| `.streamlit/config.toml` | Streamlit primary `#5546F5` |
| `app.py` | 폰 셸, 앱바 타이틀, 아이콘 탭, 스크롤 리셋 |

### 성능 메모

- `pandas`/`altair` import 제거 → 리포트는 **CSS bar**로 렌더
- 시드 1회 플래그로 불필요한 DB 쓰기 제거

---

## 8. 다음 단계

- 다크 모드 토큰
- Pretendard 셀프호스팅
- 피드 카드 120ms fade/slide
- 접근성 자동 검사(axe)
- 딥링크 (`?nav=feed`)
