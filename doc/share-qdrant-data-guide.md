# Hướng Dẫn Chia Sẻ/Đồng Bộ Dữ Liệu Qdrant Sang Máy Khác

Khi bạn đã nhúng (embed) và đẩy thành công các vector (ví dụ: 18 vectors) vào Qdrant trên máy của mình, nếu muốn một máy tính khác cũng có dữ liệu này, bạn có 3 cách thực hiện. Dưới đây là hướng dẫn chi tiết cho từng cách.

---

## Cách 1: Cung cấp file JSON và chạy lại Script (Dễ nhất cho team dev)
Đây là cách phổ biến nhất khi làm việc nhóm bằng Git.

**Quy trình:**
1. Bạn đưa toàn bộ mã nguồn bao gồm thư mục `data_rules/` chứa các file JSON, file `init_qdrant.py` và `ingest_data.py` lên GitHub/GitLab.
2. Người ở máy tính khác clone code về.
3. Người đó khởi chạy Docker Qdrant trên máy họ.
4. Người đó làm theo `gcp-setup-guide.md` để cài đặt xác thực Google Cloud.
5. Cuối cùng, người đó chạy lệnh `python init_qdrant.py` và `python ingest_data.py` để máy tự động gọi Vertex AI và nạp lại 18 vectors đó vào Qdrant của họ.

*Ưu điểm:* Dễ quản lý bằng Git, luôn giữ data mới nhất.
*Nhược điểm:* Phải gọi lại API của Google Vertex AI (có thể tốn thêm một chút chi phí/credits nếu số lượng vector cực kỳ lớn).

---

## Cách 2: Sử dụng tính năng Snapshot của Qdrant (Khuyên dùng để tiết kiệm chi phí)
Thay vì bắt máy khác phải gọi API Vertex AI để nhúng lại từ đầu, bạn có thể "đóng gói" toàn bộ 18 vectors thành 1 file nén (snapshot) và gửi cho người khác.

### 2.1. Tạo file Snapshot trên máy của bạn
Tạo một file có tên `export_snapshot.py` với nội dung sau và chạy nó:

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
# Tạo snapshot cho collection
snapshot = client.create_snapshot(collection_name="factory_data_dictionary")
print(f"Tạo thành công snapshot: {snapshot.name}")
```
*(Mặc định file snapshot sẽ được lưu bên trong container Docker của Qdrant tại thư mục `/qdrant/snapshots/factory_data_dictionary/`). Bạn cần copy file `.snapshot` này ra ngoài máy tính và gửi cho người kia.*

### 2.2. Khôi phục (Restore) Snapshot trên máy người khác
Ở máy tính mới, người đó tạo một file `import_snapshot.py`:

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
# Khôi phục từ file snapshot bạn gửi qua
client.recover_snapshot(
    collection_name="factory_data_dictionary",
    location="file:///đường_dẫn_tới_file_snapshot_cua_ban.snapshot"
)
print("Khôi phục dữ liệu thành công!")
```

*Ưu điểm:* Máy tính mới không cần tài khoản Google Cloud, không tốn tiền gọi API AI. Phù hợp khi chia sẻ cho môi trường Production.

---

## Cách 3: Copy trực tiếp thư mục Volume của Docker
Khi bạn chạy Qdrant bằng Docker, dữ liệu thực tế được lưu trong một thư mục trên máy tính của bạn (được mount thông qua volume).

1. Bạn kiểm tra trong file `docker-compose.yml` hoặc câu lệnh `docker run` xem thư mục nào đang mount vào `/qdrant/storage`.
2. Ví dụ bạn chạy: `docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant`
3. Bạn chỉ cần copy toàn bộ thư mục `qdrant_storage/` này, nén lại thành file `.zip`.
4. Gửi file zip sang máy tính khác.
5. Máy khác giải nén ra và chạy lại lệnh Docker y hệt trỏ vào thư mục đó là xong! Toàn bộ 18 endpoints sẽ xuất hiện ngay lập tức mà không cần code Python nào cả.
