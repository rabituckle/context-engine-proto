from src.ce.lexical import tokenize, LexicalIndex
from src.ce.models import Chunk


def test_tokenize_camel_and_snake():
    tokens = tokenize("getUserName_v2 calculate_sum")
    # Phải chứa cả token gốc lẫn token đã tách
    assert "getusername_v2" in tokens
    assert "get" in tokens
    assert "user" in tokens
    assert "name" in tokens
    assert "calculate" in tokens
    assert "sum" in tokens


def test_lexical_search_relevance():
    c1 = Chunk("1", "a.py", 1, 5, "function", "login_user", "def login_user(username, password): pass")
    c2 = Chunk("2", "b.py", 1, 5, "function", "render_ui", "def render_ui(theme_name): pass")

    index = LexicalIndex([c1, c2])
    results = index.search("login", k=2)

    assert len(results) >= 1
    top_chunk_idx, score = results[0]
    assert top_chunk_idx == 0  # Chunk 1 (login_user) phải đứng đầu