from github import Github
from typing import List, Dict
from datetime import datetime, timedelta
from src.ingestion.base_collector import BaseCollector
from src.utils.config import Config

class GitHubCollector(BaseCollector):
    def __init__(self):
        super().__init__("GitHub")
        try:
            self.github = Github(Config.GITHUB_TOKEN)
            self.logger.info("GitHub collector initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize GitHub collector: {e}")
            self.github = None

    def fetch_recent(self, days: int = 7) -> List[Dict]:
        """
        Searches for new repositories tagged with 'startup', 'launched', or 'mvp'.
        """
        if not self.github:
            self.logger.warning("GitHub token not provided, skipping...")
            return []

        # Construct search query
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        queries = [
            f"created:>{since_date} startup",
            f"created:>{since_date} mvp",
            f"created:>{since_date} launched"
        ]

        all_repos = []
        for query in queries:
            try:
                self.logger.info(f"Searching GitHub with query: {query}")
                results = self.github.search_repositories(query, sort="stars", order="desc")
                
                # Fetch top 20 for each query
                for repo in results[:20]:
                    if repo.stargazers_count > 5:  # Basic filter for quality
                        all_repos.append({
                            "title": repo.name,
                            "link": repo.html_url,
                            "summary": repo.description if repo.description else "No description available",
                            "published_at": repo.created_at.isoformat(),
                            "stars": repo.stargazers_count,
                            "language": repo.language
                        })
            except Exception as e:
                self.logger.error(f"Error searching GitHub with query '{query}': {e}")
                continue

        self.logger.info(f"Found {len(all_repos)} recent repositories from GitHub")
        return all_repos
