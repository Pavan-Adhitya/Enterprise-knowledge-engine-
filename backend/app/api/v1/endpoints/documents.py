from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.document import (
    DocumentResponse, 
    DocumentDetailResponse, 
    DocumentUploadResponse
)
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/upload", 
    response_model=DocumentUploadResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Ingest Document"
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a PDF, DOCX, or TXT file to parse, chunk, embed, and index into ChromaDB."""
    document = await DocumentService.process_and_ingest_document(db, file)
    return DocumentUploadResponse(
        message=f"Successfully uploaded and indexed '{file.filename}' into vector store ({document.chunk_count} chunks).",
        document=document
    )


@router.get(
    "", 
    response_model=List[DocumentResponse],
    summary="List Uploaded Documents"
)
async def list_documents(db: AsyncSession = Depends(get_db)):
    """Fetch list of all ingested documents and their status."""
    return await DocumentService.get_all_documents(db)


@router.get(
    "/{doc_id}", 
    response_model=DocumentDetailResponse,
    summary="Get Document Details & Chunks"
)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch detailed metadata and chunk list for a specific document ID."""
    document = await DocumentService.get_document_by_id(db, doc_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{doc_id}' not found."
        )
    return document


@router.delete(
    "/{doc_id}", 
    status_code=status.HTTP_200_OK,
    summary="Delete Document"
)
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """Delete document from database, vector storage, and disk."""
    success = await DocumentService.delete_document(db, doc_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{doc_id}' not found."
        )
    return {"message": f"Document '{doc_id}' and all associated vector embeddings successfully deleted."}
