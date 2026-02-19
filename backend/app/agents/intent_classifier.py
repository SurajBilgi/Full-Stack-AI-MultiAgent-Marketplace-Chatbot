"""
Intent classifier for categorizing user queries.
"""

from typing import Dict, Any
import logging
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifier for user intent detection."""

    def __init__(self):
        """Initialize intent classifier."""
        self.llm_service = LLMService()

        # Intent keywords for fallback classification
        self.intent_keywords = {
            "product_info": [
                "laptop",
                "phone",
                "tv",
                "product",
                "specs",
                "features",
                "tell me about",
                "what is",
                "price",
                "cost",
                "how much",
                "available",
                "in stock",
                "warranty",
            ],
            "order_status": [
                "order",
                "ord-",
                "track",
                "status",
                "where is my",
                "when will",
                "shipped",
                "delivered",
            ],
            "complaint": [
                "problem",
                "issue",
                "complaint",
                "broken",
                "damaged",
                "not working",
                "defective",
                "wrong",
                "mistake",
            ],
            "refund": [
                "refund",
                "return",
                "money back",
                "give back",
                "cancel order",
                "want to return",
            ],
            "delivery": [
                "delivery",
                "shipping",
                "ship",
                "arrive",
                "tracking",
                "eta",
                "when will it arrive",
            ],
            "comparison": [
                "compare",
                "vs",
                "versus",
                "difference between",
                "which is better",
                "should i get",
            ],
        }

    async def classify(self, message: str) -> str:
        """
        Classify user intent from message.

        Args:
            message: User message

        Returns:
            Intent classification
        """
        logger.info(f"🔍 Classifying intent for: {message[:50]}...")

        # Use LLM for classification
        intent = await self.llm_service.classify_intent(message)

        logger.info(f"✅ Classified intent: {intent}")
        return intent

    def extract_order_id(self, message: str) -> str:
        """
        Extract order ID from message.

        Args:
            message: User message

        Returns:
            Order ID or empty string
        """
        import re

        order_pattern = r"ORD-\d{4}"
        matches = re.findall(order_pattern, message)
        return matches[0] if matches else ""

    def extract_product_ids(self, message: str) -> list:
        """
        Extract product IDs from message.

        Args:
            message: User message

        Returns:
            List of product IDs
        """
        import re

        # Look for numbers that might be product IDs
        number_pattern = r"\b\d+\b"
        matches = re.findall(number_pattern, message)
        return [int(m) for m in matches if 1 <= int(m) <= 100]
