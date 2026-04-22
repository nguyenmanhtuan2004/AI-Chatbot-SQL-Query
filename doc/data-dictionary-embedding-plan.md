# Kế Hoạch Xây Dựng & Hướng Dẫn Embedding Data Dictionary vào Qdrant

Dựa trên sơ đồ ERD cung cấp, dưới đây là kế hoạch từng bước (step-by-step) để xây dựng Data Dictionary (Từ điển dữ liệu) và đưa nó vào Qdrant (Vector Database) nhằm phục vụ RAG cho AI Chatbot.

## Bước 1: Xây dựng Data Dictionary (Từ điển dữ liệu) Semantic

AI không chỉ cần biết cấu trúc bảng (Schema), mà còn cần "hiểu" ngữ nghĩa (Semantics). Chúng ta cần tạo ra các tài liệu text/JSON chứa cả hai.

**1.1. Chi tiết các bước tạo Data Dictionary dạng JSON cho Qdrant:**

Để AI (RAG) tìm kiếm chính xác và LLM sinh SQL đúng, file JSON của mỗi bảng không chỉ chứa tên cột mà phải chứa **ngữ nghĩa** (semantics). Dữ liệu này sẽ được tách thành `metadata` (để filter trong Qdrant) và `content` (nội dung text để nhúng embedding).

*   **Bước 1.1.1: Trích xuất thông tin bảng (Table Level)**
    *   Xác định tên bảng thực tế trong Database.
    *   Viết `description`: Phải dùng ngôn ngữ tự nhiên, giải thích rõ bảng này chứa dữ liệu gì, dùng để trả lời cho những loại câu hỏi nào (VD: tính năng suất, xem thông tin lỗi). Đây là phần quan trọng nhất để vector DB (Qdrant) match với câu hỏi của user.

*   **Bước 1.1.2: Cấu trúc hóa các cột (Column Level)**
    *   Mỗi cột cần: `name` (tên cột), `type` (kiểu dữ liệu).
    *   Đặc biệt cần `description`: Giải thích ý nghĩa của cột bằng ngôn ngữ tự nhiên (Vd: `Quantity` là "Số lượng sản phẩm làm ra / Sản lượng thực tế"). Chú thích rõ ràng nếu cột là Primary Key (PK) hoặc Foreign Key (FK).

*   **Bước 1.1.3: Xác định ràng buộc & phép kết nối (Joins/Relationships)**
    *   Liệt kê bằng lời văn rõ ràng bảng này có thể JOIN với bảng nào, thông qua trường nào (Rất hữu ích để AI tự động tham chiếu và tạo lập các câu `JOIN` không bị sai lệch).

*   **Bước 1.1.4: Hoàn thiện cấu trúc JSON chuẩn cho một bảng**
    
Dưới đây là ví dụ chuẩn tạo file `schemas/PRODUCTIVITY.json` (Năng suất) với cấu trúc thiết kế tối ưu cho việc embedding vào Qdrant (chia rõ metadata và phần text content):

```json
{
  "metadata": {
    "type": "table_schema",
    "table_name": "PRODUCTIVITY",
    "domain": "năng suất, sản lượng, thực hiện"
  },
  "content": {
    "description": "Bảng PRODUCTIVITY ghi nhận số lượng sản phẩm hoàn thành thực tế (năng suất) theo từng dây chuyền, sản phẩm, ca làm việc và khoảng thời gian. Dùng để tính toán tổng sản lượng, năng suất thực tế, tiến độ hoàn thành.",
    "columns": [
      {"name": "ID", "type": "int", "description": "Khóa chính (PK) của bản ghi năng suất."},
      {"name": "LineID", "type": "string", "description": "Mã dây chuyền sản xuất (FK). Dùng để phân nhóm dữ liệu theo dây chuyền."},
      {"name": "ProductID", "type": "string", "description": "Mã sản phẩm (FK). Dùng để phân nhóm tính toán theo loại sản phẩm."},
      {"name": "Quantity", "type": "int", "description": "Số lượng sản phẩm làm ra (sản lượng thực tế thu được)."},
      {"name": "StartTime", "type": "datetime", "description": "Thời điểm bắt đầu ghi nhận."},
      {"name": "EndTime", "type": "datetime", "description": "Thời điểm kết thúc ghi nhận."},
      {"name": "ShiftID", "type": "int", "description": "Mã ca làm việc (FK). Dùng để lọc hoạc phân nhóm theo ca (sáng/chiều/tối)."}
    ],
    "relationships": [
      "JOIN với PRODUCTION_LINES trên LineID = PRODUCTION_LINES.LineID để lấy tên và thông tin bộ phận của dây chuyền.",
      "JOIN với PRODUCTS trên ProductID = PRODUCTS.ProductID để tính doanh thu (Quantity * UnitPrice) hoặc lấy tên sản phẩm.",
      "JOIN với SHIFTS trên ShiftID = SHIFTS.ShiftID để lấy chi tiết thời gian ca làm việc."
    ]
  }
}
```

