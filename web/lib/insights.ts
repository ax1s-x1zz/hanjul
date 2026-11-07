import type { DemoState } from "./types";
import { addDays, parseISO, todayISO } from "./utils";

export interface ReadinessComponent {
  key: string;
  label: string;
  value: number;
  detail: string;
}

export interface WeakConcept {
  concept: string;
  subject: string;
  reps: number;
}

export interface Readiness {
  score: number;
  days: number;
  examName: string;
  examDate: string;
  components: ReadinessComponent[];
  weak: WeakConcept[];
}

export type Mastery = "understood" | "review" | "stuck";

export interface KnowledgeConcept {
  concept: string;
  subject: string;
  mastery: Mastery;
  reps: number;
}

export interface KnowledgeMap {
  concepts: KnowledgeConcept[];
  counts: Record<Mastery, number>;
}

/**
 * A transparent, locally computed readiness estimate.
 * It is deliberately not a grade: it measures the habit + recall loop.
 */
export function computeReadiness(state: DemoState): Readiness {
  const reference = state.referenceDate ?? todayISO();
  const logs = state.logs.filter((log) => log.userId === state.user.id);
  const recall = state.recall.filter((item) => item.userId === state.user.id);

  const recordedDays = new Set(logs.map((log) => log.date)).size;
  const coverage = Math.min(100, Math.round((recordedDays / 5) * 100));

  const reviewed = recall.filter((item) => item.reps > 0).length;
  const recallScore = recall.length
    ? Math.min(100, Math.round((reviewed / recall.length) * 100))
    : 0;

  const resolved = recall.filter((item) => item.reps >= 2).length;
  const resolvedScore = recall.length
    ? Math.min(100, Math.round((resolved / recall.length) * 100))
    : 0;

  const score = Math.min(
    100,
    Math.round(0.35 * coverage + 0.4 * recallScore + 0.25 * resolvedScore),
  );

  const weak = [...recall]
    .sort((a, b) => a.reps - b.reps)
    .slice(0, 3)
    .map((item) => {
      const source = logs.find((log) => log.stuck.trim() === item.concept);
      return {
        concept: item.concept,
        subject: source?.subject ?? "기타",
        reps: item.reps,
      };
    });

  const examDate = addDays(reference, 37);
  const days = Math.round(
    (parseISO(examDate).getTime() - parseISO(reference).getTime()) / 86400000,
  );
  return {
    score,
    days,
    examName: "2학기 기말고사",
    examDate,
    components: [
      {
        key: "coverage",
        label: "기록 커버리지",
        value: coverage,
        detail: `${recordedDays}/5일`,
      },
      {
        key: "recall",
        label: "복습 신뢰도",
        value: recallScore,
        detail: `${reviewed}/${recall.length}개`,
      },
      {
        key: "resolved",
        label: "막힘 해결",
        value: resolvedScore,
        detail: `${resolved}/${recall.length}개`,
      },
    ],
    weak,
  };
}

export interface DailyQuestion {
  concept: string;
  subject: string;
  daysAgo: number;
  reps: number;
  recallId?: string;
}

export function pickDailyQuestion(state: DemoState): DailyQuestion | null {
  const reference = state.referenceDate ?? todayISO();
  const logs = state.logs.filter((log) => log.userId === state.user.id);
  const recall = state.recall.filter((item) => item.userId === state.user.id);
  if (!logs.length && !recall.length) return null;

  const candidates = recall.map((item) => ({
    item,
    log: logs.find((log) => log.stuck.trim() === item.concept),
  }));

  if (!candidates.length) {
    const log = logs.find((entry) => entry.stuck.trim());
    if (!log) return null;
    return {
      concept: log.stuck.trim(),
      subject: log.subject,
      daysAgo: 0,
      reps: 0,
    };
  }

  candidates.sort(
    (a, b) =>
      a.item.reps - b.item.reps ||
      (a.log?.date ?? "").localeCompare(b.log?.date ?? ""),
  );
  const chosen = candidates[0];
  const daysAgo = chosen.log
    ? Math.max(
        0,
        Math.round(
          (parseISO(reference).getTime() - parseISO(chosen.log.date).getTime()) /
            86400000,
        ),
      )
    : 0;

  return {
    concept: chosen.item.concept,
    subject: chosen.log?.subject ?? "기타",
    daysAgo,
    reps: chosen.item.reps,
    recallId: chosen.item.id,
  };
}

export interface PlanItem {
  concept: string;
  subject: string;
  recallId: string;
  reason: string;
  reps: number;
}

export function buildThreeMinutePlan(state: DemoState): PlanItem[] {
  const logs = state.logs.filter((log) => log.userId === state.user.id);
  const recall = state.recall.filter((item) => item.userId === state.user.id);
  const today = state.referenceDate ?? todayISO();
  const due = recall.filter((item) => item.dueDate <= today);
  const ordered = [...due, ...recall].sort(
    (a, b) => a.reps - b.reps || a.dueDate.localeCompare(b.dueDate),
  );

  const seen = new Set<string>();
  const plan: PlanItem[] = [];
  for (const item of ordered) {
    if (seen.has(item.concept)) continue;
    seen.add(item.concept);
    const log = logs.find((entry) => entry.stuck.trim() === item.concept);
    const isDue = item.dueDate <= today;
    plan.push({
      concept: item.concept,
      subject: log?.subject ?? "기타",
      recallId: item.id,
      reason: isDue
        ? item.reps === 0
          ? "오늘 첫 복습"
          : "오늘 복습"
        : "가장 약한 개념",
      reps: item.reps,
    });
    if (plan.length === 3) break;
  }
  return plan;
}

export function computeKnowledgeMap(state: DemoState): KnowledgeMap {
  const logs = state.logs.filter((log) => log.userId === state.user.id);
  const recall = state.recall.filter((item) => item.userId === state.user.id);
  const map = new Map<string, { subject: string; concept: string; reps: number }>();

  for (const log of logs) {
    const concept = log.stuck.trim();
    if (!concept) continue;
    const item = recall.find((entry) => entry.concept === concept);
    map.set(concept, {
      concept,
      subject: log.subject,
      reps: item?.reps ?? 0,
    });
  }

  for (const item of recall) {
    if (!map.has(item.concept)) {
      map.set(item.concept, {
        concept: item.concept,
        subject: "기타",
        reps: item.reps,
      });
    }
  }

  const concepts: KnowledgeConcept[] = Array.from(map.values())
    .map(({ concept, subject, reps }): KnowledgeConcept => {
      const mastery: Mastery =
        reps >= 2 ? "understood" : reps >= 1 ? "review" : "stuck";
      return { concept, subject, reps, mastery };
    })
    .sort(
      (a, b) =>
        a.subject.localeCompare(b.subject, "ko") ||
        a.concept.localeCompare(b.concept, "ko"),
    );

  return {
    concepts,
    counts: {
      understood: concepts.filter((item) => item.mastery === "understood").length,
      review: concepts.filter((item) => item.mastery === "review").length,
      stuck: concepts.filter((item) => item.mastery === "stuck").length,
    },
  };
}
