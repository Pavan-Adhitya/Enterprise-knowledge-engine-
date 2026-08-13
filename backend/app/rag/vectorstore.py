import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.rag.embedder import embedding_manager
from app.rag.chunker import TextChunk


class VectorStoreManager:
    """Persistent ChromaDB Vector Database Manager."""

    COLLECTION_NAME = "enterprise_knowledge_base"

    def __init__(self):
        persist_dir = str(settings.chroma_path)
        os.makedirs(persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection with cosine similarity metric
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(
        self, 
        document_id: str, 
        filename: str, 
        chunks: List[TextChunk]
    ) -> List[str]:
        """Store document chunks and their generated vector embeddings into ChromaDB."""
        if not chunks:
            return []

        ids = [f"{document_id}_chunk_{c.chunk_index}" for c in chunks]
        texts = [c.content for c in chunks]
        
        # Generate embeddings
        embeddings = embedding_manager.embed_documents(texts)
        
        # Construct metadata payloads
        metadatas = [
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": c.chunk_index,
                "page_number": c.page_number if c.page_number is not None else 0,
                "character_count": c.character_count,
                "token_count": c.token_count
            }
            for c in chunks
        ]

        # Upsert into ChromaDB
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        return ids

    def vector_search(
        self, 
        query: str, 
        top_k: int = 4, 
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Perform dense Cosine Similarity vector search."""
        query_embedding = embedding_manager.embed_query(query)
        
        where_clause = None
        if document_ids and len(document_ids) > 0:
            if len(document_ids) == 1:
                where_clause = {"document_id": document_ids[0]}
            else:
                where_clause = {"document_id": {"$in": document_ids}}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and results.get("ids") and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for i in range(len(ids)):
                # Convert cosine distance to similarity score (0.0 to 1.0)
                distance = distances[i]
                similarity_score = max(0.0, 1.0 - distance)
                
                meta = metas[i]
                formatted_results.append({
                    "chunk_id": ids[i],
                    "document_id": meta.get("document_id"),
                    "filename": meta.get("filename"),
                    "page_number": meta.get("page_number") if meta.get("page_number") != 0 else None,
                    "chunk_index": meta.get("chunk_index"),
                    "content": docs[i],
                    "score": round(similarity_score, 4),
                    "retrieval_source": "vector"
                })

        return formatted_results

    def delete_document_chunks(self, document_id: str) -> None:
        """Delete all stored vector embeddings belonging to a specific document."""
        try:
            self.collection.delete(where={"document_id": document_id})
        except Exception as e:
            print(f"[WARNING] Error deleting vector chunks for document {document_id}: {str(e)}")


# Global singleton instance
vector_store = VectorStoreManager()
