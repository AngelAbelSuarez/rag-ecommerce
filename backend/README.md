# BimBam Chatbot — Backend

API REST con RAG (Retrieval-Augmented Generation) para el asistente virtual de BimBam Buy, un e-commerce LATAM. Construido con **FastAPI**, **LangChain** y **ChromaDB**, usando modelos de **NVIDIA AI Endpoints**.

## Stack

| Capa           | Tecnología                                                      |
| -------------- | --------------------------------------------------------------- |
| Framework      | FastAPI + Uvicorn                                               |
| RAG pipeline   | LangChain LCEL                                                  |
| Vector store   | ChromaDB (persistente, local)                                   |
| Embeddings     | `nvidia/nv-embed-v1` via NVIDIA AI Endpoints                    |
| LLM            | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` via NVIDIA AI Endpoints |
| Extracción PDF | pypdf + pdfplumber (fallback)                                   |

## Estructura

```
backend/
├── app.py              # FastAPI app, endpoints, SSE streaming
├── config.py           # Config centralizada vía pydantic-settings + .env
├── ingest.py           # Pipeline de ingestión offline (PDF → chunks → ChromaDB)
├── rag.py              # Cadena RAG (retrieval + prompt + LLM)
├── store.py            # Cliente ChromaDB y factory de retrievers
├── test_query.py       # CLI interactivo para probar queries
├── requirements.txt    # Dependencias Python
├── .env.example        # Template de configuración
├── .env                # Config local (gitignored)
├── chroma_db/          # Persistencia local de ChromaDB (gitignored)
└── tests/
    ├── conftest.py
    ├── test_app.py     # Tests de la API HTTP
    ├── test_ingest.py  # Tests del pipeline de ingestión
    ├── test_rag.py     # Tests de la cadena RAG
    └── test_store.py   # Tests del vector store
```

## Requisitos

- Python 3.13+
- NVIDIA API key ([build.nvidia.com](https://build.nvidia.com))

## Setup

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar NVIDIA_API_KEY=nvapi-...
```

## Uso

### Ingestión de documentos

Colocá los PDFs en `documents/` (raíz del proyecto) y ejecutá:

```bash
python backend/ingest.py
```

Esto extrae el texto, lo divide en chunks, genera embeddings y los persiste en `backend/chroma_db/`.

### Servidor API

```bash
uvicorn app:app --reload --port 8000
```

La API queda en `http://localhost:8000`.

### Documentación interactiva

FastAPI genera automáticamente:

- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- También podés consultar el archivo [`openapi.yaml`](openapi.yaml) en este directorio.

### CLI de prueba

```bash
# Query única
python backend/test_query.py "¿cuánto tarda un envío a Colombia?"

# Modo interactivo
python backend/test_query.py -i
```

## Endpoints

### `GET /api/health`

Devuelve el estado de ChromaDB y el LLM.

```json
// 200 — todo bien
{ "status": "healthy", "chromadb": "connected", "llm": "available" }

// 503 — degraded
{ "status": "degraded", "chromadb": "disconnected", "llm": "unavailable" }
```

### `POST /api/chat`

**Request:**

```json
{ "message": "¿cuál es el plazo de entrega?", "conversation_id": "abc-123" }
```

**Response:** Server-Sent Events (SSE) con tokens del LLM en vivo.

```
data: El
data: plazo
data: de
data: entrega
...
data: [DONE]
```

Si ocurre un error:

```
event: error
data: {"message": "El servicio está congestionado, intentá de nuevo en unos segundos"}
```

## Tests

```bash
# Todos los tests
pytest tests/ -v

# Por archivo
pytest tests/test_app.py -v
pytest tests/test_rag.py -v
```

## Configuración vía entorno

| Variable               | Default                                         | Descripción                        |
| ---------------------- | ----------------------------------------------- | ---------------------------------- |
| `NVIDIA_API_KEY`       | `""`                                            | API key de NVIDIA (requerida)      |
| `NVIDIA_BASE_URL`      | `https://integrate.api.nvidia.com/v1`           | Base URL del API de NVIDIA         |
| `EMBEDDING_MODEL`      | `nvidia/nv-embed-v1`                            | Modelo de embeddings               |
| `CHAT_MODEL`           | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1`      | Modelo de chat                     |
| `CHROMA_PERSIST_DIR`   | `chroma_db`                                     | Directorio de persistencia         |
| `COLLECTION_NAME`      | `bimbam_docs`                                   | Nombre de la colección ChromaDB    |
| `CHUNK_SIZE`           | `600`                                           | Tamaño de chunk para ingestión     |
| `CHUNK_OVERLAP`        | `80`                                            | Superposición entre chunks         |
| `RETRIEVER_K`          | `4`                                             | Cantidad de documentos a recuperar |
| `SIMILARITY_THRESHOLD` | `0.0`                                           | Umbral de similaridad mínima       |
| `LOG_LEVEL`            | `INFO`                                          | Nivel de log                       |
| `REQUEST_TIMEOUT`      | `30.0`                                          | Timeout para llamadas a NVIDIA     |
