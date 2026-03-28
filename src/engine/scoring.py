from typing import Dict, List
import logging

class ScoringEngine:
    def __init__(self, base_weights: Dict[str, float] = None):
        self.logger = logging.getLogger("engine.scoring")
        self.logger.setLevel(logging.INFO)
        # Default weights for confidence score breakdown
        self.weights = base_weights or {
            "sector": 1.0,
            "geography": 1.0,
            "funding": 1.0,
            "sdg": 1.0,
            "innovation": 1.0
        }

    def calculate_confidence_score(self, breakdown: Dict[str, int]) -> int:
        """
        Calculates the weighted confidence score from 0-100.
        """
        total_score = 0
        total_weight = sum(self.weights.values())

        for key, value in breakdown.items():
            weight = self.weights.get(key, 1.0)
            total_score += (int(value) * weight)

        # Normalize to 0-100 assuming each value is 0-20
        normalized_score = int((total_score / (20 * total_weight)) * 100)
        return min(max(normalized_score, 0), 100)

    def adjust_weights(self, feedback_memory: List[Dict]):
        """
        Adjusts scoring weights based on user feedback.
        - If 'Ignore' or 'N/A' is clicked for a high-scoring category, reduce that weight.
        - If 'Save' or 'Progress' is clicked for a category, increase that weight.
        """
        # Simple heuristic for dynamic adjustment
        for fb in feedback_memory:
            action = fb.get("action")
            if action in ["Ignore", "Not Applicable"]:
                for key in self.weights:
                    # Slightly reduce weights for all if not specific, 
                    # but logic could be more targeted based on item attributes.
                    self.weights[key] *= 0.99
            elif action in ["Save", "Progress"]:
                for key in self.weights:
                    self.weights[key] *= 1.01
        
        self.logger.info(f"Updated weights: {self.weights}")
