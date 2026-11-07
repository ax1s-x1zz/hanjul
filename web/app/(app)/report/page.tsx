"use client";

import { useMemo, useState } from "react";

import { Bar, Empty, MetricRow, Section, Segmented } from "@/components/ui";
import { KnowledgeMapView } from "@/components/knowledge-map";
import { useDemo } from "@/lib/demo-store";
import { DEMO_REGION, DEMO_SCHOOL } from "@/lib/seed";
import { todayISO } from "@/lib/utils";

type Tab = "mine" | "map" | "region";

function streak(days: string[]): number {
  const unique = Array.from(new Set(days)).sort();
  if (!unique.length) return 0;
  let best = 1;
  let current = 1;
  for (let i = 1; i < unique.length; i += 1) {
    const gap =
      (new Date(`${unique[i]}T00:00:00`).getTime() -
        new Date(`${unique[i - 1]}T00:00:00`).getTime()) /
      86400000;
    if (gap === 1) {
      current += 1;
      best = Math.max(best, current);
    } else {
      current = 1;
    }
  }
  return best;
}

export default function ReportPage() {
  const { state } = useDemo();
  const [tab, setTab] = useState<Tab>("mine");

  const logs = state.logs.filter((log) => log.userId === state.user.id);

  const { subjectCounts, activityCounts, stuckTop } = useMemo(() => {
    const subjectMap = new Map<string, number>();
    const activityMap = new Map<string, number>();
    const stuckMap = new Map<string, number>();
    for (const log of logs) {
      subjectMap.set(log.subject, (subjectMap.get(log.subject) ?? 0) + 1);
      activityMap.set(log.activity, (activityMap.get(log.activity) ?? 0) + 1);
      if (log.stuck.trim()) {
        stuckMap.set(log.stuck.trim(), (stuckMap.get(log.stuck.trim()) ?? 0) + 1);
      }
    }
    return {
      subjectCounts: Array.from(subjectMap.entries()).sort((a, b) => b[1] - a[1]),
      activityCounts: Array.from(activityMap.entries()).sort((a, b) => b[1] - a[1]),
      stuckTop: Array.from(stuckMap.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3),
    };
  }, [logs]);

  const days = logs.map((log) => log.date);
  const summary = logs.length
    ? `이번 주 ${logs.length}개의 수업을 기록했습니다. 가장 자주 막힌 개념은 ${
        stuckTop.map(([concept]) => concept).join(", ") || "아직 없음"
      }입니다. 시험 전에 이 개념부터 다시 확인해보세요.`
    : "이번 주 기록이 아직 없습니다.";

  const regionRows = useMemo(() => {
    const counts = new Map<string, number>();
    for (const post of state.posts) {
      if (post.hidden) continue;
      for (const tag of post.tags) {
        counts.set(tag, (counts.get(tag) ?? 0) + 1);
      }
    }
    return Array.from(counts.entries())
      .filter(([, count]) => count >= 5)
      .sort((a, b) => b[1] - a[1]);
  }, [state.posts]);

  const subjectMax = Math.max(1, ...subjectCounts.map(([, count]) => count));
  const activityMax = Math.max(1, ...activityCounts.map(([, count]) => count));
  const regionMax = Math.max(1, ...regionRows.map(([, count]) => count));

  return (
    <div className="page">
      <Segmented<Tab>
        value={tab}
        onChange={setTab}
        options={[
          { value: "mine", label: "내 기록" },
          { value: "map", label: "지식 지도" },
          { value: "region", label: "지역 막힘" },
        ]}
      />

      {tab === "map" ? (
        <KnowledgeMapView />
      ) : tab === "mine" ? (
        <>
          <div style={{ height: 12 }} />
          <MetricRow
            items={[
              { value: logs.length, label: "기록한 수업" },
              { value: new Set(days).size, label: "기록한 날" },
              { value: streak(days), label: "최장 연속" },
            ]}
          />

          <Section>이번 주 요약</Section>
          <div className="summary">{summary}</div>

          <div className="grid-2">
            <div>
              <Section>과목</Section>
              {subjectCounts.map(([name, count]) => (
                <Bar key={name} label={name} value={count} max={subjectMax} suffix="회" />
              ))}
            </div>
            <div>
              <Section>활동</Section>
              {activityCounts.map(([name, count]) => (
                <Bar key={name} label={name} value={count} max={activityMax} suffix="회" />
              ))}
            </div>
          </div>

          <Section>막힌 개념</Section>
          {stuckTop.length ? (
            <div className="group">
              {stuckTop.map(([concept, count], index) => (
                <div className="list-row" key={concept}>
                  <span className="row-num">{index + 1}</span>
                  <div className="row-main">
                    <div className="row-title">{concept}</div>
                    <div className="row-sub">{count}회 막힘</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <Empty>막힌 개념을 기록하면 여기에 모입니다.</Empty>
          )}
        </>
      ) : (
        <>
          <p className="helper" style={{ marginTop: 12 }}>
            {DEMO_REGION} 공개 글의 개념 태그를 익명 집계합니다. 5명 이상일 때만
            표시합니다.
          </p>
          {regionRows.length ? (
            <>
              <Section>이번 주 광명의 막힘</Section>
              {regionRows.map(([concept, count]) => (
                <Bar
                  key={concept}
                  label={concept}
                  value={count}
                  max={regionMax}
                  suffix="명"
                />
              ))}
            </>
          ) : (
            <Empty>아직 충분히 쌓인 개념이 없습니다.</Empty>
          )}
        </>
      )}

      <p className="helper" style={{ marginTop: 16 }}>
        {DEMO_SCHOOL} · {todayISO()} 기준
      </p>
    </div>
  );
}
