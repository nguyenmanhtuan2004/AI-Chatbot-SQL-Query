# AI Chatbot SQL Query - Tai Lieu Kien Truc va Context

## 1. Boi Canh va Muc Tieu

### 1.1 Van de hien tai
- Kho truy xuat bao cao nang suat, ti le loi, doanh thu theo thoi gian thuc.
- Quy trinh tao bao cao thu cong ton nhieu thoi gian, phu thuoc vao ky nang SQL cua tung ca nhan.
- Toc do ra quyet dinh bi cham, kho theo sat van hanh chuyen may theo ca/gio.

### 1.2 Muc tieu he thong
Xay dung AI Chatbot cho phep nguoi dung dat cau hoi bang ngon ngu tu nhien va nhan ket qua so lieu chinh xac trong vai giay.

Vi du cau hoi:
- "Top 5 loi cua chuyen 1 hom nay?"
- "Tong doanh thu theo ma hang A trong ca sang?"
- "Ti le loi trung binh theo gio trong 3 ngay gan nhat?"

### 1.3 Tieu chi thanh cong
- Do chinh xac truy van: uu tien tuyet doi.
- Thoi gian phan hoi muc tieu: 5-10 giay/cau hoi.
- Giam thao tac thu cong tao bao cao, ho tro van hanh ra quyet dinh nhanh.

## 2. Giai Phap Kien Truc Duoc Chon

### 2.1 Lua chon kien truc
Su dung kien truc AI Agent + RAG + SQL Execution + Self-Correction.

### 2.2 Trade-off va ly do lua chon
- Vuot troi hon Few-shot Prompting trong xu ly logic phuc tap (vi du: tinh doanh thu theo ma hang, khung gio, don gia), giam nguy co hallucination.
- Linh hoat va toi uu chi phi hon Fine-tuning vi khong can huan luyen lai mo hinh moi khi schema CSDL thay doi.
- Chap nhan do tre 5-10 giay de doi lay do chinh xac va tinh on dinh.

## 3. Luong Xu Ly Ky Thuat (Technical Workflow)

He thong van hanh qua 4 buoc cot loi:

### Buoc 1 - Loc Ngu Nghia (RAG)
Input: cau hoi nguoi dung.

Xu ly:
- Truy van Vector DB de lay "Tu dien du lieu" lien quan den cau hoi.
- Goi y cong thuc nghiep vu, y nghia cot, mapping ten cot/ten bang.

Output:
- Context da duoc loc (metadata schema, business rules, cong thuc).

Vi du context lay ra:
- Cong thuc: Doanh thu = San luong * Don gia.
- Mapping: bang san luong, bang loi, bang danh muc ma hang.

### Buoc 2 - Lap ke hoach (Agent Planning)
Input: cau hoi nguoi dung + context tu Buoc 1.

Xu ly:
- Agent xac dinh muc tieu cau hoi.
- Chon bang/field can dung (vi du: Bang_NangSuat, Bang_Loi).
- Xac dinh dieu kien loc: ngay, ca, chuyen, ma hang.

Output:
- Ke hoach truy van (query plan) ro rang truoc khi tao SQL.

### Buoc 3 - Thuc thi va Tu sua (Execution & Self-Correction)
Input: query plan.

Xu ly:
- Agent tao cau SQL dau tien.
- Chay SQL tren he quan tri du lieu read-only.
- Neu loi cu phap/khong hop schema: doc loi, phan tich va tu sua SQL.
- Lap lai den khi truy van thanh cong hoac dat nguong retry.

Output:
- Du lieu tho dang JSON/table.
- Log truy van va lich su sua loi de truy vet.

### Buoc 4 - Trinh bay ket qua (Output)
Input: du lieu tho tu Buoc 3.

Xu ly:
- Agent tong hop, tinh toan chi so cuoi (neu can).
- Trinh bay ket qua de hieu cho nguoi dung (bang, top N, nhan xet ngan).
- Co the kem canh bao du lieu neu mau qua nho hoac thieu du lieu.

Output:
- Cau tra loi tu nhien + so lieu co cau truc.

## 4. De Xuat Cong Nghe va Ha Tang

### 4.1 Mo hinh LLM
- GPT-4o hoac Claude 3.5 Sonnet.

### 4.2 Framework dieu phoi
- LangChain hoac Microsoft Semantic Kernel.

### 4.3 Vector DB luu tru Tu dien du lieu
- Qdrant hoac pgvector.

### 4.4 Tang du lieu va an toan van hanh (quan trong)
Khong cho AI query truc tiep vao CSDL OLTP dang van hanh xuong.

Kien truc du lieu khuyen nghi:
- Dong bo du lieu tu OLTP sang Data Warehouse/OLAP theo chu ky ngan.
- Cap quyen read-only cho AI tren kho du lieu phuc vu phan tich.
- Tach tai nguyen van hanh va tai nguyen phan tich de tranh anh huong he thong san xuat.

## 5. Nguyen Tac Thiet Ke de Dam Bao Do Chinh Xac

- Schema-aware prompting: prompt phai kem schema/business rules da duoc RAG lay ve.
- SQL guardrails:
  - Chi cho phep SELECT.
  - Gioi han LIMIT mac dinh cho truy van chi tiet.
  - Chan truy van can toan bo bang neu khong can thiet.
- Retry co kiem soat:
  - So lan retry gioi han (vi du 2-3 lan).
  - Co fallback message neu that bai.
- Logging day du:
  - Cau hoi goc, context RAG, SQL cuoi, thoi gian thuc thi, loi neu co.

## 6. Phi Chuc Nang (Non-functional Requirements)

- SLA phan hoi: 5-10 giay cho cau hoi thong thuong.
- Auditability: moi cau tra loi phai truy vet duoc SQL va nguon du lieu.
- Bao mat:
  - An danh thong tin nhay cam trong log (neu co).
  - Quan ly role va quyen truy cap theo nhom nguoi dung.
- Kha nang mo rong:
  - De dang them bang/chi so moi qua cap nhat Data Dictionary + embeddings.

## 7. Pham Vi Cau Hoi uu tien

- Nang suat theo chuyen/ca/ngay.
- Top loi theo thoi gian/chuyen/ma hang.
- Doanh thu theo ma hang/ca/gio.
- So sanh xu huong theo ngay-tuan-thang.

## 8. Mau Prompt Muc Tieu cho He thong

"Ban la tro ly phan tich du lieu nha may. Nhiem vu la tao SQL SELECT chinh xac dua tren schema va business rules duoc cung cap. Khong duoc su dung thong tin ngoai context. Neu gap loi SQL, hay doc loi va tu sua. Chi tra ve ket qua da duoc xac minh tu du lieu."

## 9. Dinh huong Trien khai

### Giai doan 1 - MVP
- Ho tro nhom cau hoi co tan suat cao (nang suat, loi, doanh thu).
- RAG tu Data Dictionary ban dau.
- SQL execution + self-correction co retry co gioi han.

### Giai doan 2 - On dinh va toi uu
- Toi uu prompt va cache ket qua cau hoi pho bien.
- Them dashboard quan sat chat luong truy van va do tre.

### Giai doan 3 - Mo rong
- Them phan tich xu huong va canh bao bat thuong.
- Mo rong pham vi KPI theo bo phan/nganh hang.

## 10. Tong ket

Kien truc Agent + RAG + SQL Self-Correction phu hop bai toan bao cao van hanh nha may, dam bao do chinh xac cao, giam hallucination, linh hoat khi schema thay doi, va an toan he thong nho tach OLTP khoi tang phan tich read-only.
