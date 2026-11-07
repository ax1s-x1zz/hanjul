import type { Period } from "./types";

const EVENT_KEYWORDS = ["현장체험", "휴업", "재량", "행사", "축제", "체육대회", "수련"];

export function isEventSubject(subject: string): boolean {
  return EVENT_KEYWORDS.some((keyword) => subject.includes(keyword));
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
  const key = process.env.NEIS_KEY;
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

  const response = await fetch(url, { next: { revalidate: 86400 } });
  if (!response.ok) return null;

  const payload = (await response.json()) as {
    hisTimetable?: Array<{ row?: Array<Record<string, string>> }>;
  };
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
    .filter((row) => Number.isFinite(row.period))
    .sort((a, b) => a.period - b.period);
}
