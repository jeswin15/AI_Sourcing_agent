import requests
from typing import List, Dict
from datetime import datetime, timedelta
from src.ingestion.base_collector import BaseCollector
from src.utils.config import Config

class ProductHuntCollector(BaseCollector):
    def __init__(self):
        super().__init__("ProductHunt")
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.api_token = Config.PRODUCT_HUNT_API_KEY
        self.logger.info("Product Hunt collector initialized")

    def fetch_recent(self, days: int = 1) -> List[Dict]:
        """
        Fetches products from Product Hunt GraphQL API.
        """
        if not self.api_token:
            self.logger.warning("Product Hunt API token not provided, skipping...")
            return []

        # Calculate ISO date for query
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

        query = f"""
        query {{
          posts(order: FEATURED_AT, postedAfter: "{since_date}") {{
            edges {{
              node {{
                id
                name
                tagline
                description
                votesCount
                slug
                website
              }}
            }}
          }}
        }}
        """

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}',
        }

        try:
            self.logger.info(f"Fetching Product Hunt posts since {since_date}")
            response = requests.post(self.api_url, headers=headers, json={'query': query})
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('posts', {}).get('edges', [])
                
                results = []
                for post in posts:
                    node = post['node']
                    results.append({
                        "title": node['name'],
                        "link": f"https://www.producthunt.com/posts/{node['slug']}",
                        "summary": f"{node['tagline']}\n\n{node.get('description', '')}",
                        "published_at": datetime.now().isoformat(), # PH API v2 posts don't always have simple created_at in basic query
                        "votes": node['votesCount'],
                        "website": node.get('website', '')
                    })
                
                self.logger.info(f"Found {len(results)} recent posts from Product Hunt")
                return results
            else:
                self.logger.error(f"Product Hunt API failed: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching Product Hunt data: {e}")
            return []
