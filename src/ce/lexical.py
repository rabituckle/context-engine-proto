import re
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from src.ce.models import Chunk


def tokenize(text: str) -> List[str]:
    """Code-aware Tokenizer: Tách theo snake_case, camelCase, giữ nguyên từ gốc."""
    tokens = []
    
    # 1. Tách theo khoảng trắng và các ký tự đặc biệt (giữ lại dấu gạch dưới)
    raw_words = re.findall(r"[a-zA-Z0-9_]+", text)

    for word in raw_words:
        word_lower = word.lower()
        tokens.append(word_lower)
        
        # Tách tiếp nếu từ chứa snake_case
        sub_words = word.split("_")
        for sw in sub_words:
            if not sw:
                continue
            sw_lower = sw.lower()
            if sw_lower != word_lower:
                tokens.append(sw_lower)
            
            # Tách tiếp camelCase (ví dụ: getUserName -> get, User, Name)
            camel_parts = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", sw).split()
            if len(camel_parts) > 1:
                for cp in camel_parts:
                    cp_lower = cp.lower()
                    if cp_lower not in tokens:
                        tokens.append(cp_lower)

    return tokens


class LexicalIndex:
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.corpus = [tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus else None

    def search(self, query: str, k: int = 30) -> List[Tuple[int, float]]:
        """Tìm kiếm từ khóa bằng BM25, trả về danh sách (chunk_index, score)."""
        if not self.bm25 or not self.chunks:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)

        # Lấy cặp (index, score), sắp xếp giảm dần theo score (lấy cả score > 0 hoặc match token)
        indexed_scores = [(idx, float(score)) for idx, score in enumerate(scores) if score > 0]
        
        # Fallback nếu tập corpus quá nhỏ làm IDF của BM25 <= 0
        if not indexed_scores:
            indexed_scores = [(idx, float(score)) for idx, score in enumerate(scores) if score >= 0]

        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        return indexed_scores[:k]