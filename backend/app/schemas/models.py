"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Types of user intents the agent can classify."""
    PRODUCT_INFO = "product_info"
    ORDER_STATUS = "order_status"
    COMPLAINT = "complaint"
    REFUND = "refund"
    DELIVERY = "delivery"
    COMPARISON = "comparison"
    GENERAL = "general"


# Chat Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message")
    session_id: str = Field(..., description="Unique session identifier")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent response")
    intent: str = Field(..., description="Classified intent")
    sources: Optional[List[str]] = Field(default=None, description="Source documents used")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


# Product Models
class ProductSpecs(BaseModel):
    """Product specifications."""
    processor: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    display: Optional[str] = None
    battery: Optional[str] = None
    camera: Optional[str] = None
    screen_size: Optional[str] = None
    resolution: Optional[str] = None
    refresh_rate: Optional[str] = None
    connectivity: Optional[List[str]] = None
    ports: Optional[List[str]] = None
    os: Optional[str] = None


class ProductResponse(BaseModel):
    """Product information response."""
    id: int
    name: str
    category: str
    price: float
    description: str
    specs: ProductSpecs
    in_stock: bool
    warranty: str
    rating: float
    reviews_count: int
    brand: str


# Order Models
class OrderItem(BaseModel):
    """Individual item in an order."""
    product_id: int
    product_name: str
    quantity: int
    price: float


class OrderResponse(BaseModel):
    """Order information response."""
    order_id: str
    customer_name: str
    customer_email: str
    items: List[OrderItem]
    total: float
    status: str
    order_date: str
    expected_delivery: Optional[str] = None
    tracking_number: Optional[str] = None


# Complaint Models
class ComplaintRequest(BaseModel):
    """Request to create a complaint."""
    order_id: str
    issue: str
    description: str


class ComplaintResponse(BaseModel):
    """Complaint creation response."""
    complaint_id: str
    order_id: str
    issue: str
    description: str
    status: str
    created_at: str
    message: str


# Comparison Models
class ComparisonFeature(BaseModel):
    """Feature comparison between products."""
    feature: str
    values: Dict[str, Any]


class ComparisonResponse(BaseModel):
    """Product comparison response."""
    products: List[Dict[str, Any]]
    comparison: List[ComparisonFeature]
    recommendation: Optional[str] = None


# Delivery Models
class DeliveryLocation(BaseModel):
    """Delivery tracking location."""
    location: str
    timestamp: str
    status: str


class DeliveryResponse(BaseModel):
    """Delivery tracking response."""
    order_id: str
    tracking_number: str
    carrier: str
    current_status: str
    estimated_delivery: str
    tracking_history: List[DeliveryLocation]


# Refund Models
class RefundResponse(BaseModel):
    """Refund status response."""
    order_id: str
    refund_id: str
    status: str
    amount: float
    requested_date: str
    processed_date: Optional[str] = None
    expected_completion: Optional[str] = None
    reason: str
