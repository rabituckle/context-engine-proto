import json
from pathlib import Path
from typing import List, Tuple
import numpy as np
from src.ce.models import Chunk


def save_index(index_dir: Path, chunks: List[Chunk], vectors: np.ndarray) -> None:
    """Lưu danh sách chunks và ma trận vectors vào thư mục chỉ mục."""
    index_dir.mkdir(parents=True, exist_ok=True)

    # 1. Lưu chunks dạng JSON
    chunks_path = index_dir / "chunks.json"
    chunks_data = [c.to_dict() for c in chunks]
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2)

    # 2. Lưu vectors dạng NumPy array (.npy)
    vectors_path = index_dir / "vectors.npy"
    np.save(vectors_path, vectors)


def load_index(index_dir: Path) -> Tuple[List[Chunk], np.ndarray]:
    """Đọc chunks và vectors từ thư mục chỉ mục."""
    chunks_path = index_dir / "chunks.json"
    vectors_path = index_dir / "vectors.npy"

    if not chunks_path.exists() or not vectors_path.exists():
        raise FileNotFoundError(f"Không tìm thấy index tại {index_dir}. Hãy chạy lệnh 'index' trước.")

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)
    chunks = [Chunk.from_dict(d) for d in chunks_data]

    vectors = np.load(vectors_path)
    return chunks, vectors