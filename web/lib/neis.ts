import type { Period } from "./types";

const EVENT_KEYWORDS = ["현장체험", "휴업", "재량", "행사", "축제", "체육대회", "수련"];
const NO_CLASS_KEYWORDS = [
  "휴업",
  "공휴일",
  "방학",
  "개교기념일",
  "일요일",
  "토요일",
  "재량휴업",
];

export function isEventSubject(subject: string): boolean {
  return EVENT_KEYWORDS.some((keyword) => subject.includes(keyword));
}

export function isNoClassSubject(subject: string): boolean {
  return NO_CLASS_KEYWORDS.some((keyword) => subject.includes(keyword));
}

export interface TimetableRequest {
  officeCode: string;
  schoolCode: string;
  date: string;
  grade: number;
  classNo: string;
}

export async function fetchTimetable({
  officeCode,
  schoolCode,
  date,
  grade,
  classNo,
}: TimetableRequest): Promise<Period[] | null> {
  const key = process.env.NEIS_KEY?.trim();
  if (!key) return null;

  const ymd = date.replaceAll("-", "");
  const url = new URL("https://open.neis.go.kr/hub/hisTimetable");
  url.searchParams.set("KEY", key);
  url.searchParams.set("Type", "json");
  url.searchParams.set("pIndex", "1");
  url.searchParams.set("pSize", "50");
  url.searchParams.set("ATPT_OFCDC_SC_CODE", officeCode);
  url.searchParams.set("SD_SCHUL_CODE", schoolCode);
  url.searchParams.set("ALL_TI_YMD", ymd);
  url.searchParams.set("GRADE", String(grade));
  url.searchParams.set("CLASS_NM", classNo);

  try {
    const response = await fetch(url, { next: { revalidate: 86400 } });
    if (!response.ok) return null;

    const payload = (await response.json()) as {
      RESULT?: { CODE?: string };
      hisTimetable?: Array<{ row?: Array<Record<string, string>> }>;
    };

    // INFO-200 = 해당 날짜 데이터 없음(정상). 그 외 ERROR-* = 키/요청 오류.
    if (payload.RESULT) {
      return payload.RESULT.CODE === "INFO-200" ? [] : null;
    }

    const rows = payload.hisTimetable?.[1]?.row ?? [];
    return rows
      .map((row) => {
        const subject = (row.ITRT_CNTNT ?? "").trim();
        return {
          period: Number(row.PERIO),
          subject: subject || "수업 정보 없음",
          isEvent: isEventSubject(subject),
        } satisfies Period;
      })
      .filter(
        (row) => Number.isFinite(row.period) && !isNoClassSubject(row.subject),
      )
      .sort((a, b) => a.period - b.period);
  } catch {
    return null;
  }
}

/** 다음 수업일(평일)을 최대 14일 앞까지 찾습니다. */
export async function findNextSchoolDay({
  officeCode,
  schoolCode,
  date,
  grade,
  classNo,
}: TimetableRequest): Promise<{ date: string; periods: Period[] } | null> {
  const cursor = new Date(`${date}T12:00:00`);
  for (let offset = 1; offset <= 14; offset += 1) {
    cursor.setDate(cursor.getDate() + 1);
    if (cursor.getDay() === 0 || cursor.getDay() === 6) continue;
    const nextDate = `${cursor.getFullYear()}-${String(
      cursor.getMonth() + 1,
    ).padStart(2, "0")}-${String(cursor.getDate()).padStart(2, "0")}`;
    const periods = await fetchTimetable({
      officeCode,
      schoolCode,
      date: nextDate,
      grade,
      classNo,
    });
    if (periods?.length) return { date: nextDate, periods };
  }
  return null;
}
