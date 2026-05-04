# Kế hoạch Triển khai Node Sinh mã SQL (SQL Generation Node)

Tài liệu này trình bày các bước chi tiết để xây dựng `generate_sql_node`, một thành phần cốt lõi trong LangGraph để chuyển đổi ngôn ngữ tự nhiên thành truy vấn MS SQL Server dựa trên ngữ cảnh đã truy xuất (RAG).

## 1. Mục tiêu
- **Đầu vào:** Câu hỏi của người dùng (`query`) và thông tin schema/quy tắc nghiệp vụ (`context`) từ Qdrant.
- **Đầu ra:** Một câu lệnh SQL hoàn chỉnh, hợp lệ về cú pháp và đúng về logic nghiệp vụ.

---

## 2. Các bước thực hiện chi tiết

### Bước 1: Thiết kế Prompt chuyên sâu
- System Role: Expert MS SQL Server Developer.
- Constraints:
  - Chỉ trả về chuỗi SQL thuần, không markdown, không giải thích.
  - Chỉ sử dụng cột, bảng, kiểu dữ liệu đã cho trong Context.
  - Nếu câu hỏi không rõ ràng (không xác định được cột/bảng nào cần dùng) hoặc không thể trả lời bằng schema hiện có → trả về '-- NO_QUERY_POSSIBLE'.
  - Luôn dùng tham số hóa: @p1, @p2,... tương ứng với giá trị người dùng. Không được ghép trực tiếp literal.
  - So sánh chuỗi:
      * Dùng `=` nếu câu hỏi yêu cầu khớp chính xác (vd: "tên là John").
      * Dùng `LIKE '%' + @p + '%'` **chỉ khi** câu hỏi chứa từ "tìm kiếm", "chứa", "gần đúng", "bắt đầu bằng", "kết thúc bằng".
      * Nếu chuỗi có ký tự wildcard `%`, `_`, `[`, `]` → tự động thêm `ESCAPE '\'` (vd: `LIKE '%' + REPLACE(REPLACE(@p, '\', '\\'), '%', '\%') + '%' ESCAPE '\'`).
  - So sánh ngày tháng:
      * Dùng `>=` và `<` cho khoảng (ngày + giờ). Không dùng `=` với datetime trừ khi biết chắc không có giờ.
      * Nếu câu hỏi chỉ có ngày (vd: "ngày 2025-01-01") → chuyển thành `date_column >= @p AND date_column < DATEADD(day, 1, @p)`.
  - So sánh số: giữ nguyên kiểu, không ép kiểu ngầm (vd: `price = @p` thay vì `price = '100'`).
  - ORDER BY mặc định: lấy cột đầu tiên của bảng đầu tiên xuất hiện trong mệnh đề FROM (theo thứ tự context cung cấp). Nếu user chỉ định rõ thứ tự thì theo user.
  - Khi có JOIN: bắt buộc dùng alias bảng (vd: `FROM Orders AS o INNER JOIN Customers AS c ON o.CustId = c.Id`).
  - Giới hạn kết quả:
      * Dùng `TOP` cho mọi truy vấn, trừ khi câu hỏi chứa "tất cả", "toàn bộ", "không giới hạn".
      * Nếu user yêu cầu "tất cả" nhưng số lượng bản ghi tiềm năng > 1000 (ngầm hiểu), vẫn dùng `TOP 1000` và thêm comment `-- limited to 1000` (để tránh crash). Nhưng ưu tiên mặc định là không giới hạn khi user nói "tất cả".

### Bước 2: Xử lý State trong LangGraph
- Đảm bảo `generate_sql_node` nhận dữ liệu từ `AgentState`.
- **Kiểm tra Context:** Trước khi gọi LLM, kiểm tra nếu context rỗng:
    ```python
    if not state.get("context") or len(state["context"].strip()) == 0:
        return {"generated_sql": "-- NO_CONTEXT", "error": "Missing context"}
    ```

