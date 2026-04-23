# 💎 Lumina AI Design System (Light Mode)

Hệ thống thiết kế tối giản, hiện đại và tập trung cao độ dành cho các giao diện AI.

## 🎨 Bảng màu (Color Palette)

### Neutrals (Màu trung tính)
- **Surface:** `#ffffff` (Pure White) - Nền chính của ứng dụng.
- **Surface Dim:** `#f9fafb` (Zinc-50) - Nền cho các phân đoạn phụ và tạo chiều sâu.
- **Border:** `#e5e7eb` (Zinc-200) - Màu viền mặc định cho input và component.
- **Text Primary:** `#18181b` (Zinc-900) - Cho tiêu đề chính và văn bản quan trọng.
- **Text Secondary:** `#71717a` (Zinc-500) - Cho tiêu đề phụ và placeholder.

### Accents (Màu nhấn)
- **Primary:** `#6366f1` (Indigo-500) - Cho các hành động chính, trạng thái focus và icon.
- **Accent Subtle:** `#f4f4f5` (Zinc-100) - Cho nền badge và trạng thái hover.

## 🔡 Typography (Kiến trúc chữ)

- **Font Family:** `Manrope` (Font Sans-serif hiện đại, hỗ trợ tiếng Việt tốt).
- **Headings:** Bold weight, tracking-tight, màu Zinc-900.
- **Body:** Medium weight, màu Zinc-500.
- **Badges:** Semibold, text-xs, màu Zinc-700.

## 🧱 Components & Style (Thành phần & Phong cách)

### Chiều sâu & Hiệu ứng (Depth & Effects)
- **Glassmorphism:** Sử dụng `backdrop-blur-xl` cho các lớp phủ (overlays).
- **Shadows:** 
  - Trạng thái thường: `shadow-sm`
  - Trạng thái tương tác (Hover/Focus): `shadow-md`
- **Background Blobs:** Sử dụng các phần tử mờ `#e0e7ff` (Indigo-100) ở nền để tạo chiều sâu mà không gây rối mắt.

### Ô nhập liệu (Inputs)
- **Radius:** `16px` (`rounded-2xl`) để tạo cảm giác thân thiện, hiện đại.
- **Focus State:** Sử dụng `ring-2 ring-indigo-500/20`, viền chuyển sang màu `indigo-400`.

### Thẻ (Badges/Pills)
- **Shape:** Dạng viên thuốc (`rounded-full`).
- **Background:** `bg-zinc-100` với hiệu ứng scale nhẹ khi hover.

---

*Tài liệu này là quy chuẩn bắt buộc cho mọi thay đổi về UI trong dự án AI-Chatbot-SQL-Query.*
