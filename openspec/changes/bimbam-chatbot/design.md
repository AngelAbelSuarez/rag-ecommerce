# Design: BimBam Chatbot — RAG Agent sobre PDFs de E-commerce

## Technical Approach

Monorepo greenfield: `backend/` (FastAPI + LangChain + ChromaDB) y `frontend/` (React 19 + Vite + Tailwind + shadcn/ui). Ingesta offline vía script separado. Chat runtime: query → embedding → ChromaDB (top-4) → prompt → LLM → SSE streaming.

```
documents/PDFs --> ingest.py --> chroma_db/
                                    |
POST /api/chat --> rag.py --> similarity_search(k=4) --> OpenRouter LLM
                     |                                      |
                     +-- SSE --> ChatArea (stream token x token)
```

## Architecture Decisions

| Decision | Choice | Rejected | Rationale |
|----------|--------|----------|-----------|
| Module split | store.py / rag.py / app.py | Single file | Testable independently; store swap trivial |
| ChromaDB mode | Persistent (disk) | In-memory | Survives restart; chroma_db/ in .gitignore |
| Chunking | RecursiveCharacterTextSplitter(500, 50) | Semantic chunking | Simple, predictable; overlap guards cross-page refs |
| PDF loader | pypdf strict=False, fallback pdfplumber | PyMuPDF (AGPL) | License-safe; handles LATAM encoding |
| Streaming | SSE via StreamingResponse | WebSocket | Unidirectional enough; simpler client parse |
| Retry | tenacity exp backoff 1s→8s, max 3 | None / infinite loop | Bounded degradation under free-tier limits |
| Similarity filter | score < 0.3 → no-info response | No threshold | Prevents hallucination on out-of-domain queries |
| Dark mode | CSS custom props + class=dark on html | next-themes | Zero deps; localStorage before first paint avoids flash |
| Frontend sessions | useState in memory | IndexedDB | Out of scope: no cross-session persistence |

## Data Flow

### RAG Pipeline

```
POST /api/chat  {"message": "..."}
  -> Embed query (llama-nemotron-embed-vl-1b-v2:free)
  -> ChromaDB.similarity_search(query_embedding, k=4)
  -> filter by score >= 0.3
  -> format_context(chunks) -> "Documento {source} (pag {page}):\n{content}"
  -> ChatOpenAI(model="nvidia/nemotron-3-ultra", temperature=0.3, streaming=True)
  -> SSE: data: token\ndata: token\n...\ndata: [DONE]
```

### SSE Event Protocol

| Event | Payload | Meaning |
|-------|---------|---------|
| (none) | data: {text} | Token chunk — append to bubble |
| (none) | data: [DONE] | Stream complete |
| event: error | data: {"message":"..."} | Backend error — show toast |

## Backend Design

### Directory

```
backend/
  app.py           # FastAPI: POST /api/chat, GET /api/health, CORS
  rag.py           # build_chain(): retriever | prompt | llm | StrOutputParser
  store.py         # get_vectorstore(), get_retriever(k=4, score_threshold=0.3)
  ingest.py        # Offline: load PDFs -> split -> embed -> persist
  test_query.py    # CLI: --query --api-key, invokes rag.py
  config.py        # Centralized env vars
  requirements.txt # fastapi, uvicorn, langchain, chromadb, openai, pypdf, pdfplumber, tenacity, python-dotenv
  tests/
    test_store.py   # add_documents, similarity_search
    test_rag.py     # Chain assembly, prompt structure
    test_ingest.py  # Text extraction, chunk count, metadata
    test_app.py     # /health 200/503, /chat SSE, error paths
```

### Endpoints

| Endpoint | Method | Success | Error |
|----------|--------|---------|-------|
| /api/health | GET | 200 {status, chromadb, llm} | 503 if ChromaDB unreachable |
| /api/chat | POST | text/event-stream SSE | 422 (FastAPI auto), 503 (LLM down after retries), 500 |

### Error Matrix

| Condition | Result |
|-----------|--------|
| Invalid JSON body | 422 (FastAPI auto-validation) |
| OPENROUTER_API_KEY unset | 500 + log "Backend misconfiguration" |
| ChromaDB empty collection | 200 — prompt returns polite "no info" |
| OpenRouter 429 | tenacity: 1s, 2s, 4s — max 3 attempts, then 503 |
| LLM timeout >30s | SSE error event, log query |
| ChromaDB disconnected | 503 health, chat returns SSE error |

