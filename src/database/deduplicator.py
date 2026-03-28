import re
from typing import List, Dict, Optional
from fuzzywuzzy import fuzz
from urllib.parse import urlparse

class Deduplicator:
    def __init__(self, threshold: int = 85):
        self.threshold = threshold

    def normalize_name(self, name: str) -> str:
        """
        Normalizes a company name for better comparison.
        - Lowercase
        - Remove special characters
        - Remove common suffixes (Inc, LLC, Corp)
        """
        name = name.lower().strip()
        # Remove special characters
        name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        # Remove common suffixes
        suffixes = r'\b(inc|llc|corp|ltd|co|gmbh|solutions|tech|technology|labs|systems)\b'
        name = re.sub(suffixes, '', name).strip()
        return name

    def extract_domain(self, url: str) -> Optional[str]:
        """
        Extracts the main domain from a URL.
        """
        if not url:
            return None
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            domain = domain.replace('www.', '')
            return domain.lower()
        except Exception:
            return None

    def is_duplicate(self, new_item: Dict, existing_items: List[Dict]) -> bool:
        """
        Checks if the new item is a duplicate of any existing item.
        Check logic:
        1. Exact domain match (if available)
        2. Normalized title match
        3. Fuzzy title match
        """
        new_name = self.normalize_name(new_item.get("title", ""))
        new_domain = self.extract_domain(new_item.get("link", "")) or self.extract_domain(new_item.get("website", ""))

        for item in existing_items:
            # 1. Domain match
            existing_domain = self.extract_domain(item.get("link", "")) or self.extract_domain(item.get("website", ""))
            if new_domain and existing_domain and new_domain == existing_domain:
                return True

            # 2. Exact normalized title match
            existing_name = self.normalize_name(item.get("title", ""))
            if new_name == existing_name:
                return True

            # 3. Fuzzy match
            similarity = fuzz.ratio(new_name, existing_name)
            if similarity >= self.threshold:
                return True

        return False
