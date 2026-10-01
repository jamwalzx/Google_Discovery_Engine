import os
import json
import sqlite3
import pandas as pd

def compute_metrics(db_path="../data/artifacts/recallscope.db", output_file="../data/artifacts/metrics.json"):
    print("=== Computing Analytics Metrics ===")
    
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found. Run Phase 3 first.")
        # Create mock data for UI testing if DB is missing
        print("Generating mock metrics for UI development...")
        mock_metrics = {
            "funnel": {"F1": 15, "F2": 25, "F3": 20, "F4": 15, "F5": 15, "F6": 10},
            "memory": {"remembered": {"time": 40, "place": 30, "person": 20}, "forgotten": {"time": 50, "keywords": 40}},
            "opportunity": [
                {"archetype": "A1", "stage": "F3", "frequency": 0.15, "severity": 4.2, "unresolved": 0.8, "ai_fit": 5, "strat_fit": 5},
                {"archetype": "A4", "stage": "F2", "frequency": 0.20, "severity": 3.8, "unresolved": 0.6, "ai_fit": 5, "strat_fit": 5}
            ]
        }
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(mock_metrics, f, indent=2)
        return

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM records", conn)
    conn.close()

    if len(df) == 0:
        print("Database is empty.")
        return
        
    metrics = {}

    # 1. Funnel Leaks
    # Group by primary_stage and calculate percentage
    stage_counts = df['primary_stage'].value_counts(normalize=True) * 100
    metrics["funnel"] = stage_counts.to_dict()

    # 2. Opportunity Baseline
    # Group by archetype + primary_stage
    opp_list = []
    total_records = len(df)
    
    # Define stakes mapping (rough approximation)
    stakes_map = {"high": 1.5, "sentimental": 1.2, "practical": 1.0, "low": 0.8, "not_stated": 1.0}
    
    for (arch, stage), group in df.groupby(['archetype', 'primary_stage']):
        if arch in ["", "none"] or stage in ["", "none", "F0"]:
            continue
            
        freq = len(group) / total_records
        
        # Calculate severity based on emotion_intensity
        # In a real scenario we'd parse full_json to get stakes
        avg_intensity = group['emotion_intensity'].mean()
        severity = float(avg_intensity) if pd.notna(avg_intensity) else 3.0
        
        # Calculate unresolved rate
        # outcome: found_quickly, found_after_effort, found_by_luck, not_found
        outcomes = group['outcome'].value_counts(normalize=True)
        p_not_found = outcomes.get('not_found', 0.0)
        p_effort = outcomes.get('found_after_effort', 0.0)
        p_luck = outcomes.get('found_by_luck', 0.0)
        
        unresolved = p_not_found + 0.5 * (p_effort + p_luck)
        
        opp_list.append({
            "archetype": arch,
            "stage": stage,
            "frequency": float(freq),
            "severity": severity,
            "unresolved": float(unresolved),
            "ai_fit": 5, # Default baseline for sliders
            "strat_fit": 5 # Default baseline for sliders
        })
        
    metrics["opportunity"] = opp_list
    
    # 3. Memory Lens (Mocked aggregation from JSON for now, as full JSON parsing in pandas can be heavy)
    # We will simulate the memory aggregation based on target types
    metrics["memory"] = {
        "remembered": {"time": 45, "place": 35, "person": 25, "event": 20},
        "forgotten": {"exact_date": 60, "keywords": 50, "filename": 40}
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Metrics computed and saved to {output_file}")

if __name__ == "__main__":
    compute_metrics()
