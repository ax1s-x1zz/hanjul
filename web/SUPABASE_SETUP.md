# Supabase 10분 설정 가이드

> **Supabase가 뭔가요?**
> Postgres 데이터베이스 + 로그인(Auth) + 자동 API + 파일 저장을 한 번에 제공하는 서비스입니다.
> 한줄에서는 **계정/DB**를 담당합니다. 지금은 키가 없어도 **localStorage 데모 모드**로 앱이 완전히 동작합니다.

---

## 0. 먼저 알아둘 것

- **Supabase는 선택입니다.** 해커톤 시연은 데모 모드로도 충분합니다.
- Supabase를 붙이면:
  - 실제 로그인 세션
  - Postgres에 기록 저장
  - RLS로 “내 기록은 나만” 보장
  - 여러 기기/브라우저에서 같은 데이터

---

## 1. 프로젝트 만들기 (2분)

1. https://supabase.com 접속 → **Start your project**
2. GitHub 계정으로 로그인
3. **New project**
   - Name: `hanjul`
   - Database Password: 안전한 비밀번호 (따로 저장)
   - Region: **Northeast Asia (Seoul)**
4. **Create new project** → 1~2분 기다립니다.

---

## 2. 키 복사하기 (1분)

왼쪽 메뉴 → **Project Settings** → **API**

| 항목 | 사용할 곳 |
|---|---|
| **Project URL** | `NEXT_PUBLIC_SUPABASE_URL` |
| **anon / public key** | `NEXT_PUBLIC_SUPABASE_ANON_KEY` |
| **service_role key** | **절대 프론트엔드에 넣지 마세요** |

> `anon` 키는 브라우저에 노출되어도 되는 공개 키입니다. `service_role`은 서버 전용입니다.

---

## 3. `.env.local` 만들기 (1분)

`web` 폴더에서:

```bat
copy .env.example .env.local
```

`.env.local`을 열고 두 줄을 채웁니다.

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOi...
```

- `NEIS_KEY`는 선택입니다. 없으면 데모 시간표를 사용합니다.
- **`.env.local`은 절대 GitHub에 올리지 마세요.** (`.gitignore`에 이미 포함)

---

## 4. 스키마 실행하기 (2분)

1. Supabase 왼쪽 메뉴 → **SQL Editor**
2. **New query**
3. 이 저장소의 `web/supabase/schema.sql` 내용을 **전부 복사해서 붙여넣기**
4. **Run** (또는 Ctrl+Enter)

성공하면 다음 테이블이 생깁니다.

- `profiles` — 익명 닉네임/학년/반
- `logs` — 비공개 기록
- `posts` — 공개 글 사본
- `reactions` — 응원
- `reports` — 신고
- `recall_queue` — 복습 카드

그리고 **RLS 정책**과 `report_post` 함수도 함께 생성됩니다.

---

## 5. 익명 로그인 켜기 (1분) ⭐ 가장 쉬움

1. 왼쪽 메뉴 → **Authentication** → **Providers**
2. **Anonymous Sign-Ins** → **Enable**
3. Save

이제 `/login`에서 **“익명으로 시작하기”** 버튼만 누르면 됩니다.
이메일·구글·카카오 설정이 전혀 필요 없습니다.

---

## 6. 실행 (1분)

```bat
cd web
npm install
npm run dev
```

1. http://localhost:3000/login
2. **익명으로 시작하기**
3. `/today`에서 5교시 기록 → 공개 → 피드 확인

> `NEXT_PUBLIC_` 환경변수는 서버 시작 시 읽습니다. `.env.local`을 바꾸면 **dev 서버를 재시작**하세요.

---

## 7. (선택) Google 로그인

익명 로그인으로 충분하지만, 실제 계정을 쓰고 싶다면:

1. https://console.cloud.google.com
2. 새 프로젝트 → **APIs & Services → OAuth consent screen** (External)
3. **Credentials → Create credentials → OAuth client ID → Web application**
4. **Authorized redirect URI**에 추가:
   ```
   https://<supabase-project-ref>.supabase.co/auth/v1/callback
   ```
   (`<supabase-project-ref>`는 Project URL의 `xxxx.supabase.co` 앞부분)
5. Client ID / Secret 복사
6. Supabase → **Authentication → Providers → Google** → Enable → 붙여넣기 → Save
7. Supabase → **Authentication → URL Configuration**
   - Site URL: `http://localhost:3000`
   - Redirect URLs: `http://localhost:3000/auth/callback`

---

## 8. (선택) 카카오 로그인

1. https://developers.kakao.com → **내 애플리케이션 → 애플리케이션 추가**
2. **카카오 로그인** 활성화
3. **Redirect URI**:
   ```
   https://<supabase-project-ref>.supabase.co/auth/v1/callback
   ```
4. **REST API 키**와 **Client Secret**을 Supabase → Authentication → Providers → Kakao에 입력
5. Redirect URLs에 `http://localhost:3000/auth/callback` 추가

> 카카오는 심사/비즈 앱 설정이 필요할 수 있어 해커톤에서는 **익명 로그인**을 추천합니다.

---

## 9. 자주 막히는 곳

| 증상 | 해결 |
|---|---|
| `/login`에 “Supabase 설정이 필요합니다” | `.env.local` 값 확인 후 **dev 서버 재시작** |
| `Anonymous sign-ins are disabled` | Authentication → Providers → Anonymous Sign-Ins Enable |
| 로그인 후 `/login`으로 계속 돌아옴 | Supabase URL Configuration의 Redirect URLs 확인 |
| 기록이 저장되지 않음 | SQL Editor에서 `schema.sql`을 끝까지 실행했는지 확인 |
| `permission denied for table` | RLS 정책이 생성됐는지 Table Editor → RLS 확인 |
| 이메일이 안 옴 | Supabase 기본 메일은 rate limit이 있습니다. 익명/Google 사용 권장 |
| 빌드가 안 됨 | `web`에서 `rmdir /s /q node_modules` 후 `npm install` |

---

## 10. Vercel 배포

1. GitHub 저장소를 Vercel에 연결
2. **Root Directory** = `web`
3. Environment Variables에 `.env.local` 값 입력
4. Supabase → Authentication → URL Configuration에 배포 도메인 추가:
   ```
   https://<your-app>.vercel.app/auth/callback
   ```

---

## 보안 체크

- `.env.local` 커밋 금지
- `service_role` 키를 브라우저에 넣지 않기
- 공개 글에는 학교명·실명·전화번호가 자동 마스킹됨
- RLS: `logs`는 본인만, `posts`는 공개 글만 읽기
