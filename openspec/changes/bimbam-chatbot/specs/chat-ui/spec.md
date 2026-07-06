# Chat UI Specification

## Purpose

Interfaz de chat estilo ChatGPT para interactuar con el asistente RAG de BimBam Buy. Layout con sidebar de historial, área de mensajes con streaming en tiempo real, y toggle dark/light mode. Responsive: sidebar colapsable en mobile. Sin mostrar fuentes ni documentos citados.

## Requirements

| ID | Requirement | Strength |
|----|-------------|----------|
| CU-REQ-01 | Layout: sidebar izquierda (historial) + área de chat central + input inferior | MUST |
| CU-REQ-02 | Sidebar con lista de sesiones de chat (título: primera pregunta), botón "Nuevo chat" | MUST |
| CU-REQ-03 | Área de mensajes: burbujas con avatar (asistente verde `#10a37f`, usuario violeta `#7c3aed`) | MUST |
| CU-REQ-04 | Input con placeholder "Preguntale a BimBam..." y botón enviar | MUST |
| CU-REQ-05 | Renderizado streaming: texto aparece token por token en la burbuja del asistente | MUST |
| CU-REQ-06 | Dark/light mode toggle en topbar, persiste preferencia en localStorage | MUST |
| CU-REQ-07 | Dark mode default: fondo `#343541`, mensajes usuario `#343541`, asistente `#444654` | MUST |
| CU-REQ-08 | Sidebar colapsable en viewport < 768px (toggle hamburger en topbar) | MUST |
| CU-REQ-09 | NO mostrar fuentes, documentos citados, ni scores de similitud | MUST |
| CU-REQ-10 | Scroll automático al último mensaje cuando llega nuevo contenido | MUST |
| CU-REQ-11 | Estado "BimBam está escribiendo..." con indicador de typing animado (3 dots) | SHOULD |
| CU-REQ-12 | Atajo de teclado: Enter envía, Shift+Enter agrega nueva línea | SHOULD |
| CU-REQ-13 | Manejar errores de conexión con toast o mensaje inline: "No se pudo conectar con BimBam" | SHOULD |

### Scenario: Enviar una pregunta y recibir respuesta streaming

- **GIVEN** el usuario está en la página de chat en una sesión nueva
- **WHEN** escribe "¿cómo hago una devolución?" y presiona Enter
- **THEN** aparece una burbuja violeta con el mensaje del usuario
- **AND** aparece una burbuja verde con el indicador de typing
- **AND** el texto de la respuesta aparece progresivamente token por token
- **AND** al finalizar, desaparece el indicador de typing
- **AND** el scroll se ajusta automáticamente para mostrar el contenido nuevo

### Scenario: Sidebar colapsa en mobile

- **GIVEN** viewport de 375px de ancho (mobile)
- **WHEN** la página carga
- **THEN** la sidebar está oculta
- **AND** el topbar muestra un icono hamburger (☰) a la izquierda
- **WHEN** el usuario toca el icono hamburger
- **THEN** la sidebar se despliega como overlay sobre el chat
- **AND** al tocar fuera de la sidebar o seleccionar un chat, la sidebar se cierra

### Scenario: Toggle dark/light mode

- **GIVEN** el usuario está en dark mode (default)
- **WHEN** hace click en el toggle de modo (ícono sol/luna) en el topbar
- **THEN** la interfaz cambia a light mode: fondo `#ffffff`, sidebar `#f7f7f8`, mensajes ajustados
- **AND** la preferencia se guarda en localStorage
- **WHEN** el usuario recarga la página
- **THEN** la interfaz se carga en light mode (respeta preferencia guardada)

### Scenario: Sesiones en sidebar

- **GIVEN** el usuario ha tenido 3 conversaciones previas
- **WHEN** la página carga
- **THEN** la sidebar muestra las 3 sesiones anteriores, cada una con título = primera pregunta
- **AND** un botón "Nuevo chat" aparece al inicio de la lista
- **WHEN** el usuario hace click en una sesión anterior
- **THEN** se cargan los mensajes de esa sesión en el área de chat

### Scenario: Error de conexión con el backend

- **GIVEN** el backend no está respondiendo
- **WHEN** el usuario envía una pregunta
- **THEN** se muestra un toast rojo: "No se pudo conectar con BimBam. Revisá tu conexión."
- **AND** el mensaje del usuario permanece visible en el chat
- **AND** el input se re-habilita para reintentar

### Scenario: Chat vacío (estado inicial)

- **GIVEN** el usuario acaba de abrir un nuevo chat
- **WHEN** no hay mensajes aún
- **THEN** el área central muestra el logo de BimBam centrado
- **AND** un texto sugerente debajo: "¿En qué puedo ayudarte hoy?"
- **AND** el input está enfocado y listo para escribir

### Scenario: Enter envía, Shift+Enter agrega nueva línea

- **GIVEN** el input tiene foco
- **WHEN** el usuario presiona Enter (sin Shift)
- **THEN** el mensaje se envía
- **WHEN** el usuario presiona Shift+Enter
- **THEN** se inserta un salto de línea en el input (sin enviar)

## Technical Details

| Aspect | Detail |
|--------|--------|
| **Ruta** | `/chat` |
| **Componentes principales** | `ChatLayout`, `Sidebar`, `ChatArea`, `MessageList`, `MessageBubble`, `ChatInput`, `TopBar` |
| **Streaming** | `fetch()` con `ReadableStream` parseando SSE `data:` events |
| **Estado** | `useState` para mensajes, `useEffect` para scroll y localStorage |
| **Estilos** | Tailwind CSS con variables CSS custom properties para theming |
| **shadcn/ui** | Button, Input, ScrollArea, Avatar, Tooltip, Toast (sonner) |
| **Dark mode** | Clase `dark` en `<html>`, variables CSS condicionales |
| **Responsive** | Sidebar: `hidden lg:flex` + overlay `fixed` en mobile |
| **Colores** | Ver variables en `design.documind.op`: `$accent` = `#10a37f`, `$bg-primary` = `#343541`, etc. |

## Visual Reference

Diseño de referencia: `design.documind.op` — páginas `Chat`, `Landing Light` (light mode).

| Variable | Dark | Light |
|----------|------|-------|
| Fondo principal | `#343541` | `#ffffff` |
| Fondo sidebar | `#202123` | `#f7f7f8` |
| Fondo msg asistente | `#444654` | `#ececf1` |
| Fondo msg usuario | `#343541` | `#ffffff` |
| Fondo input | `#40414f` | `#ffffff` |
| Texto principal | `#ececf1` | `#2d2d2d` |
| Texto secundario | `#8e8ea0` | `#6b6b6b` |
| Acento | `#10a37f` | `#10a37f` |
| Bordes | `#4d4d5f` | `#e5e5e5` |

## Non-Functional Requirements

| ID | Requirement | Strength |
|----|-------------|----------|
| CU-NFR-01 | Layout funcional en viewports 375px–1440px | MUST |
| CU-NFR-02 | Primer render (LCP) < 2 segundos | SHOULD |
| CU-NFR-03 | Transiciones de modo dark/light sin flicker (aplica antes del primer paint) | SHOULD |
| CU-NFR-04 | Scroll suave (smooth scroll behavior) al recibir nuevo contenido | SHOULD |
