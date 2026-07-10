# BimBam Chatbot — Frontend

Web client for the BimBam Buy virtual assistant. Built with **React 19**, **Vite**, **TypeScript** and **Tailwind CSS 4**.

## Stack

| Layer         | Technology                                |
| ------------- | ----------------------------------------- |
| Framework     | React 19                                  |
| Build tool    | Vite 6                                    |
| Language      | TypeScript 5.6                            |
| Styling       | Tailwind CSS 4                            |
| Routing       | React Router 7                            |
| Icons         | Lucide React                              |
| UI Kit        | Radix UI (`@radix-ui/react-slot`) + CVA   |
| Testing       | Vitest + Testing Library                  |

## Structure

```
frontend/
├── src/
│   ├── main.tsx              # Entry point, BrowserRouter
│   ├── App.tsx               # Routes (/ , /chat, *)
│   ├── index.css             # Global styles + CSS variables
│   ├── pages/
│   │   ├── Landing.tsx       # Landing page with hero, features, CTA
│   │   ├── Chat.tsx          # Chat page
│   │   └── NotFound.tsx      # 404
│   ├── components/
│   │   ├── ChatLayout.tsx    # Main chat layout (sidebar + area)
│   │   ├── ChatArea.tsx      # Message area + input
│   │   ├── ChatInput.tsx     # Text input with send
│   │   ├── MessageBubble.tsx # Individual message bubble
│   │   ├── MessageList.tsx   # Scrollable message list
│   │   ├── Sidebar.tsx       # Conversations sidebar
│   │   ├── TopBar.tsx        # Top bar with menu and title
│   │   ├── Navbar.tsx        # Landing navbar
│   │   ├── ThemeToggle.tsx   # Dark/light mode toggle
│   │   └── ui/
│   │       └── button.tsx    # Button component (shadcn-style)
│   ├── hooks/
│   │   ├── useChat.ts        # Chat state and logic
│   │   ├── useTheme.ts       # Dark/light theme hook
│   │   └── __tests__/        # Hook tests
│   ├── lib/
│   │   ├── api.ts            # HTTP client (SSE, health check)
│   │   ├── utils.ts          # General utilities
│   │   └── __tests__/        # Utility tests
│   └── types/
│       └── chat.ts           # Message, Conversation, ChatState types
├── index.html
├── vite.config.ts            # Proxy /api → localhost:8000
├── vitest.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Requirements

- Node.js 22+
- pnpm 11+ (recommended) or npm

## Setup

```bash
cd frontend

# Install dependencies
pnpm install
# or: npm install
```

## Usage

### Development

```bash
pnpm dev
# → http://localhost:5173
```

The `vite.config.ts` has a proxy configured: all requests to `/api` are forwarded to `http://localhost:8000` (the backend). No CORS or manual URL configuration needed.

### Production build

```bash
pnpm build
# → Output in frontend/dist/
```

### Build preview

```bash
pnpm preview
```

## Tests

```bash
# All tests
pnpm test

# Watch mode
pnpm test -- --watch
```

## Linting

```bash
pnpm lint
```

## Architecture

### Data flow

```
User → ChatInput → useChat.sendMessage()
                  ↓
           lib/api.ts → fetch POST /api/chat (SSE)
                  ↓
           useChat receives tokens → updates state
                  ↓
           MessageList + MessageBubble render
```

### Theme

The frontend supports **dark** and **light mode** via CSS variables (`--bg-primary`, `--text-primary`, etc.) and a `useTheme` hook that persists the preference in `localStorage`.

### Responsive

- **Desktop**: fixed sidebar on the left + chat area.
- **Mobile**: sidebar as an overlay triggered from the top bar.

## API Proxy

The `vite.config.ts` forwards `/api/*` to the backend:

```ts
server: {
  proxy: {
    "/api": {
      target: "http://localhost:8000",
      changeOrigin: true,
    },
  },
}
```

In production, the proxy is handled by a reverse proxy (nginx, etc.) or by serving the frontend from the same domain as the backend.
