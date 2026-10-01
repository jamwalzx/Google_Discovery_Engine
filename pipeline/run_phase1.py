import os
import yaml
from collectors import PlayStoreCollector, AppStoreCollector, RedditCollector
from cleaners import Cleaner

def load_config():
    config_path = os.path.join("config", "sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    print("=== RecallScope: Phase 1 Data Collection & Cleaning ===")
    
    # 1. Load config
    config = load_config()
    start_date = config.get("date_range", {}).get("start", "2023-01-01")
    keywords = config.get("keywords", [])
    
    # Create output dirs
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/cleaned", exist_ok=True)
    
    # 2. Run Collectors
    print("\n--- Running Collectors ---")
    
    # Play Store
    ps_config = config.get("play_store", {})
    if ps_config:
        ps_collector = PlayStoreCollector(
            app_id=ps_config["app_id"], 
            countries=ps_config["countries"],
            start_date=start_date
        )
        ps_collector.run()

    # App Store
    as_config = config.get("app_store", {})
    if as_config:
        as_collector = AppStoreCollector(
            app_id=as_config["app_id"], 
            countries=as_config["countries"],
            start_date=start_date
        )
        as_collector.run()

    # Reddit
    reddit_config = config.get("subreddits", [])
    if reddit_config:
        reddit_collector = RedditCollector(
            subreddits=reddit_config,
            keywords=keywords,
            start_date=start_date
        )
        reddit_collector.run()

    # 3. Clean Data
    print("\n--- Cleaning Data ---")
    cleaner = Cleaner()
    cleaner.process()

    print("\n=== Phase 1 Complete ===")

if __name__ == "__main__":
    main()
