# Kế hoạch Xây dựng Giao diện Chatbot với Streamlit

## 1. Mục tiêu (Objective)
Xây dựng một giao diện người dùng (UI) dạng chat tương tác thời gian thực bằng **Streamlit**. Giao diện này sẽ kết nối trực tiếp với backend FastAPI hiện tại để gửi câu hỏi và hiển thị kết quả một cách trực quan, đầy đủ.

## 2. Kiến trúc Hệ thống (Architecture)
- **Backend (Đã có):** FastAPI chạy ở cổng mặc định `http://localhost:8000`. Cung cấp endpoint POST `/chat`.
- **Frontend (Sắp xây dựng):** Streamlit app chạy ở cổng `http://localhost:8501`.
- **Cơ chế giao tiếp:** Streamlit sẽ đóng vai trò là Client, dùng thư viện `requests` để bắn API payload `{"query": "..."}` xuống backend và nhận về cục JSON chứa `answer`, `sql_result`, và `sql_query`.

## 3. Cấu trúc thư mục định hướng
Dự kiến sẽ tạo một thư mục riêng biệt ngang hàng với `chatbot_api` để tránh code frontend lẫn lộn với code LangGraph:
```text
AI-Chatbot-SQL-Query/
│
├── chatbot_api/          # Backend (FastAPI, LangGraph) - Không đụng đến
├── streamlit_app/        # [MỚI] Frontend Streamlit
│   ├── app.py            # File chạy chính của giao diện
│   ├── requirements.txt  # Thư viện riêng cho frontend (streamlit, pandas, requests)
│   └── .env              # Biến môi trường (Ví dụ: URL của backend)
```

## 4. Danh sách Tính năng (Features)
- [x] **Khung Chat (Chatbot UI):** Sử dụng `st.chat_message` và `st.chat_input` để tạo cảm giác nhắn tin quen thuộc giống ChatGPT.
- [x] **Lưu Trạng thái Giao diện:** Sử dụng `st.session_state` để lưu giữ các câu hỏi và câu trả lời trong suốt phiên làm việc.
- [x] **Hiển thị Câu trả lời (Văn bản):** Vẽ câu trả lời tóm tắt siêu ngắn từ AI (từ trường `answer`).
- [x] **Render Bảng Dữ liệu Cứng:** Chuyển đổi JSON `sql_result` thành Pandas DataFrame và render ra bảng đẹp mắt (sử dụng `st.dataframe`).
- [x] **Nút Tải Xuống (Tính năng ăn tiền):** Cung cấp nút để user tải `sql_result` trực tiếp dưới dạng `.csv` hoặc `.xlsx`.
- [x] **Góc Debug (Accordion):** Một thẻ có thể mở ra/đóng lại chứa câu lệnh SQL thực tế giúp kỹ thuật viên debug.

## 5. Các bước triển khai chi tiết
1. **Thiết lập Môi trường:** Tạo thư mục `streamlit_app`, cài `streamlit` và `pandas`.
2. **Dựng Layout:** Tạo tiêu đề, sidebar (nếu cần để setup config), và vùng chứa chat.
3. **Cài đặt Session State:** Khởi tạo danh sách `messages` rỗng khi mới load trang.
4. **Logic Kết nối API:** Viết hàm `send_query_to_backend(query: str)` xử lý việc gọi HTTP POST tới `http://127.0.0.1:8000/chat` và cover các trường hợp báo lỗi mạng.
5. **Render Dữ liệu thông minh:**
   - Nếu Data trả về báo lỗi (`status="error"`), vẽ cảnh báo lỗi.
   - Nếu có `answer`, dùng `st.markdown()`.
   - Nếu `sql_result` có data, nạp qua Pandas để bảng hiển thị xịn xò.
6. **Chạy thử và Tối ưu UI.**