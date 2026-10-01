import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const dataPath = path.join(process.cwd(), '../pipeline/data/artifacts/metrics.json');
    if (fs.existsSync(dataPath)) {
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
      return NextResponse.json(data);
    } else {
      // Return beautiful mock data so the dashboard renders even without the pipeline
      return NextResponse.json({
        funnel: { F1: 100, F2: 85, F3: 42, F4: 38, F5: 30, F6: 12 },
        opportunity: [
          { archetype: "Fuzzy Place & Atmospheric Memory", stage: "F3", frequency: 0.25, severity: 4.8, ai_fit: 85, strat_fit: 90 },
          { archetype: "Utility & Document Text", stage: "F2", frequency: 0.18, severity: 3.2, ai_fit: 95, strat_fit: 60 },
          { archetype: "Fleeting Serendipity", stage: "F4", frequency: 0.15, severity: 4.1, ai_fit: 40, strat_fit: 50 },
          { archetype: "Co-temporal Events", stage: "F3", frequency: 0.22, severity: 3.9, ai_fit: 75, strat_fit: 80 }
        ],
        memory: {
          remembered: { "Spatial Context": 0.82, "Temporal Context": 0.75, "Emotional State": 0.65 },
          forgotten: { "Exact Date": 0.95, "Specific Nouns": 0.88, "Visual Composition": 0.72 }
        }
      });
    }
  } catch (err) {
    return NextResponse.json({ error: 'Failed to load metrics' }, { status: 500 });
  }
}
