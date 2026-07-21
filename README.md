# BimBam Chatbot

## Description

This project is a full-stack RAG (Retrieval-Augmented Generation) chatbot application built with FastAPI and React, developed as a solution for a backend challenge. It provides a conversational e-commerce assistant that answers questions about products, shipping, and policies by retrieving relevant context from product documentation using vector search and LLM-generated responses, all through a modern chat interface.

Built with a modular architecture that separates ingestion, retrieval, generation, and presentation concerns. The backend uses LangChain for the RAG pipeline, Pinecone Serverless as the vector store, and NVIDIA AI Endpoints for embeddings and LLM inference. The frontend is built with React, TypeScript, and Tailwind CSS. The entire stack is containerized with Docker and includes automated CI/CD pipelines via CircleCI with coverage reporting through Coveralls. The app is deployed on free tiers (Vercel + Render + Pinecone).

## Badges

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/8Vocs9Wi1dzq3hdj7Xm8N6/RoSAjBDZEeShem5ytogQa1/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/8Vocs9Wi1dzq3hdj7Xm8N6/RoSAjBDZEeShem5ytogQa1/tree/main)

[![Coverage Status](https://coveralls.io/repos/github/AngelAbelSuarez/rag-ecommerce/badge.svg?branch=main)](https://coveralls.io/github/AngelAbelSuarez/rag-ecommerce?branch=main)

## Features

- Ingest PDF documents and index them into a vector store (Pinecone Serverless)
- Ask questions via REST API and get LLM-generated answers grounded in your documents
- Streaming responses via Server-Sent Events (SSE) for real-time chat
- Modern chat UI with desktop and mobile responsive layout
- Health check endpoint to monitor Pinecone vector store and LLM availability
- Configurable chunk size, overlap, retriever K, and similarity threshold
- CLI tool for interactive query testing

## Pre-Requisites

- Python 3.13+
- Node.js 22+
- pnpm 11+ (`corepack enable pnpm` or `npm install -g pnpm`)
- Docker Desktop
- NVIDIA API key ([build.nvidia.com](https://build.nvidia.com))
- Ports free: 8000 (backend) and 5173 (frontend)

## How to run the APP

```bash
# permissions
$ chmod 711 ./up_dev.sh

# start app
$ ./up_dev.sh
```

## How to run the tests

```bash
# permissions
$ chmod 711 ./up_test.sh

# start test
$ ./up_test.sh
```

## Architecture decisions

- **FastAPI**: Async-first Python framework, ideal for I/O-bound RAG workloads and SSE streaming. Type validation via Pydantic out of the box.
- **LangChain LCEL**: Declarative chain composition that makes the RAG pipeline easy to modify, test, and debug without custom orchestration code.
- **Pinecone Serverless**: Managed cloud vector store (AWS us-east-1 free tier) — scales without infrastructure maintenance and works on serverless hosts like Render.
- **NVIDIA AI Endpoints**: No GPU required; embeddings and LLM inference are handled externally via API, keeping the backend slim.
- **React + Vite + Tailwind**: Modern frontend stack with fast HMR, responsive design, and utility-first styling.
- **Separated ingestion pipeline**: `ingest.py` is a standalone offline script — the API doesn't need write access to the vector store at runtime.
- **Docker Compose**: Single command to spin up the full stack with hot-reload in development.
- **CircleCI + Coveralls**: Automated testing and coverage visibility on every push.
- **Deployment on free tiers**: Frontend on Vercel, backend on Render, vector store on Pinecone Serverless.

## Route

### Production (deployed)
- Frontend: [https://rag-ecommerce.vercel.app/](https://rag-ecommerce.vercel.app/)
- Backend API: deployed on Render (see `deploy/RENDER.md` for setup)

### Local development
- Backend API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend: [http://localhost:5173](http://localhost:5173)

## Env vars

| Variable                 | Default                                         | Description                          |
|--------------------------|-------------------------------------------------|--------------------------------------|
| `NVIDIA_API_KEY`         | `""`                                            | API key for NVIDIA AI Endpoints      |
| `NVIDIA_BASE_URL`        | `https://integrate.api.nvidia.com/v1`           | Base URL for NVIDIA API              |
| `EMBEDDING_MODEL`        | `nvidia/nv-embed-v1`                            | Model for embeddings                 |
| `CHAT_MODEL`             | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1`       | Model for chat responses             |
| `PINECONE_API_KEY`       | `""`                                            | API key for Pinecone Serverless      |
| `PINECONE_INDEX_NAME`    | `bimbam-docs`                                   | Pinecone index name                  |
| `PINECONE_NAMESPACE`     | `bimbam_docs`                                   | Pinecone namespace                   |
| `DOCUMENTS_DIR`          | `""` (defaults to `documents/`)                 | Directory with PDFs to ingest        |
| `CHUNK_SIZE`             | `600`                                           | Characters per chunk                 |
| `CHUNK_OVERLAP`          | `80`                                            | Overlap between chunks               |
| `RETRIEVER_K`            | `4`                                             | Documents retrieved per query        |
| `SIMILARITY_THRESHOLD`   | `0.0`                                           | Minimum similarity score             |
| `REQUEST_TIMEOUT`        | `30.0`                                          | Timeout for NVIDIA API calls         |

## Areas to improve

- Add authentication and rate limiting for the chat endpoint.
- Implement a feedback mechanism (thumbs up/down) to evaluate response quality.
- Add support for multiple collections and document types (CSV, JSON, Markdown).
- Cache frequent queries to reduce LLM calls and latency.
- Monitor embedding and LLM costs per session.
- Add E2E tests with Playwright or Cypress for the full chat flow.

## Techs

- Python 3.13 + FastAPI
- LangChain + LangChain-Pinecone
- Pinecone Serverless (vector store)
- NVIDIA AI Endpoints
- React + TypeScript + Vite
- Tailwind CSS
- Docker + Docker Compose
- CircleCI + Coveralls
- Vercel + Render (deployment)
- pytest + pytest-cov
- Vitest + Testing Library
