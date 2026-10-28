
import numpy as np
from src.ce.vector import VectorIndex

def test_vector_search_cosine():
    # Tạo 3 vector giả lập (đã normalize)
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    v3 = np.array([0.707, 0.707, 0.0], dtype=np.float32)

    vectors = np.stack([v1, v2, v3])
    index = VectorIndex(vectors)

    # Query giống v1 nhất
    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    results = index.search(query, k=2)

    assert results[0][0] == 0  # v1 phải đứng đầu (score = 1.0)
    assert results[1][0] == 2  # v3 đứng thứ 2 (score ≈ 0.707)