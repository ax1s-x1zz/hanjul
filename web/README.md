# 한줄 web — Next.js

> 오늘 배운 한 줄, 광명의 배움 피드.
> Streamlit 프로토타입의 **제품용 프론트엔드**입니다.

- **Stack**: Next.js 15 (App Router) · React 19 · TypeScript · Supabase (optional) · Vercel
- **Demo mode**: localStorage + seeded data (no keys required)
- **Design**: 390×844 phone shell, icon tab bar, inset grouped list, bottom sheet, page transitions
- **Legacy**: Streamlit app remains in the repository root as a fallback demo.

---

## 실행

```bash
cd web
npm install
npm run dev
# http://localhost:3000
```

- 첫 화면: `/` 온보딩 → **데모로 시작하기**
- 데모 데이터: 진성고 2학년 5반 · **기준일 2026-11-03(화)** · 월·화 기록, 수~금 수학여행
- **시간표**: `/today`에서 NEIS `hisTimetable`을 **실시간 조회** (현장체험학습일은 체험학습 카드, 주말은 다음 수업일 안내)
- 모든 기록은 **브라우저 localStorage**에 저장됩니다 (서버 DB 없이 동작).

### 빌드

```bash
npm run build
npm start
```

---

## 화면

| Route | 설명 |
|---|---|
| `/` | 온보딩 · **데모 / 게스트 / 친구 계정** 선택 |
| `/today` | **실제 NEIS 시간표** · 주간 스트립 · 교시 그룹 리스트 · 10초 기록 바텀시트 · **오늘의 질문** |
| `/feed` | 광명시 공개 피드 · 과목 칩 · 응원·신고 |
| `/report` | **이번 주 실제 기록** / 지식 지도 / 지역 막힘 |
| `/recall` | **시험 준비도** + **3분 플랜** + SM-2 복습 |
| `/settings` | 계정 전환 · JSON 내보내기 · 삭제/초기화 |

### 데이터 가치 (V3)

- **오늘의 질문**: 내 기록에서 매일 1개 질문 → 3문장 설명 → 복습 반영
- **시험 준비도**: 기록 커버리지 + 복습 신뢰도 + 막힘 해결 → 0~100 추정치
- **3분 플랜**: 준비도·취약 개념으로 오늘 복습할 3개를 제시
- **지식 지도**: 개념이 `막힘 → 복습 중 → 이해`로 색이 바뀜
- 복습 카드를 누를수록 준비도와 지도가 **즉시 갱신**
- DB 없이 localStorage로 동작 → 가치 검증이 먼저, DB는 확장 수단

---

## Supabase 연결 (Postgres + Auth + RLS)

> **처음이면 [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)를 먼저 보세요.**
> 익명 로그인만 켜면 이메일/구글 설정 없이 10분 안에 실제 DB를 사용할 수 있습니다.

1. Supabase 프로젝트 생성
2. SQL Editor에서 [`supabase/schema.sql`](./supabase/schema.sql) 실행
3. `.env.example` → `.env.local` 복사 후 값 입력

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

- `lib/demo-store.tsx`는 **이중 모드**입니다.
  - 키가 있으면 Supabase Auth/DB/RLS 사용
  - 키가 없으면 localStorage 데모 모드
- `logs`는 본인만, `posts`는 공개 글만 읽을 수 있습니다.
- `report_post` RPC가 신고 3회 누적 시 글을 숨깁니다.

### Auth

- `/login`: **익명 시작** · Google · 카카오 · 이메일 매직 링크
- 익명 로그인: Authentication → Providers → Anonymous Sign-Ins 활성화
- `/auth/callback`: OAuth code exchange
- `middleware.ts`: `/today`, `/feed`, `/report`, `/recall`, `/settings` 보호
- Supabase Dashboard → Authentication → Providers에서 Google/Kakao 활성화
- Redirect URL 등록:
  - `http://localhost:3000/auth/callback`
  - `https://<your-domain>/auth/callback`

---

## NEIS 연동

- 서버 Route: `GET /api/neis/timetable?date=YYYY-MM-DD&grade=2&class=5`
- `/today`가 선택한 날짜마다 이 Route를 호출해 **실제 시간표를 표시**합니다.
- `.env.local`에 `NEIS_KEY`가 있으면 실제 데이터를, 없으면 **샘플** 배지와 함께 시드 시간표를 반환합니다.
- 수~금처럼 모든 교시가 `숙박형 현장체험학습`이면 교시를 반복하지 않고 **체험학습 카드** 하나로 표시합니다.
- 주말·휴업일은 `periods: []`와 함께 **다음 수업일**을 계산해 `nearest`로 내려줍니다.
  화면은 “수업 없음” 카드 + `다음 수업일 시간표 보기` 버튼을 표시합니다.
- 브라우저에 키를 노출하지 않도록 **서버에서만** 호출합니다.
- 24시간 캐시 + `s-maxage=3600` 으로 NEIS 호출을 줄입니다.

```env
# web/.env.local
NEIS_KEY=발급받은_키
NEIS_OFFICE_CODE=J10
NEIS_SCHOOL_CODE=7530207
```

---

## 디자인

- 디자인 토큰·레퍼런스: [`../DESIGN.md`](../DESIGN.md)
- 폰 셸: `components/phone-shell.tsx`
- 스타일: `app/globals.css`
- 아이콘: `components/icons.tsx` (inline SVG)
- 바텀시트/토스트: `components/ui.tsx`

---

## Vercel 배포

1. GitHub 저장소 연결
2. **Root Directory**를 `web`으로 설정
3. Environment Variables에 `.env.local` 값 입력
4. Deploy

---

## 데모 리셋

설정 → **데모 데이터 초기화**  
또는 브라우저 DevTools → Application → Local Storage → `hanjul-demo-v1` 삭제
