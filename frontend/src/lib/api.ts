export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  uptime_seconds: number;
  llm_model: string;
  embedding_model: string;
}

// Fallback to direct backend URL if proxy or environment variable is unset
const PRIMARY_API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
const FALLBACK_API_URL = 'http://127.0.0.1:8000/api/v1';

export async function fetchBackendHealth(): Promise<HealthResponse> {
  try {
    const res = await fetch(`${PRIMARY_API_URL}/health`, {
      cache: 'no-store',
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // Retry with direct fallback if rewrite proxy failed
  }

  try {
    const res = await fetch(`${FALLBACK_API_URL}/health`, {
      cache: 'no-store',
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error('Backend health check failed:', error);
    throw error;
  }
}
