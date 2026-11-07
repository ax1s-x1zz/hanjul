import type {
  DemoState,
  LogEntry,
  Period,
  Post,
  RecallItem,
  User,
} from "./types";
import { addDays, normalizeSubject, todayISO } from "./utils";

export const DEMO_SCHOOL = "진성고등학교";
export const DEMO_REGION = "경기도 광명시";

/**
 * 데모 기준일: 이번 주 화요일(수학여행 전 마지막 수업일).
 * 수~금은 NEIS에 숙박형 현장체험학습으로 등록되어 있습니다.
 * 데모를 다른 주에 시연할 때는 이 값만 바꾸면 됩니다.
 */
export const DEMO_ANCHOR = "2026-11-03";

export const DEMO_USERS: User[] = [
  { id: "demo-main", nickname: "고2_기하러_0503", grade: 2, classNo: "5", track: "이과", region: "경기도 광명시" },
  { id: "demo-friend", nickname: "고2_미분러_0217", grade: 2, classNo: "2", track: "이과", region: "경기도 광명시" },
  { id: "seed-1", nickname: "고2_미적분러_1102", grade: 2, classNo: "5", track: "이과", region: "경기도 광명시" },
  { id: "seed-2", nickname: "고2_영어러_0421", grade: 2, classNo: "2", track: "이과", region: "경기도 광명시" },
  { id: "seed-3", nickname: "고2_생명러_0731", grade: 2, classNo: "3", track: "이과", region: "경기도 광명시" },
  { id: "seed-4", nickname: "고1_국어러_0210", grade: 1, classNo: "4", track: "문과", region: "경기도 광명시" },
  { id: "seed-5", nickname: "고2_데이터러_0515", grade: 2, classNo: "5", track: "이과", region: "경기도 광명시" },
  { id: "seed-6", nickname: "고2_화학러_0908", grade: 2, classNo: "6", track: "이과", region: "경기도 광명시" },
];

export const TIMETABLE: Period[] = [
  { period: 1, subject: "세포와 물질대사" },
  { period: 2, subject: "기하" },
  { period: 3, subject: "독서와 작문" },
  { period: 4, subject: "데이터 과학" },
  { period: 5, subject: "영어Ⅱ" },
  { period: 6, subject: "미적분Ⅰ" },
  { period: 7, subject: "물질과 에너지" },
];

const LOG_SEED: Array<
  Omit<LogEntry, "id" | "userId" | "isPublic" | "date"> & { dayOffset: number }
> = [
  { dayOffset: 0, period: 1, subject: "세포와 물질대사", learned: "세포 호흡과 물질대사의 관계를 배웠다.", activity: "질문", stuck: "ATP 생성 과정" },
  { dayOffset: 0, period: 2, subject: "기하", learned: "이차곡선의 접선의 방정식을 유도했다.", activity: "문제풀이", stuck: "타원 접선의 기울기" },
  { dayOffset: 0, period: 3, subject: "독서와 작문", learned: "설득하는 글의 논증 구조를 분석했다.", activity: "필기", stuck: "" },
  { dayOffset: 0, period: 4, subject: "데이터 과학", learned: "pandas groupby로 반별 평균을 계산했다.", activity: "문제풀이", stuck: "인덱스 재설정" },
  { dayOffset: 0, period: 6, subject: "미적분Ⅰ", learned: "합성함수의 미분법을 배웠다.", activity: "문제풀이", stuck: "연쇄법칙" },
  { dayOffset: 0, period: 7, subject: "물질과 에너지", learned: "이상기체 상태방정식을 배웠다.", activity: "필기", stuck: "" },
  { dayOffset: 1, period: 1, subject: "세포와 물질대사", learned: "세포막의 선택적 투과성을 배웠다.", activity: "들음", stuck: "능동 수송" },
  { dayOffset: 1, period: 2, subject: "미적분Ⅰ", learned: "판별식으로 근의 개수를 판별했다.", activity: "문제풀이", stuck: "판별식" },
  { dayOffset: 1, period: 3, subject: "스포츠 생활1", learned: "배드민턴 복식 규칙을 익혔다.", activity: "들음", stuck: "" },
  { dayOffset: 1, period: 4, subject: "윤리와 사상", learned: "공리주의의 기본 원리를 배웠다.", activity: "필기", stuck: "최대 행복 원칙" },
  { dayOffset: 4, period: 1, subject: "미적분Ⅰ", learned: "미분계수의 정의를 복습했다.", activity: "문제풀이", stuck: "극한" },
  { dayOffset: 4, period: 2, subject: "영어Ⅱ", learned: "본문에서 관계대명사를 찾아 해석했다.", activity: "문제풀이", stuck: "관계대명사" },
];

