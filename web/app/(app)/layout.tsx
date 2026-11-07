"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { PhoneShell } from "@/components/phone-shell";
import { useDemo } from "@/lib/demo-store";

const TITLES: Record<string, string | undefined> = {
  "/today": undefined,
  "/feed": "광명 피드",
  "/report": "리포트",
  "/recall": "시험 리콜",
  "/settings": "설정",
};

export default function AppLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { mode, ready, authenticated } = useDemo();

  useEffect(() => {
    if (mode === "supabase" && ready && !authenticated) {
      router.replace("/login");
    }
  }, [mode, ready, authenticated, router]);

  if (mode === "supabase" && (!ready || !authenticated)) {
    return (
      <PhoneShell noNav noHeader>
        <div className="empty">로그인 확인 중…</div>
      </PhoneShell>
    );
  }

  const title = TITLES[pathname];
  return (
    <PhoneShell title={title} brand={pathname === "/today"}>
      {children}
    </PhoneShell>
  );
}
