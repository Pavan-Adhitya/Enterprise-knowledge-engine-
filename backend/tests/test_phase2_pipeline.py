import os
import sys
import asyncio
from pathlib import Path

# Ensure backend path is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_phase2_rag_pipeline():
    print("\n==================================================")
    print("🚀 TESTING PHASE 2: RAG INGESTION & HYBRID RETRIEVAL PIPELINE")
    print("==================================================")

    # 1. Test Health Endpoint
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    health_data = response.json()
    print(f"✅ Health Check PASSED: Service={health_data['service']}, Model={health_data['llm_model']}")

    # 2. Test Document Ingestion (Upload TXT Sample)
    sample_content = """
Enterprise Knowledge Engine Architectural Specification.

The Knowledge Engine utilizes Retrieval-Augmented Generation (RAG) to process unstructured enterprise data.
Document Ingestion converts PDF, DOCX, and TXT files into semantic vector embeddings stored in a persistent ChromaDB vector store.
Chunking strategy uses a 768 token window with 100 token overlap to preserve contextual boundaries.

Hybrid Retrieval combines dense vector cosine similarity with sparse Okapi BM25 keyword matching using Reciprocal Rank Fusion (RRF).
The LLM Generator synthesizes natural language answers with explicit inline source citations including file names, page numbers, and exact chunk text.
    """.strip()

    sample_filename = "test_enterprise_spec.txt"
    files = {"file": (sample_filename, sample_content.encode("utf-8"), "text/plain")}

    upload_res = client.post("/api/v1/documents/upload", files=files)
    assert upload_res.status_code == 201, f"Upload failed: {upload_res.text}"
    upload_data = upload_res.json()
    doc_id = upload_data["document"]["id"]
    chunk_count = upload_data["document"]["chunk_count"]
    print(f"✅ Document Upload PASSED: ID={doc_id}, Chunks Created={chunk_count}")

    # 3. Test List Documents
    list_res = client.get("/api/v1/documents")
    assert list_res.status_code == 200
    docs_list = list_res.json()
    assert any(d["id"] == doc_id for d in docs_list)
    print(f"✅ Document Listing PASSED: Total Ingested Documents={len(docs_list)}")

    # 4. Test Get Document Details
    detail_res = client.get(f"/api/v1/documents/{doc_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert len(detail_data["chunks"]) == chunk_count
    print(f"✅ Document Detail & Chunk Inspection PASSED: Retrieved {len(detail_data['chunks'])} chunk records.")

    # 5. Test Dense Vector Search
    vector_search_payload = {
        "query": "What chunking strategy is used for RAG?",
        "top_k": 2,
        "search_type": "vector"
    }
    vec_res = client.post("/api/v1/search/hybrid", json=vector_search_payload)
    assert vec_res.status_code == 200
    vec_data = vec_res.json()
    assert vec_data["total_results"] > 0
    print(f"✅ Dense Vector Search PASSED: Top match score={vec_data['results'][0]['score']}, source={vec_data['results'][0]['retrieval_source']}")

    # 6. Test Sparse BM25 Keyword Search
    bm25_search_payload = {
        "query": "Reciprocal Rank Fusion",
        "top_k": 2,
        "search_type": "bm25"
    }
    bm25_res = client.post("/api/v1/search/hybrid", json=bm25_search_payload)
    assert bm25_res.status_code == 200
    bm25_data = bm25_res.json()
    assert bm25_data["total_results"] > 0
    print(f"✅ BM25 Keyword Search PASSED: Top match score={bm25_data['results'][0]['score']}, source={bm25_data['results'][0]['retrieval_source']}")

    # 7. Test Hybrid RRF Search
    hybrid_search_payload = {
        "query": "How does Document Ingestion process PDF files into ChromaDB?",
        "top_k": 3,
        "search_type": "hybrid",
        "vector_weight": 0.6
    }
    hybrid_res = client.post("/api/v1/search/hybrid", json=hybrid_search_payload)
    assert hybrid_res.status_code == 200
    hybrid_data = hybrid_res.json()
    assert hybrid_data["total_results"] > 0
    print(f"✅ Hybrid RRF Search PASSED: Retried {hybrid_data['total_results']} chunks with source '{hybrid_data['results'][0]['retrieval_source']}'")

    # 8. Test Document Cleanup / Delete
    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 200
    print(f"✅ Document Deletion & Vector Cleanup PASSED: {del_res.json()['message']}")

    print("\n==================================================")
    print("🎉 ALL PHASE 2 PIPELINE TESTS PASSED 100% SUCCESSFULLY!")
    print("==================================================\n")


if __name__ == "__main__":
    test_phase2_rag_pipeline()
