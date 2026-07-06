# Proposal: BimBam Chatbot — RAG Agent sobre PDFs de E-commerce

## Intent

BimBam Buy necesita un asistente IA que responda preguntas de clientes y empleados sobre sus 5 PDFs operativos (envíos, garantía, reembolsos, pagos, afiliados) en español LATAM. Hoy la info está en documentos estáticos y no hay forma de consultarla conversacionalmente. Este cambio construye un chatbot RAG full-stack desde cero.

## Scope

### In Scope
- **3 páginas frontend + versión mobile responsive**: Landing, Chat, 404 (adaptables a 375px)
- **Backend API REST + streaming**: ingesta de PDFs, RAG con LangChain + ChromaDB
- **Dark mode default** con toggle a light (paleta ChatGPT, acento #10a37f)
- **5 documentos** de BimBam Buy como fuente de conocimiento
- **OpenRouter** como LLM provider (modelo free: nvidia/nemotron-3-ultra, embedding free: llama-nemotron-embed-vl-1b-v2)
- **Historial de chat** en sidebar (sesión en memoria, no persistente)
- **Script `test_query.py`** con soporte para API key del usuario
- Diseño OpenPencil existente (`design.documind.op`) como referencia visual — no se replica en código, se inspira
- **CircleCI** para CI/CD pipeline (tests automáticos en cada push/PR)
- **Coveralls** para reporte de cobertura de tests

### Out of Scope
- Páginas de Afiliados y Documentos (links en navbar del diseño, pero no se implementan)
- Autenticación de usuarios
- Persistencia de historial entre sesiones
- Mostrar fuentes / documentos citados en el chat
- Panel admin o dashboard

## Capabilities

> Contract with sdd-spec. Each capability becomes a spec.

### New Capabilities
- `chat-rag`: Conversación Q&A sobre los 5 PDFs usando RAG
- `document-ingestion`: Pipeline de ingesta de PDFs a ChromaDB
- `landing-page`: Página de presentación de BimBam Buy
- `chat-ui`: Interfaz de chat tipo ChatGPT con sidebar

### Modified Capabilities
- None (greenfield project — no existing specs)

## Approach

Monorepo con `backend/` (FastAPI + LangChain + ChromaDB) y `frontend/` (React 19 + Vite + Tailwind + shadcn/ui). PDFs se ingieren offline con script separado (`ingest.py`). El chat usa RAG: query → embedding → ChromaDB similarity search → LLM con contexto → respuesta streamed vía SSE.

**Flujo de datos**:
```
Usuario → Chat UI → POST /api/chat → LangChain RAG chain
  → ChromaDB similarity search (top-k chunks)
  → Prompt con contexto + pregunta
  → OpenRouter LLM (stream) → SSE response → Chat UI
```

## Technical Decisions

| Decisión | Opción | Razón |
|----------|--------|-------|
| LLM Provider | OpenRouter | Acceso a modelos free sin API key propia, múltiples modelos |
| Chat model | nvidia/nemotron-3-ultra (free) | Buen rendimiento en español, sin costo |
| Embedding | llama-nemotron-embed-vl-1b-v2:free | Gratuito, compatible con el ecosistema |
| Vector store | ChromaDB | Simple, embebible, sin infraestructura externa |
| Backend | FastAPI + LangChain | Async nativo, integración directa con LangChain |
| Frontend | React 19 + Vite + shadcn/ui | Componentes accesibles, dark mode nativo |
| Chunking | RecursiveCharacterTextSplitter (500 chars, overlap 50) | Balance entre precisión y contexto |
| Streaming | SSE (Server-Sent Events) | Simple, unidireccional, bien soportado |

## Specifications Needed

| Capability | File | Priority |
|------------|------|----------|
| document-ingestion | `openspec/changes/bimbam-chatbot/specs/document-ingestion/spec.md` | P0 |
| chat-rag | `openspec/changes/bimbam-chatbot/specs/chat-rag/spec.md` | P0 |
| chat-ui | `openspec/changes/bimbam-chatbot/specs/chat-ui/spec.md` | P0 |
| landing-page | `openspec/changes/bimbam-chatbot/specs/landing-page/spec.md` | P1 |

## Deliverables

| Artefacto | Descripción |
|-----------|-------------|
| `backend/app.py` | FastAPI app con endpoints `/api/chat` y `/api/health` |
| `backend/ingest.py` | Script de ingesta de PDFs a ChromaDB |
| `backend/rag.py` | Chain RAG con contexto y generación |
| `backend/store.py` | Cliente ChromaDB y funciones de vector store |
| `backend/test_query.py` | Script CLI para probar RAG con API key |
| `backend/requirements.txt` | Dependencias Python |
| `frontend/` | App React 19 con Vite, Tailwind, shadcn/ui |
| `frontend/src/pages/Landing.tsx` | Hero, features, stats, CTA, footer |
| `frontend/src/pages/Chat.tsx` | Chat layout con sidebar |
| `frontend/src/pages/NotFound.tsx` | Página 404 |

## Risks

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Encoding PDFs (tildes, ñ) | Alta | Usar PyPDFLoader con `extraction_mode="layout"`, fallback a pdfminer |
| Cross-references entre docs | Media | Chunking con overlap 50, metadata por documento fuente |
| Rate limits OpenRouter free | Media | Implementar retry con backoff exponencial, cache de respuestas |
| Sin fuentes visibles (transparencia) | Media | El brief lo exige, pero documentar como decisión arquitectónica |
| Modelo free cambia o se degrada | Baja | Abstraer LLM via LangChain para swap fácil |

## Rollback Plan

1. **Backend**: `git revert` del commit del backend — la API no está en producción
2. **Frontend**: `git revert` del commit del frontend — solo páginas nuevas sin dependencias externas
3. **ChromaDB**: Eliminar directorio `chroma_db/` si existe — se regenera con `ingest.py`
4. **Full revert**: Si todo falla, `git reset --hard HEAD~N` y forzar push, luego reinstalar dependencias

## Dependencies

- Python 3.11+
- Node.js 20+
- OpenRouter API key (gratuita, registrarse en openrouter.ai)
- Acceso a los 5 PDFs en `documents/`

## Success Criteria

- [ ] Backend responde `200 OK` en `/api/health`
- [ ] `/api/chat` responde con streaming SSE a una pregunta sobre cualquier PDF
- [ ] Landing page carga con hero, features, stats, CTA, footer
- [ ] Chat UI permite escribir, recibe respuesta streamed, muestra en burbujas
- [ ] Dark/light mode toggle funciona y persiste preferencia
- [ ] Página 404 muestra diseño coherente con botón de volver
- [ ] `test_query.py` responde correctamente con API key del usuario
- [ ] Toda respuesta del chatbot es en español LATAM y coherente con los PDFs
