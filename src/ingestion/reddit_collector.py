import feedparser
from typing import List, Dict
from datetime import datetime, timedelta
from src.ingestion.base_collector import BaseCollector

class RedditRSSCollector(BaseCollector):
    def __init__(self):
        super().__init__("Reddit")
        # Subreddits to track via RSS
        self.subreddits = ["startups", "entrepreneur", "sideproject"]
        self.logger.info("Reddit RSS collector initialized")

    def fetch_recent(self, days: int = 7) -> List[Dict]:
        """
        Fetches submissions from various subreddits using RSS (.rss).
        No API key required.
        """
        all_submissions = []
        now = datetime.now()
        threshold = now - timedelta(days=days)

        for sub_name in self.subreddits:
            url = f"https://www.reddit.com/r/{sub_name}/new/.rss"
            self.logger.info(f"Fetching RSS from r/{sub_name}")
            
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                published_time = self._parse_date(entry)
                if published_time and published_time > threshold:
                    all_submissions.append({
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", ""),
                        "published_at": published_time.isoformat(),
                        "subreddit": sub_name,
                        "author": entry.get("author", "Unknown")
                    })

        self.logger.info(f"Found {len(all_submissions)} recent submissions from Reddit RSS")
        return all_submissions

    def _parse_date(self, entry):
        import time
        for attr in ['updated_parsed', 'published_parsed']:
            if hasattr(entry, attr) and getattr(entry, attr):
                return datetime.fromtimestamp(time.mktime(getattr(entry, attr)))
        return None
