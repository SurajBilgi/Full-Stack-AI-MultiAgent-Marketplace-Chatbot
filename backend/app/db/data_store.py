"""
In-memory data store for orders, products, complaints, and refunds.

In production, this would be replaced with a proper database (PostgreSQL, etc.)
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataStore:
    """In-memory data store with JSON persistence."""
    
    def __init__(self):
        """Initialize data store."""
        self.products = []
        self.orders = []
        self.complaints = []
        self.refunds = []
        self.deliveries = []
        self.data_path = "./data"
        
        # Counters for ID generation
        self.complaint_counter = 100
        self.refund_counter = 100
    
    async def initialize(self):
        """Load data from JSON files."""
        logger.info("📂 Loading data from files...")
        
        # Ensure data directory exists
        os.makedirs(self.data_path, exist_ok=True)
        
        # Load products
        self._load_json("products.json", "products")
        
        # Load orders
        self._load_json("orders.json", "orders")
        
        # Load complaints
        self._load_json("complaints.json", "complaints")
        
        # Load refunds
        self._load_json("refunds.json", "refunds")
        
        # Load deliveries
        self._load_json("deliveries.json", "deliveries")
        
        logger.info(
            f"✅ Data loaded: {len(self.products)} products, "
            f"{len(self.orders)} orders, {len(self.complaints)} complaints, "
            f"{len(self.refunds)} refunds"
        )
    
    def _load_json(self, filename: str, attribute: str):
        """Load JSON file into attribute."""
        filepath = os.path.join(self.data_path, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    setattr(self, attribute, data)
                logger.info(f"✅ Loaded {filename}")
            except Exception as e:
                logger.error(f"❌ Error loading {filename}: {e}")
                setattr(self, attribute, [])
        else:
            logger.warning(f"⚠️  {filename} not found, using empty list")
            setattr(self, attribute, [])
    
    # Product methods
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products."""
        return self.products
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        for product in self.products:
            if product.get("id") == product_id:
                return product
        return None
    
    def search_products(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search products with filters."""
        results = self.products
        
        if category:
            results = [p for p in results if p.get("category") == category]
        
        if min_price is not None:
            results = [p for p in results if p.get("price", 0) >= min_price]
        
        if max_price is not None:
            results = [p for p in results if p.get("price", float("inf")) <= max_price]
        
        return results
    
    # Order methods
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Get all orders."""
        return self.orders
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID."""
        for order in self.orders:
            if order.get("order_id") == order_id:
                return order
        return None
    
    # Complaint methods
    def get_all_complaints(self) -> List[Dict[str, Any]]:
        """Get all complaints."""
        return self.complaints
    
    def get_complaint(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """Get complaint by ID."""
        for complaint in self.complaints:
            if complaint.get("complaint_id") == complaint_id:
                return complaint
        return None
    
    def create_complaint(
        self,
        order_id: str,
        issue: str,
        description: str
    ) -> Dict[str, Any]:
        """Create a new complaint."""
        self.complaint_counter += 1
        complaint_id = f"CMP-{self.complaint_counter}"
        
        complaint = {
            "complaint_id": complaint_id,
            "order_id": order_id,
            "issue": issue,
            "description": description,
            "status": "open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.complaints.append(complaint)
        return complaint
    
    # Refund methods
    def get_all_refunds(self) -> List[Dict[str, Any]]:
        """Get all refunds."""
        return self.refunds
    
    def get_refund(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get refund by order ID."""
        for refund in self.refunds:
            if refund.get("order_id") == order_id:
                return refund
        return None
    
    def create_refund(
        self,
        order_id: str,
        amount: float,
        reason: str
    ) -> Dict[str, Any]:
        """Create a new refund request."""
        self.refund_counter += 1
        refund_id = f"REF-{self.refund_counter}"
        
        now = datetime.now()
        expected = now + timedelta(days=7)
        
        refund = {
            "refund_id": refund_id,
            "order_id": order_id,
            "amount": amount,
            "status": "pending",
            "reason": reason,
            "requested_date": now.strftime("%Y-%m-%d"),
            "expected_completion": expected.strftime("%Y-%m-%d")
        }
        
        self.refunds.append(refund)
        return refund
    
    # Delivery methods
    def get_delivery_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery status by order ID."""
        for delivery in self.deliveries:
            if delivery.get("order_id") == order_id:
                return delivery
        return None
