import { NextResponse } from "next/server";

import { fetchTimetable } from "@/lib/neis";

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

  const periods = await fetchTimetable({
    officeCode: process.env.NEIS_OFFICE_CODE ?? "J10",
    schoolCode: process.env.NEIS_SCHOOL_CODE ?? "7530207",
    date,
    grade,
    classNo,
  });

  if (!periods) {
    return NextResponse.json({
      periods: [],
      demo: true,
      message: "NEIS_KEY가 없어 데모 시간표를 사용합니다.",
    });
  }

  return NextResponse.json({ periods, demo: false });
}
