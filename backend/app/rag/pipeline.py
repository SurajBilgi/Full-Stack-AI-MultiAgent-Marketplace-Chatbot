"""
RAG (Retrieval-Augmented Generation) Pipeline.

This pipeline:
1. Loads documents (product manuals, FAQs, policies)
2. Chunks them into smaller pieces
3. Generates embeddings
4. Stores in vector database
5. Retrieves relevant context for queries
"""

import os
import json
from typing import List, Dict, Any, Tuple
import logging

from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG pipeline for document retrieval."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.embedding_service = None
        self.vector_store = None
        self.top_k = int(os.getenv("TOP_K_RESULTS", "3"))
        self.documents_path = "./data/documents"
    
    async def initialize(self):
        """Initialize embedding service and vector store."""
        logger.info("🔧 Initializing RAG pipeline...")
        
        # Initialize embedding service
        self.embedding_service = EmbeddingService()
        
        # Initialize vector store with correct dimension
        dimension = self.embedding_service.get_dimension()
        self.vector_store = VectorStore(dimension=dimension)
        
        # Try to load existing vector store
        if self.vector_store.load():
            logger.info("✅ Loaded existing vector store")
        else:
            # Build new vector store
            logger.info("🏗️  Building new vector store...")
            await self._build_vector_store()
        
        logger.info("✅ RAG pipeline initialized")
    
    async def _build_vector_store(self):
        """Build vector store from documents."""
        documents = await self._load_documents()
        
        if not documents:
            logger.warning("⚠️  No documents found to index")
            return
        
        # Chunk documents
        chunks = self._chunk_documents(documents)
        logger.info(f"📄 Created {len(chunks)} document chunks")
        
        # Extract texts and metadata
        texts = [chunk["text"] for chunk in chunks]
        metadata = [chunk["metadata"] for chunk in chunks]
        
        # Generate embeddings
        logger.info("🔢 Generating embeddings...")
        embeddings = await self.embedding_service.embed_batch(texts)
        
        # Add to vector store
        self.vector_store.add_documents(embeddings, texts, metadata)
        
        # Save vector store
        self.vector_store.save()
        
        logger.info("✅ Vector store built successfully")
    
    async def _load_documents(self) -> List[Dict[str, Any]]:
        """Load all documents from the documents directory."""
        documents = []
        
        # Create documents directory if it doesn't exist
        os.makedirs(self.documents_path, exist_ok=True)
        
        # Define document files
        document_files = {
            "product_manuals": "product_manuals.json",
            "faqs": "faqs.json",
            "policies": "policies.json"
        }
        
        for doc_type, filename in document_files.items():
            filepath = os.path.join(self.documents_path, filename)
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        for item in data:
                            item["doc_type"] = doc_type
                            documents.append(item)
                    logger.info(f"📖 Loaded {len(data)} documents from {filename}")
                except Exception as e:
                    logger.error(f"❌ Error loading {filename}: {e}")
            else:
                logger.warning(f"⚠️  Document file not found: {filepath}")
        
        return documents
    
    def _chunk_documents(
        self,
        documents: List[Dict[str, Any]],
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Chunk documents into smaller pieces with overlap.
        
        Args:
            documents: List of document dicts
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dicts with text and metadata
        """
        chunks = []
        
        for doc in documents:
            # Get main text content
            if "content" in doc:
                text = doc["content"]
            elif "answer" in doc:
                text = f"Q: {doc.get('question', '')}\nA: {doc['answer']}"
            else:
                text = str(doc)
            
            # Simple chunking by character count
            for i in range(0, len(text), chunk_size - overlap):
                chunk_text = text[i:i + chunk_size]
                
                # Create metadata
                metadata = {
                    "doc_type": doc.get("doc_type", "unknown"),
                    "title": doc.get("title", doc.get("question", "Untitled")),
                    "product_id": doc.get("product_id"),
                    "category": doc.get("category")
                }
                
                chunks.append({
                    "text": chunk_text,
                    "metadata": metadata
                })
        
        return chunks
    
    async def retrieve(
        self,
        query: str,
        top_k: int = None
    ) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results (uses default if None)
            
        Returns:
            List of tuples: (text, metadata, score)
        """
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        logger.info(f"🔍 Retrieved {len(results)} documents for query: {query[:50]}...")
        
        return results
    
    async def get_context(
        self,
        query: str,
        top_k: int = None
    ) -> str:
        """
        Get formatted context for a query.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            Formatted context string
        """
        results = await self.retrieve(query, top_k)
        
        if not results:
            return "No relevant information found."
        
        # Format results
        context_parts = []
        for i, (text, metadata, score) in enumerate(results, 1):
            source = metadata.get("title", "Unknown")
            context_parts.append(f"[Source {i}: {source}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics."""
        return {
            "vector_store": self.vector_store.get_stats() if self.vector_store else {},
            "top_k": self.top_k,
            "documents_path": self.documents_path
        }
