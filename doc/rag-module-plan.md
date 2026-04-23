# Kế hoạch Xây dựng RAG Module: Lấy ngữ cảnh từ Qdrant

Tài liệu này vạch ra từng bước (step-by-step) để xây dựng Module RAG (Retrieval-Augmented Generation). Nhiệm vụ của module này là: Nhận câu hỏi của người dùng -> Nhúng (Embed) câu hỏi -> Tìm kiếm trong Qdrant -> Trả về ngữ cảnh (Context) liên quan nhất (các Table Schema và Business Rules).

---

## 1. Mục tiêu và Luồng hoạt động (Workflow)

**Luồng xử lý khi có câu hỏi mới:**
1. **Input:** Câu hỏi từ user (VD: *"Tính tỉ lệ lỗi của chuyền 1 hôm qua"*).
2. **Embedding:** Gửi câu hỏi lên Google Vertex AI (`text-multilingual-embedding-002`) để lấy về vector 768 chiều.
3. **Retrieval (Truy xuất):** Truy vấn vector vừa tạo vào collection `factory_data_dictionary` trong Qdrant để tìm Top K (VD: 5) vector gần nhất (Cosine Similarity).
4. **Formatting:** Trích xuất phần `payload` (chứa tên bảng, file JSON schema, logic rule) từ kết quả của Qdrant và ghép thành một đoạn văn bản (String) rõ ràng.
5. **Output:** Trả về đoạn Context String đó để module sinh SQL (LLM) sử dụng làm Prompt.

---

## 2. Kế hoạch từng bước (Step-by-Step)

### Bước 1: Cấu trúc thư mục cho RAG Module
Nên tách RAG thành một service độc lập để dễ bảo trì. Dự kiến tạo:
- Thư mục: `services/rag/`
- File: `services/rag/qdrant_retriever.py` (Chứa logic tìm kiếm).
- File: `services/rag/embedding_service.py` (Chứa logic gọi Vertex AI để tránh lặp code với phần Ingest).

### Bước 2: Xây dựng Embedding Service (`embedding_service.py`)
- **Nhiệm vụ:** Tái sử dụng logic lấy vector từ Vertex AI.
- **Chi tiết:**
  - Viết một class hoặc function `get_query_embedding(query_text: str) -> list[float]`.
  - Khởi tạo `TextEmbeddingModel` của Vertex AI giống như lúc chúng ta làm `ingest_data.py`.
  - Có cơ chế xử lý lỗi (Try-Catch) nếu Google API bị timeout.

### Bước 3: Xây dựng Qdrant Retriever (`qdrant_retriever.py`)
- **Nhiệm vụ:** Kết nối Qdrant và thực hiện lệnh Search.
- **Chi tiết:**
  - Khởi tạo `QdrantClient` kết nối tới `localhost:6333`.
  - Viết hàm `search_context(query_vector: list[float], top_k: int = 5) -> list[dict]`.
  - Cấu hình search: Dùng `client.search(...)`, truyền `query_vector`, chỉ định `collection_name="factory_data_dictionary"`.
  - Đặt một ngưỡng điểm số (Score Threshold) khoảng `0.5` hoặc `0.6` để loại bỏ những kết quả không liên quan.

### Bước 4: Xử lý và Định dạng Kết quả (Context Formatter)
- **Nhiệm vụ:** Biến danh sách Point trả về từ Qdrant thành một chuỗi văn bản (Prompt Context) đọc hiểu được đối với LLM (Claude 3.6).
- **Chi tiết:**
  - Viết hàm `format_retrieved_results(search_results) -> str`.
  - Duyệt qua từng kết quả trả về, trích xuất dữ liệu từ trường `payload['raw_json']`.
  - Phân loại: 
    - Nếu là `table_schema`: Sắp xếp thành đoạn *"Bảng {Tên}: {Mô tả}. Cột: {DS Cột}. Liên kết: {Rels}"*.
    - Nếu là `business_rule`: Sắp xếp thành đoạn *"Quy tắc tính {Tên}: Logic SQL là {Logic}. Điều kiện: {Condition}"*.
  - Ghép tất cả lại cách nhau bằng ký tự xuống dòng `\n\n`.

### Bước 5: Viết File Main/Test để chạy thử (`test_rag.py`)
- Chạy thử toàn bộ luồng.
- **Kịch bản test:** 
  1. Gọi hàm `retrieve_context("Top 5 lỗi của chuyền 1 là gì?")`.
  2. In ra màn hình console đoạn Context lấy được.
  3. Kiểm tra xem Context đó có chứa thông tin bảng `DEFECTS` và quy tắc tính lỗi hay không.

---

## 3. Đầu ra (Deliverable) dự kiến của Module

Một function duy nhất mà các hệ thống khác (API, LLM Agent) có thể gọi:

```python
def get_sql_generation_context(user_query: str) -> str:
    # 1. Embed
    vector = embedding_service.get_query_embedding(user_query)
    
    # 2. Search Qdrant
    raw_results = qdrant_retriever.search_context(vector, top_k=5)
    
    # 3. Format
    formatted_context = format_retrieved_results(raw_results)
    
    return formatted_context
```

---

*Ghi chú: Khi bạn đã đọc xong và đồng ý với kế hoạch này, hãy báo cho tôi biết, chúng ta sẽ bắt tay vào code từng bước một!*
