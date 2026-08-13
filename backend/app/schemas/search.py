from typing import List, Optional
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    top_k: int = Field(default=4, ge=1, le=20, description="Number of top chunks to retrieve")
    document_ids: Optional[List[str]] = Field(default=None, description="Optional document ID filter")
    search_type: str = Field(default="hybrid", description="Search strategy: 'vector', 'bm25', or 'hybrid'")
    vector_weight: float = Field(default=0.6, ge=0.0, le=1.0, description="Weight for vector search in hybrid mode")


class SearchResultChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: Optional[int]
    chunk_index: int
    content: str
    score: float
    retrieval_source: str  # "vector", "bm25", or "hybrid_rrf"


class HybridSearchResponse(BaseModel):
    query: str
    search_type: str
    total_results: int
    results: List[SearchResultChunk]
