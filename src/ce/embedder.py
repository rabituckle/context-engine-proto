from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load mô hình embedding
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Tạo vector embeddings cho danh sách các văn bản/chunk text."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,  # Chuẩn hóa L2 để tính Cosine Similarity bằng tích vô hướng (Dot Product)
        )
        return np.array(embeddings, dtype=np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Tạo vector embedding cho 1 câu query."""
        embedding = self.model.encode(
            [query],
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.array(embedding[0], dtype=np.float32)