### Bước 3: Gọi Model và Xử lý Chuỗi đầu ra
- Sử dụng mô hình `gemini-1.5-pro` với `temperature=0` để đảm bảo kết quả ổn định.
- **Hậu xử lý (Post-processing):** Triển khai hàm `clean_sql` để làm sạch mã SQL:
    ```python
    def clean_sql(raw: str) -> str:
        raw = raw.strip()
        # Loại bỏ markdown code block
        if raw.startswith("```sql"):
            raw = raw[6:]
        elif raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        # Loại bỏ các đoạn dẫn giải bằng cách lấy khối text cuối cùng
        # (Thường SQL sẽ nằm ở cuối nếu LLM lỡ giải thích)
        raw = raw.split("\n\n")[-1]
        return raw.strip()
    ```

### Bước 4: Cập nhật AgentState
- Lưu câu lệnh SQL được sinh ra vào biến `generated_sql` trong State để các node sau (như `execute_sql_node`) có thể sử dụng.

---

## 3. Cấu trúc Prompt đề xuất (Markdown + Structured Messages)

Sử dụng `ChatPromptTemplate` để phân tách rõ ràng vai trò:

### System Message (Đóng vai & Ràng buộc)
```markdown
# ROLE
Bạn là một chuyên gia MS SQL Server cấp cao.

# CONSTRAINTS
{list_of_constraints_from_step_1}

# OUTPUT FORMAT
- Trả về câu lệnh SQL thuần túy.
- Nếu không thể tạo SQL, trả về: -- NO_QUERY_POSSIBLE
```

### User Message (Ngữ cảnh & Câu hỏi)
```markdown
# DATA CONTEXT
{context}

# USER QUESTION
{query}

# SQL RESPONSE:
```

---

## 4. Kiểm thử và Tối ưu (Evaluation)
- **Kiểm tra cú pháp:** Thử nghiệm với các câu hỏi về doanh thu, số lượng lỗi, năng suất.
- **Xử lý Error:** Nếu SQL sinh ra sai, Agent cần có cơ chế "Self-Correction" (sẽ được lên kế hoạch ở node tiếp theo).

---

## 5. Danh sách công việc (Checklist)
- [x] Định nghĩa kế hoạch triển khai.
- [x] Cấu hình `ChatPromptTemplate` trong `agent/sql_generator.py`.
- [x] Triển khai logic gọi LLM trong hàm `generate_sql`.
- [x] Thêm bước xóa bỏ Markdown code blocks và làm sạch SQL.
- [x] Kết nối node vào `nodes.py` và tách biệt logic minh bạch.
- [x] Kết nối node vào `graph.py`.
- [ ] Chạy thử nghiệm với 5 câu hỏi thực tế.

---

## 6. Sơ đồ Luồng Agent (Agent Workflow)
Dựa trên cấu hình LangGraph tại các file `graph.py`, `nodes.py`, và `edges.py`, dưới đây là sơ đồ luồng thực thi của Bot dưới dạng Text ASCII để tránh lỗi giới hạn plugin của VS Code:

```text
[Bắt đầu] 
   │
   ▼
[1. Lấy dữ liệu từ Qdrant (retrieve_context)]
   │
   ├─► (Thất bại / Không có ngữ cảnh) ──► [5. Ghi log lỗi (handle_error)] ──► [Kết thúc]
   │
   ▼ (Thành công)
[2. Sinh mã SQL (generate_sql)] ◄────────────────────────────────────────┐
   │                                                                     │
   ├─► (Sinh mã thất bại) ──────────────► [5. Ghi log lỗi] ──► [Kết thúc]│
   │                                                                     │
   ▼ (Sinh SQL thành công)                                               │
[3. Chạy SQL query (execute_sql)]                                        │
   │                                                                     │
   ├─► (Lỗi thực thi SQL) ──► Kiểm tra [retry_count < 2]? ───────────────┘
   │                           ├─► (Đã thử 2 lần) ──► [5. Ghi log lỗi] ──► [Kết thúc]
   │                           └─► (Chưa tới 2 lần) ─► Tăng retry_count, quay lại bước 2.
   │
   ▼ (Thực thi thành công)
[4. Diễn giải kết quả (generate_answer)]
   │
   ▼
[Kết thúc]
```

