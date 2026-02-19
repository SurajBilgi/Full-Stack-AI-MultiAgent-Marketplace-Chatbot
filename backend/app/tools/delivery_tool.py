"""
Delivery tool for tracking shipments and delivery status.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DeliveryTool:
    """Tool for delivery tracking operations."""
    
    def __init__(self, data_store):
        """
        Initialize delivery tool.
        
        Args:
            data_store: DataStore instance
        """
        self.data_store = data_store
    
    async def get_delivery_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get delivery tracking information.
        
        Args:
            order_id: Order ID
            
        Returns:
            Delivery tracking information
        """
        logger.info(f"🚚 Tracking delivery for order: {order_id}")
        
        delivery = self.data_store.get_delivery_status(order_id)
        
        if not delivery:
            # Check if order exists
            order = self.data_store.get_order(order_id)
            if not order:
                return {
                    "success": False,
                    "message": f"Order {order_id} not found."
                }
            
            return {
                "success": True,
                "message": f"Delivery information not yet available for order {order_id}."
            }
        
        # Format tracking history
        tracking_summary = []
        for event in delivery.get("tracking_history", []):
            tracking_summary.append(
                f"• {event['timestamp']}: {event['status']} at {event['location']}"
            )
        
        message = (
            f"Order {order_id} is currently {delivery['current_status']}. "
            f"Estimated delivery: {delivery['estimated_delivery']}. "
            f"Tracking number: {delivery['tracking_number']} ({delivery['carrier']})"
        )
        
        logger.info(f"✅ Delivery status: {delivery['current_status']}")
        
        return {
            "success": True,
            "delivery": delivery,
            "tracking_summary": "\n".join(tracking_summary),
            "message": message
        }
    
    async def estimate_delivery(self, order_id: str) -> Dict[str, Any]:
        """
        Get estimated delivery date.
        
        Args:
            order_id: Order ID
            
        Returns:
            Estimated delivery information
        """
        order = self.data_store.get_order(order_id)
        
        if not order:
            return {
                "success": False,
                "message": f"Order {order_id} not found."
            }
        
        if order.get("expected_delivery"):
            return {
                "success": True,
                "estimated_delivery": order["expected_delivery"],
                "message": f"Your order is expected to arrive by {order['expected_delivery']}."
            }
        
        return {
            "success": True,
            "message": "Delivery estimate is being calculated. Please check back soon."
        }
