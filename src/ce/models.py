from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class Chunk:
    id: str             # Ví dụ: "src/main.py:10-25"
    path: str           # Đường dẫn file
    start_line: int     # Dòng bắt đầu (1-indexed)
    end_line: int       # Dòng kết thúc (1-indexed)
    kind: str           # "function", "class", "block"
    name: str           # Tên hàm/lớp
    text: str           # Nội dung code kèm context header

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chunk":
        return cls(**data)