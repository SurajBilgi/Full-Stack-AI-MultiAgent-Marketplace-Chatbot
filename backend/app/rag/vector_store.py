"""
Vector store implementation using FAISS for efficient similarity search.
"""

import os
import pickle
from typing import List, Tuple, Dict, Any
import logging
import numpy as np
import faiss

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for document retrieval."""
    
    def __init__(self, dimension: int = 384):
        """
        Initialize vector store.
        
        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadata = []
        self.store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        
        logger.info(f"✅ Vector store initialized with dimension: {dimension}")
    
    def add_documents(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ):
        """
        Add documents with their embeddings to the store.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document texts
            metadata: List of metadata dicts for each document
        """
        if not embeddings or not documents:
            logger.warning("⚠️  No documents to add")
            return
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store documents and metadata
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        
        logger.info(f"✅ Added {len(documents)} documents to vector store")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 3
    ) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of tuples: (document_text, metadata, distance)
        """
        if self.index.ntotal == 0:
            logger.warning("⚠️  Vector store is empty")
            return []
        
        # Convert to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
        
        # Prepare results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append((
                    self.documents[idx],
                    self.metadata[idx],
                    float(distance)
                ))
        
        return results
    
    def save(self):
        """Save vector store to disk."""
        try:
            os.makedirs(self.store_path, exist_ok=True)
            
            # Save FAISS index
            index_path = os.path.join(self.store_path, "index.faiss")
            faiss.write_index(self.index, index_path)
            
            # Save documents and metadata
            data_path = os.path.join(self.store_path, "data.pkl")
            with open(data_path, "wb") as f:
                pickle.dump({
                    "documents": self.documents,
                    "metadata": self.metadata,
                    "dimension": self.dimension
                }, f)
            
            logger.info(f"✅ Vector store saved to {self.store_path}")
            
        except Exception as e:
            logger.error(f"❌ Error saving vector store: {e}")
            raise
    
    def load(self):
        """Load vector store from disk."""
        try:
            index_path = os.path.join(self.store_path, "index.faiss")
            data_path = os.path.join(self.store_path, "data.pkl")
            
            if not os.path.exists(index_path) or not os.path.exists(data_path):
                logger.info("ℹ️  No saved vector store found")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load documents and metadata
            with open(data_path, "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]
                self.dimension = data["dimension"]
            
            logger.info(f"✅ Vector store loaded from {self.store_path}")
            logger.info(f"📊 Total documents: {len(self.documents)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading vector store: {e}")
            return False
    
    def clear(self):
        """Clear the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = []
        logger.info("🗑️  Vector store cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal,
            "dimension": self.dimension
        }
