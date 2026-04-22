erDiagram
    CUSTOMERS {
        NUMBER customer_id PK "Mã khách hàng"
        NVARCHAR2 full_name "Họ và tên"
        VARCHAR2 email UK "Email đăng nhập"
        VARCHAR2 password_hash "Mật khẩu mã hóa"
        VARCHAR2 phone UK "Số điện thoại"
        NVARCHAR2 address "Địa chỉ giao hàng"
        DATE created_at "Ngày tạo tài khoản"
        VARCHAR2 status "Trạng thái"
    }

    CATEGORIES {
        NUMBER category_id PK "Mã danh mục"
        NVARCHAR2 category_name UK "Tên danh mục"
        NVARCHAR2 description "Mô tả"
    }

    AUTHORS {
        NUMBER author_id PK "Mã tác giả"
        NVARCHAR2 author_name "Tên tác giả"
        NCLOB biography "Tiểu sử"
        DATE birth_date "Ngày sinh"
        NVARCHAR2 nationality "Quốc tịch"
    }

    PUBLISHERS {
        NUMBER publisher_id PK "Mã NXB"
        NVARCHAR2 publisher_name UK "Tên NXB"
        NVARCHAR2 address "Địa chỉ"
        VARCHAR2 phone "Số điện thoại"
        VARCHAR2 email UK "Email liên hệ"
    }

    BOOKS {
        NUMBER book_id PK "Mã sách"
        NVARCHAR2 title "Tên sách"
        VARCHAR2 isbn UK "Mã ISBN"
        NUMBER price "Giá bán"
        NUMBER stock_quantity "Tồn kho"
        NCLOB description "Mô tả sách"
        NUMBER publication_year "Năm xuất bản"
        NUMBER page_count "Số trang"
        VARCHAR2 cover_image_url "Link ảnh bìa"
        NUMBER category_id FK "Mã danh mục"
        NUMBER publisher_id FK "Mã NXB"
        DATE created_at "Ngày thêm"
    }

    BOOK_AUTHORS {
        NUMBER book_id PK, FK "Mã sách"
        NUMBER author_id PK, FK "Mã tác giả"
    }

    ORDERS {
        NUMBER order_id PK "Mã đơn hàng"
        NUMBER customer_id FK "Mã khách hàng"
        DATE order_date "Ngày đặt hàng"
        NUMBER total_amount "Tổng tiền"
        VARCHAR2 status "Trạng thái"
        NVARCHAR2 shipping_address "Địa chỉ giao hàng"
        VARCHAR2 payment_method "Phương thức TT"
    }

    ORDER_DETAILS {
        NUMBER order_detail_id PK "Mã chi tiết"
        NUMBER order_id FK "Mã đơn hàng"
        NUMBER book_id FK "Mã sách"
        NUMBER quantity "Số lượng"
        NUMBER unit_price "Đơn giá"
        NUMBER subtotal "Thành tiền - Virtual"
    }

    REVIEWS {
        NUMBER review_id PK "Mã đánh giá"
        NUMBER customer_id FK "Mã khách hàng"
        NUMBER book_id FK "Mã sách"
        NUMBER rating "Số sao 1-5"
        NCLOB review_comment "Bình luận"
        DATE review_date "Ngày đánh giá"
    }

    %% === RELATIONSHIPS === %%

    CUSTOMERS ||--o{ ORDERS : "đặt hàng"
    CUSTOMERS ||--o{ REVIEWS : "viết đánh giá"

    CATEGORIES ||--o{ BOOKS : "phân loại"

    PUBLISHERS ||--o{ BOOKS : "xuất bản"

    BOOKS ||--o{ BOOK_AUTHORS : "được viết bởi"
    AUTHORS ||--o{ BOOK_AUTHORS : "viết"

    BOOKS ||--o{ ORDER_DETAILS : "được đặt mua"
    BOOKS ||--o{ REVIEWS : "nhận đánh giá"

    ORDERS ||--o{ ORDER_DETAILS : "chứa"
