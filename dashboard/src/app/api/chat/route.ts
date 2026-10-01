import { GoogleGenAI, Type } from '@google/genai';
import Database from 'better-sqlite3';
import { NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs';

export async function POST(req: Request) {
  try {
    const { message } = await req.json();
    if (!message) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
    
    // We will attempt to connect to the DB
    const dbPath = path.join(process.cwd(), '../pipeline/data/artifacts/recallscope.db');
    let db: any = null;
    let schemaStr = "No database found. Tell the user they need to run Phase 3 to generate the SQLite database.";
    
    if (fs.existsSync(dbPath)) {
      db = new Database(dbPath, { readonly: true });
      schemaStr = "The database has tables: archetypes, memory_clues, raw_feedback. Query them to answer the user.";
    }

    const query_database = (query: string) => {
        if (!db) return "Error: Database file not found.";
        try {
            return JSON.stringify(db.prepare(query).all());
        } catch (e: any) {
            return `Error executing query: ${e.message}`;
        }
    };

    const response = await ai.models.generateContent({
      model: 'gemini-1.5-flash',
      contents: message,
      config: {
        systemInstruction: `You are the RecallScope Evidence Assistant. You help product managers understand photo retrieval failures. ${schemaStr}`,
        tools: [{
          functionDeclarations: [{
            name: 'query_database',
            description: 'Executes a SQL SELECT query against the local SQLite database.',
            parameters: {
              type: Type.OBJECT,
              properties: {
                query: {
                  type: Type.STRING,
                  description: 'A valid SQL query.'
                }
              },
              required: ['query']
            }
          }]
        }]
      }
    });

    // Simple handling: if the model decided to call the tool
    if (response.functionCalls && response.functionCalls.length > 0) {
        const call = response.functionCalls[0];
        if (call.name === 'query_database' && typeof call.args === 'object' && call.args !== null) {
            // @ts-ignore
            const sqlQuery = call.args.query as string;
            const toolResult = query_database(sqlQuery);
            
            // Send result back to model to get final answer
            const finalResponse = await ai.models.generateContent({
              model: 'gemini-1.5-flash',
              contents: [
                { role: 'user', parts: [{ text: message }] },
                { role: 'model', parts: [{ functionCall: call }] },
                { role: 'function', parts: [{ functionResponse: { name: call.name, response: { result: toolResult } } }] }
              ]
            });
            return NextResponse.json({ reply: finalResponse.text });
        }
    }

    return NextResponse.json({ reply: response.text });
  } catch (err: any) {
    console.error(err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
