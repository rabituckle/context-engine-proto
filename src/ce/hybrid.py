from typing import List, Dict, Tuple
from src.ce.models import Chunk
from src.ce.lexical import LexicalIndex
from src.ce.vector import VectorIndex
from src.ce.embedder import Embedder


def rrf(rankings: List[List[int]], k: int = 60) -> List[Tuple[int, float]]:
    """
    Thuật toán Reciprocal Rank Fusion (RRF).
    rankings: Danh sách các list các index (ví dụ: [lexical_top_indices, vector_top_indices])
    """
    scores: Dict[int, float] = {}

    for ranking in rankings:
        for rank, idx in enumerate(ranking, start=1):
            if idx not in scores:
                scores[idx] = 0.0
            scores[idx] += 1.0 / (k + rank)

    # Sắp xếp các chỉ số theo điểm RRF giảm dần
    sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_items


def hybrid_search(
    query: str,
    lex_index: LexicalIndex,
    vec_index: VectorIndex,
    embedder: Embedder,
    chunks: List[Chunk],
    top_k: int = 10,
    top_n_candidates: int = 30,
) -> List[Chunk]:
    """Kết hợp tìm kiếm Lexical (BM25) và Vector (Cosine) bằng RRF."""
    if not chunks:
        return []

    # 1. Tìm từ khóa với BM25
    lex_results = lex_index.search(query, k=top_n_candidates)
    lex_indices = [idx for idx, _ in lex_results]

    # 2. Tìm ngữ nghĩa với Vector Embedding
    qvec = embedder.encode_query(query)
    vec_results = vec_index.search(qvec, k=top_n_candidates)
    vec_indices = [idx for idx, _ in vec_results]

    # 3. Gộp kết quả bằng RRF
    fused_results = rrf([lex_indices, vec_indices], k=60)

    # 4. Trả về danh sách các đối tượng Chunk hoàn chỉnh
    final_chunks = [chunks[idx] for idx, _ in fused_results[:top_k]]
    return final_chunks