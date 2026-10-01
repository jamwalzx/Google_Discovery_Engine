# RecallScope: AI-Powered Photo Retrieval Discovery Engine

RecallScope is an analytical pipeline and dashboard designed to discover, categorize, and extract meaning from user complaints regarding photo retrieval failures. It bridges the semantic gap between what users vividly remember (e.g., atmosphere, sensory cues, episodic context) and what systems actually index (literal nouns, timestamps, metadata bounding boxes).

## Project Architecture

This project is divided into 7 structured phases:

1. **Data Collection**: Scalable ingesters for App Store, Google Play, and Reddit to capture raw user frustration.
2. **Evaluation & Labeling**: Local Streamlit interface to establish a ground-truth dataset and evaluation metrics (Precision, Recall, F1).
3. **LLM Pipeline (The Engine)**:
   - **Stage A**: Gemini-Flash quickly classifies if a review relates to photo retrieval.
   - **Stage B**: Gemini-Pro enforces strict JSON extraction (Pydantic) to mine temporal, spatial, and semantic cues.
   - **Stage C**: Unsupervised clustering (UMAP + HDBSCAN) creates embeddings of failure archetypes.
4. **Analytics Modules**: Deterministic Python scripts that aggregate pipeline output into quantifiable metrics, funnel leak percentages, and opportunity scores.
5. **Web Dashboard**: A fully static, Vercel-ready Next.js application that visualizes the engine's intelligence.
6. **Conversational Features**: Next.js API Routes (`/api/chat` and `/api/try-live`) powered by the Google GenAI Node SDK, allowing stakeholders to use RAG to talk to the evidence database or run the Stage A/B extraction logic live in the browser.
7. **Polish & Deploy**: Built to strict accessibility standards, seamlessly deployable to Vercel without requiring heavy backend servers.

## Method & Trust

RecallScope employs a multi-tiered validation approach to ensure the AI's conclusions are trustworthy:
- **Verbatim Evidence**: Every calculated metric and generated archetype is fully traceable back to the raw, verbatim user quote. No hallucinated problems.
- **Deterministic Scoring**: While LLMs extract the data, the opportunity matrix uses deterministic, transparent rubric math based on frequency and severity.
- **SQL RAG Tooling**: The Chat agent does not guess metrics; it executes raw SQL `SELECT` queries against the generated `recallscope.db` SQLite database to answer your analytical questions.

## Quick Start

### 1. Run the Python Pipeline
```bash
cd pipeline
pip install -r requirements.txt
# Populate your .env with GEMINI_API_KEY
python run_phase1.py # Ingests Data
python run_phase3.py # Runs LLM Engine -> generates recallscope.db
python run_phase4.py # Computes Metrics -> generates metrics.json
```

### 2. Boot the Dashboard
```bash
cd dashboard
npm install
npm run dev
```
Open `http://localhost:3000` to view the beautiful interactive dashboard, complete with dynamic Funnel Leak analysis and the Live RAG Sandbox!

---
*Developed as a capstone project for analyzing Google Photos search disconnects.*
