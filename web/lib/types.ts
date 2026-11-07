export type Activity = "들음" | "필기" | "문제풀이" | "질문" | "이해못함";

export interface User {
  id: string;
  nickname: string;
  grade: number;
  classNo: string;
  track: string;
  region: string;
}

export interface Period {
  period: number;
  subject: string;
  isEvent?: boolean;
}

export interface LogEntry {
  id: string;
  userId: string;
  date: string;
  period: number;
  subject: string;
  learned: string;
  activity: Activity;
  stuck: string;
  isPublic: boolean;
}

export interface Post {
  id: string;
  logId?: string;
  userId: string;
  nickname: string;
  grade: number;
  subject: string;
  text: string;
  tags: string[];
  createdAt: string;
  cheers: string[];
  reports: number;
  hidden?: boolean;
}

export interface RecallItem {
  id: string;
  userId: string;
  concept: string;
  dueDate: string;
  interval: number;
  ease: number;
  reps: number;
}

export interface DemoState {
  user: User;
  users: User[];
  logs: LogEntry[];
  posts: Post[];
  recall: RecallItem[];
}
