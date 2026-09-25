# Second brain

Vault Obsidian lưu kiến thức, ghi chú và bối cảnh công việc (định nghĩa KPI, ghi chú họp, ý tưởng báo cáo…). Cấu trúc theo PARA.

| Thư mục | Dùng cho |
|---|---|
| `00-inbox/` | Ghi nhanh, chưa phân loại (ghi chú mới mặc định vào đây) |
| `10-projects/` | Việc có mục tiêu và hạn chót (vd một báo cáo đang làm) |
| `20-areas/` | Mảng trách nhiệm lâu dài (vd kinh doanh miền Nam, vận hành kho) |
| `30-resources/` | Tài liệu tham khảo: `kpi/` định nghĩa KPI, `apis/` ghi chú API, … |
| `40-archive/` | Thứ đã xong hoặc không còn dùng |
| `daily/` | Ghi chú hằng ngày `YYYY-MM-DD.md` |
| `_templates/` | Template ghi chú: daily, note, meeting, kpi, project |
| `_attachments/` | Ảnh, file đính kèm |

Liên kết giữa các ghi chú bằng `[[Tên ghi chú]]`; gắn thẻ trong frontmatter `tags: [...]`.

Cách mở vault, bật plugin và dùng cùng Claude: `instruction/second-brain.md`.
