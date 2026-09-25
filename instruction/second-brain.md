# Second brain (Obsidian)

Thư mục `second-brain/` là một vault Obsidian: mọi ghi chú là file `.md` thường, nằm trong repo nên được version bằng git và Claude Code đọc được.

## Cài Obsidian (Ubuntu)

```bash
sudo snap install obsidian --classic
# hoặc tải .deb / AppImage tại https://obsidian.md/download
```

## Mở vault

Obsidian → **Open folder as vault** → chọn `<repo>/second-brain`.

Cấu hình đã có sẵn trong `second-brain/.obsidian/`:
- Ghi chú mới vào `00-inbox/`, file đính kèm vào `_attachments/`.
- Daily note: thư mục `daily/`, tên `YYYY-MM-DD`, template `_templates/daily`.
- Templates: thư mục `_templates/`.

Vào **Settings → Core plugins**, bật **Daily notes** và **Templates** nếu chưa bật. Chèn template bằng lệnh *Templates: Insert template*.

## Cấu trúc (PARA)

Xem `second-brain/README.md`. Tóm tắt: `00-inbox` → phân loại dần vào `10-projects` (có hạn), `20-areas` (lâu dài), `30-resources` (tham khảo), `40-archive` (đã xong).

## Dùng cùng Claude Code

- Định nghĩa KPI đặt ở `second-brain/30-resources/kpi/` (template `_templates/kpi`). Khi làm báo cáo, Claude đọc các ghi chú này để tính đúng công thức.
- Có thể nhờ Claude: "ghi chú cuộc họp này vào second brain", "tóm tắt các ghi chú tuần này", "tạo ghi chú KPI cho tỷ lệ giao thành công".
- Không lưu token/mật khẩu trong vault (vault được commit lên git). Dữ liệu nhạy cảm của khách hàng cũng không để ở đây.

## Git

`.gitignore` đã bỏ qua trạng thái cá nhân của Obsidian (`workspace*.json`, cache, `.trash/`); cấu hình chung trong `.obsidian/` vẫn được commit để mọi người dùng giống nhau.
