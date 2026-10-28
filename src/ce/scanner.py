from pathlib import Path
from typing import Iterator
import pathspec
from src.ce.config import EXTENSIONS, MAX_FILE_BYTES

DEFAULT_IGNORES = [
    ".git/",
    ".venv/",
    "venv/",
    "__pycache__/",
    "node_modules/",
    ".ce_index/",
    "*.pyc",
]

def load_ignore(repo: Path) -> pathspec.PathSpec:
    patterns = list(DEFAULT_IGNORES)
    gitignore_path = repo / ".gitignore"
    if gitignore_path.is_file():
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
            patterns.extend(f.readlines())
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

def iter_files(repo: Path) -> Iterator[Path]:
    spec = load_ignore(repo)
    repo = repo.resolve()

    for path in repo.rglob("*"):
        if not path.is_file():
            continue

        # Lấy path tương đối so với repo để kiểm tra gitignore
        rel_path = path.relative_to(repo)
        
        # Bỏ qua nếu thuộc danh sách ignore
        if spec.match_file(rel_path):
            continue

        # Kiểm tra đuôi file
        if path.suffix not in EXTENSIONS:
            continue

        # Kiểm tra kích thước file
        if path.stat().st_size > MAX_FILE_BYTES:
            continue

        # Kiểm tra có đọc được UTF-8 không
        try:
            with open(path, "r", encoding="utf-8") as f:
                f.read(1024)
        except (UnicodeDecodeError, PermissionError):
            continue

        yield rel_path