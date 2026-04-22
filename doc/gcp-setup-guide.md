# Hướng Dẫn Cài Đặt và Kết Nối Google Cloud Platform (GCP) Cho Dự Án

Tài liệu này hướng dẫn chi tiết các bước để thiết lập máy tính cá nhân (local) kết nối với Google Cloud Platform, đặc biệt là để sử dụng các dịch vụ AI như Vertex AI.

## Bước 1: Cài đặt Google Cloud CLI (SDK)

1. Tải file cài đặt **GoogleCloudSDKInstaller.exe** từ trang chủ Google Cloud:
   [Link tải Google Cloud CLI cho Windows](https://cloud.google.com/sdk/docs/install)
2. Chạy file `.exe` vừa tải về và cài đặt theo các bước mặc định (Cứ nhấn Next).
3. Sau khi cài đặt xong, hãy đảm bảo bạn khởi động lại (Restart) các cửa sổ Terminal (hoặc VS Code) để máy tính nhận diện được câu lệnh `gcloud`.

## Bước 2: Xác thực tài khoản (Application Default Credentials)

Để code Python trên máy bạn có quyền truy cập vào Project trên Google Cloud, bạn cần thực hiện lệnh đăng nhập và cấp quyền.

1. Mở Terminal (trong VS Code, PowerShell hoặc Command Prompt).
2. Chạy câu lệnh sau:
   ```bash
   gcloud auth application-default login
   ```
3. Lệnh này sẽ tự động mở trình duyệt web của bạn.
4. Chọn tài khoản Google mà bạn đã dùng để tạo project GCP (ví dụ: `ntb-text-to-sql`).
5. **CỰC KỲ QUAN TRỌNG:** Ở màn hình xin quyền (Consent Screen), Google sẽ hiển thị một danh sách các quyền truy cập. Bạn **phải đánh dấu tích (✓) vào TẤT CẢ các ô trống** (đặc biệt là ô *See, edit, configure, and delete your Google Cloud data*).
6. Nhấn **Continue (Tiếp tục)** hoặc **Allow (Cho phép)**.
7. Quay lại terminal, nếu thấy dòng chữ `Credentials saved to file...` nghĩa là bạn đã đăng nhập và lưu file credential thành công trên máy tính của mình.

*(Lưu ý: Nếu bị lỗi trình duyệt không bật lên được, bạn có thể thử lệnh `gcloud auth application-default login --no-browser` và làm theo hướng dẫn copy link lên trình duyệt)*

## Bước 3: Bật Thanh toán (Billing) cho Project

Google Vertex AI yêu cầu Project của bạn phải được liên kết với một Tài Khoản Thanh Toán (Billing Account) có thêm thẻ Visa/Mastercard thì mới cho phép API hoạt động. (Kể cả khi bạn dùng bản free).

1. Truy cập vào link bật Billing cho project của bạn: 
   👉 [Enable Billing](https://console.developers.google.com/billing/enable)
2. Chọn đúng Project mà bạn đang làm việc (ví dụ: `ntb-text-to-sql`).
3. Nếu bạn chưa có Billing Account, hệ thống sẽ yêu cầu bạn tạo mới và nhập thông tin thẻ.
4. Xác nhận liên kết thẻ với Project.

## Bước 4: Viết Code Python Sử dụng Vertex AI

Sau khi hoàn tất 3 bước trên, máy tính của bạn đã hoàn toàn sẵn sàng. Bạn không cần phải cấu hình file key dạng JSON rườm rà, thư viện của Google sẽ tự động tìm thấy chứng chỉ đã lưu ở Bước 2.

**Ví dụ khởi tạo Vertex AI trong Python:**

```python
import vertexai
from vertexai.language_models import TextEmbeddingModel

# Khởi tạo kết nối tới Project của bạn
# Sửa 'ntb-text-to-sql' thành tên Project ID của bạn
vertexai.init(project="ntb-text-to-sql", location="asia-southeast1") 

# Gọi model AI
embedding_model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")

# Sử dụng model để nhúng văn bản
vector = embedding_model.get_embeddings(["Chào bạn, mình đang test AI"])[0].values
print("Kết nối thành công, độ dài vector:", len(vector))
```

Chạy file script Python của bạn (ví dụ `python ingest_data.py`), nếu không còn lỗi `PermissionDenied` hoặc `DefaultCredentialsError` nghĩa là bạn đã setup hoàn hảo!
