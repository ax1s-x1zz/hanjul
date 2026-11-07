import Link from "next/link";

import type { User } from "@/lib/types";
import { userInitial } from "@/lib/utils";

interface AppBarProps {
  user: User;
  title?: string;
  brand?: boolean;
}

export function AppBar({ user, title, brand }: AppBarProps) {
  return (
    <div className="appbar">
      {brand ? (
        <div className="logo">
          한줄<span>.</span>
        </div>
      ) : (
        <div className="appbar-title">{title ?? "한줄"}</div>
      )}
      <div className="appbar-right">
        <span className="region">{user.region.replace("경기도 ", "")}</span>
        <Link href="/settings" className="avatar" aria-label="설정">
          {userInitial(user.nickname)}
        </Link>
      </div>
    </div>
  );
}
