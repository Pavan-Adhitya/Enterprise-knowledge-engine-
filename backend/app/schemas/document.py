from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.document import DocumentStatus


class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    token_count: int
    vector_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    error_message: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []


class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse
