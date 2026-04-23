from fastapi import FastAPI
import uvicorn
from api.routes import router

app = FastAPI(
    title="AI SQL Chatbot API",
    description="API Gateway for Text-to-SQL Chatbot with RAG capabilities",
    version="1.0.0"
)

# Gắn router từ thư mục api/
app.include_router(router, prefix="/api")

from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def read_root():
    # Tự động chuyển hướng trang chủ (/) sang giao diện Swagger UI (/docs)
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    # Chạy server FastAPI
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
