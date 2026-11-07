"use client";

import { Button, Empty, MetricRow, Section } from "@/components/ui";
import { ReadinessCard } from "@/components/readiness-card";
import { ThreeMinutePlan } from "@/components/three-minute-plan";
import { useDemo } from "@/lib/demo-store";
import { todayISO } from "@/lib/utils";

export default function RecallPage() {
  const { state, reviewRecall } = useDemo();
  const items = state.recall.filter((item) => item.userId === state.user.id);
  const due = items.filter((item) => item.dueDate <= todayISO());
  const remaining = items.length - due.length;

  return (
    <div className="page">
      <ReadinessCard />

      <div style={{ height: 12 }} />
      <MetricRow
        items={[
          { value: due.length, label: "오늘 복습" },
          { value: items.length, label: "전체 카드" },
          { value: remaining, label: "다음 대기" },
        ]}
      />

      <div style={{ height: 12 }} />
      <ThreeMinutePlan />

      <Section>오늘의 복습</Section>
      {due.length === 0 ? (
        <Empty>오늘 복습할 카드가 없습니다.</Empty>
      ) : (
        <div className="group">
          {due.map((item) => (
            <div className="list-row recall-row" key={item.id}>
              <div className="row-main">
                <div className="row-title">{item.concept}</div>
                <div className="row-sub">
                  복습 {item.reps}회 · 다음 {item.dueDate} · 간격 {item.interval}일
                </div>
              </div>
              <div className="recall-actions">
                <Button
                  type="button"
                  variant="soft"
                  className="btn-small"
                  onClick={() => void reviewRecall(item.id, 5)}
                >
                  기억남
                </Button>
                <Button
                  type="button"
                  className="btn-small"
                  onClick={() => void reviewRecall(item.id, 2)}
                >
                  헷갈림
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
