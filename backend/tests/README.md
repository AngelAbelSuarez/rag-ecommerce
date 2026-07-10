# Backend Tests

Test suite for the BimBam Chatbot backend. Uses **pytest** with `pytest-cov` for coverage reporting.

## Structure

```
tests/
├── conftest.py         # Path setup (adds backend/ to sys.path)
├── test_app.py         # HTTP API tests (FastAPI TestClient)
├── test_config.py      # Configuration model tests (pydantic-settings)
├── test_ingest.py      # Ingestion pipeline tests (PDF → chunks → ChromaDB)
├── test_rag.py         # RAG chain tests (retrieval + prompt + LLM)
└── test_store.py       # Vector store tests (ChromaDB client + retrievers)
```

## Running tests

```bash
# From the backend/ directory
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Single file
pytest tests/test_app.py -v
```

## Test coverage

| File          | Tests | What it covers                                      |
|---------------|-------|-----------------------------------------------------|
| `test_app.py` | 21    | Health endpoint, chat SSE streaming, auto-ingest, error handling, request/response models |
| `test_rag.py` | 12    | Chain building, streaming answers, context formatting, rate-limit retries, fallback on empty context |
| `test_ingest.py` | 16 | PDF extraction (pypdf + pdfplumber fallback), chunking, ingest success/failure, main CLI |
| `test_store.py`  | 5  | Embeddings factory, vector store creation, retriever defaults and overrides |
| `test_config.py` | 4  | Chroma path resolution, documents path defaults and overrides |

**Total: 58 tests**

## Test design

### conftest.py

Adds the `backend/` directory to `sys.path` so imports like `from config import Settings` work without `PYTHONPATH` manipulation.

### test_app.py

Uses FastAPI's `TestClient` with monkeypatched dependencies:

- `client` fixture disables auto-ingest and sets an empty API key (for error-path testing)
- `client_with_key` fixture sets a fake API key and base URL (for success-path testing)
- Tests cover: `GET /api/health` (200, 503), `POST /api/chat` (SSE streaming, 422, 500), auto-ingest lifecycle, SSE event formatting, and lifespan events

### test_rag.py

Tests the RAG chain in isolation:

- `no_api_key` / `fake_api_key` fixtures control NVIDIA key presence
- Verifies chain building returns a `RunnableSerializable`
- Tests `stream_answer` with mocked retrievers (empty, with docs, rate-limited, errored)
- Validates prompt templates, context formatting, and fallback responses

### test_ingest.py

Tests the ingestion pipeline with real generated PDFs (via `reportlab`):

- `sample_pdf` and `empty_page_pdf` fixtures create temporary PDFs
- Tests both pypdf and pdfplumber extractors, including fallback behavior when pypdf fails
- Tests chunk splitting respects `CHUNK_SIZE`
- Tests full `ingest()` with mocked ChromaDB
- Tests CLI `main()` entry point

### test_store.py

Tests the ChromaDB client factory:

- Creates real `NVIDIAEmbeddings` instances (with fake API key)
- Creates real `Chroma` vector stores in temporary directories
- Tests retriever creation with default and custom `k` values

### test_config.py

Tests the `Settings` model from `config.py`:

- Verifies `chroma_path` resolves relative to `backend/`
- Verifies `documents_path` defaults to project root `documents/`
- Verifies `documents_dir` env var override
