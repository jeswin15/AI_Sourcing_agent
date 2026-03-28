import feedparser
import time
from typing import List, Dict
from datetime import datetime, timedelta
from src.ingestion.base_collector import BaseCollector

class RSSCollector(BaseCollector):
    def __init__(self, source_name: str, feed_url: str):
        super().__init__(source_name)
        self.feed_url = feed_url

    def fetch_recent(self, days: int = 30) -> List[Dict]:
        """
        Fetches and returns feed entries from the last X days.
        """
        self.logger.info(f"Fetching RSS feed from {self.feed_url}")
        feed = feedparser.parse(self.feed_url)
        
        recent_entries = []
        now = datetime.now()
        threshold = now - timedelta(days=days)

        for entry in feed.entries:
            published_time = self._parse_date(entry)
            if published_time and published_time > threshold:
                recent_entries.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published_at": published_time.isoformat(),
                    "raw_content": str(entry)
                })
        
        self.logger.info(f"Found {len(recent_entries)} recent entries from {self.source_name}")
        return recent_entries

    def _parse_date(self, entry):
        """
        Helper to parse different RSS date formats.
        """
        # Try different common date attributes
        for attr in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, attr) and getattr(entry, attr):
                return datetime.fromtimestamp(time.mktime(getattr(entry, attr)))
        return None

# Factory to create specific RSS collectors
def get_rss_collectors() -> List[RSSCollector]:
    return [
        RSSCollector("TechCrunch", "https://techcrunch.com/category/startups/feed/"),
        RSSCollector("EU-Startups", "https://www.eu-startups.com/feed/"),
        RSSCollector("Sifted", "https://sifted.eu/feed/"),
        RSSCollector("YCombinator-Blog", "https://blog.ycombinator.com/feed/"),
        RSSCollector("Show-HN-RSS", "https://news.ycombinator.com/showrss")
    ]
