import requests
from qdrant_client import QdrantClient

collection_name = "factory_data_dictionary"
client = QdrantClient(url="http://localhost:6333")

# 1. Yêu cầu Qdrant server tạo snapshot
print(f"Đang yêu cầu Qdrant tạo snapshot cho collection '{collection_name}'...")
snapshot = client.create_snapshot(collection_name=collection_name)
snapshot_name = snapshot.name
print(f"Đã tạo thành công snapshot trên Qdrant server: {snapshot_name}")

# 2. Tự động tải file snapshot đó về thư mục hiện tại
download_url = f"http://localhost:6333/collections/{collection_name}/snapshots/{snapshot_name}"
print(f"Đang tải file snapshot về thư mục của dự án...")

response = requests.get(download_url, stream=True)
if response.status_code == 200:
    with open(snapshot_name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Tải xuống hoàn tất! Bạn có thể gửi file '{snapshot_name}' này cho máy khác.")
else:
    print(f"Lỗi khi tải file: {response.status_code}")
