# Deploy guide — BimBam Chatbot (Vercel + Render + Pinecone)

This guide covers the full deployment of the BimBam Chatbot stack on free tiers:

- **Frontend** (React + Vite) → Vercel
- **Backend** (FastAPI + NVIDIA + Pinecone) → Render
- **Vector store** → Pinecone Serverless (AWS us-east-1, 4096 dims, cosine)

The architecture uses three separate services because:
- Vercel serverless functions have no persistent filesystem, so ChromaDB was migrated to Pinecone.
- SSE streaming on the backend needs a persistent process, not serverless → Render web service.

---

## Prerequisites

- GitHub repo `AngelAbelSuarez/rag-ecommerce` (or your fork) with `bugfix/rag` pushed.
- Accounts on: https://vercel.com, https://render.com, https://app.pinecone.io.
- A Pinecone index named `bimbam-docs`, dimension 4096, metric cosine, serverless, AWS us-east-1.
- The Pinecone namespace `bimbam_docs` already populated with PDFs (run `python backend/ingest.py` once locally — see [Ingest once](#ingest-once-locally)).
- Your `NVIDIA_API_KEY` (https://build.nvidia.com) and `PINECONE_API_KEY` (https://app.pinecone.io → API Keys) at hand.

---

## 1. Deploy backend on Render

### Option A — Blueprint (recommended)

1. Go to https://dashboard.render.com → **New +** → **Blueprint**.
2. Select your `rag-ecommerce` repo. Render detects `render.yaml` at repo root.
3. Review the service `bimbam-backend` and approve.
4. Once the service is created, open it and go to **Environment**.
5. Set the two secret values (kept as `sync: false` in the blueprint):
   - `NVIDIA_API_KEY` = your NVIDIA key (`nvapi-...`)
   - `PINECONE_API_KEY` = your Pinecone key (`pcsk-...`)
6. The other env vars (`PINECONE_INDEX_NAME`, `PINECONE_NAMESPACE`, etc.) are already set by the blueprint.
7. Render auto-deploys. Wait for "Live" status.
8. Note the public URL: `https://bimbam-backend.onrender.com` (or whatever name you chose).

### Option B — Manual web service

1. Go to https://dashboard.render.com → **New +** → **Web Service**.
2. Connect your GitHub and select the `rag-ecommerce` repo.
3. Configure:
   - **Name**: `bimbam-backend`
   - **Runtime**: Docker
   - **Region**: Oregon (or any free region)
   - **Branch**: `bugfix/rag` (or `main` once the migration is merged)
   - **Root Directory**: `backend`
   - **Plan**: Free
4. Under **Environment**, add:
   - `NVIDIA_API_KEY` = your NVIDIA key
   - `PINECONE_API_KEY` = your Pinecone key
   - `PINECONE_INDEX_NAME` = `bimbam-docs`
   - `PINECONE_NAMESPACE` = `bimbam_docs`
   - `SIMILARITY_THRESHOLD` = `0.0`
   - `LOG_LEVEL` = `INFO`
   - `PORT` is injected automatically by Render — do not set it manually.
5. **Create Web Service**. Wait for "Live" status.
6. Note the public URL.

### Verify backend health

Once the service is live:

```bash
curl https://bimbam-backend.onrender.com/api/health
```

Expected (degraded if LLM key is missing, healthy otherwise):

```json
{
  "status": "healthy",
  "vectorstore": "connected",
  "llm": "available"
}
```

---

## 2. Ingest once locally (populate Pinecone)

> Skip this if you already ran ingest locally after the migration.

The Pinecone namespace `bimbam_docs` stores the indexed PDFs. This is a one-time operation; the data persists in Pinecone across backend deploys.

From the repo root:

```bash
source backend/.venv/Scripts/activate   # Windows Git Bash
pip install -r backend/requirements.txt
python backend/ingest.py
```

Expected output:

```
INFO: Processing <file>.pdf
INFO:   -> N pages, M chunks
...
INFO: Embedding M chunks into Pinecone...
INFO: Namespace 'bimbam_docs' did not exist or could not be deleted: ...
INFO: Ingestion complete: N files, M chunks persisted to Pinecone index 'bimbam-docs' namespace 'bimbam_docs'
Done in X.XXs (N files, M chunks)
```

You only need to re-run this if the PDFs in `documents/` change and you want to refresh the index.

---

## 3. Deploy frontend on Vercel

1. Go to https://vercel.com → log in with GitHub.
2. **Add New...** → **Project** → import `rag-ecommerce`.
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite (auto-detected from `vercel.json`)
   - **Build Command**: `pnpm build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `pnpm install --no-frozen-lockfile` (pinned; avoids lockfile drift when Vercel's pnpm version differs)
4. Under **Environment Variables**, add:
   - `VITE_API_URL` = `https://bimbam-backend.onrender.com` (the Render URL from step 1)
5. **Deploy**.

> If you deployed Vercel before having the Render URL, you can set `VITE_API_URL` later and trigger a redeploy from the Vercel dashboard (Deployments → Redeploy).

### Verify frontend

```bash
open https://<your-project>.vercel.app
```

The chat UI should load. Send a question and confirm the RAG response streams in. If the chat shows an error, check:
- The Render backend is live (`curl .../api/health`).
- `VITE_API_URL` in Vercel matches the Render URL (no trailing slash, no path).
- The browser console shows requests going to `https://bimbam-backend.onrender.com/api/chat` and not `/api/chat`.

---

## Environment variables reference

### Backend (Render)

| Variable               | Example                          | Required | Description                          |
|------------------------|----------------------------------|----------|--------------------------------------|
| `NVIDIA_API_KEY`       | `nvapi-...`                      | yes      | NVIDIA AI endpoints key              |
| `PINECONE_API_KEY`     | `pcsk-...`                       | yes      | Pinecone Serverless key              |
| `PINECONE_INDEX_NAME`  | `bimbam-docs`                    | yes      | Pinecone index name                  |
| `PINECONE_NAMESPACE`   | `bimbam_docs`                    | yes      | Namespace inside the index           |
| `SIMILARITY_THRESHOLD` | `0.0`                            | no       | Min similarity score                 |
| `LOG_LEVEL`            | `INFO`                           | no       | Python logging level                 |
| `PORT`                 | (auto)                           | no       | Injected by Render                   |

### Frontend (Vercel)

| Variable        | Example                              | Required | Description                          |
|-----------------|--------------------------------------|----------|--------------------------------------|
| `VITE_API_URL`  | `https://bimbam-backend.onrender.com`  | yes (prod) | Backend base URL (no trailing slash) |

> In local dev, `VITE_API_URL` is unset and the frontend falls back to `/api` which Vite proxies to `http://localhost:8000` via `vite.config.ts`.

### Pinecone index

| Property     | Value          |
|--------------|----------------|
| Name         | `bimbam-docs`  |
| Dimension    | `4096`         |
| Metric       | `cosine`       |
| Type         | Serverless     |
| Cloud/Region | AWS / us-east-1 |
| Namespace    | `bimbam_docs`  |

---

## Free-tier constraints to know

- **Render free web services sleep after 15 min of inactivity**. First request after sleep takes ~30s to wake up. For a demo this is fine.
- **Pinecone Starter plan**: 2 GB storage (≈ 125k vectors of 4096 dim), AWS us-east-1 only, 5 indexes per project. Your 159 chunks use far less than this.
- **Vercel Hobby**: 100 GB bandwidth / month. Plenty for a chat UI.
- **NVIDIA build.nvidia.com** has its own rate limits; `rag.py` already implements `tenacity` retries with exponential backoff for 429s.

---

## Troubleshooting

### Backend health returns `vectorstore: disconnected`

- Re-check `PINECONE_API_KEY` and `PINECONE_INDEX_NAME` in Render env vars.
- Confirm the index `bimbam-docs` exists in the Pinecone account that matches the key.
- Run `python backend/ingest.py` locally with the same key to confirm the namespace has data.

### Frontend chat shows "Chat request failed"

- Open DevTools → Network. Check the request URL points to the Render backend (should be `https://bimbam-backend.onrender.com/api/chat`).
- If it points to `/api/chat` (same origin), `VITE_API_URL` is missing in Vercel — add it and redeploy.
- If the URL is correct but returns 504/timeout, the backend may be sleeping on Render. Wait ~30s and retry.

### SSE stream cuts or returns no tokens

- Try a simple question like "¿hola?" — the greeting fast-path returns without calling the LLM.
- Check backend logs in Render dashboard: `/api/chat` errors are logged with the query text.
- If you see `RuntimeError: NVIDIA API rate limit`, the NVIDIA endpoint is throttling — wait and retry.

---

## Re-running ingest after PDF changes

If you add new PDFs to `documents/` and want the chatbot to answer from them:

1. Locally (with `NVIDIA_API_KEY` and `PINECONE_API_KEY` set):
   ```bash
   python backend/ingest.py
   ```
2. The script deletes the existing namespace and re-embeds all PDFs. No backend redeploy needed — Pinecone updates in place.