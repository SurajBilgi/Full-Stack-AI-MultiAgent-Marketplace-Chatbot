"""
Order tool for retrieving order status and information.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OrderTool:
    """Tool for order-related operations."""
    
    def __init__(self, data_store):
        """
        Initialize order tool.
        
        Args:
            data_store: DataStore instance
        """
        self.data_store = data_store
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status and details.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order information dict
        """
        logger.info(f"🔍 Looking up order: {order_id}")
        
        order = self.data_store.get_order(order_id)
        
        if not order:
            return {
                "success": False,
                "message": f"Order {order_id} not found. Please check the order ID."
            }
        
        # Format response
        response = {
            "success": True,
            "order_id": order["order_id"],
            "status": order["status"],
            "order_date": order["order_date"],
            "total": order["total"],
            "items": order["items"],
            "customer_name": order["customer_name"],
            "message": f"Order {order_id} is currently {order['status']}."
        }
        
        if order.get("expected_delivery"):
            response["expected_delivery"] = order["expected_delivery"]
            response["message"] += f" Expected delivery: {order['expected_delivery']}"
        
        if order.get("tracking_number"):
            response["tracking_number"] = order["tracking_number"]
        
        logger.info(f"✅ Order {order_id} found: {order['status']}")
        return response
    
    async def list_user_orders(self, customer_email: str) -> Dict[str, Any]:
        """
        List all orders for a customer.
        
        Args:
            customer_email: Customer email
            
        Returns:
            List of orders
        """
        all_orders = self.data_store.get_all_orders()
        user_orders = [
            order for order in all_orders
            if order.get("customer_email") == customer_email
        ]
        
        return {
            "success": True,
            "orders": user_orders,
            "count": len(user_orders)
        }
