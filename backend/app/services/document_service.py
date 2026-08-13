import os
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.rag.loader import DocumentLoader
from app.rag.chunker import DocumentChunker
from app.rag.vectorstore import vector_store


class DocumentService:
    """Business service handling document upload, ingestion pipeline execution, and vector storage."""

    @staticmethod
    async def process_and_ingest_document(
        db: AsyncSession, 
        file: UploadFile
    ) -> Document:
        """Save file, parse content, split chunks, generate embeddings, and record in DB."""
        # 1. Validate file extension
        file_ext = Path(file.filename).suffix.lower().lstrip(".")
        allowed_extensions = ["pdf", "docx", "doc", "txt", "md", "markdown", "log"]
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '.{file_ext}'. Allowed formats: {', '.join(allowed_extensions)}"
            )

        # 2. Save raw file to uploads directory
        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{Path(file.filename).name}"
        saved_file_path = settings.uploads_path / safe_filename
        
        try:
            content_bytes = await file.read()
            if len(content_bytes) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uploaded file is empty (0 bytes)."
                )

            with open(saved_file_path, "wb") as f:
                f.write(content_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded file to storage: {str(e)}"
            )

        # 3. Create initial Document record in DB with PENDING status
        document_record = Document(
            id=doc_id,
            filename=file.filename,
            file_type=file_ext,
            file_size=len(content_bytes),
            file_path=str(saved_file_path),
            status=DocumentStatus.PROCESSING,
            chunk_count=0
        )
        db.add(document_record)
        await db.commit()
        await db.refresh(document_record)

        # 4. Execute RAG Ingestion Pipeline
        try:
            # Step A: Parse raw file text
            loaded_doc = DocumentLoader.load(saved_file_path)
            
            # Step B: Split text into overlapping chunks
            chunker = DocumentChunker()
            text_chunks = chunker.chunk_document(loaded_doc)

            if not text_chunks:
                raise ValueError("No readable text chunks extracted from file.")

            # Step C: Generate Embeddings & Store in ChromaDB
            vector_ids = vector_store.add_chunks(
                document_id=doc_id,
                filename=file.filename,
                chunks=text_chunks
            )

            # Step D: Save DocumentChunks to SQLite DB
            db_chunks = []
            for i, chunk in enumerate(text_chunks):
                vec_id = vector_ids[i] if i < len(vector_ids) else f"{doc_id}_chunk_{chunk.chunk_index}"
                db_chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=doc_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    token_count=chunk.token_count,
                    vector_id=vec_id
                )
                db_chunks.append(db_chunk)

            db.add_all(db_chunks)
            
            # Update Document status to COMPLETED
            document_record.status = DocumentStatus.COMPLETED
            document_record.chunk_count = len(text_chunks)
            await db.commit()
            await db.refresh(document_record)

            return document_record

        except Exception as e:
            # Handle pipeline failure
            document_record.status = DocumentStatus.FAILED
            document_record.error_message = str(e)
            await db.commit()
            await db.refresh(document_record)
            print(f"[ERROR] Document Ingestion failed for {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Document processing failed: {str(e)}"
            )

    @staticmethod
    async def get_all_documents(db: AsyncSession) -> List[Document]:
        """Fetch list of all uploaded documents."""
        stmt = select(Document).order_by(Document.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_document_by_id(db: AsyncSession, doc_id: str) -> Optional[Document]:
        """Fetch document details including associated chunks."""
        stmt = select(Document).options(selectinload(Document.chunks)).where(Document.id == doc_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_document(db: AsyncSession, doc_id: str) -> bool:
        """Delete document from DB, ChromaDB vector store, and local filesystem."""
        document = await DocumentService.get_document_by_id(db, doc_id)
        if not document:
            return False

        # 1. Delete vector embeddings from ChromaDB
        vector_store.delete_document_chunks(doc_id)

        # 2. Delete raw file from local storage
        if os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                print(f"[WARNING] Could not delete raw file {document.file_path}: {str(e)}")

        # 3. Delete database record
        await db.delete(document)
        await db.commit()
        return True

    @staticmethod
    async def get_all_corpus_chunks(db: AsyncSession) -> List[Dict[str, Any]]:
        """Fetch all chunks across completed documents for BM25 keyword index building."""
        stmt = (
            select(DocumentChunk, Document.filename)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.status == DocumentStatus.COMPLETED)
        )
        result = await db.execute(stmt)
        rows = result.all()

        corpus = []
        for chunk, filename in rows:
            corpus.append({
                "chunk_id": chunk.vector_id,
                "document_id": chunk.document_id,
                "filename": filename,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content
            })

        return corpus
