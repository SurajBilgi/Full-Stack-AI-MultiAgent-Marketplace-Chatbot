"""
Agent Orchestrator - Main AI agent that coordinates all components.

This is the brain of the chatbot. It:
1. Maintains conversation memory
2. Classifies intent
3. Routes to appropriate tools
4. Uses RAG for product information
5. Queries graph DB for comparisons
6. Generates natural responses
"""

from typing import Dict, Any, List
import logging
from collections import defaultdict

from app.agents.intent_classifier import IntentClassifier
from app.services.llm_service import LLMService
from app.tools.order_tool import OrderTool
from app.tools.complaint_tool import ComplaintTool
from app.tools.refund_tool import RefundTool
from app.tools.delivery_tool import DeliveryTool
from app.schemas.models import ChatResponse

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Main AI agent orchestrator."""

    def __init__(self, data_store, graph_db, rag_pipeline):
        """
        Initialize agent orchestrator.

        Args:
            data_store: DataStore instance
            graph_db: GraphDatabase instance
            rag_pipeline: RAGPipeline instance
        """
        self.data_store = data_store
        self.graph_db = graph_db
        self.rag_pipeline = rag_pipeline

        # Initialize components
        self.intent_classifier = IntentClassifier()
        self.llm_service = LLMService()

        # Initialize tools
        self.order_tool = OrderTool(data_store)
        self.complaint_tool = ComplaintTool(data_store)
        self.refund_tool = RefundTool(data_store)
        self.delivery_tool = DeliveryTool(data_store)

        # Conversation memory (session_id -> messages)
        self.conversations = defaultdict(list)
        self.max_history = 10

        logger.info("✅ Agent orchestrator initialized")

    async def process_message(self, message: str, session_id: str) -> ChatResponse:
        """
        Process user message and generate response.

        This is the main entry point for the agent.

        Args:
            message: User message
            session_id: Session identifier

        Returns:
            ChatResponse with answer and metadata
        """
        logger.info(f"🤖 Processing message from session {session_id}")

        try:
            # Add user message to conversation history
            self._add_to_history(session_id, "user", message)

            # Step 1: Classify intent
            intent = await self.intent_classifier.classify(message)
            logger.info(f"📋 Intent: {intent}")

            # Step 2: Route to appropriate handler
            response_data = await self._route_to_handler(intent, message, session_id)

            # Step 3: Generate natural language response
            response_text = await self._generate_response(
                intent=intent,
                message=message,
                data=response_data,
                session_id=session_id,
            )

            # Add assistant response to history
            self._add_to_history(session_id, "assistant", response_text)

            # Create response
            return ChatResponse(
                response=response_text,
                intent=intent,
                sources=response_data.get("sources", []),
                metadata=response_data.get("metadata", {}),
            )

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}", exc_info=True)
            return ChatResponse(
                response=(
                    "I apologize, but I encountered an error processing your request. "
                    "Please try again or rephrase your question."
                ),
                intent="error",
                sources=[],
                metadata={"error": str(e)},
            )

    async def _route_to_handler(
        self, intent: str, message: str, session_id: str
    ) -> Dict[str, Any]:
        """
        Route message to appropriate handler based on intent.

        Args:
            intent: Classified intent
            message: User message
            session_id: Session ID

        Returns:
            Handler response data
        """
        if intent == "product_info":
            return await self._handle_product_info(message)

        elif intent == "order_status":
            return await self._handle_order_status(message)

        elif intent == "complaint":
            return await self._handle_complaint(message)

        elif intent == "refund":
            return await self._handle_refund(message)

        elif intent == "delivery":
            return await self._handle_delivery(message)

        elif intent == "comparison":
            return await self._handle_comparison(message)

        else:  # general
            return await self._handle_general(message)

    async def _handle_product_info(self, message: str) -> Dict[str, Any]:
        """Handle product information queries using RAG."""
        logger.info("📦 Handling product info query")

        # Retrieve relevant information from RAG
        results = await self.rag_pipeline.retrieve(message, top_k=3)

        context_parts = []
        sources = []

        for text, metadata, score in results:
            context_parts.append(text)
            sources.append(metadata.get("title", "Product Information"))

        context = (
            "\n\n".join(context_parts)
            if context_parts
            else "No specific information found."
        )

        return {
            "context": context,
            "sources": sources,
            "metadata": {"num_results": len(results)},
        }

    async def _handle_order_status(self, message: str) -> Dict[str, Any]:
        """Handle order status queries."""
        logger.info("📦 Handling order status query")

        # Extract order ID
        order_id = self.intent_classifier.extract_order_id(message)

        if not order_id:
            return {
                "success": False,
                "message": "Please provide your order ID (format: ORD-XXXX) to check status.",
            }

        # Get order status
        result = await self.order_tool.get_order_status(order_id)
        return result

    async def _handle_complaint(self, message: str) -> Dict[str, Any]:
        """Handle complaint submission."""
        logger.info("📝 Handling complaint")

        # Extract order ID
        order_id = self.intent_classifier.extract_order_id(message)

        if not order_id:
            return {
                "success": False,
                "message": "Please provide your order ID (format: ORD-XXXX) to file a complaint.",
            }

        # Create complaint
        result = await self.complaint_tool.create_complaint(
            order_id=order_id, issue="Product issue", description=message
        )

        return result

    async def _handle_refund(self, message: str) -> Dict[str, Any]:
        """Handle refund queries."""
        logger.info("💰 Handling refund query")

        # Extract order ID
        order_id = self.intent_classifier.extract_order_id(message)

        if not order_id:
            return {
                "success": False,
                "message": "Please provide your order ID (format: ORD-XXXX) to check refund status.",
            }

        # Check if requesting new refund or checking status
        if any(
            word in message.lower()
            for word in ["want", "request", "initiate", "return"]
        ):
            result = await self.refund_tool.initiate_refund(
                order_id=order_id, reason="Customer request"
            )
        else:
            result = await self.refund_tool.get_refund_status(order_id)

        return result

    async def _handle_delivery(self, message: str) -> Dict[str, Any]:
        """Handle delivery tracking queries."""
        logger.info("🚚 Handling delivery query")

        # Extract order ID
        order_id = self.intent_classifier.extract_order_id(message)

        if not order_id:
            return {
                "success": False,
                "message": "Please provide your order ID (format: ORD-XXXX) to track delivery.",
            }

        # Get delivery status
        result = await self.delivery_tool.get_delivery_status(order_id)
        return result

    async def _handle_comparison(self, message: str) -> Dict[str, Any]:
        """Handle product comparison queries using graph database."""
        logger.info("⚖️  Handling product comparison")

        # Extract product IDs from message
        product_ids = self.intent_classifier.extract_product_ids(message)

        if len(product_ids) < 2:
            # If no specific IDs, try to get product info from RAG
            return await self._handle_product_info(message)

        # Compare products using graph database
        comparison = await self.graph_db.compare_products(product_ids)

        return {"comparison": comparison, "metadata": {"product_ids": product_ids}}

    async def _handle_general(self, message: str) -> Dict[str, Any]:
        """Handle general queries."""
        logger.info("💬 Handling general query")

        # Try to get relevant context from RAG
        results = await self.rag_pipeline.retrieve(message, top_k=2)

        context = ""
        sources = []

        if results:
            for text, metadata, score in results:
                context += text + "\n\n"
                sources.append(metadata.get("title", "Information"))

        return {
            "context": context,
            "sources": sources if sources else None,
            "metadata": {},
        }

    async def _generate_response(
        self, intent: str, message: str, data: Dict[str, Any], session_id: str
    ) -> str:
        """
        Generate natural language response using LLM.

        Args:
            intent: Classified intent
            message: Original user message
            data: Data from handler
            session_id: Session ID

        Returns:
            Natural language response
        """
        # If data already has a formatted message, use it
        if "message" in data and isinstance(data["message"], str):
            return data["message"]

        # Build context for LLM
        context_parts = []

        if "context" in data:
            context_parts.append(f"Relevant Information:\n{data['context']}")

        if "comparison" in data:
            comp = data["comparison"]
            if comp.get("products"):
                context_parts.append(
                    f"Comparing products: {[p['name'] for p in comp['products']]}"
                )
                context_parts.append(
                    f"Recommendation: {comp.get('recommendation', '')}"
                )

        if data.get("success") is False:
            return data.get("message", "I couldn't process that request.")

        # Add any structured data
        if "order_id" in data:
            context_parts.append(f"Order ID: {data['order_id']}")
        if "status" in data:
            context_parts.append(f"Status: {data['status']}")

        context = "\n\n".join(context_parts) if context_parts else None

        # Get conversation history
        history = self._get_recent_history(session_id, max_messages=6)

        # Build messages for LLM
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant for TechPro Electronics, "
                    "an electronics e-commerce company. Provide accurate, friendly, "
                    "and concise responses. Use the provided context to answer questions. "
                    "If you don't have enough information, ask for clarification."
                ),
            }
        ]

        # Add history
        for msg in history:
            messages.append(msg)

        # Add context if available
        if context:
            messages.append(
                {"role": "system", "content": f"Context for answering:\n{context}"}
            )

        # Add current message
        messages.append({"role": "user", "content": message})

        # Generate response
        response = await self.llm_service.generate_with_history(
            messages, max_tokens=500
        )

        return response

    def _add_to_history(self, session_id: str, role: str, content: str):
        """Add message to conversation history."""
        self.conversations[session_id].append({"role": role, "content": content})

        # Trim history if too long
        if len(self.conversations[session_id]) > self.max_history * 2:
            self.conversations[session_id] = self.conversations[session_id][
                -self.max_history * 2 :
            ]

    def _get_recent_history(
        self, session_id: str, max_messages: int = 6
    ) -> List[Dict[str, str]]:
        """Get recent conversation history."""
        history = self.conversations.get(session_id, [])
        return history[-max_messages:] if len(history) > max_messages else history
