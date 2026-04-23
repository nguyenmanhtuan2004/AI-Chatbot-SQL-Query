# 🤖 SQL AI Insight - AI-Powered SQL Chatbot

Dự án này là một hệ thống Chatbot thông minh cho phép người dùng truy vấn dữ liệu SQL Server bằng ngôn ngữ tự nhiên thông qua sức mạnh của Google Gemini AI. Hệ thống được xây dựng với kiến trúc hiện đại, hỗ trợ Streaming thời gian thực và khả năng chuyển đổi linh hoạt giữa các phương thức kết nối.

---

## ✨ Tính năng nổi bật

-   **Natural Language to SQL**: Chuyển đổi câu hỏi ngôn ngữ tự nhiên thành câu lệnh SQL chính xác.
-   **Real-time Streaming**: Phản hồi từ AI được hiển thị dần dần ngay khi đang xử lý (Event-Stream).
-   **Hybrid API Mode**: 
    -   `Direct Mode`: Kết nối trực tiếp Gemini qua proxy Next.js (nhanh, gọn).
    -   `Dotnet Mode`: Kết nối qua ASP.NET Core API (bảo mật, hỗ trợ logic nghiệp vụ phức tạp).
-   **Giao diện Premium**: UI hiện đại với Glassmorphism, Dark Mode, và hiệu ứng mượt mà (Next.js + Tailwind CSS).
-   **Cấu hình linh hoạt**: Dễ dàng điều chỉnh `Temperature`, `Max Tokens` ngay từ file môi trường.

---

## 🏗️ Kiến trúc hệ thống

### 1. Frontend (`/frontend`)
-   **Framework**: Next.js 14 (App Router)
-   **Styling**: Tailwind CSS + Shadcn UI
-   **Icons**: Phosphor Icons
-   **Logic**: Centralized `ChatService` xử lý đa luồng kết nối.

### 2. Backend API (`/API_ChatBot`)
-   **Framework**: ASP.NET Core 8
-   **ORM**: Entity Framework Core
-   **Documentation**: Swagger / OpenAPI

### 3. Infrastructure (Docker Stack)
-   **Database**: SQL Server 2022
-   **Vector DB**: Qdrant (phục vụ cho RAG/Knowledge Base trong tương lai)

---

## ⚡ Khởi chạy nhanh (Quick Start)

Nếu bạn đang dùng Windows, bạn có thể chạy toàn bộ dự án (tự động dọn dẹp port cũ và mở FE/BE) bằng một trong hai cách:

1.  **Double-click** vào file `run-all.bat` ở thư mục gốc.
2.  Hoặc chạy lệnh sau trong PowerShell:
    ```powershell
    ./run-all.ps1
    ```

---

## 🚀 Hướng dẫn khởi chạy

### 1. Chạy với Docker (Khuyên dùng)

Để chạy toàn bộ hệ thống (API, SQL Server, Qdrant) trong một lệnh duy nhất:

```bash
docker compose up --build
```

-   **API Swagger**: [http://localhost:5026/swagger](http://localhost:5026/swagger)
-   **Frontend**: [http://localhost:3000](http://localhost:3000)
-   **Qdrant Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

### 2. Chạy Local (Không Docker)

#### Backend:
```bash
cd API_ChatBot
dotnet run
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ Cấu hình hệ thống (Environment Variables)

Hệ thống sử dụng các file `.env` và `.env.local` để quản lý cấu hình.

### Các thông số quan trọng:
-   `NEXT_PUBLIC_API_MODE`: Chọn `dotnet` hoặc `direct`.
-   `TEMPERATURE`: Độ sáng tạo của AI (0.0 - 2.0).
-   `MAX_OUTPUT_TOKENS`: Độ dài tối đa của câu trả lời.

*Xem chi tiết hướng dẫn trong từng file `.env` tại thư mục `/frontend` và `/API_ChatBot`.*

---

## 🛠️ Kết nối cơ sở dữ liệu (SSMS)

Nếu bạn muốn quản lý dữ liệu trực tiếp qua SQL Server Management Studio:
-   **Server name**: `localhost,14330`
-   **Authentication**: SQL Server Authentication
-   **Login**: `sa`
-   **Password**: `YourStrong@Passw0rd` (Mặc định trong docker-compose)

---

## 📝 Giấy phép
Dự án được phát triển cho mục đích học tập và triển khai hệ thống chatbot truy vấn dữ liệu thực tế.
