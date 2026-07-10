# BimBam Chatbot — Backend

REST API with RAG (Retrieval-Augmented Generation) for the BimBam Buy virtual assistant, a LATAM e-commerce platform. Built with **FastAPI**, **LangChain** and **ChromaDB**, using **NVIDIA AI Endpoints** models.

## Stack

| Layer          | Technology                                                       |
| -------------- | ---------------------------------------------------------------- |
| Framework      | FastAPI + Uvicorn                                                |
| RAG pipeline   | LangChain LCEL                                                   |
| Vector store   | ChromaDB (persistent, local)                                     |
| Embeddings     | `nvidia/nv-embed-v1` via NVIDIA AI Endpoints                     |
| LLM            | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` via NVIDIA AI Endpoints |
| PDF extraction | pypdf + pdfplumber (fallback)                                    |

## Structure

```
backend/
├── app.py              # FastAPI app, endpoints, SSE streaming
├── config.py           # Centralized config via pydantic-settings + .env
├── ingest.py           # Offline ingestion pipeline (PDF → chunks → ChromaDB)
├── rag.py              # RAG chain (retrieval + prompt + LLM)
├── store.py            # ChromaDB client and retriever factory
├── test_query.py       # Interactive CLI for testing queries
├── requirements.txt    # Python dependencies
├── .env.example        # Configuration template
├── .env                # Local config (gitignored)
├── chroma_db/          # Local ChromaDB persistence (gitignored)
└── tests/
    ├── conftest.py
    ├── test_app.py     # HTTP API tests
    ├── test_ingest.py  # Ingestion pipeline tests
    ├── test_rag.py     # RAG chain tests
    └── test_store.py   # Vector store tests
```

## Requirements

- Python 3.13+
- NVIDIA API key ([build.nvidia.com](https://build.nvidia.com))

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and add NVIDIA_API_KEY=nvapi-...
```

## Usage

### Document ingestion

Place PDFs in `documents/` (project root) and run:

```bash
python backend/ingest.py
```

This extracts text, splits it into chunks, generates embeddings, and persists them to `backend/chroma_db/`.

### API Server

```bash
uvicorn app:app --reload --port 8000
```

The API is available at `http://localhost:8000`.

### Interactive documentation

FastAPI automatically generates:

- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Endpoints

### `GET /api/health`

Returns ChromaDB and LLM status.

```json
// 200 — all good
{ "status": "healthy", "chromadb": "connected", "llm": "available" }

// 503 — degraded
{ "status": "degraded", "chromadb": "disconnected", "llm": "unavailable" }
```

### `POST /api/chat`

**Request:**

```json
{ "message": "what is the delivery time?", "conversation_id": "abc-123" }
```

**Response:** Server-Sent Events (SSE) with live LLM tokens.

```
data: The
data: delivery
data: time
data: is
...
data: [DONE]
```

On error:

```
event: error
data: {"message": "The service is congested, please try again in a few seconds"}
```

## Tests

```bash
# All tests
pytest tests/ -v

# By file
pytest tests/test_app.py -v
pytest tests/test_rag.py -v
```

## Environment configuration

| Variable               | Default                                         | Description                        |
| ---------------------- | ----------------------------------------------- | ---------------------------------- |
| `NVIDIA_API_KEY`       | `""`                                            | NVIDIA API key (required)          |
| `NVIDIA_BASE_URL`      | `https://integrate.api.nvidia.com/v1`           | NVIDIA API base URL                |
| `EMBEDDING_MODEL`      | `nvidia/nv-embed-v1`                            | Embedding model                    |
| `CHAT_MODEL`           | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1`      | Chat model                         |
| `CHROMA_PERSIST_DIR`   | `chroma_db`                                     | Persistence directory              |
| `COLLECTION_NAME`      | `bimbam_docs`                                   | ChromaDB collection name           |
| `CHUNK_SIZE`           | `600`                                           | Chunk size for ingestion           |
| `CHUNK_OVERLAP`        | `80`                                            | Overlap between chunks             |
| `RETRIEVER_K`          | `4`                                             | Number of documents to retrieve    |
| `SIMILARITY_THRESHOLD` | `0.0`                                           | Minimum similarity threshold       |
| `LOG_LEVEL`            | `INFO`                                          | Log level                          |
| `REQUEST_TIMEOUT`      | `30.0`                                          | Timeout for NVIDIA API calls       |
