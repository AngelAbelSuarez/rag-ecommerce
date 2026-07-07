"""Shared pytest configuration for backend tests.

Adds the ``backend/`` directory to ``sys.path`` so the application modules can
be imported with their top-level names (``config``, ``store``, ``rag``, etc.)
as the runtime code expects.
"""

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_DIR))
