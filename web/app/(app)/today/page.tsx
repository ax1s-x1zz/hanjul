"use client";

import { useEffect, useMemo, useState } from "react";

import { DailyQuestion } from "@/components/daily-question";
import { Button, Chip, Sheet } from "@/components/ui";
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

interface TimetableResponse {
  date: string;
  school: string;
  source: "neis" | "sample";
  periods: Period[];
  nearest?: { date: string; periods: Period[] };
  event?: string;
  message?: string;
}

export default function TodayPage() {
  const { state, saveLog, publishPost, unpublish, notify } = useDemo();
  const demoDay = state.referenceDate ?? todayISO();
  const [selectedDay, setSelectedDay] = useState(demoDay);
  const [timetable, setTimetable] = useState<TimetableResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Period | null>(null);
  const [learned, setLearned] = useState("");
  const [activity, setActivity] = useState<Activity>("들음");
  const [stuck, setStuck] = useState("");
  const [isPublic, setIsPublic] = useState(false);

  useEffect(() => {
    // 데모는 기준일(월·화 수업일)에 고정하고, 실서비스는 오늘을 사용합니다.
    setSelectedDay(state.referenceDate ?? todayISO());
  }, [state.referenceDate]);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setLoading(true);

    const query = new URLSearchParams({
      date: selectedDay,
      grade: String(state.user.grade),
      class: state.user.classNo,
    });

    fetch(`/api/neis/timetable?${query.toString()}`, {
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) throw new Error("timetable request failed");
        return response.json() as Promise<TimetableResponse>;
      })
      .then((data) => {
        if (!active) return;
        setTimetable(data);
      })
      .catch((error: unknown) => {
        if (!active || (error instanceof DOMException && error.name === "AbortError")) {
          return;
        }
        setTimetable({
          date: selectedDay,
          school: DEMO_SCHOOL,
          source: "sample",
          periods: TIMETABLE,
          message:
            "NEIS 시간표를 불러오지 못해 샘플 시간표를 표시합니다. 잠시 후 다시 시도해주세요.",
        });
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [selectedDay, state.user.grade, state.user.classNo]);

  const week = useMemo(() => weekDays(selectedDay), [selectedDay]);
  const current = timetable?.date === selectedDay ? timetable : null;
  const periods = current?.periods ?? [];
  const dayLogs = state.logs.filter(
    (log) => log.userId === state.user.id && log.date === selectedDay,
  );
  const logged = periods.filter((period) =>
    dayLogs.some((log) => log.period === period.period),
  ).length;
  const percent = periods.length ? Math.round((logged / periods.length) * 100) : 0;

  function openEditor(period: Period) {
    const existing = dayLogs.find((log) => log.period === period.period);
    setEditing(
      existing ? { ...period, subject: existing.subject } : period,
    );
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
          {current ? (
            <span className={current.source === "neis" ? "pill" : "pill-muted"}>
              {current.source === "neis" ? "NEIS" : "샘플"}
            </span>
          ) : null}
        </div>
        <div className="date-sub">
          고{state.user.grade} · {state.user.classNo}반 · {DEMO_SCHOOL} ·{" "}
          {current
            ? current.source === "neis"
              ? "실제 시간표"
              : "샘플 시간표"
            : "시간표 불러오는 중"}
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

      {loading || !current ? (
        <div className="timetable-skeleton" aria-hidden>
          <div className="skeleton-row" />
          <div className="skeleton-row" />
          <div className="skeleton-row" />
          <div className="skeleton-row" />
        </div>
      ) : current.event ? (
        <div className="holiday-card event-card">
          <div className="holiday-eyebrow">체험학습</div>
          <div className="holiday-title">{current.event}</div>
          <p className="holiday-sub">
            {current.message ?? "이 날은 수업 대신 체험학습 일정입니다."}
          </p>
        </div>
      ) : periods.length === 0 ? (
        <div className="holiday-card">
          <div className="holiday-eyebrow">수업 없음</div>
          <div className="holiday-title">
            {formatKoreanDate(selectedDay)}은 수업이 없습니다.
          </div>
          <p className="holiday-sub">
            {current.message ?? "주말·휴업일에는 시간표가 없습니다."}
          </p>
          {current.nearest ? (
            <>
              <p className="helper">
                다음 수업일은 {formatKoreanDate(current.nearest.date)}입니다.
              </p>
              <Button
                variant="primary"
                block
                onClick={() => setSelectedDay(current.nearest!.date)}
              >
                다음 수업일 시간표 보기
              </Button>
            </>
          ) : null}
        </div>
      ) : (
        <>
          <div className="progress-head">
            <span>{selectedDay === demoDay ? "오늘의 기록" : "이 날의 기록"}</span>
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
                      {log ? log.subject : period.subject}
                      {period.isEvent && !log ? (
                        <span className="pill-muted">행사</span>
                      ) : null}
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
