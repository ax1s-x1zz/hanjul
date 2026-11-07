import { NextResponse } from "next/server";

import { fetchTimetable, findNextSchoolDay } from "@/lib/neis";
import { DEMO_SCHOOL, TIMETABLE } from "@/lib/seed";
import type { Period } from "@/lib/types";

export const dynamic = "force-dynamic";

interface NearestSchoolDay {
  date: string;
  periods: Period[];
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const date = url.searchParams.get("date");

  if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return NextResponse.json(
      { error: "date must be YYYY-MM-DD" },
      { status: 400 },
    );
  }

  const grade = Number(url.searchParams.get("grade") ?? "2");
  const classNo = url.searchParams.get("class") ?? "5";
  const officeCode = process.env.NEIS_OFFICE_CODE ?? "J10";
  const schoolCode = process.env.NEIS_SCHOOL_CODE ?? "7530207";
  const requestParams = { officeCode, schoolCode, date, grade, classNo };

  const hasKey = Boolean(process.env.NEIS_KEY?.trim());

  if (!hasKey) {
    return NextResponse.json(
      {
        date,
        school: DEMO_SCHOOL,
        source: "sample",
        periods: TIMETABLE,
        message:
          "NEIS_KEY가 없어 샘플 시간표를 표시합니다. web/.env.local에 키를 넣으면 실제 시간표를 불러옵니다.",
      },
      { headers: { "Cache-Control": "no-store" } },
    );
  }

  const periods = await fetchTimetable(requestParams);

  if (periods === null) {
    return NextResponse.json(
      {
        date,
        school: DEMO_SCHOOL,
        source: "sample",
        periods: TIMETABLE,
        message:
          "NEIS에 연결하지 못해 샘플 시간표를 표시합니다. 잠시 후 다시 시도해주세요.",
      },
      { headers: { "Cache-Control": "no-store" } },
    );
  }

  if (!periods.length) {
    const nearest: NearestSchoolDay | null = await findNextSchoolDay(
      requestParams,
    );
    return NextResponse.json(
      {
        date,
        school: DEMO_SCHOOL,
        source: "neis",
        periods: [],
        nearest,
        message: "주말·휴업일에는 수업이 없습니다.",
      },
      {
        headers: {
          "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
        },
      },
    );
  }

  return NextResponse.json(
    {
      date,
      school: DEMO_SCHOOL,
      source: "neis",
      periods,
    },
    {
      headers: {
        "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
      },
    },
  );
}
