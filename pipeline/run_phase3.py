import os
from dotenv import load_dotenv
from llm_pipeline import run_stage_a, run_stage_b, run_stage_c, export_to_sqlite

def main():
    print("=== RecallScope: Phase 3 Full Run (LLM Pipeline) ===")
    
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not found in environment. Please set it in .env")
        return
        
    # 1. Stage A: Filter
    run_stage_a(
        input_file="data/cleaned/cleaned_dataset.json",
        output_file="data/llm_output/stage_a_filtered.json"
    )
    
    # 2. Stage B: Extraction
    run_stage_b(
        input_file="data/llm_output/stage_a_filtered.json",
        output_file="data/llm_output/stage_b_extracted.json"
    )
    
    # 3. Stage C: Clustering
    run_stage_c(
        input_file="data/llm_output/stage_b_extracted.json",
        output_file="data/llm_output/stage_c_enriched.json"
    )
    
    # 4. DB Export
    export_to_sqlite(
        input_file="data/llm_output/stage_c_enriched.json",
        db_path="data/artifacts/recallscope.db"
    )
    
    print("\n=== Phase 3 Complete ===")

if __name__ == "__main__":
    main()
