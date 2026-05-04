# Hướng dẫn Khởi chạy Hệ thống AI Chatbot (FastAPI + Streamlit)

Để ứng dụng Chatbot hoạt động hoàn chỉnh, bạn cần chạy song song 2 dịch vụ: **Backend (FastAPI)** để xử lý logic LLM/SQL và **Frontend (Streamlit)** để hiển thị giao diện người dùng. Chúng ta sẽ cần mở **2 cửa sổ Terminal** riêng biệt.

---

## BƯỚC 1: Khởi động API Backend (FastAPI)

1. Mở một cửa sổ Terminal (PowerShell) mới trong VS Code.
2. Chuyển thư mục làm việc vào thư mục chứa code API:
   ```powershell
   cd E:\thuctap\AI-Chatbot-SQL-Query\chatbot_api
   ```
3. Kích hoạt môi trường ảo (nếu bạn sử dụng virtual environment):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Chạy file chính để bật server FastAPI:
   ```powershell
   python main.py
   ```
5. Đợi đến khi màn hình Terminal hiển thị thông báo tương tự như: 
   `Application startup complete.` và `Uvicorn running on http://127.0.0.1:8000`. Cứ để nguyên cửa sổ Terminal này chạy ngầm.

---

## BƯỚC 2: Khởi động Giao diện Cục bộ (Streamlit)

1. Mở thêm **một cửa sổ Terminal thứ hai** (Bấm dấu `+` New Terminal trong VS Code).
2. Chuyển thư mục vào nơi chứa code giao diện:
   ```powershell
   cd E:\thuctap\AI-Chatbot-SQL-Query\streamlit_app
   ```
3. Kích hoạt lại môi trường ảo ở Terminal mới này (nếu cần):
   ```powershell
   ..\chatbot_api\venv\Scripts\Activate.ps1
   ```
4. (Chỉ chạy lần đầu tiên) Cài đặt các thư viện bắt buộc cho giao diện:
   ```powershell
   pip install -r requirements.txt
   ```
5. Khởi động Giao diện Streamlit:
   ```powershell
   streamlit run app.py
   ```

🎉 **Xong!** Lúc này hệ điều hành sẽ tự động bật một tab trình duyệt chạy ở địa chỉ `http://localhost:8501`. Bạn có thể gõ câu hỏi vào khung chat để trải nghiệm.

---

## 🛠 Mẹo tối ưu (Tuỳ chọn)

Nếu bạn không muốn mỗi ngày lập lại việc mở 2 Terminal thủ công như thế này, bạn có thể tạo một file tự động hoá `run-app.bat` hoặc update file `run-all.ps1` ở thư mục ngoài cùng với nội dung kích hoạt đồng thời cả 2 tiến trình trên.