const EMAIL = /[\w.+-]+@[\w-]+\.[\w.-]+/g;
const PHONE = /\b0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}\b/g;
const RRN = /\b\d{6}[-.\s]?[1-4]\d{6}\b/g;
const URL_RE = /(https?:\/\/\S+|www\.\S+)/gi;
const LONG_DIGITS = /\b\d{6,}\b/g;
const TEACHER = /([가-힣]{2,4})\s*선생님/g;

const PROFANITY = ["씨발", "시발", "개새끼", "병신", "지랄", "좆", "꺼져", "죽어라"];

export function containsProfanity(text: string): boolean {
  const normalized = (text || "").replace(/\s+/g, "").toLowerCase();
  return PROFANITY.some((word) => normalized.includes(word));
}

export function stripPII(text: string, schoolName?: string): string {
  let result = text ?? "";
  if (schoolName) {
    const short = schoolName.replace(/(고등학교|중학교|초등학교)$/, "");
    result = result.replaceAll(schoolName, "○○고");
    if (short && short !== schoolName) result = result.replaceAll(short, "○○");
  }
  return result
    .replace(EMAIL, "[이메일]")
    .replace(RRN, "[주민번호]")
    .replace(PHONE, "[전화번호]")
    .replace(URL_RE, "[링크]")
    .replace(TEACHER, "선생님")
    .replace(LONG_DIGITS, "[숫자]")
    .replace(/[ \t]+/g, " ")
    .trim();
}

export function sanitizeForPublic(
  text: string,
  schoolName = "진성고등학교",
): { clean: string; changed: boolean } {
  const clean = stripPII(text, schoolName);
  return { clean, changed: clean !== (text ?? "").trim() };
}

const TAG_RULES: Array<[string, string[]]> = [
  ["판별식", ["판별식", "이차방정식", "근의 개수"]],
  ["미분", ["미분", "도함수", "연쇄법칙"]],
  ["적분", ["적분", "부정적분", "정적분"]],
  ["관계대명사", ["관계대명사", "whose", "of which"]],
  ["세포호흡", ["세포호흡", "ATP", "미토콘드리아"]],
  ["이상기체", ["이상기체", "PV=nRT", "상태방정식"]],
  ["판다스", ["판다스", "groupby", "데이터프레임"]],
  ["이차곡선", ["이차곡선", "타원", "포물선"]],
];

export function ruleBasedTags(text: string, subject: string): string[] {
  const lower = (text || "").toLowerCase();
  const tags = TAG_RULES.filter(([, words]) =>
    words.some((word) => lower.includes(word.toLowerCase())),
  ).map(([tag]) => tag);
  return (tags.length ? tags : [subject]).slice(0, 3);
}
