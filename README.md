# AI-Chatbot-SQL-Query

ASP.NET Core 8 Web API + Docker Compose (SQL Server 2022, Qdrant).

## Cấu trúc project

```
AI-Chatbot-SQL-Query/
├── docker-compose.yml          # Khởi chạy toàn bộ stack
├── API_ChatBot/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── Program.cs
│   ├── appsettings.json
│   ├── Data/
│   │   └── AppDbContext.cs
│   └── Controllers/
```

## Services

| Service    | Port host | Mô tả                    |
|------------|-----------|--------------------------|
| API        | 5025      | ASP.NET Core 8 Web API   |
| SQL Server | 1433      | Microsoft SQL Server 2022|
| Qdrant     | 6333/6334 | Vector database          |

## Chạy với Docker

```bash
docker compose up --build
```

Swagger UI: http://localhost:5025/swagger/index.html  
Qdrant Dashboard: http://localhost:6333/dashboard

## Chạy local (không Docker)

```bash
cd API_ChatBot
dotnet run
```

> Yêu cầu SQL Server và Qdrant đang chạy ở localhost.

## Kết nối SQL Server bằng SSMS

**Dùng SSMS (SQL Server Management Studio)**

1. Mở SSMS → cửa sổ **Connect to Server** hiện ra
2. Điền:
   - **Server name:** `localhost,14330`
   - **Authentication:** `SQL Server Authentication`
   - **Login:** `sa`
   - **Password:** `YourStrong@Passw0rd`
3. Nhấn **Connect**

> Docker container SQL Server phải đang chạy (`docker compose up`) thì mới kết nối được.

## Đổi mật khẩu SA (mặc định)

Thay `YourStrong@Passw0rd` trong `docker-compose.yml` và `appsettings.json`.