*(Quy trình tương tự cần được lặp lại, tạo thành các file JSON riêng biệt cho: `DEFECTS.json`, `PRODUCTS.json`, `PRODUCTION_PLANS.json`, `SHIFTS.json`, `WORK_ASSIGNMENTS.json`, `EMPLOYEES.json`, `DEFECT_CATEGORIES.json`, `PRODUCTION_LINES.json`).*

**1.2. Viết các Ghi chú Nghiệp vụ (Business Rules - Cực kỳ quan trọng để chống sinh câu lệnh sai):**
AI rất hay sai ở phần logic nghiệp vụ, nên cần tạo các chunk text riêng biệt chứa công thức toán học và định nghĩa logic cho từng metrics (chỉ số). Dưới đây là bộ các Use case phổ biến cần cấu hình:
Pattern mẫu
```
{
  "metadata": {
    "type": "business_rule",
    "domain": "quality",
    "metric_name": "Tỉ lệ lỗi theo sản phẩm",
    "trigger_keywords": ["tỉ lệ lỗi", "hàng hư", "defect rate", "phế phẩm"],
    "tables_involved": ["DEFECTS", "PRODUCTIVITY"] 
  },
  "content": {
    "description": "Tính toán phần trăm sản phẩm bị lỗi trên tổng sản lượng thực tế của một sản phẩm cụ thể.",
    "sql_logic": "JOIN DEFECTS d ON p.ID = d.ProductivityID. Công thức: (SUM(d.DefectCount) * 1.0 / SUM(p.Quantity)) * 100",
    "conditions": "Luôn luôn GROUP BY d.ProductID hoặc d.LineID tùy theo câu hỏi.",
    "few_shot_example": {
       "user_query": "Tỉ lệ lỗi của áo sơ mi hôm nay là bao nhiêu?",
       "expected_sql": "SELECT (SUM(d.DefectCount) * 1.0 / SUM(p.Quantity)) * 100 FROM PRODUCTIVITY p JOIN DEFECTS d ON p.ID = d.ProductivityID WHERE p.ProductID = 'Ao_So_Mi' AND p.WorkDate = CAST(GETDATE() AS DATE)"
    }
  }
}
```

**A. Nhóm Chỉ số Tài chính (Financial Metrics):**
- **1. Tổng Doanh thu (Total Revenue):** "Để tính doanh thu, lấy tổng hàm SUM của (sản lượng `PRODUCTIVITY.Quantity` nhân với đơn giá `PRODUCTS.UnitPrice`) thông qua khóa kết nối `ProductID`."
- **2. Giá trị thiệt hại do phế phẩm (Cost of Scrap):** "Để tính số tiền bị thiệt hại do hàng rớt/phế phẩm, lấy tổng hàm SUM của (`DEFECTS.DefectCount` nhân với `PRODUCTS.UnitPrice`), nhưng bắt buộc phải có điều kiện lọc `DEFECT_CATEGORIES.IsRepairable = 0` (lỗi không thể sửa chữa)."

**B. Nhóm Chỉ số Chất lượng (Quality & Defect Metrics):**
- **3. Tỉ lệ lỗi tổng thể (Overall Defect Rate):** "Để tính tỉ lệ lỗi, chia (tổng số lỗi `DEFECTS.DefectCount`) cho (tổng sản lượng `PRODUCTIVITY.Quantity`) theo cùng `LineID`, `ProductID` và `ShiftID` tương ứng với lô hàng `ProductivityID`."
- **4. Tỉ lệ hàng phế phẩm (Scrap Rate):** "Tương tự tỉ lệ lỗi, nhưng tử số chỉ là tổng `DEFECTCount` của các lỗi có `DEFECT_CATEGORIES.IsRepairable = 0`."
- **5. Mức độ lỗi nghiêm trọng (Critical Defects):** "Khi người dùng hỏi 'các lỗi nghiêm trọng', bắt buộc phải thêm điều kiện `WHERE DEFECT_CATEGORIES.Severity = 'Cao'` hoặc `'High'`."

**C. Nhóm Chỉ số Tiến độ và Kế hoạch (Planning & Performance):**
- **6. Tiến độ hoàn thành kế hoạch (% Plan Completion):** "Công thức = `(SUM(PRODUCTIVITY.Quantity) / PRODUCTION_PLANS.TargetQuantity) * 100`. Cần GROUP BY theo `PlanID` và kiểm tra xem tổng sản lượng đã đạt hay vượt `TargetQuantity` chưa."
- **7. Tốc độ sản xuất theo giờ (Hourly Productivity / UPH - Units per Hour):** "Nếu câu hỏi yêu cầu năng suất theo giờ, cần dùng hàm trích xuất giờ từ cột `PRODUCTIVITY.EndTime` hoặc `RecordedAt` để gom nhóm (GROUP BY) và tính tổng `Quantity` trong giờ đó."

