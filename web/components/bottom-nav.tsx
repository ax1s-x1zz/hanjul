"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  ChartIcon,
  ClockIcon,
  FeedIcon,
  HomeIcon,
  SettingsIcon,
} from "./icons";

const ITEMS = [
  { href: "/today", label: "오늘", Icon: HomeIcon },
  { href: "/feed", label: "피드", Icon: FeedIcon },
  { href: "/report", label: "리포트", Icon: ChartIcon },
  { href: "/recall", label: "리콜", Icon: ClockIcon },
  { href: "/settings", label: "설정", Icon: SettingsIcon },
];

export function BottomNav() {
  const pathname = usePathname();
  return (
    <nav className="bottom-nav" aria-label="주 메뉴">
      {ITEMS.map(({ href, label, Icon }) => {
        const active = pathname === href;
        return (
          <Link
            key={href}
            href={href}
            className={active ? "nav-item active" : "nav-item"}
            aria-current={active ? "page" : undefined}
          >
            <Icon />
            <span>{label}</span>
          </Link>
        );
      })}
      <span className="home-indicator" aria-hidden="true" />
    </nav>
  );
}
