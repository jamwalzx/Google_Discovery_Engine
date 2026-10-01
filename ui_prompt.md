# Prompt for UI Generator (Google Stitch)

**Instructions for User:** Copy and paste the text below into Google Stitch (or your preferred AI UI generation tool) to have it generate the complete Next.js dashboard for RecallScope.

***

**System Role:** You are an expert frontend engineer and UI/UX designer. You build incredibly premium, modern, and highly interactive web applications. 

**Task:** I need you to build the frontend dashboard for **"RecallScope"**, an AI-powered Discovery Engine that analyzes user feedback regarding photo retrieval failures. 

**Tech Stack:** 
- Next.js (App Router)
- React
- Tailwind CSS
- Recharts (for data visualization)
- Lucide React (for icons)
- shadcn/ui (for core components like sliders, tables, and cards)

**Design System & Aesthetics:**
- **Theme:** Sleek, modern Dark Mode by default.
- **Style:** Use glassmorphism (translucent backgrounds with blur), subtle gradients (e.g., deep purples, blues, and near-blacks), and highly refined typography (Inter or similar).
- **Vibe:** It should feel like a premium, state-of-the-art internal Google tool used by product managers and engineers. It must NOT look basic or generic.

**Architecture & Layout:**
- **Sidebar Navigation:** Fixed on the left, containing links/tabs for: Overview, Funnel, Discovery Map, Opportunity, Query Lab, and Hypothesis Court.
- **Top Bar:** Simple header with the "RecallScope" logo/title and a global date-range filter.
- **Main Content Area:** A scrollable, responsive grid layout for the dashboard widgets.

**Data Requirements:**
For now, hardcode mock data for the visualizations. Assume the data matches this structure:
1. `funnel_metrics`: Percentages of users dropping off at stages F1 through F6.
2. `opportunity_metrics`: A list of objects containing `archetype`, `stage`, `frequency`, `severity`, `ai_fit`, and `strat_fit`.
3. `discovery_map`: A list of 2D coordinates `(x, y)` and a `cluster_id` representing semantic groupings of user feedback.

**Key Views to Implement (as interactive components):**

1. **The Funnel Leak Chart**
   - Use `Recharts` to build a visually striking Bar Chart or Funnel Chart showing drop-off rates across 6 stages (F1: Gave up, F2: Express, F3: Understand, F4: Recognize, F5: Refine, F6: Finish).

2. **Memory Lenses (Remembered vs Forgotten)**
   - Build a comparison visualization (like a Radar chart or side-by-side horizontal bar charts) showing what users remember (e.g., Time, Place, Person) versus what they forget (e.g., Exact Date, Keywords, Filename).

3. **Discovery Map (Interactive Scatter Plot)**
   - Use a `Recharts` ScatterChart to plot thousands of dots (UMAP coordinates). Color them by their `cluster_id`. This represents novel groupings of user pain points.
   - Include a custom tooltip that reveals a mock "user quote" when hovering over a dot.

4. **Opportunity Scoring Matrix (Dynamic)**
   - A beautiful Data Table listing different "Archetypes" (e.g., 'Fuzzy place memory', 'Utility photos').
   - Include **Interactive Sliders** at the top of the view for "AI Addressability Weight" and "Strategic Fit Weight".
   - As the user moves the sliders, the "Total Opportunity Score" in the table should dynamically recalculate and re-sort the table.

5. **Query Lab (Vocabulary Mismatch)**
   - A grid/table showing the "User's Attempted Query" side-by-side with the "Actual Photo Content", highlighting the vocabulary mismatch (e.g., User searched "receipt", photo contains text "invoice").

**Final Polish:**
- Add subtle micro-animations (e.g., hover states on cards lifting up slightly).
- Ensure all charts have dark-mode compatible grid lines and tooltips.
- Do not use placeholders for the design—write the actual Tailwind classes and React logic to make it look stunning immediately.
