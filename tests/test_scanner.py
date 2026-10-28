import pytest
from pathlib import Path
from src.ce.scanner import iter_files

def test_scanner_ignores_and_filters(tmp_path: Path):
    # Tạo cấu trúc thư mục giả định
    (tmp_path / "valid.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("ignore me", encoding="utf-8")
    
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "lib.py").write_text("secret = 1", encoding="utf-8")

    files = list(iter_files(tmp_path))
    assert len(files) == 1
    assert files[0] == Path("valid.py")