"""
Embedding service for converting text to vectors.

Supports both OpenAI embeddings and local sentence transformers.
"""

import os
from typing import List
import logging
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.use_openai = os.getenv("OPENAI_API_KEY") is not None
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        
        if self.use_openai:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                logger.info(f"✅ Using OpenAI embeddings: {self.embedding_model}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize OpenAI, falling back to local: {e}")
                self.use_openai = False
        
        if not self.use_openai:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Using local sentence transformers: all-MiniLM-L6-v2")
            except Exception as e:
                logger.error(f"❌ Failed to initialize embedding service: {e}")
                raise
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if self.use_openai:
            return await self._embed_openai(text)
        else:
            return await self._embed_local(text)
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if self.use_openai:
            return await self._embed_batch_openai(texts)
        else:
            return await self._embed_batch_local(texts)
    
    async def _embed_openai(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ Error generating OpenAI embedding: {e}")
            raise
    
    async def _embed_batch_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate batch embeddings using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"❌ Error generating OpenAI batch embeddings: {e}")
            raise
    
    async def _embed_local(self, text: str) -> List[float]:
        """Generate embedding using local model."""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating local embedding: {e}")
            raise
    
    async def _embed_batch_local(self, texts: List[str]) -> List[List[float]]:
        """Generate batch embeddings using local model."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating local batch embeddings: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self.use_openai:
            # OpenAI ada-002 has 1536 dimensions
            return 1536
        else:
            # all-MiniLM-L6-v2 has 384 dimensions
            return 384
