export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  uptime_seconds: number;
  llm_model: string;
  embedding_model: string;
}

export interface DocumentResponse {
  id: str;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  error_message?: string;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  chunk_index: number;
  content: string;
  page_number?: number;
  token_count: number;
  vector_id: string;
  created_at: string;
}

export interface DocumentDetailResponse extends DocumentResponse {
  chunks: DocumentChunk[];
}

export interface SearchQueryPayload {
  query: string;
  top_k?: number;
  document_ids?: string[];
  search_type?: 'vector' | 'bm25' | 'hybrid';
  vector_weight?: number;
}

export interface SearchResultChunk {
  chunk_id: string;
  document_id: string;
  filename: string;
  page_number?: number;
  chunk_index: number;
  content: string;
  score: number;
  retrieval_source: string;
}

export interface HybridSearchResponse {
  query: string;
  search_type: string;
  total_results: number;
  results: SearchResultChunk[];
}

const PRIMARY_API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
const FALLBACK_API_URL = 'http://127.0.0.1:8000/api/v1';

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${PRIMARY_API_URL}${endpoint}`, {
      ...options,
      cache: 'no-store',
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Retry with fallback URL
  }

  const res = await fetch(`${FALLBACK_API_URL}${endpoint}`, {
    ...options,
    cache: 'no-store',
  });

  if (!res.ok) {
    let errorDetail = `HTTP error! status: ${res.status}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {}
    throw new Error(errorDetail);
  }

  return await res.json();
}

export async function fetchBackendHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health');
}

export async function uploadDocument(file: File): Promise<{ message: string; document: DocumentResponse }> {
  const formData = new FormData();
  formData.append('file', file);
  return apiFetch<{ message: string; document: DocumentResponse }>('/documents/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function fetchDocuments(): Promise<DocumentResponse[]> {
  return apiFetch<DocumentResponse[]>('/documents');
}

export async function fetchDocumentDetail(docId: string): Promise<DocumentDetailResponse> {
  return apiFetch<DocumentDetailResponse>(`/documents/${docId}`);
}

export async function deleteDocument(docId: string): Promise<{ message: string }> {
  return apiFetch<{ message: string }>(`/documents/${docId}`, {
    method: 'DELETE',
  });
}

export async function searchHybrid(payload: SearchQueryPayload): Promise<HybridSearchResponse> {
  return apiFetch<HybridSearchResponse>('/search/hybrid', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}
