from pathlib import Path

BASE_DIR = Path.cwd()

UPLOAD_FOLDER = BASE_DIR / "uploads" / "resumes"

GENERATED_FOLDER = BASE_DIR / "generated"

MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_RESUME_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
}