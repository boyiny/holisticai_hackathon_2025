import { NextResponse } from "next/server";

import { listEvalReports } from "@/lib/evalData";

export async function GET() {
  try {
    const evals = await listEvalReports();
    return NextResponse.json({ evals });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

