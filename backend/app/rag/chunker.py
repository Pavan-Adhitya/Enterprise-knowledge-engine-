from typing import List, Optional
from pydantic import BaseModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.loader import LoadedDocument
from app.core.config import settings


class TextChunk(BaseModel):
    chunk_index: int
    content: str
    page_number: Optional[int]
    character_count: int
    token_count: int


class DocumentChunker:
    """Text chunking manager using RecursiveCharacterTextSplitter with overlap preservation."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.DEFAULT_CHUNK_OVERLAP
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )

    def chunk_document(self, doc: LoadedDocument) -> List[TextChunk]:
        """Split loaded document pages into TextChunk models."""
        chunks: List[TextChunk] = []
        global_chunk_index = 0

        for page in doc.pages:
            split_texts = self.splitter.split_text(page.content)
            for text in split_texts:
                if not text.strip():
                    continue
                
                # Approximate token count (~4 characters per token average)
                approx_tokens = max(1, len(text) // 4)
                
                chunks.append(TextChunk(
                    chunk_index=global_chunk_index,
                    content=text.strip(),
                    page_number=page.page_number,
                    character_count=len(text),
                    token_count=approx_tokens
                ))
                global_chunk_index += 1

        return chunks
