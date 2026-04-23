import os
from dotenv import load_dotenv

# Đường dẫn gốc của dự án (chatbot_api/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load file .env từ đường dẫn tuyệt đối
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Đảm bảo GOOGLE_APPLICATION_CREDENTIALS là đường dẫn tuyệt đối
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if creds_path and not os.path.isabs(creds_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, creds_path)

class Settings:
    # Xác thực Google (Vertex AI / Gemini)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Kết nối Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    # Kết nối SQL Server
    SQL_SERVER = os.getenv("SQL_SERVER", "localhost,14330")
    SQL_DATABASE = os.getenv("SQL_DATABASE", "ChatBotDB")
    SQL_USER = os.getenv("SQL_USER", "sa")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")

    @property
    def sql_connection_string(self):
        # Tạo chuỗi kết nối PyODBC cho SQL Server
        return (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.SQL_SERVER};"
            f"DATABASE={self.SQL_DATABASE};"
            f"UID={self.SQL_USER};"
            f"PWD={self.SQL_PASSWORD};"
            "TrustServerCertificate=yes;"
        )

settings = Settings()
