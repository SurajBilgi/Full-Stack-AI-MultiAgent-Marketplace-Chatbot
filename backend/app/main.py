"""
Main FastAPI application for AI Agent Marketplace Chatbot.

This module sets up the FastAPI application with all routes, middleware,
and initializes the AI agent, RAG pipeline, and graph database.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from app.schemas.models import (
    ChatRequest,
    ChatResponse,
    OrderResponse,
    ComplaintRequest,
    ComplaintResponse,
    ProductResponse,
    ComparisonResponse,
)
from app.agents.orchestrator import AgentOrchestrator
from app.db.data_store import DataStore
from app.db.graph_db import GraphDatabase
from app.rag.pipeline import RAGPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
agent_orchestrator: AgentOrchestrator = None
data_store: DataStore = None
graph_db: GraphDatabase = None
rag_pipeline: RAGPipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    global agent_orchestrator, data_store, graph_db, rag_pipeline
    
    logger.info("🚀 Initializing AI Agent Marketplace Chatbot...")
    
    try:
        # Initialize data store
        data_store = DataStore()
        await data_store.initialize()
        logger.info("✅ Data store initialized")
        
        # Initialize graph database
        graph_db = GraphDatabase()
        await graph_db.initialize()
        logger.info("✅ Graph database initialized")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline()
        await rag_pipeline.initialize()
        logger.info("✅ RAG pipeline initialized")
        
        # Initialize agent orchestrator
        agent_orchestrator = AgentOrchestrator(
            data_store=data_store,
            graph_db=graph_db,
            rag_pipeline=rag_pipeline
        )
        logger.info("✅ Agent orchestrator initialized")
        
        logger.info("🎉 Application startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down application...")
    if graph_db:
        await graph_db.close()
    logger.info("👋 Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="AI Agent Marketplace Chatbot",
    description="Production-grade AI-powered chatbot for electronics e-commerce",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Agent Marketplace Chatbot",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check with component status."""
    return {
        "status": "healthy",
        "components": {
            "agent": agent_orchestrator is not None,
            "data_store": data_store is not None,
            "graph_db": graph_db is not None,
            "rag_pipeline": rag_pipeline is not None,
        }
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Processes user messages through the AI agent.
    
    The agent will:
    1. Classify intent
    2. Route to appropriate tools
    3. Use RAG for product information
    4. Query graph DB for relationships
    5. Generate natural language response
    """
    try:
        logger.info(f"📨 Chat request from session {request.session_id}: {request.message}")
        
        response = await agent_orchestrator.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        logger.info(f"✅ Response generated for session {request.session_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products")
async def get_products():
    """Get all products."""
    try:
        products = data_store.get_all_products()
        return {"products": products}
    except Exception as e:
        logger.error(f"❌ Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Get specific product by ID."""
    try:
        product = data_store.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/compare", response_model=ComparisonResponse)
async def compare_products(ids: str):
    """
    Compare multiple products using graph database.
    
    Example: /api/products/compare?ids=1,2,3
    """
    try:
        product_ids = [int(id.strip()) for id in ids.split(",")]
        
        if len(product_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 product IDs required for comparison"
            )
        
        comparison = await graph_db.compare_products(product_ids)
        return comparison
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product IDs")
    except Exception as e:
        logger.error(f"❌ Error comparing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """Get order status by order ID."""
    try:
        order = data_store.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/complaints", response_model=ComplaintResponse)
async def create_complaint(request: ComplaintRequest):
    """Create a new complaint."""
    try:
        complaint = data_store.create_complaint(
            order_id=request.order_id,
            issue=request.issue,
            description=request.description
        )
        return complaint
    except Exception as e:
        logger.error(f"❌ Error creating complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/refunds/{order_id}")
async def get_refund_status(order_id: str):
    """Get refund status for an order."""
    try:
        refund = data_store.get_refund(order_id)
        if not refund:
            return {
                "order_id": order_id,
                "status": "not_found",
                "message": "No refund request found for this order"
            }
        return refund
    except Exception as e:
        logger.error(f"❌ Error fetching refund: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/delivery/{order_id}")
async def get_delivery_status(order_id: str):
    """Get delivery tracking information."""
    try:
        delivery = data_store.get_delivery_status(order_id)
        if not delivery:
            raise HTTPException(status_code=404, detail="Delivery information not found")
        return delivery
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching delivery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
async def get_metrics():
    """Get application metrics."""
    try:
        metrics = {
            "total_products": len(data_store.get_all_products()),
            "total_orders": len(data_store.get_all_orders()),
            "total_complaints": len(data_store.get_all_complaints()),
            "total_refunds": len(data_store.get_all_refunds()),
        }
        return metrics
    except Exception as e:
        logger.error(f"❌ Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
