# BimBam Chatbot — Frontend

Cliente web del asistente virtual de BimBam Buy. Construido con **React 19**, **Vite**, **TypeScript** y **Tailwind CSS 4**.

## Stack

| Capa         | Tecnología                                |
| ------------ | ----------------------------------------- |
| Framework    | React 19                                  |
| Build tool   | Vite 6                                    |
| Lenguaje     | TypeScript 5.6                            |
| Estilos      | Tailwind CSS 4                            |
| Routing      | React Router 7                            |
| Iconos       | Lucide React                              |
| UI Kit       | Radix UI (`@radix-ui/react-slot`) + CVA   |
| Testing      | Vitest + Testing Library                  |

## Estructura

```
frontend/
├── src/
│   ├── main.tsx              # Entry point, BrowserRouter
│   ├── App.tsx               # Routes (/ , /chat, *)
│   ├── index.css             # Estilos globales + variables CSS
│   ├── pages/
│   │   ├── Landing.tsx       # Landing page con hero, features, CTA
│   │   ├── Chat.tsx          # Página del chat
│   │   └── NotFound.tsx      # 404
│   ├── components/
│   │   ├── ChatLayout.tsx    # Layout principal del chat (sidebar + área)
│   │   ├── ChatArea.tsx      # Área de mensajes + input
│   │   ├── ChatInput.tsx     # Input de texto con envío
│   │   ├── MessageBubble.tsx # Burbuja de mensaje individual
│   │   ├── MessageList.tsx   # Lista scrollable de mensajes
│   │   ├── Sidebar.tsx       # Sidebar de conversaciones
│   │   ├── TopBar.tsx        # Barra superior con menú y título
│   │   ├── Navbar.tsx        # Navbar de la landing
│   │   ├── ThemeToggle.tsx   # Toggle dark/light mode
│   │   └── ui/
│   │       └── button.tsx    # Componente Button (shadcn-style)
│   ├── hooks/
│   │   ├── useChat.ts        # Estado y lógica del chat
│   │   ├── useTheme.ts       # Hook de tema dark/light
│   │   └── __tests__/        # Tests de hooks
│   ├── lib/
│   │   ├── api.ts            # Cliente HTTP (SSE, health check)
│   │   ├── utils.ts          # Utilidades generales
│   │   └── __tests__/        # Tests de utilidades
│   └── types/
│       └── chat.ts           # Tipos Message, Conversation, ChatState
├── index.html
├── vite.config.ts            # Proxy /api → localhost:8000
├── vitest.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Requisitos

- Node.js 22+
- pnpm 11+ (recomendado) o npm

## Setup

```bash
cd frontend

# Instalar dependencias
pnpm install
# o: npm install
```

## Uso

### Desarrollo

```bash
pnpm dev
# → http://localhost:5173
```

El `vite.config.ts` tiene un proxy configurado: toda request a `/api` se redirige a `http://localhost:8000` (el backend). No hace falta CORS ni configurar URLs manualmente.

### Build producción

```bash
pnpm build
# → Salida en frontend/dist/
```

### Preview del build

```bash
pnpm preview
```

## Tests

```bash
# Todos los tests
pnpm test

# Modo watch
pnpm test -- --watch
```

## Linting

```bash
pnpm lint
```

## Arquitectura

### Flujo de datos

```
Usuario → ChatInput → useChat.sendMessage()
                  ↓
           lib/api.ts → fetch POST /api/chat (SSE)
                  ↓
           useChat recibe tokens → actualiza estado
                  ↓
           MessageList + MessageBubble renderizan
```

### Temas

El frontend soporta **dark** y **light mode** vía variables CSS (`--bg-primary`, `--text-primary`, etc.) y un hook `useTheme` que persiste la preferencia en `localStorage`.

### Responsive

- **Desktop**: sidebar fijo a la izquierda + área de chat.
- **Mobile**: sidebar como overlay accionado desde la barra superior.

## API Proxy

El `vite.config.ts` redirige `/api/*` al backend:

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

En producción, el proxy lo resuelve el reverse proxy (nginx, etc.) o servís el frontend desde el mismo dominio que el backend.
