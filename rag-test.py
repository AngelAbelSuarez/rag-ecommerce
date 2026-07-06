#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  BimBam Buy — RAG Chatbot Test Suite                   ║
║                                                        ║
║  Uso: python rag-test.py                                ║
║       python rag-test.py "¿Cuánto tarda un envío?"      ║
║       python rag-test.py --interactive                  ║
║       python rag-test.py --ingest-only                  ║
╚══════════════════════════════════════════════════════════╝

  La primera vez te va a pedir la API key de OpenRouter.
  Se guarda en backend/.env y no se sube a git.
"""

import sys
import subprocess
import os
from pathlib import Path

ROOT = Path(__file__).parent
BACKEND = ROOT / "backend"
ENV_FILE = BACKEND / ".env"
ENV_EXAMPLE = BACKEND / ".env.example"


# ── Colores ─────────────────────────────────────────────────────────

class C:
    VERDE = "\033[92m"
    AMAR = "\033[93m"
    ROJO = "\033[91m"
    CYAN = "\033[96m"
    GRIS = "\033[90m"
    NEG = "\033[0m"
    BOLD = "\033[1m"


# ── Setup ───────────────────────────────────────────────────────────

def ensure_env():
    """Si no existe backend/.env, lo crea pidiendo la API key."""
    if ENV_FILE.exists():
        return

    print(f"\n{C.AMAR}╔{'═'*50}╗{C.NEG}")
    print(f"{C.AMAR}║  Primera vez — configurando API key               ║{C.NEG}")
    print(f"{C.AMAR}╚{'═'*50}╝{C.NEG}")
    print()
    print(f"  Necesitás una API key de {C.BOLD}OpenRouter{ C.NEG} (gratis).")
    print(f"  1. Andá a https://openrouter.ai/keys")
    print(f"  2. Creá una cuenta")
    print(f"  3. Generá una API key")
    print(f"  4. Pegala abajo")
    print()

    key = input(f"  {C.CYAN}▸ API key de OpenRouter:{C.NEG} ").strip()

    if not key:
        print(f"\n  {C.ROJO}✗ No ingresaste ninguna key. Ejecutá de nuevo cuando tengas una.{C.NEG}")
        sys.exit(1)

    # Copiar .env.example si existe
    if ENV_EXAMPLE.exists():
        env_content = ENV_EXAMPLE.read_text(encoding="utf-8")
    else:
        env_content = "OPENROUTER_API_KEY=\n"

    env_content = env_content.replace("OPENROUTER_API_KEY=", f"OPENROUTER_API_KEY={key}")

    ENV_FILE.write_text(env_content, encoding="utf-8")
    print(f"\n  {C.VERDE}✓ API key guardada en backend/.env{C.NEG}")
    print(f"  {C.GRIS}  No se sube a git — está en .gitignore{C.NEG}\n")


def ensure_deps():
    """Instala dependencias si falta alguna."""
    try:
        import fastapi  # noqa
        return  # ya instalado
    except ImportError:
        pass

    print(f"\n  {C.AMAR}📦 Instalando dependencias...{C.NEG}")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=str(BACKEND),
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  {C.ROJO}✗ Error instalando dependencias:{C.NEG}")
        print(result.stderr)
        sys.exit(1)
    print(f"  {C.VERDE}✓ Dependencias instaladas{C.NEG}\n")


# ── Comandos ────────────────────────────────────────────────────────

def run_ingest():
    """Ejecuta la ingesta de PDFs."""
    print(f"\n{C.CYAN}📥 Ingestando PDFs...{C.NEG}")
    result = subprocess.run(
        [sys.executable, "-c", """
import sys; sys.path.insert(0, '.')
from app.config import settings
from app.ingestion import run_ingestion
run_ingestion(force=True)
print("OK")
"""],
        cwd=str(BACKEND),
        capture_output=True, text=True,
    )
    for line in result.stdout.split("\n"):
        if line.strip():
            print(f"  {line}")
    if result.returncode != 0:
        print(f"  {C.ROJO}✗ Error en ingesta:{C.NEG}")
        print(result.stderr)
        return False
    print(f"  {C.VERDE}✓ Ingesta completada{C.NEG}")
    return True


def run_server():
    """Arranca el servidor FastAPI."""
    print(f"\n{C.CYAN}🚀 Arrancando servidor en http://localhost:8000{C.NEG}")
    print(f"  {C.GRIS}  Doc: http://localhost:8000/docs{C.NEG}")
    print(f"  {C.GRIS}  Ctrl+C para detener{C.NEG}\n")
    os.chdir(str(BACKEND))
    result = subprocess.run([sys.executable, "run.py"])
    return result.returncode


def run_query(query: str):
    """Ejecuta una consulta directa."""
    print(f"\n{C.CYAN}❓ Consulta: {query}{C.NEG}")
    print(f"  {'─'*50}")
    result = subprocess.run(
        [sys.executable, "test_query.py", query],
        cwd=str(BACKEND),
        capture_output=True, text=True,
    )
    for line in (result.stdout + result.stderr).split("\n"):
        if line.strip():
            print(f"  {line}")
    if result.returncode != 0:
        print(f"\n  {C.ROJO}✗ Error ejecutando consulta{C.NEG}")


def run_interactive():
    """Modo interactivo."""
    result = subprocess.run(
        [sys.executable, "test_query.py", "--interactive"],
        cwd=str(BACKEND),
    )


# ── Main ────────────────────────────────────────────────────────────

def main():
    print(f"\n{C.BOLD}{C.VERDE}╔{'═'*50}╗")
    print(f"║  🛒  BimBam Buy — RAG Chatbot            ║")
    print(f"╚{'═'*50}╝{C.NEG}\n")

    ensure_env()
    ensure_deps()

    args = [a for a in sys.argv[1:] if a != "--ingest-only"]

    if "--ingest-only" in sys.argv:
        ensure_deps()
        run_ingest()
        return

    # Siempre asegurar ingesta antes de consultar
    run_ingest()

    if "--interactive" in sys.argv or "-i" in sys.argv:
        run_interactive()
    elif args:
        run_query(" ".join(args))
    else:
        run_server()


if __name__ == "__main__":
    main()
