from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.search import SearchQuery, HybridSearchResponse
from app.services.document_service import DocumentService
from app.rag.retriever import hybrid_retriever

router = APIRouter()


@router.post(
    "/hybrid",
    response_model=HybridSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Dense, BM25, or Hybrid Vector Search"
)
async def perform_search(
    query_payload: SearchQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Search over document chunks using:
    - **vector**: Dense Cosine Similarity vector search via ChromaDB
    - **bm25**: Sparse Okapi BM25 keyword matching
    - **hybrid**: Reciprocal Rank Fusion (RRF) combining dense & sparse search
    """
    # Fetch document chunks corpus for BM25 ranking if needed
    corpus_chunks = await DocumentService.get_all_corpus_chunks(db)
    
    if not corpus_chunks:
        return HybridSearchResponse(
            query=query_payload.query,
            search_type=query_payload.search_type,
            total_results=0,
            results=[]
        )

    results = hybrid_retriever.search(
        query=query_payload.query,
        corpus_chunks=corpus_chunks,
        top_k=query_payload.top_k,
        search_type=query_payload.search_type,
        vector_weight=query_payload.vector_weight,
        document_ids=query_payload.document_ids
    )

    return HybridSearchResponse(
        query=query_payload.query,
        search_type=query_payload.search_type,
        total_results=len(results),
        results=results
    )
