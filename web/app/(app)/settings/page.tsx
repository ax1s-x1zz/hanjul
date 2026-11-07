"use client";

import { useState } from "react";

import { Button, Section, Sheet } from "@/components/ui";
import { useDemo } from "@/lib/demo-store";
import { DEMO_REGION } from "@/lib/seed";
import { userInitial } from "@/lib/utils";


type Confirm = "delete" | "reset" | null;

export default function SettingsPage() {
  const { state, switchUser, exportData, deleteMyData, resetDemo } = useDemo();
  const [confirm, setConfirm] = useState<Confirm>(null);
  const supabaseEnabled = Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL);
  const demoUsers = state.users.filter(
    (user) => user.id === "demo-main" || user.id === "demo-friend",
  );

  const confirmTitle =
    confirm === "delete" ? "내 데이터를 모두 삭제할까요?" : "데모 데이터를 초기화할까요?";

  return (
    <div className="page">
      <div className="group">
        <div className="profile">
          <span className="avatar-lg">{userInitial(state.user.nickname)}</span>
          <div>
            <div className="profile-name">{state.user.nickname}</div>
            <div className="profile-sub">
              고{state.user.grade} · {state.user.classNo}반 · {state.user.track}
            </div>
          </div>
        </div>
      </div>

      <Section>계정</Section>
      <div className="group">
        {demoUsers.map((user) => {
          const active = user.id === state.user.id;
          return (
            <button
              type="button"
              className="list-row"
              key={user.id}
              onClick={() => switchUser(user.id)}
            >
              <div className="row-main">
                <div className="row-title">
                  {user.id === "demo-main" ? "나" : "친구"} · {user.grade}학년{" "}
                  {user.classNo}반
                </div>
                <div className="row-sub">{user.nickname}</div>
              </div>
              {active ? <span className="pill">현재</span> : <span className="row-action">›</span>}
            </button>
          );
        })}
      </div>

      <Section>데이터</Section>
      <button type="button" className="settings-link" onClick={exportData}>
        내 기록 내보내기
      </button>
      <button type="button" className="settings-link" onClick={() => setConfirm("delete")}>
        내 데이터 모두 삭제
      </button>
      <button type="button" className="settings-link" onClick={() => setConfirm("reset")}>
        데모 데이터 초기화
      </button>

      <Section>정보</Section>
      <div className="info-row" style={{ marginBottom: 6 }}>
        <span className="dot on" />
        <span>
          {supabaseEnabled ? "Supabase 연결됨" : "데모 모드 · 브라우저 저장"}
        </span>
      </div>
      <div className="info-row">
        <span className="dot" />
        <span>AI 보조 · 규칙 기반으로 동작 중</span>
      </div>
      <p className="helper" style={{ marginTop: 12 }}>
        v0.2.0 · {DEMO_REGION}
        <br />
        한줄은 학교 공식 서비스가 아닙니다. NEIS·공공데이터 출처 표시 조건을 따릅니다.
      </p>

      <Sheet
        open={confirm !== null}
        onClose={() => setConfirm(null)}
        title={confirmTitle}
        sub={
          confirm === "delete"
            ? "기록·공개 글·복습 카드가 이 브라우저에서 삭제됩니다."
            : "시드 데이터로 되돌립니다. 현재 기록은 사라집니다."
        }
      >
        <div className="sheet-actions">
          <Button type="button" onClick={() => setConfirm(null)}>
            취소
          </Button>
          <Button
            type="button"
            variant="primary"
            onClick={() => {
              if (confirm === "delete") deleteMyData();
              if (confirm === "reset") resetDemo();
              setConfirm(null);
            }}
          >
            {confirm === "delete" ? "삭제" : "초기화"}
          </Button>
        </div>
      </Sheet>
    </div>
  );
}
