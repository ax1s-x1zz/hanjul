"use client";

import { Bar } from "@/components/ui";
import { useDemo } from "@/lib/demo-store";
import { computeReadiness } from "@/lib/insights";

export function ReadinessCard() {
  const { state } = useDemo();
  const readiness = computeReadiness(state);

  return (
    <div className="readiness-card">
      <div className="readiness-top">
        <div
          className="readiness-ring"
          style={{
            background: `conic-gradient(var(--accent) ${
              readiness.score * 3.6
            }deg, #ececf2 0)`,
          }}
        >
          <div className="readiness-inner">{readiness.score}</div>
        </div>
        <div>
          <div className="readiness-label">시험 준비도</div>
          <div className="readiness-title">D-{readiness.days}</div>
          <div className="readiness-sub">
            {readiness.examName} · {readiness.examDate}
          </div>
        </div>
      </div>

      <div className="readiness-bars">
        {readiness.components.map((component) => (
          <Bar
            key={component.key}
            label={`${component.label} · ${component.detail}`}
            value={component.value}
            max={100}
            suffix="%"
          />
        ))}
      </div>

      <div className="readiness-weak">
        <div className="readiness-weak-title">가장 위험한 개념</div>
        {readiness.weak.length ? (
          readiness.weak.map((item) => (
            <span className="weak-chip" key={item.concept} title={item.subject}>
              {item.concept}
            </span>
          ))
        ) : (
          <span className="helper" style={{ margin: 0 }}>
            아직 막힌 개념이 없습니다.
          </span>
        )}
      </div>

      <p className="helper" style={{ margin: "8px 0 0" }}>
        기록과 복습이 쌓일수록 점수가 올라갑니다.
      </p>
    </div>
  );
}
