from typing import List, Tuple
import numpy as np


class VectorIndex:
    def __init__(self, vectors: np.ndarray):
        """
        vectors: NumPy array kích thước (N, D) chứa các vector embedding đã normalize L2.
        """
        self.vectors = vectors

    def search(self, qvec: np.ndarray, k: int = 30) -> List[Tuple[int, float]]:
        """
        Tìm kiếm vector gần nhất bằng Cosine Similarity.
        Trả về danh sách (chunk_index, similarity_score) sắp xếp giảm dần.
        """
        if self.vectors is None or len(self.vectors) == 0:
            return []

        # Tích vô hướng giữa ma trận vectors (N, D) và query vector (D,)
        scores = self.vectors @ qvec

        # Lấy chỉ số top-k điểm cao nhất
        top_k_indices = np.argsort(scores)[::-1][:k]

        results = [(int(idx), float(scores[idx])) for idx in top_k_indices]
        return results