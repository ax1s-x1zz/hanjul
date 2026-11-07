import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import { DemoProvider } from "@/lib/demo-store";

import "./globals.css";

export const metadata: Metadata = {
  title: "한줄 · 오늘 배운 한 줄",
  description:
    "시간표는 학교가, 기록은 학생이. 오늘 배운 한 줄을 남기고 광명 친구들과 나누는 학습 피드.",
  manifest: "/manifest.json",
  icons: {
    icon: "/icon.svg",
    apple: "/icon.svg",
  },
  applicationName: "한줄",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "한줄",
  },
};

export const viewport: Viewport = {
  themeColor: "#5546F5",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ko">
      <body>
        <DemoProvider>{children}</DemoProvider>
      </body>
    </html>
  );
}
