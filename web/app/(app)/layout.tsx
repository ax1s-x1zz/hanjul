"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { PhoneShell } from "@/components/phone-shell";

const TITLES: Record<string, string | undefined> = {
  "/today": undefined,
  "/feed": "광명 피드",
  "/report": "리포트",
  "/recall": "시험 리콜",
  "/settings": "설정",
};

export default function AppLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const title = TITLES[pathname];
  return (
    <PhoneShell title={title} brand={pathname === "/today"}>
      {children}
    </PhoneShell>
  );
}
