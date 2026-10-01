from analytics.compute_metrics import compute_metrics

def main():
    print("=== RecallScope: Phase 4 Analytics Modules ===")
    
    # Run the metric computations
    compute_metrics(
        db_path="data/artifacts/recallscope.db",
        output_file="data/artifacts/metrics.json"
    )
    
    print("\n=== Phase 4 Complete ===")

if __name__ == "__main__":
    main()
