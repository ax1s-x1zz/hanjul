"use client";

import Link from "next/link";
import { useState } from "react";

import { PhoneShell } from "@/components/phone-shell";
import { Button } from "@/components/ui";
import { getSupabaseBrowser } from "@/lib/supabase/client";
import { isSupabaseEnabled } from "@/lib/supabase/config";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function signInAnonymously() {
    const supabase = await getSupabaseBrowser();
    if (!supabase) {
      setMessage("Supabase 키를 먼저 설정해주세요.");
      return;
    }
    setBusy(true);
    const { error } = await supabase.auth.signInAnonymously();
    if (error) {
      setMessage(
        `${error.message} — Supabase Authentication → Providers에서 Anonymous Sign-Ins를 켜주세요.`,
      );
      setBusy(false);
      return;
    }
    window.location.assign("/today");
  }

  async function signIn(provider: "google" | "kakao") {
    const supabase = await getSupabaseBrowser();
    if (!supabase) {
      setMessage("Supabase 키를 먼저 설정해주세요.");
      return;
    }
    setBusy(true);
    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/auth/callback?next=/today`,
      },
    });
    if (error) setMessage(error.message);
    setBusy(false);
  }

  async function signInWithEmail() {
    const supabase = await getSupabaseBrowser();
    if (!supabase) {
      setMessage("Supabase 키를 먼저 설정해주세요.");
      return;
    }
    if (!email.includes("@")) {
      setMessage("이메일 주소를 확인해주세요.");
      return;
    }
    setBusy(true);
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback?next=/today`,
      },
    });
    setMessage(
      error ? error.message : "메일함에서 로그인 링크를 확인해주세요.",
    );
    setBusy(false);
  }

  return (
    <PhoneShell noNav noHeader screenClassName="login-screen">
      <div className="login-body">
        <div className="onboarding-brand">한줄.</div>
        <h1 className="login-title">로그인</h1>
        <p className="login-sub">
          오늘 배운 한 줄을 쌓고,
          <br />
          광명 친구들과 나눠보세요.
        </p>

        {!isSupabaseEnabled ? (
          <div className="group" style={{ marginTop: 22 }}>
            <div className="list-row" style={{ display: "block" }}>
              <div className="row-title">Supabase 설정이 필요합니다</div>
              <div className="row-sub" style={{ marginTop: 6 }}>
                web/.env.local에 NEXT_PUBLIC_SUPABASE_URL,
                NEXT_PUBLIC_SUPABASE_ANON_KEY를 추가하고 다시 시작해주세요.
              </div>
            </div>
            <Link href="/" className="settings-link" style={{ display: "flex" }}>
              데모로 둘러보기
            </Link>
          </div>
        ) : (
          <>
            <div className="login-actions">
              <Button
                variant="primary"
                block
                disabled={busy}
                onClick={() => void signInAnonymously()}
              >
                익명으로 시작하기
              </Button>
              <p className="helper" style={{ margin: "0 0 4px", textAlign: "center" }}>
                이메일 없이 바로 시작합니다.
              </p>
              <Button
                block
                disabled={busy}
                onClick={() => void signIn("google")}
              >
                Google로 계속하기
              </Button>
              <Button
                block
                disabled={busy}
                onClick={() => void signIn("kakao")}
              >
                카카오로 계속하기
              </Button>
            </div>

            <div className="login-divider">또는 이메일</div>

            <label className="field-label" htmlFor="email">
              이메일
            </label>
            <input
              id="email"
              className="input"
              type="email"
              inputMode="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
            <div style={{ height: 8 }} />
            <Button block disabled={busy} onClick={() => void signInWithEmail()}>
              매직 링크 받기
            </Button>

            {message ? <p className="helper" style={{ marginTop: 12 }}>{message}</p> : null}
          </>
        )}

        <p className="helper" style={{ marginTop: 22 }}>
          로그인하면 실명 대신 자동 닉네임이 생성됩니다. 상세 기록은 나만 보고,
          공개를 선택한 한 줄만 피드에 올라갑니다.
        </p>
      </div>
    </PhoneShell>
  );
}
