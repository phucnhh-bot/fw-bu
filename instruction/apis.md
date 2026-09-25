# API dữ liệu

Ghi lại mỗi API đã dùng để lần sau Claude (và người) gọi lại đúng cách. Token đặt trong `.env`, chỉ ghi **tên biến** ở đây.

## Mẫu khai báo

```markdown
### <Tên API>
- Base URL: https://...
- Xác thực: header `Authorization: Bearer ${TEN_BIEN_TOKEN}`
- Endpoint: `GET /v1/...` — mô tả dữ liệu trả về
- Tham số kỳ: `from`, `to` (YYYY-MM-DD) | múi giờ
- Phân trang: `page`/`limit` hoặc cursor `meta.next_cursor`
- records-path: `data.items`
- Trường chính: id, created_at, amount (VND), region, channel...
- Lệnh mẫu: python3 .claude/skills/fetch-business-data/scripts/fetch_api.py ...
- Lưu ý: giới hạn rate, độ trễ dữ liệu, ...
```

## Danh sách

_Chưa có API nào. Thêm mục mới theo mẫu trên._
