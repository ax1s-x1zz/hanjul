"use client";

import { useEffect, useState } from "react";

import { Button, Sheet } from "@/components/ui";
import { useDemo } from "@/lib/demo-store";
import { pickDailyQuestion, type DailyQuestion as DailyQuestionData } from "@/lib/insights";
import { todayISO } from "@/lib/utils";

export function DailyQuestion() {
  const { state, ready, reviewRecall, notify } = useDemo();
  const reference = state.referenceDate ?? todayISO();
  const choiceKey = `hanjul-question-choice-${reference}`;
  const answerPrefix = `hanjul-question-answer-${reference}-`;
  const [question, setQuestion] = useState<DailyQuestionData | null>(null);
  const [open, setOpen] = useState(false);
  const [answer, setAnswer] = useState("");
  const [saved, setSaved] = useState("");

  useEffect(() => {
    if (!ready) return;
    try {
      const stored = window.localStorage.getItem(choiceKey);
      if (stored) {
        setQuestion(JSON.parse(stored) as DailyQuestionData);
        return;
      }
    } catch {
      // ignore
    }
    const picked = pickDailyQuestion(state);
    setQuestion(picked);
    if (picked) {
      try {
        window.localStorage.setItem(choiceKey, JSON.stringify(picked));
      } catch {
        // ignore
      }
    }
  }, [ready, state, choiceKey]);

  useEffect(() => {
    if (!question) return;
    try {
      const value = window.localStorage.getItem(`${answerPrefix}${question.concept}`);
      setSaved(value ?? "");
    } catch {
      setSaved("");
    }
  }, [question, answerPrefix]);

  function openSheet() {
    setAnswer(saved);
    setOpen(true);
  }

  async function submit(quality: number) {
    if (!question) return;
    const text = answer.trim();
    if (!text) {
      notify("설명을 한 줄 이상 적어주세요.");
      return;
    }
    if (question.recallId) {
      await reviewRecall(question.recallId, quality);
    }
    try {
      window.localStorage.setItem(`${answerPrefix}${question.concept}`, text);
    } catch {
      // ignore
    }
    setSaved(text);
    setOpen(false);
    notify(
      quality >= 3
        ? "설명을 저장하고 복습 완료로 표시했습니다."
        : "설명을 저장했습니다. 내일 다시 복습합니다.",
    );
  }

  if (!question) {
    return (
      <section className="question-card">
        <div className="question-eyebrow">오늘의 질문</div>
        <p className="question-sub" style={{ marginTop: 8 }}>
          기록에 막힌 개념을 남기면 매일 질문이 도착합니다.
        </p>
      </section>
    );
  }

  return (
    <>
      <section className="question-card">
        <div className="question-eyebrow">오늘의 질문</div>
        <div className="question-concept">“{question.concept}”</div>
        <p className="question-sub">
          {question.daysAgo > 0 ? `${question.daysAgo}일 전 ` : ""}
          {question.subject}에서 막힌 개념 · 3문장으로 설명해보세요.
        </p>
        {saved ? (
          <div className="question-answer">
            <b>내 설명</b>
            {saved}
          </div>
        ) : null}
        <Button
          variant={saved ? "secondary" : "soft"}
          block
          onClick={openSheet}
        >
          {saved ? "다시 답하기" : "답하기"}
        </Button>
      </section>

      <Sheet
        open={open}
        onClose={() => setOpen(false)}
        title="오늘의 질문"
        sub={`${question.subject} · 3문장으로 설명해보세요.`}
      >
        <div className="question-sheet-concept">“{question.concept}”</div>
        <textarea
          className="textarea"
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          placeholder="내 말로 3문장..."
          maxLength={600}
        />
        <div className="sheet-actions">
          <Button type="button" onClick={() => void submit(2)}>
            아직 어려움
          </Button>
          <Button type="button" variant="primary" onClick={() => void submit(5)}>
            설명 완료
          </Button>
        </div>
      </Sheet>
    </>
  );
}
