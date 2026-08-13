import asyncio
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import AsyncSessionLocal, init_db
from app.rag.loader import DocumentLoader
from app.rag.chunker import DocumentChunker
from app.rag.vectorstore import vector_store
from app.rag.retriever import hybrid_retriever
from app.services.document_service import DocumentService
from app.schemas.search import SearchQuery


async def run_phase2_verification():
    print("\n==================================================")
    print("[INFO] DIRECT PHASE 2 PIPELINE VERIFICATION")
    print("==================================================")

    # 1. Initialize DB tables
    await init_db()
    print("[SUCCESS] 1. Database schema initialized successfully.")

    # 2. Test Document Loader with a sample text file
    sample_file_path = Path(__file__).resolve().parent / "sample_rag_doc.txt"
    sample_text = """
Enterprise Knowledge Engine Architectural Specification.

The Knowledge Engine utilizes Retrieval-Augmented Generation (RAG) to process unstructured enterprise data.
Document Ingestion converts PDF, DOCX, and TXT files into semantic vector embeddings stored in a persistent ChromaDB vector store.
Chunking strategy uses a 768 token window with 100 token overlap to preserve contextual boundaries.

Hybrid Retrieval combines dense vector cosine similarity with sparse Okapi BM25 keyword matching using Reciprocal Rank Fusion (RRF).
The LLM Generator synthesizes natural language answers with explicit inline source citations including file names, page numbers, and exact chunk text.
    """.strip()

    with open(sample_file_path, "w", encoding="utf-8") as f:
        f.write(sample_text)

    loaded_doc = DocumentLoader.load(sample_file_path)
    print(f"[SUCCESS] 2. DocumentLoader PASSED: Loaded '{loaded_doc.filename}' ({loaded_doc.total_characters} characters, {len(loaded_doc.pages)} pages)")

    # 3. Test Document Chunker
    chunker = DocumentChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.chunk_document(loaded_doc)
    print(f"[SUCCESS] 3. DocumentChunker PASSED: Generated {len(chunks)} text chunks.")

    # 4. Test ChromaDB Vector Store Insertion
    doc_id = "test_doc_phase2_demo"
    vector_ids = vector_store.add_chunks(document_id=doc_id, filename=sample_file_path.name, chunks=chunks)
    print(f"[SUCCESS] 4. ChromaDB VectorStore PASSED: Indexed {len(vector_ids)} vectors into collection.")

    # 5. Test Dense Vector Search
    vector_results = vector_store.vector_search(query="What chunking strategy is used?", top_k=2)
    assert len(vector_results) > 0
    print(f"[SUCCESS] 5. Dense Vector Search PASSED: Retried chunk '{vector_results[0]['chunk_id']}' with score={vector_results[0]['score']}")

    # 6. Test BM25 Keyword Search & Hybrid RRF Search
    corpus_chunks = [
        {
            "chunk_id": f"{doc_id}_chunk_{c.chunk_index}",
            "document_id": doc_id,
            "filename": sample_file_path.name,
            "page_number": c.page_number,
            "chunk_index": c.chunk_index,
            "content": c.content
        }
        for c in chunks
    ]

    hybrid_results = hybrid_retriever.search(
        query="Reciprocal Rank Fusion hybrid retrieval",
        corpus_chunks=corpus_chunks,
        top_k=2,
        search_type="hybrid"
    )
    assert len(hybrid_results) > 0
    print(f"[SUCCESS] 6. Hybrid RRF Search PASSED: Top match score={hybrid_results[0]['score']}, source={hybrid_results[0]['retrieval_source']}")

    # 7. Cleanup ChromaDB & Sample File
    vector_store.delete_document_chunks(doc_id)
    if os.path.exists(sample_file_path):
        os.remove(sample_file_path)
    print("[SUCCESS] 7. Vector Cleanup PASSED.")

    print("\n==================================================")
    print("[SUCCESS] ALL PHASE 2 PIPELINE VERIFICATIONS PASSED 100%!")
    print("==================================================\n")


if __name__ == "__main__":
    asyncio.run(run_phase2_verification())