### OpenRouter Config

```
ChatOpenAI(
  model="nvidia/nemotron-3-ultra",
  openai_api_base="https://openrouter.ai/api/v1",
  api_key=os.environ["OPENROUTER_API_KEY"],
  temperature=0.3,
  streaming=True,
  timeout=30,
  max_retries=0  # we handle retries via tenacity
)

OpenAIEmbeddings(
  model="llama-nemotron-embed-vl-1b-v2:free",
  openai_api_base="https://openrouter.ai/api/v1",
  api_key=os.environ["OPENROUTER_API_KEY"]
)
```

## Frontend Design

### Component Tree

```
App
  ThemeProvider (localStorage "bimbam-theme", class on html)
  Navbar (sticky, Landing only: logo + links + ThemeToggle + CTA)
  Routes
    / -> Landing
           Hero, Features (4 cards), Stats, CTASection, Footer
    /chat -> ChatLayout
               TopBar (hamburger mobile + ThemeToggle)
               Sidebar (NewChatButton + SessionList, hidden <768px, overlay)
               ChatArea
                 EmptyState (logo + "En que puedo ayudarte hoy?")
                 MessageList -> MessageBubble[] (user: #7c3aed, asst: #10a37f)
                 TypingIndicator (3 animated dots)
                 ChatInput (textarea, Enter=send, Shift+Enter=newline)
    * -> NotFound (icon + heading + subtitle + "Volver al inicio" button)
```

### Chat State Machine (useChat hook)

```
idle --> sending (user submits message)
sending --> streaming (first SSE data event, input disabled)
sending --> error (fetch fails immediately, toast shown)
streaming --> done (SSE [DONE] or stream close, input re-enabled)
streaming --> error (SSE error event mid-stream, toast)
error --> idle (user dismisses toast)
done --> sending (user sends next message)
```

### Color Palette

| Token | Dark | Light |
|-------|------|-------|
| bg-primary | #343541 | #ffffff |
| bg-sidebar | #202123 | #f7f7f8 |
| bg-msg-assistant | #444654 | #ececf1 |
| bg-msg-user | #343541 | #ffffff |
| bg-input | #40414f | #ffffff |
| text-primary | #ececf1 | #2d2d2d |
| text-secondary | #8e8ea0 | #6b6b6b |
| accent | #10a37f | #10a37f |
| avatar-user | #7c3aed | #7c3aed |
| border | #4d4d5f | #e5e5e5 |

### API Client (lib/api.ts)

- `streamChat(message: string): AsyncGenerator<string>` — fetch POST + ReadableStream + SSE parse
- `healthCheck(): Promise<HealthStatus>` — fetch GET, typed response

## CI/CD

### CircleCI (.circleci/config.yml)

Two parallel jobs:

- **backend-test**: Python 3.13, install deps, `pytest --cov=backend --cov-report=xml:coverage.xml`, upload to Coveralls
- **frontend-test**: Node 20, `npm ci`, `npm run lint`, `npm run build` (type-check + Vite build)

Trigger: every push and PR. Coveralls orb for coverage reporting. No deploy — local-only app.

### Tests Required

| Layer | What | Tool |
|-------|------|------|
| Backend unit | store.py CRUD, rag.py chain assembly, config.py env fallback | pytest |
| Backend integration | /health endpoint, /chat SSE stream | pytest + httpx.AsyncClient |
| Backend ingestion | PDF extraction, chunk metadata, idempotency | pytest |
| Frontend build | tsc --noEmit, vite build (no runtime errors) | npm |
| Frontend lint | ESLint pass | npm |

## ChromaDB Schema

- **Collection**: `bimbam_docs`
- **Metadata per chunk**: `{"source": "Guia_de_Envios.pdf", "page": 3}`
- **Embedding dim**: auto from OpenRouter model
- **Distance**: cosine (default)

## Data Model (Frontend)

```typescript
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface Session {
  id: string;
  title: string;       // first user message
  messages: Message[];
  createdAt: number;
}

interface ChatState {
  sessions: Session[];
  activeSessionId: string | null;
  isStreaming: boolean;
  error: string | null;
}
```

## Open Questions

- [ ] Confirmar si se necesita un directorio `chroma_db/` inicial vacío o se crea en runtime
- [ ] Definir estructura exacta de `test_query.py` (CLI args, formato de salida)
