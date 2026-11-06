"""
Shield AI — Single Command Application Launcher
DecodeLabs Full Stack Development Internship (Batch 2026)

Starts the unified full-stack application:
- Auto-initializes the SQLite relational database (SQLAlchemy models)
- Mounts REST API routes and Gatekeeper policy engine
- Serves the mobile-first responsive frontend at http://127.0.0.1:8000
"""

import sys
import uvicorn
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def main():
    print("=" * 70)
    print("  SHIELD AI — AI AGENT SECURITY SHIELD")
    print("  Secure Every Prompt. Control Every Action. Trust Every Agent.")
    print("=" * 70)
    print("  Starting unified full-stack application on http://127.0.0.1:8000")
    print("  - Frontend Command Center:  http://127.0.0.1:8000")
    print("  - Interactive Swagger Docs: http://127.0.0.1:8000/docs")
    print("  - API Health Endpoint:      http://127.0.0.1:8000/api/health")
    print("  - Relational Database:      data/shield_ai.db (SQLite + SQLAlchemy 2.0)")
    print("=" * 70)
    print("  Press Ctrl+C to stop the server.\n")

    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
