"use client";

import { Empty, MetricRow, Section } from "@/components/ui";
import { useDemo } from "@/lib/demo-store";
import { computeKnowledgeMap } from "@/lib/insights";

const MASTERY_LABEL = {
  understood: "이해",
  review: "복습 중",
  stuck: "막힘",
} as const;

export function KnowledgeMapView() {
  const { state } = useDemo();
  const map = computeKnowledgeMap(state);

  if (!map.concepts.length) {
    return <Empty>기록에 막힌 개념을 남기면 지식 지도가 만들어집니다.</Empty>;
  }

  const subjects = Array.from(new Set(map.concepts.map((item) => item.subject)));

  return (
    <div>
      <MetricRow
        items={[
          { value: map.counts.understood, label: "이해" },
          { value: map.counts.review, label: "복습 중" },
          { value: map.counts.stuck, label: "막힘" },
        ]}
      />

      <div className="map-legend">
        <span>
          <i className="legend-dot understood" /> 이해
        </span>
        <span>
          <i className="legend-dot review" /> 복습 중
        </span>
        <span>
          <i className="legend-dot stuck" /> 막힘
        </span>
      </div>

      <Section>내 지식 지도</Section>
      {subjects.map((subject) => (
        <div className="map-group" key={subject}>
          <div className="map-subject">{subject}</div>
          <div className="concept-grid">
            {map.concepts
              .filter((item) => item.subject === subject)
              .map((item) => (
                <span
                  className={`concept-chip ${item.mastery}`}
                  key={item.concept}
                  title={`복습 ${item.reps}회`}
                >
                  {item.concept}
                </span>
              ))}
          </div>
        </div>
      ))}

      <p className="helper" style={{ marginTop: 14 }}>
        복습 카드에서 ‘기억남’을 누를수록 막힘 → 복습 중 → 이해로 바뀝니다.
      </p>
    </div>
  );
}
