from .base_collector import BaseCollector
import praw
import datetime
import os
from dotenv import load_dotenv

class RedditCollector(BaseCollector):
    def __init__(self, subreddits, keywords, start_date, output_dir="data/raw"):
        super().__init__(output_dir)
        load_dotenv()
        self.subreddits = subreddits
        self.keywords = keywords
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "RecallScope:v1.0 (by /u/researcher)")
        
        self.reddit = None
        if client_id and client_secret:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
        else:
            print(f"[{self.name}] WARNING: Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET in .env")

    def fetch(self):
        if not self.reddit:
            print(f"[{self.name}] Skipping Reddit collection due to missing credentials.")
            return []
            
        all_posts = []
        for subreddit_name in self.subreddits:
            print(f"[{self.name}] Searching r/{subreddit_name}...")
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                # To maximize coverage, we search for each keyword
                for keyword in self.keywords:
                    # Search limit 100 per keyword
                    for submission in subreddit.search(keyword, limit=100, sort='new'):
                        dt = datetime.datetime.fromtimestamp(submission.created_utc)
                        if dt >= self.start_date:
                            content = f"{submission.title}\n{submission.selftext}"
                            all_posts.append({
                                "source": "reddit",
                                "url": f"https://www.reddit.com{submission.permalink}",
                                "date": dt.strftime("%Y-%m-%d"),
                                "rating": None,
                                "language_original": "en",
                                "original_text": content,
                                "subreddit": subreddit_name,
                                "keyword": keyword
                            })
            except Exception as e:
                print(f"[{self.name}] Error searching r/{subreddit_name}: {e}")
                
        return all_posts
