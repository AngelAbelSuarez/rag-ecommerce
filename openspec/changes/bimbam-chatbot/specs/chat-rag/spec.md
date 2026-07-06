# Chat RAG Specification

## Purpose

API REST con streaming que recibe preguntas en español LATAM, ejecuta un pipeline RAG sobre los 5 PDFs de BimBam Buy, y devuelve respuestas generadas por LLM contextualizadas con los chunks relevantes de ChromaDB. El endpoint usa SSE para transmitir la respuesta token por token.

## Requirements

| ID | Requirement | Strength |
|----|-------------|----------|
| CR-REQ-01 | Exponer `POST /api/chat` que acepte `{ "message": string }` y responda con streaming SSE | MUST |
| CR-REQ-02 | Pipeline RAG: query → embedding → ChromaDB similarity (top-4) → prompt → LLM | MUST |
| CR-REQ-03 | System prompt que instruya al LLM a responder SOLO con el contexto de los PDFs | MUST |
| CR-REQ-04 | LLM provider: OpenRouter, modelo `nvidia/nemotron-3-ultra` (free) | MUST |
| CR-REQ-05 | Exponer `GET /api/health` que devuelva `200 OK` con status de ChromaDB y LLM | MUST |
| CR-REQ-06 | Manejar rate limits de OpenRouter con retry + backoff exponencial | MUST |
| CR-REQ-07 | Respuestas siempre en español LATAM | MUST |
| CR-REQ-08 | Si no hay chunks relevantes (similarity < threshold), responder que no tiene información | SHOULD |
| CR-REQ-09 | Timeout de 30 segundos para la generación completa de respuesta | SHOULD |
| CR-REQ-10 | Loguear queries, latency de cada etapa y errores | SHOULD |

### Scenario: Pregunta con contexto relevante

- **GIVEN** ChromaDB tiene chunks de los 5 PDFs
- **WHEN** se envía `POST /api/chat` con `{"message": "¿cuánto tarda un envío a Colombia?"}`
- **THEN** se recibe una respuesta vía SSE con chunks de texto
- **AND** la respuesta contiene información extraída de la Guía de Envíos
- **AND** el texto fluye token por token (no aparece de golpe)

### Scenario: Pregunta fuera del dominio

- **GIVEN** ChromaDB tiene chunks de los 5 PDFs
- **WHEN** se envía `POST /api/chat` con `{"message": "¿quién ganó el mundial 2022?"}`
- **THEN** se recibe una respuesta indicando que no tiene información sobre ese tema
- **AND** la respuesta sugiere consultar temas de BimBam Buy (envíos, pagos, garantía, devoluciones, afiliados)

### Scenario: Rate limit de OpenRouter

- **GIVEN** OpenRouter devuelve HTTP 429
- **WHEN** la chain RAG intenta generar la respuesta
- **THEN** se aplica retry con backoff exponencial (1s, 2s, 4s, 8s máx)
- **AND** si después de 3 reintentos sigue fallando, se devuelve error `503 Service Unavailable`
- **AND** el mensaje de error sugiere "El servicio está congestionado, intentá de nuevo en unos segundos"

### Scenario: Health check exitoso

- **GIVEN** el backend está corriendo y ChromaDB tiene datos
- **WHEN** se consulta `GET /api/health`
- **THEN** se devuelve `200 OK` con `{"status": "healthy", "chromadb": "connected", "llm": "available"}`
- **AND** tiempo de respuesta < 500 ms

### Scenario: Health check con ChromaDB caído

- **GIVEN** ChromaDB no está accesible
- **WHEN** se consulta `GET /api/health`
- **THEN** se devuelve `503` con `{"status": "degraded", "chromadb": "disconnected"}`

### Scenario: Timeout de generación

- **GIVEN** el LLM tarda más de 30 segundos en generar
- **WHEN** se supera el timeout configurado
- **THEN** se cierra el stream SSE con un evento `error`
- **AND** se loggea el timeout con la query original

## Technical Details

| Aspect | Detail |
|--------|--------|
| **Endpoint** | `POST /api/chat` — streaming SSE |
| **Request body** | `{ "message": string }` |
| **Response** | `text/event-stream` con eventos `data:`, `error:`, `done:` |
| **Top-K chunks** | 4 chunks con mayor similarity score |
| **System prompt** | "Sos BimBam, el asistente virtual de BimBam Buy. Respondé preguntas ÚNICAMENTE usando la información proporcionada en el contexto. Si el contexto no contiene la respuesta, decí amablemente que no tenés esa información y sugerí consultar sobre envíos, pagos, garantía, devoluciones o afiliados. Respondé en español LATAM, con tono cálido y profesional." |
| **User prompt template** | "Contexto:\n{context}\n\nPregunta: {question}\n\nRespuesta:" |
| **LLM** | `ChatOpenAI(model="nvidia/nemotron-3-ultra", openai_api_base="https://openrouter.ai/api/v1", temperature=0.3, streaming=True)` |
| **Embedding** | `OpenAIEmbeddings(model="llama-nemotron-embed-vl-1b-v2:free")` |
| **Retry** | `tenacity` con `wait_exponential(multiplier=1, min=1, max=8)` — máx 3 intentos |
| **Similarity threshold** | `score < 0.3` → "no tengo información suficiente" |

## Non-Functional Requirements

| ID | Requirement | Strength |
|----|-------------|----------|
| CR-NFR-01 | P50 latency (primer token) < 3 segundos | SHOULD |
| CR-NFR-02 | P95 latency (primer token) < 8 segundos | SHOULD |
| CR-NFR-03 | Tasa de error (5xx) < 5% bajo carga normal | SHOULD |
| CR-NFR-04 | Respuesta final < 500 tokens (controlado vía prompt) | SHOULD |

## Data Flow

```
POST /api/chat {"message": "..."}
  → Embedding del query
  → ChromaDB.similarity_search(query_embedding, k=4)
  → Formatear contexto: "Documento {source} (pág {page}): {content}"
  → Prompt template: system + contexto + pregunta
  → OpenRouter LLM (stream=True)
  → SSE: data: "token1"\n\ndata: "token2"\n\n...\ndata: [DONE]\n\n
```
