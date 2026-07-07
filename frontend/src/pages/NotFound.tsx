import { Link } from "react-router";

import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[var(--bg-primary)] px-4 text-center">
      <h1 className="mb-2 text-8xl font-extrabold tracking-tighter text-[var(--accent-hex)] sm:text-9xl">
        404
      </h1>
      <h2 className="mb-4 text-2xl font-semibold text-[var(--text-primary)] sm:text-3xl">
        Página no encontrada
      </h2>
      <p className="mb-8 max-w-md text-[var(--text-secondary)]">
        La página que buscás no existe o fue movida.
      </p>
      <Button asChild size="lg">
        <Link to="/">Volver al inicio</Link>
      </Button>
    </div>
  );
}
