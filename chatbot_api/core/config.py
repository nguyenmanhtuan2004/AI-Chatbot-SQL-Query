import os
from dotenv import load_dotenv

# Load file .env
load_dotenv()

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
