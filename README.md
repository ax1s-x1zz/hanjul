# 한줄 (hanjul)

> 오늘 배운 한 줄, 광명의 배움 피드.

수업 시간표는 학교가 알려주고, **배운 것은 학생이 한 줄로 남깁니다.**
상세 기록은 나만 보고, 공개를 선택한 한 줄만 같은 지역(경기 광명시) 친구들과 나눕니다.

- **서비스명**: 한줄 (hanjul)
- **한 줄 소개**: NEIS 시간표로 자동 채워지는 10초 학습 기록 + 광명시 배움 피드
- **개발 배경**: 2026 지역연합 해커톤
- **데모 학교·학급**: 진성고등학교 2학년 5반
- **주요 문서**: [PRD.md](./PRD.md) · [DESIGN.md](./DESIGN.md) · [DATA_VALUE.md](./DATA_VALUE.md) · [web/README.md](./web/README.md)

> **제품용 웹앱**: [`web/`](./web) — Next.js 15 · React 19 · TypeScript · Supabase  
> **Streamlit**: 이 README의 루트 앱 — 해커톤 fallback / 프로토타입

---

## Next.js 웹앱 (권장)

```bash
cd web
npm install
npm run dev
# http://localhost:3000
```

프로덕션 데모(권장, dev 배지 없음):

```bash
cd web
npm run build
npm start
```

- 실제 라우팅(`/today`, `/feed`, `/report`, `/recall`, `/settings`)
- **진짜 바텀시트** 기록 UI · 페이지 전환 · 즉각 상태 반영
- 데모는 localStorage 시드로 동작 (Supabase 키 없이 가능)
- Supabase 키를 넣으면 **Google/카카오/이메일 로그인 + Postgres/RLS**로 자동 전환
- `middleware.ts`가 `/today`·`/feed`·`/report`·`/recall`·`/settings` 보호
- Supabase 스키마·RLS·신고 RPC: [`web/supabase/schema.sql`](./web/supabase/schema.sql)
- NEIS 프록시: `GET /api/neis/timetable?date=2026-11-03&grade=2&class=5`
- 환경 변수: `web/.env.example` → `web/.env.local`
- Supabase 처음 설정: [`web/SUPABASE_SETUP.md`](./web/SUPABASE_SETUP.md) (익명 로그인 10분 가이드)

---

## 디자인

- **레퍼런스**: Threads(헤어라인 피드), Toss(390px·4px 그리드·단일 액센트), BeReal(정직한 기록), 당근(지역 필), Duolingo(스트릭), **Things 3(inset grouped list)**, **Day One(사적 기록)**, Linear/Notion(차분한 타이포), Apple HIG(44pt·탭 바), Material 3(segmented button)
- **폰 프레임**: 390×844px, 8px 베젤, 44px 라운드, 내부 스크롤, **아이콘 하단 탭 + 홈 인디케이터**
- **디자인 토큰**: 단일 액센트 `#5546F5`, 5단 타이포 위계, 1px 헤어라인, 그림자 최소
- **모바일**: `max-width: 640px`에서 프레임을 제거하고 풀블리드
- 상세 진단·토큰·컴포넌트 규칙: [DESIGN.md](./DESIGN.md)

---

## 데이터 가치 (V3)

> **DB 연결은 미뤄도 됩니다. 학생에게 중요한 건 “기록이 쌓여서 무엇이 돌아오나”입니다.**

- **시험 준비도** (`/recall`): 기록 커버리지 + 복습 신뢰도 + 막힘 해결 → 0~100 추정치
- **지식 지도** (`/report` → 지식 지도): 개념이 `막힘 → 복습 중 → 이해`로 색이 바뀜
- 복습 카드를 누르면 **준비도와 지도가 즉시 갱신** (데모: 21점 → 34점)
- DB 없이 localStorage로 동작 → 가치 검증이 먼저, DB는 확장 수단
- 상세: [DATA_VALUE.md](./DATA_VALUE.md)

---

## 데모 시나리오 (3분)

| 시간 | 장면 | 확인할 것 |
|---|---|---|
| 0:00 | 온보딩에서 “데모로 시작하기 · 2학년 5반” | 11/3(화) 실제 7교시 시간표 자동 로드 |
| 0:30 | 5교시 영어Ⅱ “기록” 클릭 | 시간표가 과목을 자동으로 채움 |
| 0:50 | 한 줄 + 막힘 입력 → 공개 토글 ON → 저장 | 개인정보 살균 미리보기 |
| 1:10 | “광명 피드에 게시” | 피드 카드 등장 |
| 1:30 | 설정 → 친구 계정 전환 → 피드에서 응원 | 응원 수 증가 |
| 1:50 | 리포트 → 지식 지도 | 막힘 9개 · 과목별 개념 지도 |
| 2:10 | 리포트 → 지역 막힘 | 익명 집계(5명 이상) |
| 2:30 | 리콜 | 준비도 21점 → 기억남 3회 → 34점, 오늘 복습 9→6 |
| 2:50 | 설정 | 데이터 내보내기·삭제, AI 상태 |

> 실제 학사일정에 시험이 없어 리콜 화면은 **“데모 일정” 배지**를 표시합니다.

