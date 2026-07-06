# Landing Page Specification

## Purpose

Página de presentación de BimBam Buy como e-commerce LATAM. Comunica la propuesta de valor, features clave, métricas de alcance, y dirige a los visitantes hacia el chat con el asistente IA. Sirve como puerta de entrada antes de la experiencia conversacional.

## Requirements

| ID | Requirement | Strength |
|----|-------------|----------|
| LP-REQ-01 | Navegación sticky con logo, links (Productos, Chat, Ayuda) y CTA "Hablar con BimBam" | MUST |
| LP-REQ-02 | Hero section: tag "✨ Asistente IA", título, subtítulo, 2 botones (CTA primario + secundario) | MUST |
| LP-REQ-03 | Features section: 4 cards con ícono, título, descripción (envíos, garantía, pagos, devoluciones) | MUST |
| LP-REQ-04 | Stats section: 4 métricas (países, métodos de pago, documentos, afiliados) con números y labels | MUST |
| LP-REQ-05 | CTA section: texto motivador + botón para ir al chat | MUST |
| LP-REQ-06 | Footer: logo, links de navegación, copyright | MUST |
| LP-REQ-07 | Responsive: layout se adapta a 375px (mobile) y 1200px+ (desktop) | MUST |
| LP-REQ-08 | Dark mode consistente con el resto de la app (variables del diseño) | MUST |
| LP-REQ-09 | Botón CTA "Hablar con BimBam" navega a `/chat` | MUST |
| LP-REQ-10 | Animaciones sutiles: fade-in en scroll para features y stats | SHOULD |

### Scenario: Visitante llega al landing page

- **GIVEN** un visitante nuevo accede a la URL raíz `/`
- **WHEN** la página carga completamente
- **THEN** ve el navbar sticky con logo "BimBam Buy" y links
- **AND** ve el hero con tag "✨ Asistente IA" y título principal
- **AND** el CTA primario "Hablar con BimBam" es visible y clickeable

### Scenario: Navegación al chat desde el landing

- **GIVEN** el visitante está en el landing page
- **WHEN** hace click en "Hablar con BimBam" (navbar o hero)
- **THEN** es redirigido a `/chat`
- **AND** la transición es instantánea (SPA client-side routing)

### Scenario: Visualización en mobile (375px)

- **GIVEN** viewport de 375px de ancho
- **WHEN** la página carga
- **THEN** el navbar muestra solo logo y CTA (links colapsados o simplificados)
- **AND** el hero se apila verticalmente (texto arriba, mockup abajo)
- **AND** las 4 feature cards se muestran en 1 columna
- **AND** las stats se organizan en 2 filas de 2
- **AND** el footer tiene layout vertical con links apilados
- **AND** todos los textos son legibles, sin overflow horizontal

### Scenario: Features section con 4 cards

- **GIVEN** la página cargó correctamente
- **WHEN** el usuario scrollea a la sección de features
- **THEN** ve 4 cards en grid (2x2 en desktop, 1 columna en mobile)
- **AND** cada card tiene: ícono representativo, título, descripción breve
- **AND** las cards son: Envíos, Garantía, Pagos, Devoluciones
- **AND** las cards tienen animación fade-in al entrar al viewport

### Scenario: Stats section

- **GIVEN** la página cargó correctamente
- **WHEN** el usuario scrollea a la sección de stats
- **THEN** ve 4 bloques con número destacado y label descriptivo
- **AND** los stats son: "12 Países", "8 Métodos de pago", "5 Documentos", "1 Programa de afiliados"
- **AND** diseño horizontal en desktop, grid 2x2 en mobile

### Scenario: CTA final y footer

- **GIVEN** el usuario está al final del landing page
- **WHEN** scrollea hasta abajo
- **THEN** ve una sección CTA con texto tipo "¿Listo para resolver tus dudas?" y botón
- **AND** debajo, el footer con logo, links (Productos, Chat, Ayuda, Términos, Privacidad) y copyright

### Scenario: Página 404

- **GIVEN** el usuario navega a una ruta inexistente
- **WHEN** la ruta no matchea `/`, `/chat`, ni recursos estáticos
- **THEN** se muestra la página 404 con: ícono o ilustración, texto "Página no encontrada", subtítulo amigable
- **AND** un botón "Volver al inicio" que navega a `/`
- **AND** diseño consistente con el dark mode del resto de la app

## Technical Details

| Aspect | Detail |
|--------|--------|
| **Ruta** | `/` |
| **Componentes** | `LandingPage`, `Navbar`, `Hero`, `Features`, `Stats`, `CTASection`, `Footer` |
| **Not Found** | `NotFoundPage` en ruta catch-all `*` |
| **Navegación** | `react-router-dom` v7 con `<Link to="/chat">` para CTAs |
| **Animaciones** | Tailwind `animate-*` o `framer-motion` para fade-in on scroll |
| **Estilos** | Tailwind CSS con variables del tema (`$bg-primary`, `$accent`, etc.) |
| **shadcn/ui** | Button, Card (para features), Badge (para tag) |
| **Imágenes** | Placeholders SVG o ilustraciones inline (sin dependencias externas de assets) |

## Visual Reference

Diseño de referencia: `design.documind.op`
- Página `Landing` — desktop layout completo (1200px)
- Página `Landing Mobile` — mobile layout (375px)
- Página `Landing Light` — variante light mode
- Página `404` — página de error

### Secciones del diseño (desktop, 1200px)

| Sección | Alto aprox | Contenido |
|---------|------------|-----------|
| Navbar | 72px | Logo + NavLinks + CTAButton |
| Hero | 600px | TagBadge + HeroTitle + HeroSub + HeroButtons + HeroMockup |
| Features | 480px | FeaturesHeader + FeatureGrid (4 cards) |
| Stats | 200px | 4 Stat cards con número + label |
| CTA | 320px | Texto + CTABtn |
| Footer | 280px | FooterMain + divider + FooterBottom |

## Copy / Contenido

| Elemento | Texto sugerido |
|----------|---------------|
| Hero tag | "✨ Asistente IA" |
| Hero title | "Todas tus dudas sobre BimBam Buy, resueltas al instante" |
| Hero subtitle | "Preguntale a BimBam sobre envíos, garantía, pagos, devoluciones o nuestro programa de afiliados." |
| Hero CTA primario | "Hablar con BimBam" |
| Hero CTA secundario | "Conocer más" |
| Features header | "¿Qué podés consultar?" |
| Feature 1 | 🚚 Envíos — Tiempos y costos a 12 países de LATAM |
| Feature 2 | 🛡️ Garantía — Cobertura y procesos de reclamo |
| Feature 3 | 💳 Pagos — 8 métodos disponibles, seguridad y FAQs |
| Feature 4 | 🔄 Devoluciones — Políticas de reembolso paso a paso |
| Stats | 12 Países / 8 Métodos de pago / 5 Documentos / 1 Programa de afiliados |
| CTA title | "¿Listo para resolver tus dudas?" |
| CTA subtitle | "BimBam te responde en segundos." |
| Footer copyright | "© 2026 BimBam Buy. Todos los derechos reservados." |

## Non-Functional Requirements

| ID | Requirement | Strength |
|----|-------------|----------|
| LP-NFR-01 | Lighthouse Performance score > 90 (desktop) | SHOULD |
| LP-NFR-02 | Lighthouse Accessibility score > 90 | SHOULD |
| LP-NFR-03 | Sin dependencia de imágenes externas (todo inline o SVG) | SHOULD |
| LP-NFR-04 | Scroll suave entre secciones (`scroll-behavior: smooth`) | SHOULD |
