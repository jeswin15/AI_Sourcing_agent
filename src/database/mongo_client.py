from pymongo import MongoClient
from typing import List, Dict, Optional
from datetime import datetime
from src.utils.config import Config
import logging
import pymongo

class MongoDBClient:
    def __init__(self):
        self.logger = logging.getLogger("database.mongo")
        self.logger.setLevel(logging.INFO)
        try:
            self.client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
            # Check connection
            self.client.server_info()
            self.db = self.client[Config.MONGO_DB_NAME]
            self.startups = self.db.startups
            self.feedback = self.db.feedback
            self.is_connected = True
            self.logger.info(f"Connected to MongoDB Atlas: {Config.MONGO_DB_NAME}")
        except Exception as e:
            self.logger.warning(f"Could not connect to MongoDB, using In-Memory Storage for Demo: {e}")
            self.client = None
            self.db = None
            self.is_connected = False
            self.in_memory_startups = []
            self.in_memory_feedback = []

    def insert_startup(self, startup: Dict) -> bool:
        """
        Inserts a new startup into the database.
        Check for internal duplicates before inserting (by domain/normalized name).
        """
        if not self.is_connected:
            # Check for duplicates in memory
            for item in self.in_memory_startups:
                if item.get("link") == startup.get("link"):
                    return False
            self.in_memory_startups.append(startup)
            self.logger.info(f"Saved to In-Memory: {startup.get('company_name')}")
            return True

        # Check if already exists in DB
        existing = self.startups.find_one({"link": startup.get("link")})
        if existing:
            return False

        try:
            self.startups.insert_one(startup)
            return True
        except Exception as e:
            self.logger.error(f"Error inserting startup: {e}")
            return False

    def get_all_startups(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieves startups from the database or in-memory storage.
        """
        if not self.is_connected:
            return self.in_memory_startups
        
        try:
            cursor = self.startups.find(filters or {})
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error fetching startups: {e}")
            return []

    def get_evaluated_startups(self, min_score: int = 70) -> List[Dict]:
        """
        Retrieves startups that have been evaluated and have a score >= min_score.
        """
        return self.get_all_startups({"confidence_score": {"$gte": min_score}})

    def update_startup_status(self, link: str, status: str):
        """
        Updates the status of a startup (Pending, Saved, Ignored, Progressed).
        """
        if not self.client:
            return
        
        try:
            self.startups.update_one({"link": link}, {"$set": {"status": status}})
            self.logger.info(f"Updated status for {link} to {status}")
        except Exception as e:
            self.logger.error(f"Error updating status for {link}: {e}")

    def add_feedback(self, link: str, action: str, reason: Optional[str] = None):
        """
        Stores user feedback for a startup/link.
        Actions: Ignore, Save, Progress, N/A
        """
        if not self.client:
            return

        feedback_entry = {
            "link": link,
            "action": action,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        try:
            self.feedback.insert_one(feedback_entry)
        except Exception as e:
            self.logger.error(f"Error adding feedback: {e}")

    def get_all_feedback(self) -> List[Dict]:
        if not self.is_connected:
            return self.in_memory_feedback
        try:
            return list(self.feedback.find({}))
        except Exception as e:
            self.logger.error(f"Error fetching feedback: {e}")
            return []