const POST_SEED: Array<{ userId: string; subject: string; tags: string[]; text: string; hoursAgo: number }> = [
  { userId: "seed-1", subject: "미적분1", tags: ["판별식", "이차방정식"], text: "오늘 미적분에서 판별식으로 근의 개수를 판별하는 법을 배웠다. 이차방정식이랑 연결되는 게 신기했다.", hoursAgo: 1 },
  { userId: "seed-2", subject: "영어2", tags: ["관계대명사", "소유격"], text: "영어Ⅱ에서 관계대명사 whose가 소유격이라는 걸 이제 알았다. of which랑 헷갈렸는데 예문으로 이해됨.", hoursAgo: 2 },
  { userId: "seed-3", subject: "세포와물질대사", tags: ["세포호흡", "ATP"], text: "세포호흡에서 ATP가 왜 중요한지 질문했다. 미토콘드리아가 에너지 공장이라는 말이 이제 이해된다.", hoursAgo: 3 },
  { userId: "seed-1", subject: "기하", tags: ["이차곡선", "타원", "판별식"], text: "기하 시간에 타원의 접선의 방정식을 유도했다. 계산이 길어서 중간에 부호를 놓쳤다.", hoursAgo: 4 },
  { userId: "seed-5", subject: "데이터과학", tags: ["판다스", "groupby"], text: "데이터 과학에서 groupby로 반별 평균을 냈다. 인덱스를 다시 정렬하는 게 아직 어색하다.", hoursAgo: 5 },
  { userId: "seed-6", subject: "물질과에너지", tags: ["이상기체", "상태방정식"], text: "물질과 에너지에서 이상기체 상태방정식을 배웠다. PV=nRT에서 단위 환산이 헷갈린다.", hoursAgo: 6 },
  { userId: "seed-1", subject: "미적분1", tags: ["판별식", "근의개수"], text: "판별식 문제를 10개 풀었다. D=0일 때 중근이라는 걸 이제 안 틀린다.", hoursAgo: 8 },
  { userId: "seed-2", subject: "영어2", tags: ["관계대명사", "whose"], text: "whose 예문을 직접 만들어봤다. 내가 만든 문장이 맞는지 선생님께 물어봐야겠다.", hoursAgo: 10 },
  { userId: "seed-3", subject: "세포와물질대사", tags: ["세포호흡", "미토콘드리아"], text: "세포호흡 단계를 그림으로 정리했다. 해당과정이 어디서 일어나는지 다시 봐야 한다.", hoursAgo: 12 },
  { userId: "seed-4", subject: "독서와작문", tags: ["설득전략", "논증"], text: "설득하는 글에서 통계 자료를 쓰는 이유를 배웠다. 근거의 신뢰도가 중요하다는 걸 알았다.", hoursAgo: 14 },
  { userId: "seed-1", subject: "미적분1", tags: ["판별식", "이차함수"], text: "이차함수 그래프와 판별식의 관계를 연결해서 이해했다.", hoursAgo: 16 },
  { userId: "seed-2", subject: "영어2", tags: ["관계대명사", "문법"], text: "관계대명사 계속적 용법을 배웠다. 콤마 하나로 의미가 달라지는 게 신기하다.", hoursAgo: 18 },
  { userId: "seed-3", subject: "세포와물질대사", tags: ["세포호흡", "ATP"], text: "ATP 합성 효소의 역할을 정리했다. 아직 세부 단계는 헷갈린다.", hoursAgo: 20 },
  { userId: "seed-5", subject: "데이터과학", tags: ["판다스", "데이터정제"], text: "결측치를 채우는 방법을 배웠다. 평균으로 채우는 게 항상 좋은 건 아니라는 걸 알았다.", hoursAgo: 22 },
  { userId: "seed-6", subject: "물질과에너지", tags: ["이상기체", "몰"], text: "몰과 부피의 관계를 계산했다. 단위 맞추는 연습이 더 필요하다.", hoursAgo: 24 },
  { userId: "seed-1", subject: "기하", tags: ["판별식", "이차곡선"], text: "이차곡선 단원에서 판별식이 다시 나왔다. 수학은 결국 연결되어 있다.", hoursAgo: 26 },
  { userId: "seed-2", subject: "영어2", tags: ["관계대명사", "독해"], text: "긴 문장에서 관계대명사가 생략된 경우를 찾았다. 해석이 빨라졌다.", hoursAgo: 28 },
  { userId: "seed-4", subject: "독서와작문", tags: ["주장", "근거"], text: "주장과 근거를 구분하는 연습을 했다. 내 글은 근거가 부족했다.", hoursAgo: 30 },
  { userId: "seed-3", subject: "세포와물질대사", tags: ["세포호흡", "발효"], text: "발효와 세포호흡의 차이를 배웠다. 산소가 있을 때와 없을 때를 비교했다.", hoursAgo: 32 },
  { userId: "seed-6", subject: "물질과에너지", tags: ["이상기체", "기체법칙"], text: "보일 법칙과 샤를 법칙을 하나의 식으로 합치는 과정을 이해했다.", hoursAgo: 34 },
  { userId: "seed-2", subject: "영어2", tags: ["관계대명사", "전치사"], text: "관계대명사 앞에 전치사가 오는 문장을 해석했다. in which가 특히 어려웠다.", hoursAgo: 36 },
  { userId: "seed-3", subject: "세포와물질대사", tags: ["세포호흡", "해당과정"], text: "해당과정이 세포질에서 일어난다는 걸 그림으로 확인했다.", hoursAgo: 38 },
];

