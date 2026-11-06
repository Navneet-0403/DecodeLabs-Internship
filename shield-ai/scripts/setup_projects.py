"""
Script to organize shield-ai into 4 modular milestone projects:
- project-1: Responsive Frontend
- project-2: Backend API Development
- project-3: Database Integration
- project-4: Full-Stack Integration
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path("C:/Users/navne/Downloads/shield-ai")

EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".agents", "project-1", "project-2", "project-3", "project-4"}
EXCLUDE_EXTS = {".pyc", ".pyo"}

def copy_tree_clean(src: Path, dst: Path, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = set()
    all_ignore = EXCLUDE_DIRS | ignore_dirs

    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in all_ignore]
        rel = Path(root).relative_to(src)
        target_dir = dst / rel
        target_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            if any(f.endswith(ext) for ext in EXCLUDE_EXTS):
                continue
            if f in {"shield-ai.zip"}:
                continue
            shutil.copy2(Path(root) / f, target_dir / f)

def setup_project_1():
    p1 = BASE_DIR / "project-1"
    print("Setting up Project 1 in", p1)
    if p1.exists():
        shutil.rmtree(p1)
    p1.mkdir(parents=True, exist_ok=True)

    # Copy frontend files
    shutil.copy2(BASE_DIR / "index.html", p1 / "index.html")
    copy_tree_clean(BASE_DIR / "css", p1 / "css")
    copy_tree_clean(BASE_DIR / "js", p1 / "js")
    if (BASE_DIR / "assets").exists():
        copy_tree_clean(BASE_DIR / "assets", p1 / "assets")
    if (BASE_DIR / "screenshots").exists():
        copy_tree_clean(BASE_DIR / "screenshots", p1 / "screenshots")

def setup_project_2():
    p2 = BASE_DIR / "project-2"
    print("Setting up Project 2 in", p2)
    if p2.exists():
        shutil.rmtree(p2)
    p2.mkdir(parents=True, exist_ok=True)

    # Copy Project 2 files (Frontend + Backend APIs)
    shutil.copy2(BASE_DIR / "index.html", p2 / "index.html")
    copy_tree_clean(BASE_DIR / "css", p2 / "css")
    copy_tree_clean(BASE_DIR / "js", p2 / "js")
    copy_tree_clean(BASE_DIR / "backend", p2 / "backend", ignore_dirs={"migrations"})
    copy_tree_clean(BASE_DIR / "data", p2 / "data")

def setup_project_3():
    p3 = BASE_DIR / "project-3"
    print("Setting up Project 3 in", p3)
    if p3.exists():
        shutil.rmtree(p3)
    p3.mkdir(parents=True, exist_ok=True)

    # Copy Project 3 files (Frontend + Backend + DB Migrations + ORM)
    shutil.copy2(BASE_DIR / "index.html", p3 / "index.html")
    shutil.copy2(BASE_DIR / "alembic.ini", p3 / "alembic.ini")
    copy_tree_clean(BASE_DIR / "css", p3 / "css")
    copy_tree_clean(BASE_DIR / "js", p3 / "js")
    copy_tree_clean(BASE_DIR / "backend", p3 / "backend")
    copy_tree_clean(BASE_DIR / "data", p3 / "data")

def setup_project_4():
    p4 = BASE_DIR / "project-4"
    print("Setting up Project 4 in", p4)
    if p4.exists():
        shutil.rmtree(p4)
    p4.mkdir(parents=True, exist_ok=True)

    # Copy full-stack files + tests + scripts + final zip
    shutil.copy2(BASE_DIR / "index.html", p4 / "index.html")
    shutil.copy2(BASE_DIR / "alembic.ini", p4 / "alembic.ini")
    if (BASE_DIR / ".gitignore").exists():
        shutil.copy2(BASE_DIR / ".gitignore", p4 / ".gitignore")
    if (BASE_DIR / "shield-ai-final.zip").exists():
        shutil.copy2(BASE_DIR / "shield-ai-final.zip", p4 / "shield-ai-final.zip")

    copy_tree_clean(BASE_DIR / "css", p4 / "css")
    copy_tree_clean(BASE_DIR / "js", p4 / "js")
    copy_tree_clean(BASE_DIR / "backend", p4 / "backend")
    copy_tree_clean(BASE_DIR / "data", p4 / "data")
    copy_tree_clean(BASE_DIR / "tests", p4 / "tests")
    copy_tree_clean(BASE_DIR / "scripts", p4 / "scripts")
    if (BASE_DIR / "screenshots").exists():
        copy_tree_clean(BASE_DIR / "screenshots", p4 / "screenshots")

if __name__ == "__main__":
    setup_project_1()
    setup_project_2()
    setup_project_3()
    setup_project_4()
    print("All 4 project directories populated.")

