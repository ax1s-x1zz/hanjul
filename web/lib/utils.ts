export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function uid(prefix = "id"): string {
  const random =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2);
  return `${prefix}-${random}`;
}

export function dateISO(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function todayISO(): string {
  return dateISO(new Date());
}

export function parseISO(value: string): Date {
  return new Date(`${value}T00:00:00`);
}

const WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"];

export function formatKoreanDate(value: string): string {
  const d = parseISO(value);
  return `${d.getMonth() + 1}월 ${d.getDate()}일 ${WEEKDAYS[d.getDay()]}요일`;
}

export function shortWeekday(value: string): string {
  return WEEKDAYS[parseISO(value).getDay()];
}

export function addDays(value: string, days: number): string {
  const d = parseISO(value);
  d.setDate(d.getDate() + days);
  return dateISO(d);
}

export function weekDays(base: string): string[] {
  const d = parseISO(base);
  const day = d.getDay();
  const mondayOffset = day === 0 ? -6 : 1 - day;
  const monday = new Date(d);
  monday.setDate(d.getDate() + mondayOffset);
  return Array.from({ length: 5 }, (_, index) => {
    const current = new Date(monday);
    current.setDate(monday.getDate() + index);
    return dateISO(current);
  });
}

export function daysUntil(target: string): number {
  const t = parseISO(target).getTime();
  const now = parseISO(todayISO()).getTime();
  return Math.round((t - now) / 86400000);
}

export function timeAgo(iso: string): string {
  const then = new Date(iso).getTime();
  const diff = Math.max(0, Date.now() - then);
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "방금 전";
  if (minutes < 60) return `${minutes}분 전`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  return `${Math.floor(hours / 24)}일 전`;
}

export function userInitial(nickname: string): string {
  const clean = (nickname || "한").trim();
  const parts = clean.split("_");
  if (parts.length > 1 && parts[1]) return parts[1][0];
  return clean[0];
}

export function downloadJSON(filename: string, data: unknown): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

const SUBJECT_MAP: Record<string, string> = {
  "수학Ⅰ": "수학1",
  "수학Ⅱ": "수학2",
  "미적분Ⅰ": "미적분1",
  "미적분Ⅱ": "미적분2",
  "화학Ⅰ": "화학1",
  "화학Ⅱ": "화학2",
  "물리학Ⅰ": "물리학1",
  "물리학Ⅱ": "물리학2",
  "생명과학Ⅰ": "생명과학1",
  "생명과학Ⅱ": "생명과학2",
  "지구과학Ⅰ": "지구과학1",
  "지구과학Ⅱ": "지구과학2",
  "영어Ⅰ": "영어1",
  "영어Ⅱ": "영어2",
  "독서와 작문": "독서와작문",
  "영어 독해와 작문": "영어독해와작문",
  "물질과 에너지": "물질과에너지",
  "역학과 에너지": "역학과에너지",
  "세포와 물질대사": "세포와물질대사",
  "데이터 과학": "데이터과학",
  "스포츠 생활1": "스포츠생활1",
  "윤리와 사상": "윤리와사상",
};

export function normalizeSubject(name: string): string {
  return SUBJECT_MAP[name] ?? name.replace(/\s+/g, "");
}

export function subjectShort(name: string): string {
  const map: Record<string, string> = {
    데이터과학: "데이터",
    독서와작문: "독서",
    물질과에너지: "물질",
    미적분1: "미적분",
    세포와물질대사: "세포",
    영어독해와작문: "영독작",
    스포츠생활1: "스포츠",
    윤리와사상: "윤리",
  };
  return map[name] ?? name;
}
