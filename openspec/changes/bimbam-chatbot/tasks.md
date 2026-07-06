# Tasks: BimBam Chatbot — RAG Agent sobre PDFs de E-commerce

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 2500–3500 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 → PR 5 → PR 6 |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | PR | Notes |
|------|------|----|-------|
| 1 | Backend infrastructure | PR 1 | config/store/ingest |
| 2 | RAG runtime + API | PR 2 | rag/app/test_query |
| 3 | Backend tests | PR 3 | pytest |
| 4 | Frontend shell | PR 4 | Vite/Tailwind/theme/API |
| 5 | Frontend pages | PR 5 | Landing/Chat/404 |
| 6 | CI/CD + verification | PR 6 | CircleCI/smoke |

## Phase 1: Backend Infrastructure (PR 1)

- [x] T1 (Low ~30) `backend/config.py`, `.env.example`: env vars.
- [x] T2 (Medium ~80) `backend/store.py`: ChromaDB client and retriever.
- [x] T3 (Medium ~100) `backend/ingest.py`: load PDFs, chunk, embed, persist.
- [x] T4 (Low ~20) `backend/requirements.txt`: Python dependencies.

## Phase 2: Backend Runtime (PR 2)

- [ ] T5 (Medium ~100) `backend/rag.py`: RAG chain, prompt, retry.
- [ ] T6 (Medium ~120) `backend/app.py`: FastAPI `/health` and `/chat` SSE.
- [ ] T7 (Low ~50) `backend/test_query.py`: CLI test tool.

## Phase 3: Backend Tests (PR 3)

- [ ] T8 (Medium ~80) `backend/tests/test_store.py`: store CRUD and threshold.
- [ ] T9 (Medium ~60) `backend/tests/test_rag.py`: chain assembly.
- [ ] T10 (Medium ~80) `backend/tests/test_ingest.py`: PDF extraction, metadata.
- [ ] T11 (Medium ~100) `backend/tests/test_app.py`: health and SSE.

## Phase 4: Frontend Shell (PR 4)

- [ ] T12 (Medium ~150) `frontend/package.json`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.*`: Vite React 19 + TS + Tailwind.
- [ ] T13 (Low ~50) `frontend/components.json` + shadcn base: shadcn/ui components.
- [ ] T14 (Medium ~80) `frontend/src/index.css`: theme variables and `dark` class.
- [ ] T15 (Medium ~80) `frontend/src/lib/api.ts`: SSE parser and health check.
- [ ] T16 (Low ~30) `frontend/src/types/chat.ts`: message and session types.
- [ ] T17 (Low ~50) `frontend/src/hooks/useTheme.ts`: theme persistence.
- [ ] T18 (Low ~30) `frontend/src/App.tsx`: router `/`, `/chat`, `*`.

## Phase 5: Frontend Pages (PR 5)

- [ ] T19 (Medium ~60) `frontend/src/components/Navbar.tsx`: sticky landing nav.
- [ ] T20 (Medium ~150) `frontend/src/pages/Landing.tsx`: hero, features, stats, CTA, footer.
- [ ] T21 (Low ~50) `frontend/src/pages/NotFound.tsx`: 404 page.
- [ ] T22 (Medium ~120) `frontend/src/hooks/useChat.ts`: sessions and SSE state.
- [ ] T23 (Medium ~250) `frontend/src/components/ChatLayout.tsx`, `Sidebar.tsx`, `ChatArea.tsx`, `MessageList.tsx`, `MessageBubble.tsx`, `ChatInput.tsx`, `TopBar.tsx`, `ThemeToggle.tsx`: chat UI.
- [ ] T24 (Medium ~100) `frontend/src/pages/Chat.tsx`: chat page composition.

## Phase 6: Verification & CI/CD (PR 6)

- [ ] T25 (Medium ~80) `frontend/src/hooks/__tests__/useChat.test.ts`, `frontend/src/lib/__tests__/api.test.ts`: Vitest tests.
- [ ] T26 (Low ~30) `frontend/vitest.config.ts`, `frontend/package.json`: Vitest config.
- [ ] T27 (Medium ~80) `.circleci/config.yml`: CircleCI backend and frontend jobs.
- [ ] T28 (Low manual) Run ingestion and verify endpoints.
- [ ] T29 (Low manual) Build, lint and responsive smoke test.
