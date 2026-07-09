
# BimBam Chatbot — Manual Verification Guide
[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/8Vocs9Wi1dzq3hdj7Xm8N6/RoSAjBDZEeShem5ytogQa1/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/8Vocs9Wi1dzq3hdj7Xm8N6/RoSAjBDZEeShem5ytogQa1/tree/main)

This document describes how to set up, ingest data, run, and verify the BimBam Chatbot stack end-to-end.

## Prerequisites

- Python 3.13+
- Node.js 22+
- pnpm 11+ (`corepack enable pnpm` or `npm install -g pnpm`)
- NVIDIA API key (set as `NVIDIA_API_KEY`)

## 1. Environment Setup

Copy the example environment file and fill in your NVIDIA API key:

```bash
cp .env.example .env
```

Edit `.env` and set at least:

```env
NVIDIA_API_KEY=your_nvidia_api_key_here
```

## 2. Run Ingestion

Place PDF documents under `documents/` and run the ingestion script:

```bash
python backend/ingest.py
```

This loads the PDFs, chunks them, embeds them, and persists the vector store under `chroma_data/`.

## 3. Start the Backend

```bash
uvicorn backend.app:app --reload
```

The API will be available at `http://localhost:8000`.

## 4. Start the Frontend

In a new terminal:

```bash
cd frontend
pnpm run dev
```

The UI will be available at `http://localhost:5173`.

## 5. Run All Tests

### Backend

```bash
pytest backend/tests/ -v
```

### Frontend

```bash
cd frontend
pnpm test
```

## 6. Build and Lint

### Frontend build

```bash
cd frontend
pnpm run build
```

### Frontend lint

```bash
cd frontend
pnpm run lint
```

## 7. Smoke Test

With the backend running, verify the health endpoint:

```bash
curl http://localhost:8000/api/health
```

Expected response:

```json
{
  "status": "ok",
  "chromadb": "ok",
  "llm": "ok"
}
```

## 8. Responsive Smoke Test

1. Open `http://localhost:5173` in a desktop browser.
2. Confirm the landing page renders the hero, feature cards, stats, and CTA.
3. Click the "Chat" CTA or navigate to `/chat`.
4. Send a message and confirm the assistant streams a response.
5. Open browser DevTools, toggle a mobile viewport (e.g., iPhone SE / 375px width), and confirm:
   - The landing page stacks vertically without horizontal overflow.
   - The chat sidebar becomes a slide-over menu accessible from the top bar.
   - Messages remain readable and the input stays anchored at the bottom.
