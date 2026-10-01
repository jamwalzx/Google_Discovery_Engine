import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const dataPath = path.join(process.cwd(), '../data/artifacts/metrics.json');
    if (fs.existsSync(dataPath)) {
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
      return NextResponse.json(data);
    } else {
      return NextResponse.json({ error: 'Metrics file not found. Run Phase 4.' }, { status: 404 });
    }
  } catch (err) {
    return NextResponse.json({ error: 'Failed to load metrics' }, { status: 500 });
  }
}
