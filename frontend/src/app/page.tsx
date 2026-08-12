'use client';

import { useState, useEffect } from 'react';
import { 
  Database, 
  Cpu, 
  FileText, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Activity, 
  Layers, 
  BookOpen, 
  Terminal,
  ShieldCheck
} from 'lucide-react';
import { fetchBackendHealth, HealthResponse } from '@/lib/api';

export default function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchBackendHealth();
      setHealth(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <main style={{ padding: '32px 48px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Top Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <span style={{ 
              background: 'var(--accent-gradient)', 
              padding: '8px', 
              borderRadius: '12px', 
              display: 'inline-flex' 
            }}>
              <Sparkles size={24} color="#fff" />
            </span>
            <h1 style={{ fontSize: '2rem' }}>
              Enterprise <span className="gradient-text">Knowledge Engine</span>
            </h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
            Next-Generation Modular Retrieval-Augmented Generation (RAG) Architecture
          </p>
        </div>

        {/* Backend Connectivity Status Badge */}
        <div className="glass-panel" style={{ padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {loading ? (
              <RefreshCw size={18} className="glow-animation" style={{ color: 'var(--accent-cyan)' }} />
            ) : error ? (
              <AlertCircle size={18} style={{ color: '#ef4444' }} />
            ) : (
              <CheckCircle2 size={18} style={{ color: 'var(--accent-emerald)' }} />
            )}
            <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>
              {loading ? 'Connecting...' : error ? 'Backend Offline' : 'Backend Connected'}
            </span>
          </div>

          <button 
            onClick={checkHealth} 
            className="btn-secondary" 
            style={{ padding: '6px 12px', fontSize: '0.85rem' }}
          >
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </header>

      {/* System Status Metrics Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', 
        gap: '20px', 
        marginBottom: '40px' 
      }}>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>System Status</span>
            <Activity size={20} color="var(--accent-emerald)" />
          </div>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {health?.status ? health.status.toUpperCase() : 'UNKNOWN'}
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '6px', display: 'block' }}>
            FastAPI Asynchronous Engine
          </span>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>Default LLM Provider</span>
            <Cpu size={20} color="var(--accent-indigo)" />
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {health?.llm_model || 'gemini-2.0-flash'}
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '6px', display: 'block' }}>
            Streaming Token Generator
          </span>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>Vector Storage Engine</span>
            <Database size={20} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            ChromaDB Persistent
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '6px', display: 'block' }}>
            Embedding Model: {health?.embedding_model || 'models/embedding-001'}
          </span>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>Architecture Phase</span>
            <Layers size={20} color="var(--accent-purple)" />
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--accent-purple)' }}>
            Phase 1 Skeleton
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '6px', display: 'block' }}>
            Infrastructure Verified
          </span>
        </div>
      </div>

      {/* Main Grid: Pipeline Overview & Verification Checklist */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        
        {/* Architecture Components Card */}
        <div className="glass-panel" style={{ padding: '32px' }}>
          <h2 style={{ fontSize: '1.4rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BookOpen size={22} color="var(--accent-indigo)" />
            RAG Pipeline Architecture Layout
          </h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ 
              background: 'rgba(255,255,255,0.02)', 
              border: '1px solid var(--border-color)', 
              borderRadius: 'var(--radius-md)', 
              padding: '18px' 
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--accent-cyan)' }}>
                <FileText size={18} />
                <h4 style={{ fontSize: '1rem' }}>1. Ingestion & Splitter</h4>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Multi-format parser for PDF, DOCX, & TXT. Recursive text chunking with 768 token window and 100 token overlap.
              </p>
            </div>

            <div style={{ 
              background: 'rgba(255,255,255,0.02)', 
              border: '1px solid var(--border-color)', 
              borderRadius: 'var(--radius-md)', 
              padding: '18px' 
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--accent-purple)' }}>
                <Database size={18} />
                <h4 style={{ fontSize: '1rem' }}>2. Vector Embeddings</h4>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Dense vector representation via Google Gemini Embeddings / HuggingFace stored persistently in ChromaDB.
              </p>
            </div>

            <div style={{ 
              background: 'rgba(255,255,255,0.02)', 
              border: '1px solid var(--border-color)', 
              borderRadius: 'var(--radius-md)', 
              padding: '18px' 
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--accent-indigo)' }}>
                <Activity size={18} />
                <h4 style={{ fontSize: '1rem' }}>3. Hybrid Retriever</h4>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Top-K Cosine Similarity retrieval combined with BM25 keyword matching for optimal search precision.
              </p>
            </div>

            <div style={{ 
              background: 'rgba(255,255,255,0.02)', 
              border: '1px solid var(--border-color)', 
              borderRadius: 'var(--radius-md)', 
              padding: '18px' 
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: 'var(--accent-emerald)' }}>
                <Sparkles size={18} />
                <h4 style={{ fontSize: '1rem' }}>4. Grounded Synthesis</h4>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Streaming response generation with explicit inline source citations (Document Name, Page, & Snippet).
              </p>
            </div>
          </div>
        </div>

        {/* Phase 1 Verification Checklist Card */}
        <div className="glass-panel" style={{ padding: '32px' }}>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldCheck size={20} color="var(--accent-emerald)" />
            Phase 1 Checklist
          </h3>

          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <li style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem' }}>
              <CheckCircle2 size={16} color="var(--accent-emerald)" />
              <span>Project Monorepo Directory Layout</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem' }}>
              <CheckCircle2 size={16} color="var(--accent-emerald)" />
              <span>FastAPI Backend Server & Config</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem' }}>
              <CheckCircle2 size={16} color="var(--accent-emerald)" />
              <span>Async SQLite Database & ORM</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem' }}>
              <CheckCircle2 size={16} color="var(--accent-emerald)" />
              <span>Next.js 14 App Router & Design System</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem' }}>
              <CheckCircle2 size={16} color="var(--accent-emerald)" />
              <span>Cross-Origin API Bridge & Proxy</span>
            </li>
          </ul>

          <div style={{ 
            marginTop: '24px', 
            padding: '14px', 
            background: 'rgba(99, 102, 241, 0.1)', 
            borderRadius: 'var(--radius-sm)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)'
          }}>
            <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '4px' }}>
              <Terminal size={14} style={{ display: 'inline', marginRight: '6px' }} />
              Ready for Phase 2 Implementation
            </strong>
            Once Phase 1 verification completes, Phase 2 will implement document ingestion & vector search pipelines.
          </div>
        </div>

      </div>
    </main>
  );
}
