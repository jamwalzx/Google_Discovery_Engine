import { GoogleGenAI, Type } from '@google/genai';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { text } = await req.json();
    if (!text) {
      return NextResponse.json({ error: 'Text input is required' }, { status: 400 });
    }

    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
    
    // Simulate Stage A (Filter) & Stage B (Extract) in one go
    const response = await ai.models.generateContent({
      model: 'gemini-1.5-flash',
      contents: `Analyze the following user feedback about a failed photo search: "${text}"`,
      config: {
        systemInstruction: "You are the RecallScope Extraction Engine. Analyze the user's feedback. Determine if it is relevant to photo retrieval. If so, extract the memory dimensions: temporal (time context), spatial (location), entities (people/objects), and the perceived failure reason.",
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            is_relevant: { type: Type.BOOLEAN, description: "True if the text describes a photo retrieval failure" },
            temporal: { type: Type.STRING, description: "Any time-related context (e.g. 'last summer')" },
            spatial: { type: Type.STRING, description: "Any location-related context (e.g. 'at the beach')" },
            entities: { type: Type.ARRAY, items: { type: Type.STRING }, description: "People, pets, or objects mentioned" },
            failure_reason: { type: Type.STRING, description: "Why the search failed" }
          },
          required: ["is_relevant"]
        }
      }
    });

    return NextResponse.json(JSON.parse(response.text || '{}'));
  } catch (err: any) {
    console.error(err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
