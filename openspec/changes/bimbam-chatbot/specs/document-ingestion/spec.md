# Document Ingestion Specification

## Purpose

Pipeline offline que lee los 5 PDFs operativos de BimBam Buy desde `documents/`, los divide en chunks, genera embeddings vía OpenRouter, y los almacena en ChromaDB. Este proceso es independiente del runtime de la API — se ejecuta como script previo al despliegue o cuando se actualizan los PDFs.

## Requirements

| ID | Requirement | Strength |
|----|-------------|----------|
| DI-REQ-01 | Leer todos los PDFs del directorio `documents/` | MUST |
| DI-REQ-02 | Chunking con RecursiveCharacterTextSplitter (500 chars, overlap 50) | MUST |
| DI-REQ-03 | Generar embeddings con OpenRouter (modelo `llama-nemotron-embed-vl-1b-v2:free`) vía LangChain | MUST |
| DI-REQ-04 | Almacenar vectores y metadatos en ChromaDB (`chroma_db/`) | MUST |
| DI-REQ-05 | Manejar PDFs con caracteres LATAM (tildes, ñ) sin pérdida de encoding | MUST |
| DI-REQ-06 | Incluir metadata: `source` (nombre del archivo), `page` (número de página) en cada chunk | MUST |
| DI-REQ-07 | Ejecutarse como script independiente: `python backend/ingest.py` | MUST |
| DI-REQ-08 | Ser idempotente: re-ejecutar reemplaza la colección sin duplicados | SHOULD |
| DI-REQ-09 | Loggear progreso: archivos procesados, chunks generados, embeddings creados | SHOULD |

### Scenario: Ingesta exitosa de todos los PDFs

- **GIVEN** 5 PDFs válidos en `documents/` y OPENROUTER_API_KEY configurada
- **WHEN** se ejecuta `python backend/ingest.py`
- **THEN** se procesan los 5 archivos, se generan chunks con sus embeddings, y se persisten en `chroma_db/`
- **AND** cada chunk contiene metadata `source` y `page`

### Scenario: PDF con caracteres LATAM (tildes, ñ)

- **GIVEN** un PDF con texto que incluye "información", "garantía", "devolución", "año"
- **WHEN** se ingiere usando pypdf con `strict=False` o pdfplumber como fallback
- **THEN** el texto extraído preserva tildes y ñ correctamente
- **AND** los embeddings generados corresponden al texto correcto

### Scenario: Re-ejecución (idempotencia)

- **GIVEN** ChromaDB ya contiene una colección con datos previos
- **WHEN** se vuelve a ejecutar `ingest.py`
- **THEN** la colección se reemplaza con los datos frescos sin crear duplicados
- **AND** el script completa sin errores

### Scenario: PDF corrupto o ilegible

- **GIVEN** un PDF corrupto en `documents/`
- **WHEN** el script intenta procesarlo
- **THEN** loggea un error descriptivo indicando el archivo problemático
- **AND** continúa procesando los PDFs restantes sin detenerse

### Scenario: API key ausente

- **GIVEN** la variable de entorno OPENROUTER_API_KEY no está configurada
- **WHEN** se ejecuta `ingest.py`
- **THEN** el script falla temprano con un mensaje claro: "OPENROUTER_API_KEY not set"

## Technical Details

| Aspect | Detail |
|--------|--------|
| **Entry point** | `backend/ingest.py` |
| **PDF loader** | `pypdf` con `strict=False`; fallback a `pdfplumber` si falla |
| **Splitter** | `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", ". ", " "])` |
| **Embedding model** | `llama-nemotron-embed-vl-1b-v2:free` via `OpenAIEmbeddings(openai_api_base="https://openrouter.ai/api/v1")` |
| **Vector store** | ChromaDB — directorio `chroma_db/`, colección `bimbam_docs` |
| **Metadata** | `{"source": "Guía_de_Envíos.pdf", "page": 3}` |
| **API key** | Desde variable de entorno `OPENROUTER_API_KEY` |

## Non-Functional Requirements

| ID | Requirement | Strength |
|----|-------------|----------|
| DI-NFR-01 | Ingesta completa de 5 PDFs (~50 páginas total) en < 60 segundos | SHOULD |
| DI-NFR-02 | Memoria pico < 512 MB durante el proceso | SHOULD |
| DI-NFR-03 | ChromaDB ocupa < 100 MB en disco para los 5 PDFs | SHOULD |

## Inputs

| Input | Source |
|-------|--------|
| 5 PDFs | `documents/` |
| API key | `OPENROUTER_API_KEY` env var |

## Outputs

| Output | Destination |
|--------|-------------|
| ChromaDB collection `bimbam_docs` | `chroma_db/` |
| Console logs | stdout (archivos procesados, chunks, tiempo total) |
