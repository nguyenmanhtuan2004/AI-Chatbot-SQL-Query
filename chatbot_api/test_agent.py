from agent.graph import app
import json

def run_test(query: str):
    print(f"\n" + "="*50)
    print(f"--- ĐANG XỬ LÝ CÂU HỎI: {query} ---")
    print("="*50)
    
    # 1. Khởi tạo trạng thái đầu vào (theo chuẩn V2)
    initial_state = {
        "query": query,
        "context": None,
        "generated_sql": None,
        "data": None,
        "error": None,
        "sql_success": False,
        "retry_count": 0
    }
    
    # 2. Chạy đồ thị
    result = app.invoke(initial_state)
    
    # 3. Hiển thị kết quả chi tiết
    if result.get("sql_success"):
        print("\n✅ TRUY VẤN THÀNH CÔNG")
    else:
        print("\n⚠️ CÓ LỖI HOẶC CẢNH BÁO")

    print(f"\n[NGỮ CẢNH (CONTEXT)]:\n{result.get('context') or 'N/A'}")
    print(f"\n[MÃ SQL SINH RA]:\n{result.get('generated_sql') or 'N/A'}")
    
    if result.get("error"):
        print(f"\n[THÔNG BÁO HỆ THỐNG]:\n{result['error']}")
    
    print("\n[DỮ LIỆU KẾT QUẢ]:")
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super().default(obj)


    data = result.get("sql_result")
    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False, cls=CustomEncoder))
    else:
        print("Không có dữ liệu trả về.")
    print("\n" + "="*50)

if __name__ == "__main__":
    # Test 1: Câu hỏi hợp lệ
    run_test("Tỉ lệ lỗi của chuyền 1 là bao nhiêu?")
    
    # Test 2: Câu hỏi không có trong nghiệp vụ (Để test nhánh Error)
    # run_test("Giá vàng hôm nay bao nhiêu?")
