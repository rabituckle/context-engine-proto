import time
from pathlib import Path
from src.ce.config import INDEX_DIR
from src.ce.scanner import iter_files
from src.ce.chunker import chunk_file
from src.ce.embedder import Embedder
from src.ce.store import save_index


def build_index(repo_path: Path, embedder: Embedder = None) -> None:
    """Quét toàn bộ repo và lập chỉ mục."""
    start_time = time.time()
    repo_path = repo_path.resolve()
    print(f"🚀 Bắt đầu lập chỉ mục cho repository: {repo_path}")

    # 1. Quét file
    files = list(iter_files(repo_path))
    print(f"📁 Đã tìm thấy {len(files)} file code phù hợp.")

    # 2. Cắt chunk theo AST
    all_chunks = []
    for rel_path in files:
        chunks = chunk_file(repo_path, rel_path)
        all_chunks.extend(chunks)

    print(f"🧩 Đã tạo tổng cộng {len(all_chunks)} chunks từ AST.")

    if not all_chunks:
        print("⚠️ Không có chunk nào được tạo. Hủy quá trình index.")
        return

    # 3. Tạo vector embedding
    if embedder is None:
        print("🤖 Đang tải mô hình embedding (all-MiniLM-L6-v2)...")
        embedder = Embedder()

    print("⚡ Đang tạo vector embeddings...")
    texts = [c.text for c in all_chunks]
    vectors = embedder.encode(texts)

    # 4. Lưu index xuống ổ đĩa
    target_index_dir = repo_path / INDEX_DIR
    save_index(target_index_dir, all_chunks, vectors)

    elapsed = time.time() - start_time
    print(f"✅ Lập chỉ mục thành công! Lưu tại: {target_index_dir}")
    print(f"⏱️ Tổng thời gian: {elapsed:.2f} giây.")