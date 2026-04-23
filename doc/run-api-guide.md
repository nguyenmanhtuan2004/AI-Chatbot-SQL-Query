# Hướng dẫn chạy và Kiểm thử AI Chatbot API

Tài liệu này hướng dẫn chi tiết cách khởi động backend FastAPI và sử dụng công cụ Swagger UI để gửi yêu cầu trích xuất ngữ cảnh RAG từ hệ thống Qdrant.

---

## Bước 1: Mở Terminal và kích hoạt môi trường

Bạn phải đảm bảo rằng mình đang ở đúng thư mục `chatbot_api` và môi trường ảo (venv) đã được kích hoạt.

1. Mở cửa sổ Terminal (PowerShell hoặc CMD).
2. Di chuyển đến thư mục `chatbot_api`:
   ```powershell
   cd E:\thuctap\AI-Chatbot-SQL-Query\chatbot_api
   ```
3. Kích hoạt môi trường ảo:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(Nếu thành công, bạn sẽ thấy chữ `(venv)` xuất hiện ở đầu dòng lệnh).*

---

## Bước 2: Khởi chạy máy chủ API

Sau khi môi trường đã kích hoạt, bạn tiến hành khởi chạy file `main.py`:

```powershell
python main.py
```

**Dấu hiệu thành công:** 
Trên màn hình Terminal sẽ xuất hiện các dòng log tương tự như sau:
```text
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```
*Lưu ý: Không đóng cửa sổ Terminal này trong suốt quá trình bạn đang sử dụng API.*

---

## Bước 3: Truy cập giao diện kiểm thử Swagger UI

FastAPI tự động sinh ra một trang web rất trực quan để bạn kiểm thử API mà không cần dùng đến Postman.

1. Mở trình duyệt web (Chrome, Edge, Cốc Cốc...).
2. Truy cập vào đường dẫn: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Bước 4: Test thử API trích xuất RAG (Qdrant)

Khi giao diện Swagger UI mở lên, bạn sẽ thấy một danh sách các API. Hãy làm theo các bước sau:

1. Tìm đến mục có chữ màu xanh lá: **`POST /api/rag/retrieve`** (API test thử việc trích xuất Vector DB).
2. Click chuột để mở rộng nó ra.
3. Bấm vào nút **Try it out** ở góc trên bên phải của hộp đó.
4. Một ô văn bản tên là **Request body** sẽ hiện ra cho phép bạn chỉnh sửa nội dung. Bạn hãy copy JSON dưới đây dán vào (xóa cái cũ đi):
   ```json
   {
     "query": "Tỉ lệ lỗi của chuyền 1 được tính như thế nào?",
     "top_k": 5
   }
   ```
5. Bấm nút xanh dương to **Execute**.

---

## Bước 5: Xem kết quả trả về

Cuộn xuống một chút tới phần **Responses**, nhìn vào ô **Response body**. Bạn sẽ thấy một cấu trúc JSON trả về tương tự như sau:

```json
{
  "status": "success",
  "query": "Tỉ lệ lỗi của chuyền 1 được tính như thế nào?",
  "context": "QUY TẮC [Tỉ lệ lỗi tổng thể (Overall Defect Rate)]:\n- Ý nghĩa: Tính toán tỉ lệ phần trăm sản phẩm bị lỗi...\n\n------------------\n\nBẢNG DEFECTS (Lĩnh vực: lỗi, chất lượng, phế phẩm...)"
}
```

Dữ liệu `context` lúc này đã sẵn sàng để chuyển tiếp (đưa vào Prompt) cho các Node LangGraph hoặc LLM xử lý câu lệnh SQL tiếp theo.

---
**Cách dừng API:**
Nếu bạn muốn tắt API, hãy mở lại cửa sổ Terminal đang chạy `python main.py` và nhấn tổ hợp phím `Ctrl + C` trên bàn phím.
