"use client";

import type { ReactNode } from "react";

import { useDemo } from "@/lib/demo-store";
import { cn } from "@/lib/utils";

import { AppBar } from "./app-bar";
import { StatusBar } from "./status-bar";
import { BottomNav } from "./bottom-nav";

interface PhoneShellProps {
  children: ReactNode;
  title?: string;
  brand?: boolean;
  noNav?: boolean;
  noHeader?: boolean;
  screenClassName?: string;
}

export function PhoneShell({
  children,
  title,
  brand,
  noNav = false,
  noHeader = false,
  screenClassName,
}: PhoneShellProps) {
  const { state, toast } = useDemo();

  return (
    <div className="stage">
      <div className="phone" id="phone-root">
        {noHeader ? (
          <div className="app-header">
            <StatusBar />
          </div>
        ) : (
          <div className="app-header">
            <StatusBar />
            <AppBar user={state.user} title={title} brand={brand} />
          </div>
        )}

        <main className={cn("screen", screenClassName)}>{children}</main>

        {!noNav && <BottomNav />}
        {toast ? <div className="toast">{toast}</div> : null}
      </div>
    </div>
  );
}
