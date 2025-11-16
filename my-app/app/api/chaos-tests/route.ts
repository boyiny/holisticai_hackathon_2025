import { NextResponse } from "next/server";

import { listChaosReports } from "@/lib/chaosData";

export async function GET() {
  try {
    const reports = await listChaosReports();
    return NextResponse.json({ reports });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

