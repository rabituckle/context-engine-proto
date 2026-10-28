from pathlib import Path
from typing import List
import tree_sitter
import tree_sitter_python as tspython
from src.ce.config import MAX_CHUNK_CHARS
from src.ce.models import Chunk


def get_parser() -> tree_sitter.Parser:
    """Khởi tạo tree-sitter Parser cho Python (API tree-sitter >=0.22.0)."""
    language = tree_sitter.Language(tspython.language())
    parser = tree_sitter.Parser(language)
    return parser


def extract_nodes(node: tree_sitter.Node) -> List[tree_sitter.Node]:
    """Trích xuất các top-level nodes: function_definition và class_definition."""
    extracted = []
    for child in node.children:
        if child.type in ("function_definition", "class_definition"):
            extracted.append(child)
    return extracted


def get_node_name(node: tree_sitter.Node, source_bytes: bytes) -> str:
    """Lấy tên hàm hoặc tên class từ AST node."""
    name_node = node.child_by_field_name("name")
    if name_node:
        return source_bytes[name_node.start_byte : name_node.end_byte].decode("utf-8")
    return ""


def node_to_chunk(node: tree_sitter.Node, rel_path: Path, source_bytes: bytes) -> Chunk:
    """Chuyển AST Node thành đối tượng Chunk."""
    kind = "function" if node.type == "function_definition" else "class"
    name = get_node_name(node, source_bytes)
    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1

    code_text = source_bytes[node.start_byte : node.end_byte].decode("utf-8")
    header = f"# Path: {rel_path} (lines {start_line}-{end_line})\n"
    full_text = header + code_text

    chunk_id = f"{rel_path}:{start_line}-{end_line}"
    return Chunk(
        id=chunk_id,
        path=str(rel_path),
        start_line=start_line,
        end_line=end_line,
        kind=kind,
        name=name,
        text=full_text,
    )


def split_big_chunk(chunk: Chunk, window_lines: int = 60, overlap: int = 10) -> List[Chunk]:
    """Cắt nhỏ chunk nếu vượt quá MAX_CHUNK_CHARS bằng sliding window."""
    if len(chunk.text) <= MAX_CHUNK_CHARS:
        return [chunk]

    lines = chunk.text.splitlines()
    sub_chunks = []
    step = window_lines - overlap
    idx = 0

    for i in range(0, len(lines), step):
        sub_lines = lines[i : i + window_lines]
        if not sub_lines:
            break
        
        start = chunk.start_line + i
        end = start + len(sub_lines) - 1
        sub_text = f"# Path: {chunk.path} (lines {start}-{end})\n" + "\n".join(sub_lines)
        sub_id = f"{chunk.path}:{start}-{end}"
        
        sub_chunks.append(
            Chunk(
                id=sub_id,
                path=chunk.path,
                start_line=start,
                end_line=end,
                kind=chunk.kind,
                name=f"{chunk.name}_part{idx}",
                text=sub_text,
            )
        )
        idx += 1
        if i + window_lines >= len(lines):
            break

    return sub_chunks


def fallback_chunks(rel_path: Path, source_bytes: bytes, window_lines: int = 60, overlap: int = 10) -> List[Chunk]:
    """Cắt file theo sliding window cho phần code nằm ngoài hàm/class hoặc khi parse lỗi."""
    text = source_bytes.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    if not lines:
        return []

    chunks = []
    step = window_lines - overlap
    idx = 0

    for i in range(0, len(lines), step):
        sub_lines = lines[i : i + window_lines]
        if not sub_lines:
            break
        
        start_line = i + 1
        end_line = i + len(sub_lines)
        chunk_text = f"# Path: {rel_path} (lines {start_line}-{end_line})\n" + "\n".join(sub_lines)
        chunk_id = f"{rel_path}:{start_line}-{end_line}"
        
        chunks.append(
            Chunk(
                id=chunk_id,
                path=str(rel_path),
                start_line=start_line,
                end_line=end_line,
                kind="block",
                name=f"block_{idx}",
                text=chunk_text,
            )
        )
        idx += 1
        if i + window_lines >= len(lines):
            break

    return chunks


def chunk_file(repo: Path, rel_path: Path) -> List[Chunk]:
    """Hàm chính: Parse file Python và trả về danh sách Chunk hoàn chỉnh."""
    full_path = repo / rel_path
    source_bytes = full_path.read_bytes()

    parser = get_parser()
    tree = parser.parse(source_bytes)

    top_nodes = extract_nodes(tree.root_node)
    
    if not top_nodes:
        return fallback_chunks(rel_path, source_bytes)

    chunks = []
    for node in top_nodes:
        c = node_to_chunk(node, rel_path, source_bytes)
        chunks.extend(split_big_chunk(c))

    return chunks