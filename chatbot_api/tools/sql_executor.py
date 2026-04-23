import pyodbc
from core.config import settings

def execute_sql_query(query: str) -> list[dict] | str:
    """
    Thực thi câu lệnh SQL trên SQL Server.
    Nếu gặp lỗi cú pháp hay bảng không tồn tại, sẽ ném ra RuntimeError để Agent bắt và sửa lại.
    """
    try:
        # Cấm các câu lệnh phá hoại (Chỉ cấp quyền SELECT để an toàn 100%)
        lower_query = query.lower()
        forbidden_keywords = ["drop ", "delete ", "truncate ", "update ", "insert ", "alter "]
        if any(keyword in lower_query for keyword in forbidden_keywords):
            raise ValueError("Lỗi bảo mật: Chỉ cho phép câu lệnh SELECT.")

        # Mở kết nối
        conn = pyodbc.connect(settings.sql_connection_string)
        cursor = conn.cursor()
        
        cursor.execute(query)
        
        # Xử lý trường hợp câu query không trả về bảng (không fetch được)
        if cursor.description is None:
            conn.close()
            return "Query thực thi thành công nhưng không có dữ liệu trả về."

        # Lấy header (tên cột)
        columns = [column[0] for column in cursor.description]
        
        # Lấy data
        rows = cursor.fetchall()
        
        # Parse thành List các Dictionary để AI dễ đọc (vd: [{"id": 1, "name": "A"}])
        result = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return result

    except pyodbc.Error as e:
        # Bắt các lỗi của SQL Server (vd: Invalid object name, Syntax error)
        raise RuntimeError(f"Lỗi SQL Execution: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Lỗi Hệ thống: {str(e)}")

# Khối code này giúp bạn có thể chạy file độc lập (python tools/sql_executor.py) để test kết nối
if __name__ == "__main__":
    try:
        test_query = "SELECT TOP 1 * FROM INFORMATION_SCHEMA.TABLES"
        print("Đang kiểm tra kết nối SQL Server...")
        data = execute_sql_query(test_query)
        print("✅ Kết nối SQL Server thành công! Dữ liệu mẫu nhận được:")
        print(data)
    except Exception as ex:
        print("❌ Kết nối thất bại, chi tiết lỗi:")
        print(ex)
