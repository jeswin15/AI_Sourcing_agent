"""
JSON-file based storage for the demo.
Replaces MongoDB so both the agent and the dashboard can share data
via a single JSON file on disk.
"""
import json
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Store data next to the project root
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
STARTUPS_FILE = os.path.join(DATA_DIR, "startups.json")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")

logger = logging.getLogger("database.json_store")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _read_json(filepath: str) -> List[Dict]:
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _write_json(filepath: str, data: List[Dict]):
    _ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


class JSONStore:
    """Drop-in replacement for MongoDBClient using local JSON files."""

    def __init__(self):
        _ensure_data_dir()
        logger.info(f"JSON Store initialized. Data directory: {DATA_DIR}")

    # ── Startups ──────────────────────────────────────────────

    def insert_startup(self, startup: Dict) -> bool:
        startups = _read_json(STARTUPS_FILE)
        # Deduplicate by link
        for existing in startups:
            if existing.get("link") == startup.get("link"):
                return False
        # Give each startup a stable id for Streamlit button keys
        startup["_id"] = f"s_{len(startups)}_{datetime.now().strftime('%H%M%S')}"
        startup.setdefault("status", "Pending")
        startups.append(startup)
        _write_json(STARTUPS_FILE, startups)
        logger.info(f"Saved startup: {startup.get('company_name', startup.get('title'))}")
        return True

    def get_all_startups(self, filters: Optional[Dict] = None) -> List[Dict]:
        startups = _read_json(STARTUPS_FILE)
        if not filters:
            return startups
        # Simple filter support
        result = []
        for s in startups:
            match = True
            for k, v in filters.items():
                if isinstance(v, dict) and "$gte" in v:
                    if s.get(k, 0) < v["$gte"]:
                        match = False
                elif s.get(k) != v:
                    match = False
            if match:
                result.append(s)
        return result

    def get_evaluated_startups(self, min_score: int = 70) -> List[Dict]:
        return self.get_all_startups({"confidence_score": {"$gte": min_score}})

    def update_startup_status(self, link: str, status: str):
        startups = _read_json(STARTUPS_FILE)
        for s in startups:
            if s.get("link") == link:
                s["status"] = status
                break
        _write_json(STARTUPS_FILE, startups)

    # ── Feedback ──────────────────────────────────────────────

    def add_feedback(self, link: str, action: str, reason: Optional[str] = None):
        feedback = _read_json(FEEDBACK_FILE)
        feedback.append({
            "link": link,
            "action": action,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        _write_json(FEEDBACK_FILE, feedback)

    def get_all_feedback(self) -> List[Dict]:
        return _read_json(FEEDBACK_FILE)
