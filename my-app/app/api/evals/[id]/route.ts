import { NextResponse } from "next/server";

import { loadEvalReport } from "@/lib/evalData";

type Params = {
  params: {
    id: string;
  };
};

export async function GET(_: Request, { params }: Params) {
  try {
    const report = await loadEvalReport(params.id);
    return NextResponse.json(report);
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

