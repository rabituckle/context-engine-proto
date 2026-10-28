from src.ce.hybrid import rrf


def test_rrf_combining_rankings():
    # Danh sách 1: [0, 1, 2]
    # Danh sách 2: [1, 0, 3]
    # Item 0 và 1 xuất hiện ở cả 2 danh sách -> Phải xếp trên 2 và 3
    ranking_bm25 = [0, 1, 2]
    ranking_vec = [1, 0, 3]

    fused = rrf([ranking_bm25, ranking_vec], k=60)
    top_indices = [idx for idx, _ in fused]

    assert set(top_indices[:2]) == {0, 1}
    assert fused[0][1] > fused[2][1]