import json
import os
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, cohen_kappa_score

GOLD_SET_FILE = "gold_set.json"
LLM_OUTPUT_FILE = "../data/llm_output/extracted_records.json" # Will be generated in Phase 3

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def main():
    print("=== RecallScope: LLM Evaluation ===")
    gold_set = load_json(GOLD_SET_FILE)
    llm_output = load_json(LLM_OUTPUT_FILE)
    
    if not gold_set:
        print("Gold set not found. Please run labeling_tool.py first.")
        return
        
    if not llm_output:
        print(f"LLM output not found at {LLM_OUTPUT_FILE}. Please run Phase 3 first.")
        # For demonstration purposes, we will mock an evaluation if no Phase 3 data exists yet.
        print("\n--- Running Mock Evaluation (Waiting for Phase 3 Data) ---")
        y_true = ["yes", "yes", "no", "adjacent", "yes"]
        y_pred = ["yes", "adjacent", "no", "adjacent", "yes"]
        
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
        kappa = cohen_kappa_score(y_true, y_pred)
        
        print(f"Mock Relevance Metrics:")
        print(f"Precision: {precision:.2f}")
        print(f"Recall:    {recall:.2f}")
        print(f"F1 Score:  {f1:.2f}")
        print(f"Kappa:     {kappa:.2f}")
        return

    # Real evaluation logic
    print("Evaluating against Gold Set...")
    # Map by record ID/URL
    llm_dict = {item["url"]: item for item in llm_output}
    
    y_true_rel = []
    y_pred_rel = []
    
    y_true_stage = []
    y_pred_stage = []
    
    for record_id, gold_data in gold_set.items():
        if record_id in llm_dict:
            labels = gold_data["labels"]
            pred = llm_dict[record_id]
            
            y_true_rel.append(labels.get("relevance", "no"))
            y_pred_rel.append(pred.get("retrieval_related", "no"))
            
            y_true_stage.append(labels.get("failure_stage", "none"))
            y_pred_stage.append(pred.get("failure", {}).get("primary_stage", "none"))

    if not y_true_rel:
        print("No overlapping records between Gold Set and LLM output.")
        return

    # Calculate Relevance Metrics
    precision, recall, f1, _ = precision_recall_fscore_support(y_true_rel, y_pred_rel, average='weighted', zero_division=0)
    
    # Calculate Stage Metrics
    stage_acc = accuracy_score(y_true_stage, y_pred_stage)
    stage_kappa = cohen_kappa_score(y_true_stage, y_pred_stage)

    report = f"""=== Evaluation Report ===
Records evaluated: {len(y_true_rel)}

-- Relevance (Stage A) --
Precision: {precision:.2f}
Recall:    {recall:.2f}
F1 Score:  {f1:.2f}

-- Funnel Stage (Stage B) --
Accuracy:  {stage_acc:.2f}
Kappa:     {stage_kappa:.2f}
"""
    print(report)
    with open("eval_report.txt", "w") as f:
        f.write(report)
    print("Saved report to eval_report.txt")

if __name__ == "__main__":
    main()
