# Context Engine (prototype)

Tìm đúng đoạn code liên quan trong repo để đưa cho AI agent. Engine **chỉ tìm context**, không tự trả lời; việc trả lời là của LLM/agent (Claude Code, Codex...).

Kiến trúc đích: `architecture-context-engine-de-xuat` (kế thừa ý tưởng vibervn, tự viết lại code).

## Chạy

```
pip install -r requirements.txt
python -m src.ce.cli index <repo_path>
python -m src.ce.cli ask "hàm tokenize xử lý camelCase thế nào" --repo <repo_path> -k 5
```

Pipeline hiện có: quét file → tree-sitter chunk theo hàm/class → BM25 + embedding local → RRF → trả top-k.

## Demo (5 phút)

1. Vấn đề: repo lớn thì AI không đọc hết, cần thứ chọn đúng đoạn code.
2. CLI, 2 câu hỏi:
   - Câu trùng từ khóa với code (VD: "hàm tokenize xử lý camelCase") → BM25 thắng.
   - Câu không trùng từ khóa (VD: "phần nào gộp kết quả hai cách tìm kiếm", đáp án `rrf`) → cho thấy vector/RRF đóng góp.
3. Cắm vào Claude Code qua MCP: hỏi cùng một câu khi tắt/bật tool, so sánh câu trả lời. (Cần xong `mcp_server.py`.)
4. Bảng "chưa đạt" bên dưới: nói rõ phần nào xong, phần nào là bước tiếp.

Chuẩn bị sẵn 3 câu đã chạy thử và biết kết quả tốt.

## Đối chiếu kiến trúc

| Khối | Trạng thái |
|---|---|
| Quét repo, parse tree-sitter, chunk | Xong (một lần, chưa incremental) |
| Lexical (BM25), vector (numpy), hybrid RRF | Xong |
| Embedding local | Xong (cần kiểm tra model code-specific + tiếng Việt) |
| MCP server | Chưa |
| Rerank cross-encoder | Chưa |
| Symbol graph, SCIP/LSP | Chưa |
| Lọc secret/PII | Chưa |
| Watcher/webhook, incremental, ghi atomic | Chưa |
| Router + worker mỗi repo | Chưa (prototype 1 repo) |
| Gateway: SSO, token, RBAC, audit | Chưa |
| Eval recall@k, metrics | Chưa |
| Web UI | Chưa |

## Ràng buộc chưa đạt

- **Không gửi code ra ngoài / không gọi máy chủ ngoài**: embedding chạy local nhưng lần đầu tải model từ Hugging Face; chưa có rerank local. Chưa lọc secret trước khi embed.
- **Dùng được cho team**: chưa có SSO, RBAC theo repo, audit log.
- **Chứng minh chất lượng**: chưa có bộ eval recall@k.
- **Cập nhật khi code đổi**: chưa có watcher, index lại toàn bộ mỗi lần.
- **Không copy code vibervn**: đang đạt (tự viết), giữ nguyên.
- Câu hỏi tiếng Việt vs code tiếng Anh: cần kiểm tra model embedding có hiểu không.

## Pipeline tiếp theo

1. `mcp_server.py` với tool `search_code(query, k)`, cắm vào Claude Code.
2. Eval recall@5: BM25 vs vector vs hybrid (~15 câu hỏi, nửa trùng từ khóa, nửa không).
3. Rerank bằng cross-encoder local.
4. Incremental index + watcher (hash file, chỉ index lại file đổi).
5. Lọc secret trước khi embed.
6. Sau đó: symbol graph (SCIP), router/worker nhiều repo, gateway.

## Câu hỏi cần hỏi sếp

- Đích là công cụ cá nhân hay dịch vụ chung cho team?
- Chỉ cần MCP cho agent, hay thêm giao diện hỏi đáp có LLM sinh câu trả lời?
- Bản cuối bằng Python hay Rust?
