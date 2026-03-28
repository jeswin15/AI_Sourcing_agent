from abc import ABC, abstractmethod
from typing import List, Dict
import logging

class BaseCollector(ABC):
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"collector.{source_name}")
        self.logger.setLevel(logging.INFO)

    @abstractmethod
    def fetch_recent(self, days: int = 30) -> List[Dict]:
        """
        Fetch recent data from the source.
        Returns a list of dicts with raw data.
        """
        pass

    def normalize(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Subclasses can implement specific normalization.
        Default adds source and ensures basic keys.
        """
        normalized_data = []
        for item in raw_data:
            item["source"] = self.source_name
            normalized_data.append(item)
        return normalized_data
