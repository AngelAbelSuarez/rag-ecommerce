import { useCallback, useEffect, useState } from "react";

type Theme = "dark" | "light" | "system";

const STORAGE_KEY = "bimbam-theme";

function getSystemTheme(): "dark" | "light" {
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function getInitialTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
  return stored ?? "system";
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  const effective = theme === "system" ? getSystemTheme() : theme;
  root.classList.remove("dark", "light");
  root.classList.add(effective);
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    applyTheme(theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  useEffect(() => {
    if (theme !== "system") return;
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => applyTheme("system");
    media.addEventListener("change", handler);
    return () => media.removeEventListener("change", handler);
  }, [theme]);

  const setTheme = useCallback((next: Theme) => {
    setThemeState(next);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((current) => {
      const effective = current === "system" ? getSystemTheme() : current;
      return effective === "dark" ? "light" : "dark";
    });
  }, []);

  const isDark =
    theme === "system" ? getSystemTheme() === "dark" : theme === "dark";

  return { theme, setTheme, toggleTheme, isDark };
}
