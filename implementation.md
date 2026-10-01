# RecallScope: Phasewise Implementation Plan

Based on the project context (`Ai_engine.md`) and architecture (`architecture.md`), this document outlines the step-by-step implementation plan for building the RecallScope AI Discovery Engine.

---

### Phase 1: Data Collection & Cleaning
**Goal**: Ingest raw user feedback and clean it for LLM processing.
- Setup `config/sources.yaml` with seed keywords.
- Implement abstract collector interface in Python.
- Build specific collectors: Google Play Scraper, App Store RSS/JSON, Reddit API (PRAW).
- Implement cleaning scripts: language translation, deduplication, and caching of raw responses.
- **Output**: Raw datasets saved locally.

### Phase 2: Evaluation & Labeling
**Goal**: Create a gold standard for LLM accuracy testing.
- Build a lightweight local labeling interface (e.g., Streamlit or CLI) for the evaluator to label 100-150 records.
- Define evaluation metrics (Precision, Recall, F1 for relevance; Accuracy/Kappa for funnel stages).
- Draft and version initial prompts for Stage A (Filtering) and Stage B (Extraction).
- **Output**: `eval/` directory containing the gold set and scoring logic.

### Phase 3: Full Run (LLM Pipeline)
**Goal**: Process the collected data into structured evidence.
- **Stage A**: Run the relevance filter via a fast LLM (Haiku/Flash).
- **Stage B**: Run structured extraction via a strong LLM (Sonnet/Pro) enforcing strict JSON schemas (using Pydantic). Validate all verbatim quotes.
- **Stage C**: Generate embeddings for the extracted records. Run UMAP for dimensionality reduction and HDBSCAN for clustering to find novel archetypes.
- **Output**: Precomputed data artifacts (JSON, SQLite database, and Vector index) stored in the `data/` directory.

### Phase 4: Analytics Modules
**Goal**: Compute all required deterministic metrics.
- Implement Python logic to compute:
  - Funnel leak sizes
  - Remembered vs. Forgotten statistics
  - Query Lab / Vocabulary mismatch tables
  - Opportunity scores based on the weighted rubric
- Ensure outputs are structured correctly for the Next.js frontend to consume without heavy client-side computation.

### Phase 5: UI/UX Development
**Goal**: Build the static/serverless web application.
- Initialize Next.js (App Router) + TypeScript + Tailwind + `shadcn/ui`.
- Create data loaders to read from the local SQLite/JSON artifacts.
- Implement core views:
  - Overview Dashboard
  - Funnel Explorer & Memory Map
  - Opportunity Board (with sliders for weights)
  - Discovery Map (UMAP visualization using Canvas/WebGL)
  - Evidence Library (filterable table)
- Ensure all numbers are clickable, opening an "Evidence Drawer".

### Phase 6: Conversational & Live Features
**Goal**: Add interactive AI layers to the application.
- **Ask the Evidence (`/api/chat`)**: Implement a RAG API route equipped with `sql_query` and `semantic_search` tools to query the precomputed data. Enforce inline citation chips.
- **Try It Live (`/api/try-live`)**: Wrap the Python Stage A/B logic into an API endpoint to allow live testing of pasted text. Include rate limiting and budget caps.

### Phase 7: Polish and Deploy
**Goal**: Ensure production readiness and public accessibility.
- Conduct a strict visual accessibility audit (Color-blind safe, WCAG AA contrast).
- Performance optimization (load times < 3s, chat streaming < 2s).
- Setup deployment on Vercel (free tier, no login required).
- Finalize documentation (`README.md`), the Method & Trust page, and a 3-minute demo script.

---

## Verification Plan

### Automated Tests
- `pytest` for the Python pipeline (schema validation, deduplication logic, quote verbatim checks).
- Unit tests for the Opportunity scoring math.

### Manual Verification
- Review the exported SVG/PNG workflow diagram.
- Ensure the deployed Vercel URL functions seamlessly on mobile devices.
- Verify that the chat interface correctly answers the 9 acceptance-test questions listed in the problem statement.
