"use client";

import { useEffect, useMemo, useState } from "react";

import { DailyQuestion } from "@/components/daily-question";
import { Button, Chip, Empty, Sheet } from "@/components/ui";
import { useDemo } from "@/lib/demo-store";
import { containsProfanity, ruleBasedTags, sanitizeForPublic } from "@/lib/privacy";
import { DEMO_SCHOOL, TIMETABLE } from "@/lib/seed";
import type { Activity, Period } from "@/lib/types";
import {
  formatKoreanDate,
  normalizeSubject,
  shortWeekday,
  todayISO,
  weekDays,
} from "@/lib/utils";

const ACTIVITIES: Activity[] = ["들음", "필기", "문제풀이", "질문", "이해못함"];

export default function TodayPage() {
  const { state, saveLog, publishPost, unpublish, notify } = useDemo();
  const demoDay = todayISO();
  const [selectedDay, setSelectedDay] = useState(demoDay);
  const [editing, setEditing] = useState<Period | null>(null);
  const [learned, setLearned] = useState("");
  const [activity, setActivity] = useState<Activity>("들음");
  const [stuck, setStuck] = useState("");
  const [isPublic, setIsPublic] = useState(false);

  useEffect(() => {
    // Keep the demo anchored to the runtime date even after a static build.
    setSelectedDay(todayISO());
  }, []);

  const week = useMemo(() => weekDays(selectedDay), [selectedDay]);
  const periods = selectedDay === demoDay ? TIMETABLE : [];
  const dayLogs = state.logs.filter(
    (log) => log.userId === state.user.id && log.date === selectedDay,
  );
  const logged = periods.filter((period) =>
    dayLogs.some((log) => log.period === period.period),
  ).length;
  const percent = periods.length ? Math.round((logged / periods.length) * 100) : 0;

  function openEditor(period: Period) {
    const existing = dayLogs.find((log) => log.period === period.period);
    setEditing(period);
    setLearned(existing?.learned ?? "");
    setActivity(existing?.activity ?? "들음");
    setStuck(existing?.stuck ?? "");
    setIsPublic(existing?.isPublic ?? false);
  }

  function close() {
    setEditing(null);
  }

  async function submit() {
    if (!editing) return;
    const trimmed = learned.trim();
    if (!trimmed) {
      notify("배운 것 한 줄을 입력해주세요.");
      return;
    }
    if (containsProfanity(trimmed) || containsProfanity(stuck)) {
      notify("부적절한 표현이 포함되어 저장할 수 없습니다.");
      return;
    }

    const log = await saveLog({
      date: selectedDay,
      period: editing.period,
      subject: normalizeSubject(editing.subject),
      learned: trimmed,
      activity,
      stuck: stuck.trim(),
      isPublic,
    });
    if (!log) return;

    if (isPublic) {
      const { clean, changed } = sanitizeForPublic(trimmed);
      if (!clean) {
        notify("공개할 수 있는 내용이 없습니다.");
        return;
      }
      await publishPost(log, clean, ruleBasedTags(trimmed, editing.subject));
      notify(changed ? "개인정보를 가려 게시했습니다." : "광명 피드에 게시했습니다.");
    } else {
      await unpublish(log.id);
      notify("저장했습니다. 상세 기록은 나만 볼 수 있습니다.");
    }
    close();
  }

  return (
    <div className="page">
      <div className="date-head">
        <div className="date-title">
          {formatKoreanDate(selectedDay)}
          {selectedDay === demoDay ? <span className="pill">DEMO</span> : null}
        </div>
        <div className="date-sub">
          고{state.user.grade} · {state.user.classNo}반 · {DEMO_SCHOOL} · 데모 시간표
        </div>
      </div>

      <div className="week-strip">
        {week.map((day) => {
          const active = day === selectedDay;
          return (
            <button
              key={day}
              className={day === selectedDay ? "week-day active" : "week-day"}
              onClick={() => setSelectedDay(day)}
              aria-pressed={active}
            >
              {shortWeekday(day)} {Number(day.slice(-2))}
            </button>
          );
        })}
      </div>

      {periods.length === 0 ? (
        <Empty>
          이 날은 데모 시간표가 없습니다.
          <br />
          11월 3일(화)로 돌아가 주세요.
        </Empty>
      ) : (
        <>
          <div className="progress-head">
            <span>오늘의 기록</span>
            <b>
              {logged}/{periods.length}
            </b>
          </div>
          <div className="progress">
            <div style={{ width: `${percent}%` }} />
          </div>

          <div className="group">
            {periods.map((period) => {
              const log = dayLogs.find((item) => item.period === period.period);
              return (
                <div className="list-row" key={period.period}>
                  <span className="row-num">{period.period}</span>
                  <div className="row-main">
                    <div className="row-title">
                      {period.subject}
                      {period.isEvent ? <span className="pill-muted">행사</span> : null}
                    </div>
                    <div className="row-sub">
                      {log ? (
                        <>
                          <span className="ok">✓ 기록 완료</span> · {log.learned.slice(0, 48)}
                          {log.isPublic ? (
                            <>
                              {" "}
                              · <span className="public">광명 공개</span>
                            </>
                          ) : null}
                        </>
                      ) : (
                        "아직 기록하지 않았습니다"
                      )}
                    </div>
                  </div>
                  <button
                    className="row-action"
                    onClick={() => openEditor(period)}
                    aria-label={`${period.period}교시 기록`}
                  >
                    {log ? "›" : "＋"}
                  </button>
                </div>
              );
            })}
          </div>
        </>
      )}

      <DailyQuestion />

      <Sheet
        open={editing !== null}
        onClose={close}
        title={editing ? `${editing.period}교시 · ${editing.subject}` : "기록"}
        sub="한 줄이면 충분합니다."
      >
        <label className="field-label" htmlFor="learned">
          배운 것 한 줄
        </label>
        <textarea
          id="learned"
          className="textarea"
          maxLength={120}
          value={learned}
          onChange={(event) => setLearned(event.target.value)}
          placeholder="예: 관계대명사 whose가 소유격이라는 걸 배웠다."
        />

        <span className="field-label">내가 한 것</span>
        <div className="chips">
          {ACTIVITIES.map((item) => (
            <Chip
              key={item}
              active={activity === item}
              onClick={() => setActivity(item)}
              type="button"
            >
              {item}
            </Chip>
          ))}
        </div>

        <label className="field-label" htmlFor="stuck">
          막힌 것 (선택)
        </label>
        <input
          id="stuck"
          className="input"
          maxLength={80}
          value={stuck}
          onChange={(event) => setStuck(event.target.value)}
          placeholder="예: whose vs of which"
        />

        <div className="switch-row">
          <div>
            <div style={{ fontSize: 13, fontWeight: 700 }}>광명 피드에 공개</div>
            <div className="row-sub">공개한 한 줄만 지역 친구들에게 보입니다.</div>
          </div>
          <button
            type="button"
            className="switch"
            data-on={isPublic}
            aria-pressed={isPublic}
            aria-label="광명 피드에 공개"
            onClick={() => setIsPublic((value) => !value)}
          />
        </div>

        <div className="sheet-actions">
          <Button type="button" onClick={close}>
            취소
          </Button>
          <Button type="button" variant="primary" onClick={() => void submit()}>
            저장
          </Button>
        </div>
      </Sheet>
    </div>
  );
}
