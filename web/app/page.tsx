"use client";

import { useRouter } from "next/navigation";

import { ClockIcon, LockIcon, PinIcon } from "@/components/icons";
import { PhoneShell } from "@/components/phone-shell";
import { Button } from "@/components/ui";
import { useDemo } from "@/lib/demo-store";
import { DEMO_REGION, DEMO_SCHOOL } from "@/lib/seed";

const FEATURES = [
  {
    Icon: ClockIcon,
    title: "10초 기록",
    body: "시간표가 과목과 교시를 자동으로 채워줍니다.",
  },
  {
    Icon: LockIcon,
    title: "나만 보는 기록",
    body: "상세 리포트와 막힘 분석은 나만 봅니다.",
  },
  {
    Icon: PinIcon,
    title: "광명 피드",
    body: "공개한 한 줄만 지역 친구들과 나눕니다.",
  },
];

export default function OnboardingPage() {
  const router = useRouter();
  const { mode, switchUser, resetDemo, startGuest, notify } = useDemo();
  const isSupabase = mode === "supabase";

  async function start(userId: string, message: string) {
    await resetDemo();
    await switchUser(userId);
    notify(message);
    router.push("/today");
  }

  async function startAsGuest() {
    await startGuest();
    router.push("/today");
  }

  return (
    <PhoneShell noNav noHeader screenClassName="onboarding-screen">
      <div className="onboarding-hero">
        <div className="onboarding-brand">한줄.</div>
        <h1 className="onboarding-title">
          오늘 배운 한 줄,
          <br />
          여기 남기세요.
        </h1>
        <p className="onboarding-sub">시간표는 학교가, 기록은 당신이.</p>
      </div>

      <div className="onboarding-body">
        <div>
          {FEATURES.map(({ Icon, title, body }) => (
            <div className="feature" key={title}>
              <span className="feature-icon">
                <Icon />
              </span>
              <div>
                <b>{title}</b>
                <p>{body}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="onboarding-actions">
          {isSupabase ? (
            <>
              <Button
                variant="primary"
                block
                onClick={() => router.push("/login")}
              >
                로그인
              </Button>
              <Button block onClick={() => router.push("/login")}>
                처음이신가요? 계정 만들기
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="primary"
                block
                onClick={() => void start("demo-main", "데모 계정으로 시작합니다.")}
              >
                데모로 시작하기
              </Button>
              <Button block onClick={() => void startAsGuest()}>
                게스트로 시작하기
              </Button>
              <p className="helper" style={{ margin: "-2px 0 0", textAlign: "center" }}>
                빈 기록으로 시작합니다. 오늘부터 직접 쌓아보세요.
              </p>
              <Button
                block
                onClick={() =>
                  void start("demo-friend", "친구 계정으로 전환했습니다.")
                }
              >
                친구 계정으로 체험하기
              </Button>
            </>
          )}
        </div>

        {!isSupabase ? (
          <details className="demo-guide">
            <summary>3분 데모 순서</summary>
            <ol>
              <li>이번 주 월·화 NEIS 시간표 (수~금은 수학여행)</li>
              <li>화요일 5교시 기록 → 공개</li>
              <li>오늘의 질문 답하기</li>
              <li>리콜 → 3분 플랜 3개 완료</li>
            </ol>
          </details>
        ) : null}

        <p className="helper" style={{ marginTop: 14 }}>
          {DEMO_SCHOOL} 2학년 5반 · {DEMO_REGION} · 데모 데이터
        </p>
        <p className="helper">
          {isSupabase
            ? "로그인하면 자동 닉네임이 생성됩니다. 실명·전화번호·주소·사진은 저장하지 않습니다."
            : "실명·전화번호·주소·사진은 저장하지 않습니다. 데모 데이터는 이 브라우저에만 저장됩니다."}
        </p>
      </div>
    </PhoneShell>
  );
}
