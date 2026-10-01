from .base_collector import BaseCollector
import requests
import datetime
import time

class AppStoreCollector(BaseCollector):
    def __init__(self, app_id, countries, start_date, output_dir="data/raw"):
        super().__init__(output_dir)
        self.app_id = app_id
        self.countries = countries
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    def fetch(self):
        all_reviews = []
        for country in self.countries:
            print(f"[{self.name}] Fetching reviews for {country}...")
            # iTunes RSS feed for customer reviews
            url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={self.app_id}/sortBy=mostRecent/json"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    entries = data.get('feed', {}).get('entry', [])
                    # The first entry is often the app metadata, so we skip if it doesn't have a rating
                    for entry in entries:
                        if 'im:rating' not in entry:
                            continue
                            
                        # App Store dates are usually in ISO 8601 format
                        # Example: 2024-05-13T09:32:00-07:00
                        date_str = entry.get('updated', {}).get('label', '')
                        if not date_str:
                            continue
                            
                        # parse date
                        dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        # remove timezone info for comparison
                        dt = dt.replace(tzinfo=None)
                        
                        if dt >= self.start_date:
                            content = entry.get('content', {}).get('label', '')
                            rating = int(entry.get('im:rating', {}).get('label', '0'))
                            id_val = entry.get('id', {}).get('label', '')
                            
                            all_reviews.append({
                                "source": "app_store",
                                "url": f"https://apps.apple.com/{country}/app/id{self.app_id}?reviewId={id_val}",
                                "date": dt.strftime("%Y-%m-%d"),
                                "rating": rating,
                                "language_original": "en",
                                "original_text": content,
                                "country": country
                            })
                time.sleep(1)
            except Exception as e:
                print(f"[{self.name}] Error fetching {country}: {e}")
                
        return all_reviews
