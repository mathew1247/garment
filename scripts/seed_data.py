import os
import sys
from pathlib import Path

# Add backend to path and delegate to backend/scripts/seed_data.py
project_root = Path(__file__).resolve().parent.parent
backend_dir = project_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.scripts.seed_data import run_seed

if __name__ == "__main__":
    run_seed()
