from .base_collector import BaseCollector
from google_play_scraper import reviews, Sort
import datetime
import time

class PlayStoreCollector(BaseCollector):
    def __init__(self, app_id, countries, start_date, output_dir="data/raw"):
        super().__init__(output_dir)
        self.app_id = app_id
        self.countries = countries
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    def fetch(self):
        all_reviews = []
        for country in self.countries:
            print(f"[{self.name}] Fetching reviews for {country}...")
            try:
                # Fetching recent reviews (count=1000 is usually the max for one request, but we can iterate or use continuation tokens if needed, here we simplify)
                # For MVP, we fetch top 2000 reviews per country
                result, _ = reviews(
                    self.app_id,
                    lang='en', # default to en, langdetect will handle others if we pass other langs
                    country=country,
                    sort=Sort.NEWEST,
                    count=1000
                )
                
                for r in result:
                    # filter by date
                    if r['at'] >= self.start_date:
                        all_reviews.append({
                            "source": "play_store",
                            "url": f"https://play.google.com/store/apps/details?id={self.app_id}&reviewId={r['reviewId']}",
                            "date": r['at'].strftime("%Y-%m-%d"),
                            "rating": r['score'],
                            "language_original": "en", # assuming en, cleaner will update
                            "original_text": r['content'],
                            "country": country
                        })
                time.sleep(1) # rate limit
            except Exception as e:
                print(f"[{self.name}] Error fetching {country}: {e}")
                
        return all_reviews
