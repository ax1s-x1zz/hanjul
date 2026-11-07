"use client";

import { useState } from "react";

import { Button, Sheet } from "@/components/ui";
import { useDemo } from "@/lib/demo-store";
import { buildThreeMinutePlan, type PlanItem } from "@/lib/insights";

export function ThreeMinutePlan() {
  const { state, reviewRecall } = useDemo();
  const plan = buildThreeMinutePlan(state);
  const [open, setOpen] = useState(false);
  const [session, setSession] = useState<PlanItem[]>([]);
  const [index, setIndex] = useState(0);
  const [done, setDone] = useState(false);

  if (!plan.length) return null;

  const current = session[index];

  function start() {
    setSession(plan);
    setIndex(0);
    setDone(false);
    setOpen(true);
  }

  async function review(quality: number) {
    if (!current) return;
    await reviewRecall(current.recallId, quality);
    if (index + 1 < session.length) {
      setIndex(index + 1);
    } else {
      setDone(true);
    }
  }

  return (
    <>
      <div className="plan-card">
        <div className="plan-head">
          <span>오늘의 3분 플랜</span>
          <b>{plan.length}개</b>
        </div>
        <ol className="plan-list">
          {plan.map((item, itemIndex) => (
            <li className="plan-row" key={item.recallId}>
              <span className="plan-num">{itemIndex + 1}</span>
              <div>
                <div className="plan-concept">{item.concept}</div>
                <div className="plan-sub">
                  {item.subject} · {item.reason}
                </div>
              </div>
            </li>
          ))}
        </ol>
        <Button variant="primary" block onClick={start}>
          3분 시작
        </Button>
        <p className="helper" style={{ margin: "8px 0 0" }}>
          1개당 1분, 소리 내어 설명해보세요.
        </p>
      </div>

      <Sheet
        open={open}
        onClose={() => setOpen(false)}
        title={
          done
            ? "3분 완료"
            : `${index + 1} / ${session.length} · 3분 플랜`
        }
        sub={done ? "오늘의 복습을 마쳤습니다." : "1분 동안 소리 내어 설명해보세요."}
      >
        {done ? (
          <div className="empty">준비도와 지식 지도가 갱신됐어요.</div>
        ) : current ? (
          <>
            <div className="plan-session-concept">“{current.concept}”</div>
            <p className="helper">
              {current.subject} · {current.reason}
            </p>
            <div className="sheet-actions">
              <Button type="button" onClick={() => void review(2)}>
                아직 어려움
              </Button>
              <Button
                type="button"
                variant="primary"
                onClick={() => void review(5)}
              >
                설명 완료
              </Button>
            </div>
          </>
        ) : null}
      </Sheet>
    </>
  );
}
