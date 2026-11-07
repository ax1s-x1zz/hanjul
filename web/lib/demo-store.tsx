"use client";

import { useRouter } from "next/navigation";
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
import { DEMO_REGION, seedState } from "./seed";
import { isSupabaseEnabled } from "./supabase/config";
import { getSupabaseBrowser } from "./supabase/client";
import type { DemoState, LogEntry, Post, RecallItem, User } from "./types";
import { addDays, downloadJSON, todayISO, uid } from "./utils";

const STORAGE_KEY = "hanjul-demo-v1";
const MODE = isSupabaseEnabled ? "supabase" : "demo";

export interface SaveLogInput {
  date: string;
  period: number;
  subject: string;
  learned: string;
  activity: LogEntry["activity"];
  stuck: string;
  isPublic: boolean;
}

type Mode = "demo" | "supabase";

interface DemoContextValue {
  state: DemoState;
  ready: boolean;
  authenticated: boolean;
  mode: Mode;
  toast: string | null;
  notify: (message: string) => void;
  switchUser: (userId: string) => Promise<void>;
  saveLog: (input: SaveLogInput) => Promise<LogEntry | null>;
  publishPost: (log: LogEntry, text: string, tags: string[]) => Promise<void>;
  unpublish: (logId: string) => Promise<void>;
  toggleCheer: (postId: string) => Promise<void>;
  reportPost: (postId: string) => Promise<void>;
  reviewRecall: (itemId: string, quality: number) => Promise<void>;
  resetDemo: () => Promise<void>;
  deleteMyData: () => Promise<void>;
  exportData: () => Promise<void>;
  signOut: () => Promise<void>;
}

const DemoContext = createContext<DemoContextValue | null>(null);

/* -------------------------------------------------------------------------- */
/* Row mappers                                                               */
/* -------------------------------------------------------------------------- */
function mapProfile(row: any): User {
  return {
    id: row.id,
    nickname: row.nickname,
    grade: Number(row.grade ?? 2),
    classNo: String(row.class_no ?? "5"),
    track: row.track ?? "",
    region: row.region ?? DEMO_REGION,
  };
}

function mapLog(row: any): LogEntry {
  return {
    id: row.id,
    userId: row.user_id,
    date: row.date,
    period: Number(row.period),
    subject: row.subject,
    learned: row.learned,
    activity: row.activity ?? "들음",
    stuck: row.stuck ?? "",
    isPublic: Boolean(row.is_public),
  };
}

function mapPost(row: any, cheers: string[]): Post {
  return {
    id: row.id,
    logId: row.log_id ?? undefined,
    userId: row.user_id,
    nickname: row.nickname,
    grade: Number(row.grade ?? 2),
    subject: row.subject ?? "기타",
    text: row.public_text,
    tags: Array.isArray(row.concept_tags) ? row.concept_tags : [],
    createdAt: row.created_at,
    cheers,
    reports: Number(row.reports ?? 0),
    hidden: row.status === "hidden",
  };
}

function mapRecall(row: any): RecallItem {
  return {
    id: row.id,
    userId: row.user_id,
    concept: row.concept,
    dueDate: row.due_date,
    interval: Number(row.interval_days ?? 1),
    ease: Number(row.ease ?? 2.5),
    reps: Number(row.reps ?? 0),
  };
}

