"""
Complaint tool for handling customer complaints and issues.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ComplaintTool:
    """Tool for complaint-related operations."""
    
    def __init__(self, data_store):
        """
        Initialize complaint tool.
        
        Args:
            data_store: DataStore instance
        """
        self.data_store = data_store
    
    async def create_complaint(
        self,
        order_id: str,
        issue: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Create a new complaint.
        
        Args:
            order_id: Order ID
            issue: Issue type/category
            description: Detailed description
            
        Returns:
            Complaint creation response
        """
        logger.info(f"📝 Creating complaint for order: {order_id}")
        
        # Verify order exists
        order = self.data_store.get_order(order_id)
        if not order:
            return {
                "success": False,
                "message": f"Order {order_id} not found. Cannot create complaint."
            }
        
        # Create complaint
        complaint = self.data_store.create_complaint(
            order_id=order_id,
            issue=issue,
            description=description
        )
        
        logger.info(f"✅ Complaint created: {complaint['complaint_id']}")
        
        return {
            "success": True,
            "complaint_id": complaint["complaint_id"],
            "order_id": order_id,
            "status": complaint["status"],
            "message": (
                f"I'm sorry to hear about the issue with your order. "
                f"I've created complaint {complaint['complaint_id']}. "
                f"Our support team will contact you within 24 hours to resolve this."
            )
        }
    
    async def get_complaint_status(self, complaint_id: str) -> Dict[str, Any]:
        """
        Get complaint status.
        
        Args:
            complaint_id: Complaint ID
            
        Returns:
            Complaint status information
        """
        complaint = self.data_store.get_complaint(complaint_id)
        
        if not complaint:
            return {
                "success": False,
                "message": f"Complaint {complaint_id} not found."
            }
        
        return {
            "success": True,
            "complaint": complaint,
            "message": f"Complaint {complaint_id} is currently {complaint['status']}."
        }
    
    async def list_order_complaints(self, order_id: str) -> Dict[str, Any]:
        """
        List all complaints for an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            List of complaints
        """
        all_complaints = self.data_store.get_all_complaints()
        order_complaints = [
            c for c in all_complaints
            if c.get("order_id") == order_id
        ]
        
        return {
            "success": True,
            "complaints": order_complaints,
            "count": len(order_complaints)
        }
