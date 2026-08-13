import os
import sys
from typing import List
from app.core.config import settings

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


class EmbeddingManager:
    """Unified Vector Embedding Manager with Gemini & local HuggingFace fallbacks."""

    def __init__(self):
        self._provider = "none"
        self._embedder = None
        self._initialize_embedder()

    def _initialize_embedder(self):
        # 1. Try Google Gemini Embeddings if API Key is configured
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() != "":
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self._embedder = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=settings.GEMINI_API_KEY
                )
                self._provider = "gemini"
                print(f"[INFO] Initialized Gemini Embeddings API (models/embedding-001)")
                return
            except Exception as e:
                print(f"[WARNING] Could not initialize Gemini embeddings ({str(e)}). Falling back to local SentenceTransformers.")

        # 2. Local Fallback via HuggingFace SentenceTransformers
        try:
            from langchain_community.embeddings import SentenceTransformerEmbeddings
            self._embedder = SentenceTransformerEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            self._provider = "sentence-transformers-local"
            print(f"[INFO] Initialized Local Embeddings model (all-MiniLM-L6-v2)")
        except Exception as e:
            print(f"[WARNING] Local SentenceTransformer fallback error: {str(e)}")
            # Ultra lightweight fallback embedding
            self._provider = "simple-deterministic-fallback"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of document chunk texts."""
        if not texts:
            return []

        if self._embedder:
            try:
                return self._embedder.embed_documents(texts)
            except Exception as e:
                print(f"[ERROR] Embedding generation failed with {self._provider}: {str(e)}")

        # Deterministic fallback embedding generator if no model loaded
        return [self._simple_hash_embedding(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Generate vector embedding for a query string."""
        if self._embedder:
            try:
                return self._embedder.embed_query(text)
            except Exception as e:
                print(f"[ERROR] Query embedding generation failed: {str(e)}")

        return self._simple_hash_embedding(text)

    def _simple_hash_embedding(self, text: str, dim: int = 384) -> List[float]:
        """Deterministic fallback vector generator when ML models are unavailable."""
        import hashlib
        import math
        
        vec = [0.0] * dim
        words = text.lower().split()
        for i, word in enumerate(words):
            h = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            val = ((h >> 8) % 1000) / 500.0 - 1.0
            vec[idx] += val
            
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    @property
    def provider(self) -> str:
        return self._provider


# Global singleton instance
embedding_manager = EmbeddingManager()