/* -------------------------------------------------------------------------- */
/* Provider                                                                  */
/* -------------------------------------------------------------------------- */
export function DemoProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<DemoState>(() => seedState());
  const [ready, setReady] = useState(false);
  const [authenticated, setAuthenticated] = useState(MODE === "demo");
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<number | null>(null);

  const notify = useCallback((message: string) => {
    setToast(message);
    if (toastTimer.current) window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(null), 2200);
  }, []);

  /* Initial load: local demo or Supabase session + rows. */
  useEffect(() => {
    let cancelled = false;

    async function init() {
      if (MODE === "demo") {
        try {
          const raw = window.localStorage.getItem(STORAGE_KEY);
          if (raw) {
            const parsed = JSON.parse(raw) as DemoState;
            if (parsed?.user?.id && parsed?.users?.length && !cancelled) {
              setState(parsed);
            }
          } else {
            // Recompute relative dates at runtime (never use the build date).
            setState(seedState());
          }
        } catch {
          // ignore corrupt demo state
        }
        if (!cancelled) {
          setReady(true);
          setAuthenticated(true);
        }
        return;
      }

      const supabase = await getSupabaseBrowser();
      if (!supabase) {
        if (!cancelled) {
          setReady(true);
          setAuthenticated(false);
        }
        return;
      }

      try {
        const {
          data: { user },
        } = await supabase.auth.getUser();

        if (!user) {
          if (!cancelled) {
            setReady(true);
            setAuthenticated(false);
          }
          return;
        }

        let { data: profile } = await supabase
          .from("profiles")
          .select("*")
          .eq("id", user.id)
          .maybeSingle();

        if (!profile) {
          const nickname =
            (user.user_metadata?.nickname as string | undefined) ||
            `고2_기록러_${user.id.slice(0, 4)}`;
          const { data: created } = await supabase
            .from("profiles")
            .insert({
              id: user.id,
              nickname,
              grade: 2,
              class_no: "5",
              track: "이과",
              region: DEMO_REGION,
            })
            .select("*")
            .single();
          profile = created;
        }

        if (!profile) throw new Error("profile not found");

        const [logsRes, postsRes, recallRes] = await Promise.all([
          supabase
            .from("logs")
            .select("*")
            .eq("user_id", user.id)
            .order("date", { ascending: false }),
          supabase
            .from("posts")
            .select("*")
            .eq("status", "visible")
            .eq("region", DEMO_REGION)
            .order("created_at", { ascending: false })
            .limit(100),
          supabase
            .from("recall_queue")
            .select("*")
            .eq("user_id", user.id)
            .order("due_date"),
        ]);

        if (logsRes.error || postsRes.error || recallRes.error) {
          throw new Error("query failed");
        }

        const postRows = postsRes.data ?? [];
        const postIds = postRows.map((row: any) => row.id);
        let reactionRows: Array<{ post_id: string; user_id: string }> = [];
        if (postIds.length) {
          const { data: reactions } = await supabase
            .from("reactions")
            .select("post_id,user_id")
            .in("post_id", postIds);
          reactionRows = reactions ?? [];
        }

        const cheerMap = new Map<string, string[]>();
        for (const reaction of reactionRows) {
          const list = cheerMap.get(reaction.post_id) ?? [];
          list.push(reaction.user_id);
          cheerMap.set(reaction.post_id, list);
        }

        const mappedUser = mapProfile(profile);
        if (!cancelled) {
          setState({
            user: mappedUser,
            users: [mappedUser],
            logs: (logsRes.data ?? []).map(mapLog),
            posts: postRows.map((row: any) => mapPost(row, cheerMap.get(row.id) ?? [])),
            recall: (recallRes.data ?? []).map(mapRecall),
          });
          setAuthenticated(true);
          setReady(true);
        }
      } catch {
        if (!cancelled) {
          setReady(true);
          setAuthenticated(false);
        }
      }
    }

    void init();
    return () => {
      cancelled = true;
    };
  }, []);

  /* Persist only the local demo. */
  useEffect(() => {
    if (MODE !== "demo" || !ready) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // ignore quota/private mode errors
    }
  }, [state, ready]);

  /* ---------------------------------------------------------------------- */
  /* Actions                                                                */
  /* ---------------------------------------------------------------------- */
  const switchUser = useCallback(
    async (userId: string) => {
      if (MODE !== "demo") {
        notify("실서비스 모드에서는 로그아웃 후 다른 계정으로 로그인해주세요.");
        return;
      }
      setState((prev) => {
        const user = prev.users.find((item) => item.id === userId);
        return user ? { ...prev, user } : prev;
      });
      const target = state.users.find((user) => user.id === userId);
      if (target) notify(`${target.nickname} 계정으로 전환했습니다.`);
    },
    [state.users, notify],
  );

  const saveLog = useCallback(
    async (input: SaveLogInput): Promise<LogEntry | null> => {
      const supabase = await getSupabaseBrowser();
      if (MODE === "demo" || !supabase) {
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

        const concept = input.stuck.trim();
        if (concept) {
          setState((prev) =>
            prev.recall.some((item) => item.concept === concept)
              ? prev
              : {
                  ...prev,
                  recall: [
                    ...prev.recall,
                    {
                      id: uid("recall"),
                      userId: state.user.id,
                      concept,
                      dueDate: todayISO(),
                      interval: 1,
                      ease: 2.5,
                      reps: 0,
                    },
                  ],
                },
          );
        }
        return log;
      }

      const { data, error } = await supabase
        .from("logs")
        .upsert(
          {
            user_id: state.user.id,
            date: input.date,
            period: input.period,
            subject: input.subject,
            learned: input.learned,
            activity: input.activity,
            stuck: input.stuck,
            is_public: input.isPublic,
          },
          { onConflict: "user_id,date,period" },
        )
        .select("*")
        .single();

      if (error || !data) {
        notify("기록 저장에 실패했습니다.");
        return null;
      }

      const log = mapLog(data);
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

      if (!log.isPublic) {
        await supabase.from("posts").delete().eq("log_id", log.id);
      }

      const concept = input.stuck.trim();
      if (concept) {
        const { data: recallRow } = await supabase
          .from("recall_queue")
          .upsert(
            {
              user_id: state.user.id,
              concept,
              due_date: todayISO(),
              interval_days: 1,
              ease: 2.5,
              reps: 0,
            },
            { onConflict: "user_id,concept" },
          )
          .select("*")
          .single();
        if (recallRow) {
          const mapped = mapRecall(recallRow);
          setState((prev) => ({
            ...prev,
            recall: [
              ...prev.recall.filter((item) => item.concept !== concept),
              mapped,
            ],
          }));
        }
      }

      return log;
    },
    [state.logs, state.user.id, notify],
  );

  const publishPost = useCallback(
    async (log: LogEntry, text: string, tags: string[]) => {
      const supabase = await getSupabaseBrowser();
      if (MODE === "demo" || !supabase) {
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
        return;
      }

      const { data, error } = await supabase
        .from("posts")
        .upsert(
          {
            log_id: log.id,
            user_id: state.user.id,
            nickname: state.user.nickname,
            grade: state.user.grade,
            subject: log.subject,
            public_text: text,
            concept_tags: tags,
            region: DEMO_REGION,
            status: "visible",
          },
          { onConflict: "log_id" },
        )
        .select("*")
        .single();

      if (error || !data) {
        notify("피드 게시에 실패했습니다.");
        return;
      }

      const post = mapPost(data, []);
      setState((prev) => ({
        ...prev,
        posts: [post, ...prev.posts.filter((item) => item.logId !== log.id)],
      }));
    },
    [state.user, notify],
  );

  const unpublish = useCallback(async (logId: string) => {
    const supabase = await getSupabaseBrowser();
    if (MODE === "demo" || !supabase) {
      setState((prev) => ({
        ...prev,
        posts: prev.posts.filter((post) => post.logId !== logId),
      }));
      return;
    }
    await supabase.from("posts").delete().eq("log_id", logId);
    setState((prev) => ({
      ...prev,
      posts: prev.posts.filter((post) => post.logId !== logId),
    }));
  }, []);

  const toggleCheer = useCallback(
    async (postId: string) => {
      const post = state.posts.find((item) => item.id === postId);
      if (!post) return;
      const active = post.cheers.includes(state.user.id);
      const supabase = await getSupabaseBrowser();

      setState((prev) => ({
        ...prev,
        posts: prev.posts.map((item) =>
          item.id === postId
            ? {
                ...item,
                cheers: active
                  ? item.cheers.filter((id) => id !== state.user.id)
                  : [...item.cheers, state.user.id],
              }
            : item,
        ),
      }));

      if (MODE === "demo" || !supabase) return;

      const { error } = active
        ? await supabase
            .from("reactions")
            .delete()
            .eq("post_id", postId)
            .eq("user_id", state.user.id)
        : await supabase
            .from("reactions")
            .insert({ post_id: postId, user_id: state.user.id });

      if (error) notify("응원 처리에 실패했습니다.");
    },
    [state.posts, state.user.id, notify],
  );

  const reportPost = useCallback(
    async (postId: string) => {
      const post = state.posts.find((item) => item.id === postId);
      const nextReports = (post?.reports ?? 0) + 1;
      setState((prev) => ({
        ...prev,
        posts: prev.posts.map((item) =>
          item.id === postId
            ? { ...item, reports: nextReports, hidden: nextReports >= 3 }
            : item,
        ),
      }));

      const supabase = await getSupabaseBrowser();
      if (MODE === "demo" || !supabase) {
        notify("신고가 접수되었습니다.");
        return;
      }

      const { error } = await supabase.rpc("report_post", {
        p_post_id: postId,
      });
      notify(
        error ? "신고 처리에 실패했습니다." : "신고가 접수되었습니다.",
      );
    },
    [state.posts, notify],
  );

  const reviewRecall = useCallback(
    async (itemId: string, quality: number) => {
      const item = state.recall.find((entry) => entry.id === itemId);
      if (!item) return;
      const next = sm2(item.interval, item.ease, item.reps, quality);
      const dueDate = addDays(todayISO(), next.interval);

      setState((prev) => ({
        ...prev,
        recall: prev.recall.map((entry) =>
          entry.id === itemId
            ? {
                ...entry,
                interval: next.interval,
                ease: next.ease,
                reps: next.reps,
                dueDate,
              }
            : entry,
        ),
      }));

      const supabase = await getSupabaseBrowser();
      if (MODE === "demo" || !supabase) {
        notify(quality >= 3 ? "다음 복습일을 늘렸습니다." : "내일 다시 복습합니다.");
        return;
      }

      const { error } = await supabase
        .from("recall_queue")
        .update({
          interval_days: next.interval,
          ease: next.ease,
          reps: next.reps,
          due_date: dueDate,
          last_reviewed: new Date().toISOString(),
        })
        .eq("id", itemId);

      notify(
        error
          ? "복습 저장에 실패했습니다."
          : quality >= 3
            ? "다음 복습일을 늘렸습니다."
            : "내일 다시 복습합니다.",
      );
    },
    [state.recall, notify],
  );

  const resetDemo = useCallback(async () => {
    if (MODE !== "demo") {
      notify("데모 모드에서만 초기화할 수 있습니다.");
      return;
    }
    try {
      window.localStorage.removeItem(STORAGE_KEY);
      Object.keys(window.localStorage)
        .filter((key) => key.startsWith("hanjul-question-"))
        .forEach((key) => window.localStorage.removeItem(key));
    } catch {
      // ignore
    }
    setState(seedState());
    setAuthenticated(true);
    notify("데모 데이터를 초기화했습니다.");
  }, [notify]);

  const deleteMyData = useCallback(async () => {
    const supabase = await getSupabaseBrowser();
    if (MODE === "demo" || !supabase) {
      setState((prev) => ({
        ...prev,
        logs: prev.logs.filter((log) => log.userId !== prev.user.id),
        posts: prev.posts.filter((post) => post.userId !== prev.user.id),
        recall: prev.recall.filter((item) => item.userId !== prev.user.id),
      }));
      notify("내 기록을 삭제했습니다.");
      return;
    }

    await Promise.all([
      supabase.from("logs").delete().eq("user_id", state.user.id),
      supabase.from("posts").delete().eq("user_id", state.user.id),
      supabase.from("recall_queue").delete().eq("user_id", state.user.id),
    ]);
    setState((prev) => ({
      ...prev,
      logs: prev.logs.filter((log) => log.userId !== prev.user.id),
      posts: prev.posts.filter((post) => post.userId !== prev.user.id),
      recall: prev.recall.filter((item) => item.userId !== prev.user.id),
    }));
    notify("내 기록을 삭제했습니다.");
  }, [state.user.id, notify]);

  const exportData = useCallback(async () => {
    downloadJSON(`hanjul-${state.user.id}.json`, state);
    notify("JSON으로 내보냈습니다.");
  }, [state, notify]);

  const signOut = useCallback(async () => {
    const supabase = await getSupabaseBrowser();
    if (supabase) await supabase.auth.signOut();
    setAuthenticated(false);
    setState(seedState());
    router.replace("/login");
    router.refresh();
  }, [router]);

  const value = useMemo<DemoContextValue>(
    () => ({
      state,
      ready,
      authenticated,
      mode: MODE,
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
      signOut,
    }),
    [
      state,
      ready,
      authenticated,
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
      signOut,
    ],
  );

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
}

export function useDemo(): DemoContextValue {
  const value = useContext(DemoContext);
  if (!value) throw new Error("useDemo must be used inside DemoProvider");
  return value;
}