export function buildRecall(
  logs: LogEntry[],
  userId: string,
  referenceDate = todayISO(),
): RecallItem[] {
  const seen = new Set<string>();
  const items: RecallItem[] = [];
  for (const log of logs) {
    if (log.userId !== userId) continue;
    const concept = log.stuck.trim();
    if (!concept || seen.has(concept)) continue;
    seen.add(concept);
    items.push({
      id: `recall-${items.length + 1}`,
      userId,
      concept,
      dueDate: referenceDate,
      interval: 1,
      ease: 2.5,
      reps: 0,
    });
  }
  return items;
}

export function seedState(): DemoState {
  const users = DEMO_USERS.map((user) => ({ ...user }));
  const now = Date.now();
  const userMap = new Map(users.map((user) => [user.id, user]));

  const anchor = DEMO_ANCHOR;
  const logs: LogEntry[] = LOG_SEED.map((log, index) => {
    const { dayOffset, ...rest } = log;
    return {
      ...rest,
      subject: normalizeSubject(rest.subject),
      id: `log-${String(index + 1).padStart(2, "0")}`,
      userId: "demo-main",
      isPublic: false,
      date: addDays(anchor, -dayOffset),
    };
  });

  const posts: Post[] = POST_SEED.map((post, index) => {
    const author = userMap.get(post.userId)!;
    return {
      id: `seed-post-${String(index + 1).padStart(2, "0")}`,
      userId: post.userId,
      nickname: author.nickname,
      grade: author.grade,
      subject: post.subject,
      text: post.text,
      tags: post.tags,
      createdAt: new Date(now - post.hoursAgo * 3600_000).toISOString(),
      cheers: Array.from({ length: index % 3 }, (_, offset) => {
        const cheerUser = users[(index + offset + 3) % users.length];
        return cheerUser.id;
      }),
      reports: 0,
    };
  });

  return {
    user: users[0],
    users,
    logs,
    posts,
    recall: buildRecall(logs, "demo-main", anchor),
    referenceDate: anchor,
  };
}

/** 기록 없이 시작하는 게스트. 시간표는 오늘 기준으로 실제 조회합니다. */
export function guestState(): DemoState {
  const base = seedState();
  const guest: User = {
    id: "guest",
    nickname: "게스트_기록러_0000",
    grade: 2,
    classNo: "5",
    track: "이과",
    region: DEMO_REGION,
  };
  return {
    ...base,
    user: guest,
    users: [guest, ...base.users],
    referenceDate: todayISO(),
  };
}