---

## 구현된 기능

| 기능 | 상태 | 설명 |
|---|---|---|
| NEIS 시간표 자동 로드 | ✅ | `hisTimetable`, 24시간 캐시, 실패 시 수동 입력 |
| NEIS 학사일정 | ✅ | 시험·휴업일 조회 |
| 10초 기록 | ✅ | 한 줄 + 활동 태그 + 막힘, 교시별 upsert |
| 공개 토글 + 살균 | ✅ | 기본 비공개, 전화·이메일·URL·학교명·교사명 마스킹 |
| 광명시 피드 | ✅ | 최신순, 과목 필터, 더 보기 |
| 응원·신고 | ✅ | 1인 1응원, 신고 3회 자동 숨김 |
| 비공개 주간 리포트 | ✅ | 기록 수·과목/활동 분포·막힘 TOP 3·연속 기록 |
| 지역 막힘 TOP | ✅ | 익명 집계, **k≥5** 일 때만 노출 |
| 시험 D-day 리콜 | ✅ | 학사일정 연동, 없으면 데모 일정 표시 |
| SM-2 간격 반복 | ✅ | 기억남(5)/헷갈림(2) |
| 익명 프로필 | ✅ | 자동 닉네임, 학교·실명 미노출 |
| 데이터 내보내기/삭제 | ✅ | JSON 다운로드, 전체 삭제 |
| AI 보조 | ⚙️ | OpenAI 키가 있으면 태그·요약, 없으면 규칙 기반 |

---

## 기술 스택

- **UI**: Streamlit (Python 단일 스택)
- **DB**: SQLite (`data/hanjul.db`, gitignore)
- **데이터**: NEIS 교육정보 개방 포털 (`schoolInfo`, `hisTimetable`, `SchoolSchedule`)
- **AI**: OpenAI `gpt-4o-mini` (선택)
- **테스트**: pytest (19 tests)

---

## 실행 방법

### Windows (권장)

```bat
cd C:\Users\LG\Desktop\2026-hackerthon\hanjul

REM 기존 가상환경 사용
..\2026_hackerthon\Scripts\activate

REM 또는 새 가상환경
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

### WSL / Linux

```bash
cd /mnt/c/Users/LG/Desktop/2026-hackerthon/hanjul
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속.

---

## 환경 변수

`.env.example`을 복사해 `.env`를 만들고 키를 채웁니다.

```bash
cp .env.example .env
```

| 변수 | 필수 | 설명 |
|---|---|---|
| `NEIS_KEY` | ✅ | NEIS 오픈API 인증키 |
| `OPENAI_API_KEY` | ⚪ | 없으면 규칙 기반 태그/템플릿 요약으로 동작 |
| `OPENAI_MODEL` | ⚪ | 기본 `gpt-4o-mini` |
| `DEMO_*` | ⚪ | 데모 학교·학급·날짜 재정의 |

> `.env`는 `.gitignore`에 포함되어 **커밋되지 않습니다.** 저장소에는 `.env.example`만 있습니다.

---

## 데모 데이터 초기화

시드 데이터는 최초 1회만 생성됩니다. 데모를 처음 상태로 되돌리려면:

```bash
rm -f data/hanjul.db
streamlit run app.py
```

다시 실행하면 진성고 2학년 5반, 시드 글 22개, 데모 기록 12개가 새로 생성됩니다.
(5교시 영어Ⅱ는 직접 기록하는 장면을 위해 비워둡니다.)

앱 안에서는 **설정 → 데모 데이터 초기화**로도 같은 작업을 할 수 있습니다.

---

## 개인정보 원칙

- 실명·전화번호·주소·사진·DM을 **수집하지 않습니다.**
- 공개 글은 저장 전 학교명·교사명·전화·이메일·URL·6자리 이상 숫자를 마스킹합니다.
- 지역 집계는 **5명 이상**일 때만 표시합니다(k-익명성).
- 만 14세 미만 가입을 차단하는 정책을 전제로 설계했습니다.

---

## 프로젝트 구조

```
hanjul/
├─ app.py                 # 진입점, 사이드바 라우팅, CSS
├─ views/
│  ├─ onboarding.py
│  ├─ today.py
│  ├─ feed.py
│  ├─ report.py
│  ├─ recall.py
│  └─ settings.py
├─ core/
│  ├─ config.py
│  ├─ utils.py
│  ├─ neis.py
│  ├─ db.py
│  ├─ privacy.py
│  ├─ recall.py
│  ├─ llm.py
│  └─ metrics.py
├─ data/                  # SQLite DB (gitignore)
├─ tests/
├─ PRD.md
├─ README.md
└─ requirements.txt
```

---

## 테스트

```bash
pytest -q
# 19 passed
```

테스트 범위: 개인정보 살균, k-익명성, SM-2, NEIS 파서, DB 시드·피드·신고·리콜.

---

## 라이선스·출처

해커톤 제출용 프로젝트입니다. NEIS·공공데이터는 각 제공기관의 이용약관과
공공누리 출처 표시 조건을 따릅니다. 본 서비스는 학교 공식 서비스가 아닙니다.
