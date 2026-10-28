import argparse
from pathlib import Path
from src.ce.config import INDEX_DIR
from src.ce.indexer import build_index
from src.ce.store import load_index
from src.ce.lexical import LexicalIndex
from src.ce.vector import VectorIndex
from src.ce.embedder import Embedder
from src.ce.hybrid import hybrid_search


def main():
    parser = argparse.ArgumentParser(description="Context Engine - Codebase Search & RAG Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: index
    index_parser = subparsers.add_parser("index", help="Lập chỉ mục cho repository")
    index_parser.add_argument("repo", type=str, nargs="?", default=".", help="Đường dẫn đến repo (mặc định là .)")

    # Subcommand: ask
    ask_parser = subparsers.add_parser("ask", help="Tìm kiếm câu trả lời trong codebase")
    ask_parser.add_argument("query", type=str, help="Câu hỏi hoặc từ khóa tìm kiếm")
    ask_parser.add_argument("--repo", type=str, default=".", help="Đường dẫn repo")
    ask_parser.add_argument("-k", type=int, default=5, help="Số lượng kết quả trả về")

    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()

    if args.command == "index":
        build_index(repo_path)

    elif args.command == "ask":
        target_index_dir = repo_path / INDEX_DIR
        try:
            chunks, vectors = load_index(target_index_dir)
        except FileNotFoundError as e:
            print(f"❌ Lỗi: {e}")
            return

        print(f"🔍 Đang tìm kiếm: \"{args.query}\"...")
        embedder = Embedder()
        lex_index = LexicalIndex(chunks)
        vec_index = VectorIndex(vectors)

        results = hybrid_search(
            query=args.query,
            lex_index=lex_index,
            vec_index=vec_index,
            embedder=embedder,
            chunks=chunks,
            top_k=args.k,
        )

        print(f"\n🎯 Tìm thấy {len(results)} kết quả hàng đầu:\n" + "=" * 60)
        for idx, chunk in enumerate(results, start=1):
            print(f"\n[Result {idx}] Kind: {chunk.kind.upper()} | Name: {chunk.name}")
            print(f"📍 Location: {chunk.path}:{chunk.start_line}-{chunk.end_line}")
            print("-" * 60)
            # In ra 5 dòng đầu của chunk để xem trước
            preview_lines = chunk.text.splitlines()[:6]
            print("\n".join(preview_lines))
            if len(chunk.text.splitlines()) > 6:
                print("   ...")
            print("=" * 60)


if __name__ == "__main__":
    main()