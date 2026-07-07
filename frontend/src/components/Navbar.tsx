import { Link } from "react-router";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-[var(--border-hex)] bg-white/80 backdrop-blur-md dark:bg-zinc-900/80">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent-hex)] text-white">
            B
          </span>
          BimBam Chat
        </Link>

        <div className="flex items-center gap-2 sm:gap-4">
          <Link
            to="/"
            className="hidden text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] sm:inline"
          >
            Inicio
          </Link>
          <Link
            to="/chat"
            className="hidden text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] sm:inline"
          >
            Chat
          </Link>
          <ThemeToggle />
          <Button asChild size="sm" className="hidden sm:inline-flex">
            <Link to="/chat">Comenzar</Link>
          </Button>
        </div>
      </nav>
    </header>
  );
}
