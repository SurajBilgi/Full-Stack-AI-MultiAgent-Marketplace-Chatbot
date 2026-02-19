"""
Seed script to initialize all data (products, orders, graph database, RAG).

Run this script to set up the application with dummy data.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.data_store import DataStore
from app.db.graph_db import GraphDatabase
from app.rag.pipeline import RAGPipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def seed_all():
    """Seed all data stores."""
    logger.info("=" * 60)
    logger.info("Starting data seeding process...")
    logger.info("=" * 60)

    try:
        # Initialize data store
        logger.info("\n📦 Step 1: Initializing data store...")
        data_store = DataStore()
        await data_store.initialize()
        logger.info("✅ Data store initialized successfully")
        logger.info(f"   - Products: {len(data_store.products)}")
        logger.info(f"   - Orders: {len(data_store.orders)}")
        logger.info(f"   - Complaints: {len(data_store.complaints)}")
        logger.info(f"   - Refunds: {len(data_store.refunds)}")

        # Initialize graph database
        logger.info("\n🕸️  Step 2: Initializing graph database...")
        graph_db = GraphDatabase()
        await graph_db.initialize()
        logger.info("✅ Graph database initialized successfully")

        # Initialize RAG pipeline
        logger.info("\n📚 Step 3: Initializing RAG pipeline...")
        rag_pipeline = RAGPipeline()
        await rag_pipeline.initialize()
        logger.info("✅ RAG pipeline initialized successfully")

        # Get stats
        stats = rag_pipeline.get_stats()
        logger.info(
            f"   - Vector store size: {stats['vector_store'].get('total_documents', 0)} documents"
        )

        # Cleanup
        await graph_db.close()

        logger.info("\n" + "=" * 60)
        logger.info("✅ Data seeding completed successfully!")
        logger.info("=" * 60)
        logger.info("\nYou can now start the application:")
        logger.info("  uvicorn app.main:app --reload")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n❌ Error during seeding: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_all())
