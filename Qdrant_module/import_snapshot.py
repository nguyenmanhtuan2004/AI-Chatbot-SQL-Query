from pathlib import Path

from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

snapshot_path = Path(
    r"factory_data_dictionary-1353333361573545-2026-04-22-05-02-55.snapshot"
)

if not snapshot_path.exists():
    raise FileNotFoundError(f"Khong tim thay file snapshot: {snapshot_path}")

# Upload snapshot local len Qdrant roi restore collection.
with snapshot_path.open("rb") as snapshot_file:
    client.http.snapshots_api.recover_from_uploaded_snapshot(
        collection_name="factory_data_dictionary",
        wait=True,
        snapshot=snapshot_file,
    )
print("Khôi phục dữ liệu thành công!")