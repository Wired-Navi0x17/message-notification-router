"""
Submission Package Builder for WhatsApp Message Notification Router.
Creates code.zip / submission.zip containing all source files, models, output.csv, and documentation.
"""

import os
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ZIP_PATH = REPO_ROOT / "code.zip"

INCLUDED_PATHS = [
    "code",
    "dataset",
    "output.csv",
    "README.md",
    "requirements.txt",
    "problem_statement.md",
    "AGENTS.md"
]

EXCLUDED_PATTERNS = [
    "__pycache__",
    ".pytest_cache",
    ".cache",
    ".git",
    ".venv",
    "*.pyc",
    "code.zip",
    "submission.zip"
]


def build_zip_package():
    """Builds clean submission zip package."""
    print(f"📦 Packaging submission artifact into {OUTPUT_ZIP_PATH}...")

    with zipfile.ZipFile(OUTPUT_ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in INCLUDED_PATHS:
            item_path = REPO_ROOT / item
            if not item_path.exists():
                print(f"⚠️ Warning: Skipping missing path {item_path}")
                continue

            if item_path.is_file():
                zipf.write(item_path, arcname=item)
                print(f"  + Added file: {item}")
            elif item_path.is_dir():
                for root, _, files in os.walk(item_path):
                    for file in files:
                        filepath = Path(root) / file
                        rel_path = filepath.relative_to(REPO_ROOT)

                        # Exclude cache and temporary files
                        if any(ex in str(rel_path) for ex in ["__pycache__", ".pytest_cache", ".pyc"]):
                            continue

                        zipf.write(filepath, arcname=str(rel_path))
                        print(f"  + Added: {rel_path}")

    zip_size_mb = OUTPUT_ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f"✅ Submission package created successfully! Size: {zip_size_mb:.2f} MB")
    return OUTPUT_ZIP_PATH


if __name__ == "__main__":
    build_zip_package()