**D. Nhóm Chỉ số Nhân sự và Nguồn lực (HR & Resources):**
- **8. Tham chiếu người làm việc (Worker lookup):** "Khi hỏi 'Ai là người làm ở chuyền X hôm nay', phải truy vấn từ bảng `WORK_ASSIGNMENTS`, kết nối (`JOIN`) với `EMPLOYEES` để lấy `EmployeeName`, và kết nối với `PRODUCTION_LINES` để lọc mã chuyền, cùng điều kiện `WorkDate = TODAY()`."
- **9. Năng suất theo người quản lý (Manager Performance):** "Để đánh giá năng suất của một quản đốc/tổ trưởng, cần lấy tổng `PRODUCTIVITY.Quantity` và `GROUP BY PRODUCTION_LINES.ManagerName`."

## Bước 2: Chiến lược chia nhỏ dữ liệu (Chunking)

Để truy xuất chính xác từ Qdrant, ta không ném toàn bộ CSDL vào một đoạn text, mà chia nhỏ thành các **tài liệu độc lập (chunks)**. Chia thành 3 loại:
1.  **Table Schema Chunk:** Mỗi bảng là 1 chunk (như JSON ở Bước 1.1).
2.  **Column Mapping Chunk:** Từ khóa tự nhiên mapping với cột. Ví dụ: *"Tiền thu được, doanh số, giá trị hàng hóa -> ánh xạ đến phép tính (PRODUCTIVITY.Quantity * PRODUCTS.UnitPrice)"*.
3.  **Business Logic Chunk:** Các quy tắc tính toán (như Bước 1.2).

## Bước 3: Lựa chọn Mô hình Embedding

Chọn một mô hình embedding để biến các chunks text ở Bước 2 thành Vector (dãy số):
- **Gợi ý 1:** `text-embedding-3-small` của OpenAI (rẻ, tiếng Việt tốt, vector size 1536).
- **Gợi ý 2:** `multilingual-e5-large` (mô hình mã nguồn mở nếu muốn chạy local, hỗ trợ tiếng Việt tốt).

## Bước 4: Khởi tạo Qdrant Collection

Sử dụng thư viện `qdrant-client` (Python).

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url="http://localhost:6333") # Hoặc Qdrant Cloud URL

# Tạo collection
client.recreate_collection(
    collection_name="factory_data_dictionary",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)
```

## Bước 5: Embedding và Lưu vào Qdrant (Ingestion)

Quét qua danh sách các chunks (Schema + Business Rules), nhúng nó thành vector và lưu kèm **Payload (Metadata)** để sau này filter dễ dàng.

```python
# Giả mã (Pseudocode) với Langchain hoặc OpenAI API
chunks = [
    {
        "text": "Bảng PRODUCTIVITY lưu sản lượng thực tế...", 
        "metadata": {"type": "table_schema", "table": "PRODUCTIVITY"}
    },
    {
        "text": "Công thức Doanh thu = PRODUCTIVITY.Quantity * PRODUCTS.UnitPrice", 
        "metadata": {"type": "business_rule", "domain": "finance"}
    }
]

points = []
for i, chunk in enumerate(chunks):
    vector = get_embedding(chunk["text"]) # Hàm gọi API OpenAI/Local
    points.append(
        PointStruct(id=i, vector=vector, payload={"text": chunk["text"], **chunk["metadata"]})
    )

client.upsert(
    collection_name="factory_data_dictionary",
    points=points
)
```

## Bước 6: Tích hợp RAG để Chatbot sinh SQL

Khi người dùng hỏi: *"Top 5 lỗi của chuyền 1 hôm nay?"*
1.  **Embed Câu hỏi:** Biến câu hỏi thành vector bằng mô hình ở Bước 3.
2.  **Tìm kiếm (Search) trong Qdrant:** Lấy ra top `K=5` chunks gần nghĩa nhất.
    *   *Kết quả mong đợi trả về:* Chunk mô tả bảng `DEFECTS`, `DEFECT_CATEGORIES`, bảng `PRODUCTION_LINES`, và Business rule về định nghĩa "Lỗi".
3.  **Tạo Prompt:** Nhúng các chunks tìm được vào Prompt, đưa cho GPT-4o/Claude để viết SQL.
    ```text
    Bạn là AI viết SQL. Dưới đây là cấu trúc được trích xuất từ Data Dictionary:
    [Nội dung từ Qdrant trả về]
    
    Yêu cầu của người dùng: Top 5 lỗi của chuyền 1 hôm nay?
    Hãy viết SQL SELECT.
    ```
