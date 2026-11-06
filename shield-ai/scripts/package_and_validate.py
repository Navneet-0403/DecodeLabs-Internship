"""
Shield AI — ZIP Packaging & Integrity Validation Script
Produces portable shield-ai-final.zip with POSIX forward slashes ('/')
"""

import os
import sys
import shutil
import zipfile
import tempfile
import subprocess
from pathlib import Path

SOURCE_DIR = Path("C:/Users/navne/Downloads/shield-ai").resolve()
ZIP_OUTPUT = SOURCE_DIR / "shield-ai-final.zip"
DOWNLOADS_ZIP = Path("C:/Users/navne/Downloads/shield-ai-final.zip")

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".agents",
    ".idea", ".vscode", "node_modules"
}
EXCLUDE_EXTS = {".pyc", ".pyo", ".pyd"}
EXCLUDE_FILES = {"shield-ai-final.zip", "shield-ai.zip"}

REQUIRED_FILES = [
    "shield-ai/index.html",
    "shield-ai/README.md",
    "shield-ai/alembic.ini",
    "shield-ai/.gitignore",
    "shield-ai/css/style.css",
    "shield-ai/css/responsive.css",
    "shield-ai/js/api.js",
    "shield-ai/js/app.js",
    "shield-ai/tests/test_api_client.js",
    "shield-ai/data/shield_ai.db",
    "shield-ai/backend/requirements.txt",
    "shield-ai/backend/app/main.py",
    "shield-ai/backend/app/exceptions.py",
    "shield-ai/backend/app/database/__init__.py",
    "shield-ai/backend/app/database/connection.py",
    "shield-ai/backend/app/database/session.py",
    "shield-ai/backend/app/database/migration.py",
    "shield-ai/backend/app/models/agent.py",
    "shield-ai/backend/app/models/tool.py",
    "shield-ai/backend/app/models/agent_tool.py",
    "shield-ai/backend/app/models/security_event.py",
    "shield-ai/backend/app/models/approval.py",
    "shield-ai/backend/app/models/settings.py",
    "shield-ai/backend/app/repositories/agent_repo.py",
    "shield-ai/backend/app/repositories/tool_repo.py",
    "shield-ai/backend/app/repositories/event_repo.py",
    "shield-ai/backend/app/repositories/approval_repo.py",
    "shield-ai/backend/app/repositories/settings_repo.py",
    "shield-ai/backend/app/routes/dashboard.py",
    "shield-ai/backend/app/routes/scanner.py",
    "shield-ai/backend/app/routes/agents.py",
    "shield-ai/backend/app/routes/permissions.py",
    "shield-ai/backend/app/routes/approvals.py",
    "shield-ai/backend/app/routes/events.py",
    "shield-ai/backend/app/routes/simulator.py",
    "shield-ai/backend/app/routes/settings.py",
    "shield-ai/backend/migrations/env.py",
    "shield-ai/backend/migrations/versions/c569f299eaed_create_project3_relational_schema.py",
    "shield-ai/backend/tests/conftest.py",
    "shield-ai/backend/tests/test_fullstack_integration.py",
]

def build_zip():
    print(f"Building {ZIP_OUTPUT} from {SOURCE_DIR}...")
    if ZIP_OUTPUT.exists():
        ZIP_OUTPUT.unlink()

    file_count = 0
    with zipfile.ZipFile(ZIP_OUTPUT, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in sorted(files):
                if file in EXCLUDE_FILES or any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue

                full_path = Path(root) / file
                rel_path = full_path.relative_to(SOURCE_DIR)

                # Force strictly forward slash POSIX paths
                posix_rel = rel_path.as_posix()
                arcname = f"shield-ai/{posix_rel}"
                assert "\\" not in arcname, f"Backslash detected in arcname: {arcname}"

                zf.write(full_path, arcname=arcname)
                file_count += 1

    print(f"Archive created with {file_count} files.")
    # Also copy to Downloads folder for user convenience
    shutil.copy2(ZIP_OUTPUT, DOWNLOADS_ZIP)
    print(f"Copied archive to {DOWNLOADS_ZIP}")

def validate_zip():
    print(f"\n--- Validating ZIP: {ZIP_OUTPUT} ---")
    assert ZIP_OUTPUT.exists(), "ZIP output does not exist!"

    with zipfile.ZipFile(ZIP_OUTPUT, 'r') as zf:
        # 1. Test CRC / file integrity
        corrupt = zf.testzip()
        assert corrupt is None, f"Corrupted file in archive: {corrupt}"
        print("✔ ZIP CRC32 integrity check passed (0 corrupt entries).")

        namelist = zf.namelist()
        print(f"✔ Archive contains {len(namelist)} total entries.")

        # 2. Check for backslashes
        backslash_entries = [n for n in namelist if "\\" in n]
        assert len(backslash_entries) == 0, f"Found entries with backslashes: {backslash_entries}"
        print("✔ 100% of archive paths use standard POSIX forward slashes ('/').")

        # 3. Check for root nesting
        non_prefixed = [n for n in namelist if not n.startswith("shield-ai/")]
        assert len(non_prefixed) == 0, f"Found entries outside 'shield-ai/' root: {non_prefixed}"
        print("✔ Directory hierarchy cleanly nested under 'shield-ai/'.")

        # 4. Check all required source files
        for req in REQUIRED_FILES:
            assert req in namelist, f"Missing required file: {req}"
        print(f"✔ All {len(REQUIRED_FILES)} key required project files verified present.")

        # 5. Check no excluded files leaked
        for n in namelist:
            for bad_dir in EXCLUDE_DIRS:
                assert f"/{bad_dir}/" not in n and not n.startswith(f"shield-ai/{bad_dir}/"), f"Excluded dir leaked: {n}"
            for bad_ext in EXCLUDE_EXTS:
                assert not n.endswith(bad_ext), f"Excluded file extension leaked: {n}"
        print("✔ No cache, virtual environment, or git files leaked into archive.")

    # 6. Test Extraction in Clean Temporary Directory
    with tempfile.TemporaryDirectory() as extract_dir:
        print(f"\nTesting extraction into clean sandbox: {extract_dir}")
        with zipfile.ZipFile(ZIP_OUTPUT, 'r') as zf:
            zf.extractall(extract_dir)

        extracted_root = Path(extract_dir) / "shield-ai"
        assert (extracted_root / "index.html").exists()
        assert (extracted_root / "backend" / "app" / "main.py").exists()
        print("✔ Extracted directory successfully verified.")

        # Run Node.js API client tests on extracted content
        print("Running Node.js API tests on extracted codebase...")
        test_js = extracted_root / "tests" / "test_api_client.js"
        node_res = subprocess.run(["node", "--test", str(test_js)], capture_output=True, text=True)
        assert node_res.returncode == 0, f"Extracted API client tests failed:\n{node_res.stderr}\n{node_res.stdout}"
        print("✔ Extracted JavaScript tests executed and passed (100%).")

    print("\n==========================================")
    print("ALL ZIP PACKAGING AND INTEGRATION CHECKS PASSED!")
    print(f"Final Artifact 1: {ZIP_OUTPUT} ({ZIP_OUTPUT.stat().st_size:,} bytes)")
    print(f"Final Artifact 2: {DOWNLOADS_ZIP} ({DOWNLOADS_ZIP.stat().st_size:,} bytes)")
    print("==========================================")

if __name__ == "__main__":
    build_zip()
    validate_zip()
