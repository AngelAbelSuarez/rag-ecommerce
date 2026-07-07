import { Menu } from "lucide-react";

import { Button } from "@/components/ui/button";

import { ThemeToggle } from "./ThemeToggle";

interface TopBarProps {
  title: string;
  onMenuClick: () => void;
}

export function TopBar({ title, onMenuClick }: TopBarProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-[var(--border-hex)] bg-[var(--bg-primary)] px-4">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
          aria-label="Abrir conversaciones"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <h1 className="max-w-[12rem] truncate text-sm font-semibold sm:max-w-md sm:text-base">
          {title}
        </h1>
      </div>
      <ThemeToggle />
    </header>
  );
}
