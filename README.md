# Enterprise Knowledge Engine (RAG)

An enterprise-grade, modular **Retrieval-Augmented Generation (RAG)** platform built with Python FastAPI, Next.js 14, ChromaDB, and Large Language Models (Google Gemini API).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)

---

## 🌟 Key Features

- 📄 **Multi-Format Document Parsing**: Upload PDF, DOCX, and TXT files with metadata extraction.
- ✂️ **Context-Preserving Chunking**: Recursive character text splitting with overlapping windows.
- 🧠 **Vector Embeddings & Storage**: High-density semantic vectors stored in a persistent ChromaDB database.
- 🔎 **Hybrid Retrieval**: Top-K Cosine Similarity retrieval combined with keyword matching.
- ⚡ **Streaming Grounded Synthesis**: Real-time streaming LLM response tokens with explicit inline source citations.
- 🎨 **Modern Glassmorphic UI**: Sleek dark-mode dashboard built with Next.js 14 App Router.

---

## 🏗️ System Architecture

```
                                    +------------------------------+
                                    | Next.js 14 Web Dashboard     |
                                    +--------------+---------------+
                                                   |
                                                   v HTTP / SSE / API Proxy
                                    +--------------+---------------+
                                    | FastAPI Asynchronous Server  |
                                    +--------------+---------------+
                                                   |
                   +-------------------------------+-------------------------------+
                   |                                                               |
                   v                                                               v
    +--------------+---------------+                               +---------------+--------------+
    | Document Ingestion Pipeline  |                               | RAG Retrieval & Synthesis    |
    | (PyPDF -> Chunker -> Embed)  |                               | (ChromaDB -> Prompt -> Gemini)|
    +--------------+---------------+                               +---------------+--------------+
                   |                                                               |
                   v                                                               v
    +--------------+---------------+                               +---------------+--------------+
    | ChromaDB Vector Store        |                               | Google Gemini LLM API        |
    +------------------------------+                               +------------------------------+
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone & Set Up Backend

```bash
cd backend
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install backend dependencies:
pip install -r requirements.txt

# Start backend server:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Set Up Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📁 Repository Structure

```
Enterprise-knowledge-engine/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API Router endpoints
│   │   ├── core/            # Database, CORS, and Pydantic configuration
│   │   ├── models/          # ORM database models
│   │   ├── rag/             # RAG ingestion, vectorstore, & generator engine
│   │   └── main.py          # FastAPI application entry point
│   ├── storage/             # Document uploads & ChromaDB vector database
│   ├── requirements.txt     # Backend dependencies
│   └── .env.example         # Environment template
│
└── frontend/
    ├── src/
    │   ├── app/             # Next.js 14 App Router layout & page
    │   ├── lib/             # API client & HTTP stream helpers
    │   └── styles/          # Modern Glassmorphic CSS design system
    ├── package.json         # Frontend dependencies
    └── next.config.mjs      # Proxy rewrites
```

---

## 📜 License
Licensed under the [MIT License](LICENSE).
