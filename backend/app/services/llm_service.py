"""
LLM Service for interfacing with OpenAI or local models.

This service abstracts LLM interactions and can be configured to use
OpenAI GPT-4 or local models like Llama/Mistral.
"""

import os
from typing import List, Dict, Any, Optional
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM interactions with conversation management."""
    
    def __init__(self):
        """Initialize LLM service with configuration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        if not self.api_key:
            logger.warning("⚠️  OPENAI_API_KEY not set. LLM functionality will be limited.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"✅ LLM service initialized with model: {self.model_name}")
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_message: Optional[str] = None,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            context: Additional context to include
            system_message: System message to set behavior
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        if not self.client:
            return self._fallback_response(prompt)
        
        try:
            messages = []
            
            # Add system message
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            else:
                messages.append({
                    "role": "system",
                    "content": "You are a helpful AI assistant for an electronics e-commerce platform. "
                               "Provide accurate, concise, and friendly responses."
                })
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context information:\n{context}"
                })
            
            # Add user prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating LLM response: {e}")
            return self._fallback_response(prompt)
    
    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000
    ) -> str:
        """
        Generate a response with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        if not self.client:
            last_message = messages[-1]["content"] if messages else ""
            return self._fallback_response(last_message)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating LLM response with history: {e}")
            last_message = messages[-1]["content"] if messages else ""
            return self._fallback_response(last_message)
    
    async def classify_intent(self, message: str) -> str:
        """
        Classify user intent from message.
        
        Args:
            message: User message
            
        Returns:
            Intent classification
        """
        if not self.client:
            return self._simple_intent_classification(message)
        
        try:
            system_message = """You are an intent classifier for an e-commerce chatbot.
Classify the user's message into one of these intents:
- product_info: Questions about products, features, specifications
- order_status: Tracking orders, order information
- complaint: Issues, problems, complaints about products or service
- refund: Return requests, refund inquiries
- delivery: Shipping, delivery tracking, delivery issues
- comparison: Comparing multiple products
- general: General questions, greetings, other

Respond with ONLY the intent name, nothing else."""
            
            response = await self.generate_response(
                prompt=message,
                system_message=system_message,
                max_tokens=50
            )
            
            intent = response.strip().lower()
            
            # Validate intent
            valid_intents = [
                "product_info", "order_status", "complaint",
                "refund", "delivery", "comparison", "general"
            ]
            
            if intent not in valid_intents:
                return "general"
            
            return intent
            
        except Exception as e:
            logger.error(f"❌ Error classifying intent: {e}")
            return self._simple_intent_classification(message)
    
    def _simple_intent_classification(self, message: str) -> str:
        """Simple rule-based intent classification fallback."""
        message_lower = message.lower()
        
        # Order related
        if any(word in message_lower for word in ["order", "track", "ord-"]):
            return "order_status"
        
        # Complaint related
        if any(word in message_lower for word in ["problem", "issue", "complaint", "broken", "damaged", "not working"]):
            return "complaint"
        
        # Refund related
        if any(word in message_lower for word in ["refund", "return", "money back"]):
            return "refund"
        
        # Delivery related
        if any(word in message_lower for word in ["delivery", "shipping", "deliver", "when will"]):
            return "delivery"
        
        # Comparison related
        if any(word in message_lower for word in ["compare", "vs", "versus", "difference between"]):
            return "comparison"
        
        # Product info (default for questions about products)
        if any(word in message_lower for word in ["laptop", "phone", "tv", "product", "specs", "features", "price"]):
            return "product_info"
        
        return "general"
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when LLM is not available."""
        return (
            "I'm currently operating in limited mode. "
            "I can help you with product information, orders, and more. "
            "Please provide your order ID or ask about specific products."
        )
    
    async def extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract entities (order IDs, product names, etc.) from message.
        
        Args:
            message: User message
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {
            "order_ids": [],
            "product_names": [],
            "numbers": []
        }
        
        # Extract order IDs (format: ORD-XXXX)
        import re
        order_pattern = r'ORD-\d{4}'
        entities["order_ids"] = re.findall(order_pattern, message)
        
        # Extract numbers
        number_pattern = r'\d+'
        entities["numbers"] = re.findall(number_pattern, message)
        
        return entities
