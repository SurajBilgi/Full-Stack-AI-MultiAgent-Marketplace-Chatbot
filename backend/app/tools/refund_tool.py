"""
Refund tool for handling refund requests and status.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class RefundTool:
    """Tool for refund-related operations."""
    
    def __init__(self, data_store):
        """
        Initialize refund tool.
        
        Args:
            data_store: DataStore instance
        """
        self.data_store = data_store
    
    async def get_refund_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get refund status for an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Refund status information
        """
        logger.info(f"🔍 Checking refund status for order: {order_id}")
        
        refund = self.data_store.get_refund(order_id)
        
        if not refund:
            # Check if order exists
            order = self.data_store.get_order(order_id)
            if not order:
                return {
                    "success": False,
                    "message": f"Order {order_id} not found."
                }
            
            return {
                "success": True,
                "has_refund": False,
                "message": (
                    f"No refund request found for order {order_id}. "
                    f"Would you like to initiate a return?"
                )
            }
        
        # Format message based on status
        status_messages = {
            "pending": "Your refund request is being processed.",
            "approved": "Your refund has been approved and is being processed.",
            "processed": f"Your refund of ${refund['amount']:.2f} has been processed.",
            "completed": f"Your refund of ${refund['amount']:.2f} has been completed."
        }
        
        message = status_messages.get(
            refund["status"],
            f"Refund status: {refund['status']}"
        )
        
        if refund.get("expected_completion"):
            message += f" Expected completion: {refund['expected_completion']}"
        
        logger.info(f"✅ Refund status: {refund['status']}")
        
        return {
            "success": True,
            "has_refund": True,
            "refund": refund,
            "message": message
        }
    
    async def initiate_refund(
        self,
        order_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Initiate a refund request.
        
        Args:
            order_id: Order ID
            reason: Reason for refund
            
        Returns:
            Refund initiation response
        """
        logger.info(f"📝 Initiating refund for order: {order_id}")
        
        # Verify order exists
        order = self.data_store.get_order(order_id)
        if not order:
            return {
                "success": False,
                "message": f"Order {order_id} not found."
            }
        
        # Check if refund already exists
        existing_refund = self.data_store.get_refund(order_id)
        if existing_refund:
            return {
                "success": False,
                "message": (
                    f"A refund request already exists for order {order_id} "
                    f"(Status: {existing_refund['status']})"
                )
            }
        
        # Create refund request
        refund = self.data_store.create_refund(
            order_id=order_id,
            amount=order["total"],
            reason=reason
        )
        
        logger.info(f"✅ Refund initiated: {refund['refund_id']}")
        
        return {
            "success": True,
            "refund_id": refund["refund_id"],
            "amount": refund["amount"],
            "message": (
                f"Refund request {refund['refund_id']} has been initiated. "
                f"Your refund of ${refund['amount']:.2f} will be processed within 5-7 business days."
            )
        }
