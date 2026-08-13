import math
import re
from typing import List, Dict, Any, Optional, Set
from collections import Counter
from app.rag.vectorstore import vector_store


class BM25Retriever:
    """Okapi BM25 Keyword Search Engine over Document Chunks."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace and non-alphanumeric tokenization."""
        return re.findall(r'\w+', text.lower())

    def search(
        self, 
        query: str, 
        corpus_chunks: List[Dict[str, Any]], 
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Calculate Okapi BM25 scores for query across candidate corpus chunks."""
        if not corpus_chunks or not query.strip():
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        doc_count = len(corpus_chunks)
        tokenized_corpus = [self._tokenize(chunk["content"]) for chunk in corpus_chunks]
        doc_lengths = [len(doc) for doc in tokenized_corpus]
        avg_doc_len = sum(doc_lengths) / doc_count if doc_count > 0 else 1.0

        # Calculate IDF for each query term
        idf = {}
        for token in set(query_tokens):
            df = sum(1 for doc in tokenized_corpus if token in doc)
            # Smooth IDF calculation
            idf[token] = math.log((doc_count - df + 0.5) / (df + 0.5) + 1.0)

        # Calculate BM25 score per document chunk
        scored_results = []
        for i, chunk in enumerate(corpus_chunks):
            doc_tokens = tokenized_corpus[i]
            doc_len = doc_lengths[i]
            tf_counts = Counter(doc_tokens)
            
            score = 0.0
            for token in query_tokens:
                if token in tf_counts:
                    tf = tf_counts[token]
                    num = tf * (self.k1 + 1)
                    denom = tf + self.k1 * (1 - self.b + self.b * (doc_len / avg_doc_len))
                    score += idf.get(token, 0.0) * (num / denom)

            if score > 0.0:
                chunk_copy = dict(chunk)
                chunk_copy["score"] = round(score, 4)
                chunk_copy["retrieval_source"] = "bm25"
                scored_results.append(chunk_copy)

        # Sort descending by BM25 score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]


class HybridRetriever:
    """Hybrid Retriever fusing Vector Cosine Similarity and Sparse BM25 Keyword Search using Reciprocal Rank Fusion (RRF)."""

    def __init__(self):
        self.bm25_engine = BM25Retriever()

    def search(
        self,
        query: str,
        corpus_chunks: List[Dict[str, Any]],
        top_k: int = 4,
        search_type: str = "hybrid",
        vector_weight: float = 0.6,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Perform search based on strategy: 'vector', 'bm25', or 'hybrid'."""
        
        # 1. Vector Dense Search
        vector_results = vector_store.vector_search(query=query, top_k=top_k * 2, document_ids=document_ids)

        if search_type == "vector":
            return vector_results[:top_k]

        # 2. BM25 Keyword Search
        bm25_results = self.bm25_engine.search(query=query, corpus_chunks=corpus_chunks, top_k=top_k * 2)

        if search_type == "bm25":
            return bm25_results[:top_k]

        # 3. Hybrid Reciprocal Rank Fusion (RRF)
        return self._reciprocal_rank_fusion(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=top_k,
            vector_weight=vector_weight
        )

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        top_k: int = 4,
        vector_weight: float = 0.6,
        rrf_k: int = 60
    ) -> List[Dict[str, Any]]:
        """Fuses ranked lists using Reciprocal Rank Fusion formula: Score = w / (k + rank)."""
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        # Process Vector Rankings
        for rank, item in enumerate(vector_results):
            cid = item["chunk_id"]
            chunk_map[cid] = item
            score = vector_weight * (1.0 / (rrf_k + rank + 1))
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + score

        # Process BM25 Rankings
        bm25_weight = 1.0 - vector_weight
        for rank, item in enumerate(bm25_results):
            cid = item["chunk_id"]
            if cid not in chunk_map:
                chunk_map[cid] = item
            score = bm25_weight * (1.0 / (rrf_k + rank + 1))
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + score

        # Sort by final RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
        
        final_results = []
        for cid in sorted_ids[:top_k]:
            item = dict(chunk_map[cid])
            item["score"] = round(rrf_scores[cid] * 100, 4)  # Scale RRF score for display
            item["retrieval_source"] = "hybrid_rrf"
            final_results.append(item)

        return final_results


# Global singleton instance
hybrid_retriever = HybridRetriever()
