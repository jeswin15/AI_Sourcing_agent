import requests
from typing import List, Dict
from datetime import datetime, timedelta
from src.ingestion.base_collector import BaseCollector

class HNCollector(BaseCollector):
    def __init__(self):
        super().__init__("HackerNews")
        self.api_url = "https://hn.algolia.com/api/v1/search"
        self.logger.info("Hacker News (Algolia) collector initialized")

    def fetch_recent(self, days: int = 7) -> List[Dict]:
        """
        Searches for 'Show HN' posts from the last X days.
        No API key required.
        """
        # Calculate timestamp for 'since'
        since_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Algolia search query
        params = {
            "tags": "show_hn",
            "numericFilters": f"created_at_i>{since_timestamp}",
            "hitsPerPage": 50
        }

        try:
            self.logger.info(f"Fetching Show HN posts since timestamp {since_timestamp}")
            response = requests.get(self.api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', [])
                
                results = []
                for hit in hits:
                    results.append({
                        "title": hit.get('title', ''),
                        "link": hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        "summary": hit.get('story_text', '') or f"Show HN post with {hit.get('points')} points.",
                        "published_at": datetime.fromtimestamp(hit.get('created_at_i')).isoformat(),
                        "points": hit.get('points'),
                        "author": hit.get('author')
                    })
                
                self.logger.info(f"Found {len(results)} recent Show HN posts")
                return results
            else:
                self.logger.error(f"HN Algolia API failed: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching HN data: {e}")
            return []
