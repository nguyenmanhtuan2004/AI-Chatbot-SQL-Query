import streamlit as st
import requests
import pandas as pd

# URL của Backend FastAPI
API_URL = "http://127.0.0.1:8000/api/chat"

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="AI Chatbot - Manufacturing Data",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Chatbot Phân tích Dữ liệu Sản xuất")

# Khởi tạo trạng thái giao diện (Session State) để lưu lịch sử tin nhắn
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Tin nhắn chào mừng mặc định
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Xin chào! Tôi là AI phân tích dữ liệu sản xuất. Bạn muốn hỏi gì về năng suất, tỉ lệ lỗi hay chuyền sản xuất hôm nay?"
    })

# Hiển thị lịch sử chat từ Session State
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Nếu có dữ liệu bảng thì render ra
        if msg.get("sql_result"):
            df = pd.DataFrame(msg["sql_result"])
            st.dataframe(df, use_container_width=True)
            
            # Tính năng ăn tiền: Tải xuống CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải xuống dữ liệu (CSV)",
                data=csv,
                file_name=f"export_data_{idx}.csv",
                mime="text/csv",
                key=f"dl_{idx}"
            )
            
        # Góc Debug: Hiển thị câu truy vấn SQL đã sinh ra
        if msg.get("sql_query"):
            with st.expander("🛠️ Xem SQL Query (Debug)"):
                st.code(msg["sql_query"], language="sql")

# Khung nhập tin nhắn (Chat Input)
if prompt := st.chat_input("Ví dụ: Tại sao Quý 2 lại có nhiều lỗi vậy?"):
    # 1. Thêm tin nhắn của User vào Session State và hiển thị ngay lập tức
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Hiển thị khung tải (Loading) trong lúc chờ AI phản hồi
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ Đang phân tích dữ liệu...")
        
        try:
            # Gửi Request lên FastAPI Backend
            response = requests.post(API_URL, json={"query": prompt})
            response.raise_for_status()
            res_data = response.json()
            
            if res_data.get("status") == "success":
                data_payload = res_data.get("data", {})
                answer_text = data_payload.get("answer", "Không có câu trả lời.")
                sql_result = data_payload.get("sql_result")
                sql_query = data_payload.get("sql_query")
                
                # Cập nhật UI với câu trả lời Text
                message_placeholder.markdown(answer_text)
                
                # Render UI cho DataFrame (Nếu có dữ liệu)
                if sql_result:
                    df = pd.DataFrame(sql_result)
                    st.dataframe(df, use_container_width=True)
                    
                    # Nút tải xuống cho kết quả mới nhất
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Tải xuống dữ liệu (CSV)",
                        data=csv,
                        file_name="export_data_new.csv",
                        mime="text/csv",
                        key="dl_new_latest"
                    )
                
                # Góc Debug cho kết quả mới nhất
                if sql_query:
                    with st.expander("🛠️ Xem SQL Query (Debug)"):
                        st.code(sql_query, language="sql")
                
                # 3. Lưu câu trả lời của AI và Data vào Session State
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer_text,
                    "sql_result": sql_result,
                    "sql_query": sql_query
                })
            else:
                error_msg = res_data.get("error", "Lỗi không xác định từ Server.")
                message_placeholder.error(f"❌ {error_msg}")
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Lỗi: {error_msg}"})
                
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Không thể kết nối tới Backend FastAPI: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
