import sys
import os
import urllib.parse
from sqlalchemy import create_engine, text

# Thêm đường dẫn gốc để import được core.config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

# 1. Tạo Connection Pool bằng SQLAlchemy
# mssql+pyodbc:///?odbc_connect=<encoded_connection_string>
params = urllib.parse.quote_plus(settings.sql_connection_string)
engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}",
    pool_size=5,        # Duy trì 5 kết nối sẵn sàng
    max_overflow=10,    # Cho phép mở thêm tối đa 10 kết nối nếu quá tải
    pool_timeout=30,    # Đợi tối đa 30s để lấy kết nối từ pool
    pool_recycle=1800,  # Tự động làm mới kết nối sau mỗi 30 phút
)

def execute_sql_query(query: str) -> list[dict] | str:
    """
    Thực thi câu lệnh SQL sử dụng Connection Pool.
    """
    try:
        # Bảo mật cơ bản
        lower_query = query.lower()
        forbidden_keywords = ["drop ", "delete ", "truncate ", "update ", "insert ", "alter "]
        if any(keyword in lower_query for keyword in forbidden_keywords):
            raise ValueError("Lỗi bảo mật: Chỉ cho phép câu lệnh SELECT.")

        # 2. Sử dụng engine để thực thi
        with engine.connect() as connection:
            result_proxy = connection.execute(text(query))
            
            # Nếu là câu lệnh không trả về dữ liệu
            if not result_proxy.returns_rows:
                return "Query thực thi thành công nhưng không có dữ liệu trả về."

            # Chuyển đổi kết quả sang list of dicts
            columns = result_proxy.keys()
            result = [dict(zip(columns, row)) for row in result_proxy.fetchall()]
            
            return result

    except Exception as e:
        # Log lỗi chi tiết nếu cần
        raise RuntimeError(f"Lỗi SQL Execution: {str(e)}")

# Khối code test
if __name__ == "__main__":
    try:
        test_query = "SELECT TOP 5 * FROM PRODUCTIVITY"
        print("Đang kiểm tra kết nối qua SQLAlchemy Pool...")
        data = execute_sql_query(test_query)
        print(f"✅ Thành công! Lấy được {len(data)} dòng dữ liệu.")
        if data:
            print("Dòng đầu tiên:", data[0])
    except Exception as ex:
        print(f"❌ Thất bại: {ex}")
