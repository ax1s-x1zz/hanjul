"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { sm2 } from "./recall";
import { seedState } from "./seed";
import type { DemoState, LogEntry, Post, RecallItem } from "./types";
import { addDays, downloadJSON, todayISO, uid } from "./utils";

const STORAGE_KEY = "hanjul-demo-v1";

export interface SaveLogInput {
  date: string;
  period: number;
  subject: string;
  learned: string;
  activity: LogEntry["activity"];
  stuck: string;
  isPublic: boolean;
}

interface DemoContextValue {
  state: DemoState;
  ready: boolean;
  toast: string | null;
  notify: (message: string) => void;
  switchUser: (userId: string) => void;
  saveLog: (input: SaveLogInput) => LogEntry;
  publishPost: (log: LogEntry, text: string, tags: string[]) => void;
  unpublish: (logId: string) => void;
  toggleCheer: (postId: string) => void;
  reportPost: (postId: string) => void;
  reviewRecall: (itemId: string, quality: number) => void;
  resetDemo: () => void;
  deleteMyData: () => void;
  exportData: () => void;
}

const DemoContext = createContext<DemoContextValue | null>(null);

export function DemoProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DemoState>(() => seedState());
  const [ready, setReady] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<number | null>(null);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as DemoState;
        if (parsed?.user && parsed?.users?.length) setState(parsed);
      }
    } catch {
      // A corrupt demo state should never block the app.
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // Ignore private-mode quota errors.
    }
  }, [state, ready]);

  const notify = useCallback((message: string) => {
    setToast(message);
    if (toastTimer.current) window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(null), 2200);
  }, []);

  const switchUser = useCallback(
    (userId: string) => {
      setState((prev) => {
        const user = prev.users.find((item) => item.id === userId);
        return user ? { ...prev, user } : prev;
      });
      const target = state.users.find((user) => user.id === userId);
      if (target) notify(`${target.nickname} 계정으로 전환했습니다.`);
    },
    [state.users, notify],
  );

  const saveLog = useCallback((input: SaveLogInput): LogEntry => {
    const existing = state.logs.find(
      (log) =>
        log.userId === state.user.id &&
        log.date === input.date &&
        log.period === input.period,
    );
    const log: LogEntry = {
      ...input,
      id: existing?.id ?? uid("log"),
      userId: state.user.id,
    };
    setState((prev) => ({
      ...prev,
      logs: [
        ...prev.logs.filter(
          (item) =>
            !(
              item.userId === log.userId &&
              item.date === log.date &&
              item.period === log.period
            ),
        ),
        log,
      ],
      posts: log.isPublic
        ? prev.posts
        : prev.posts.filter((post) => post.logId !== log.id),
    }));
    return log;
  }, [state.logs, state.user.id]);

  const publishPost = useCallback(
    (log: LogEntry, text: string, tags: string[]) => {
      const post: Post = {
        id: uid("post"),
        logId: log.id,
        userId: state.user.id,
        nickname: state.user.nickname,
        grade: state.user.grade,
        subject: log.subject,
        text,
        tags,
        createdAt: new Date().toISOString(),
        cheers: [],
        reports: 0,
      };
      setState((prev) => ({
        ...prev,
        posts: [post, ...prev.posts.filter((item) => item.logId !== log.id)],
      }));
    },
    [state.user],
  );

  const unpublish = useCallback((logId: string) => {
    setState((prev) => ({
      ...prev,
      posts: prev.posts.filter((post) => post.logId !== logId),
    }));
  }, []);

  const toggleCheer = useCallback((postId: string) => {
    setState((prev) => ({
      ...prev,
      posts: prev.posts.map((post) => {
        if (post.id !== postId) return post;
        const has = post.cheers.includes(prev.user.id);
        return {
          ...post,
          cheers: has
            ? post.cheers.filter((id) => id !== prev.user.id)
            : [...post.cheers, prev.user.id],
        };
      }),
    }));
  }, []);

  const reportPost = useCallback(
    (postId: string) => {
      setState((prev) => ({
        ...prev,
        posts: prev.posts.map((post) => {
          if (post.id !== postId) return post;
          const reports = post.reports + 1;
          return { ...post, reports, hidden: reports >= 3 };
        }),
      }));
      notify("신고가 접수되었습니다.");
    },
    [notify],
  );

  const reviewRecall = useCallback(
    (itemId: string, quality: number) => {
      setState((prev) => ({
        ...prev,
        recall: prev.recall.map((item) => {
          if (item.id !== itemId) return item;
          const next = sm2(item.interval, item.ease, item.reps, quality);
          return {
            ...item,
            interval: next.interval,
            ease: next.ease,
            reps: next.reps,
            dueDate: addDays(todayISO(), next.interval),
          } satisfies RecallItem;
        }),
      }));
      notify(quality >= 3 ? "다음 복습일을 늘렸습니다." : "내일 다시 복습합니다.");
    },
    [notify],
  );

  const resetDemo = useCallback(() => {
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
    setState(seedState());
    notify("데모 데이터를 초기화했습니다.");
  }, [notify]);

  const deleteMyData = useCallback(() => {
    setState((prev) => ({
      ...prev,
      logs: prev.logs.filter((log) => log.userId !== prev.user.id),
      posts: prev.posts.filter((post) => post.userId !== prev.user.id),
      recall: prev.recall.filter((item) => item.userId !== prev.user.id),
    }));
    notify("내 기록을 삭제했습니다.");
  }, [notify]);

  const exportData = useCallback(() => {
    downloadJSON(`hanjul-${state.user.id}.json`, state);
    notify("JSON으로 내보냈습니다.");
  }, [state, notify]);

  const value = useMemo<DemoContextValue>(
    () => ({
      state,
      ready,
      toast,
      notify,
      switchUser,
      saveLog,
      publishPost,
      unpublish,
      toggleCheer,
      reportPost,
      reviewRecall,
      resetDemo,
      deleteMyData,
      exportData,
    }),
    [
      state,
      ready,
      toast,
      notify,
      switchUser,
      saveLog,
      publishPost,
      unpublish,
      toggleCheer,
      reportPost,
      reviewRecall,
      resetDemo,
      deleteMyData,
      exportData,
    ],
  );

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
}

export function useDemo(): DemoContextValue {
  const value = useContext(DemoContext);
  if (!value) throw new Error("useDemo must be used inside DemoProvider");
  return value;
}
