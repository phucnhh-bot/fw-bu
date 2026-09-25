# Lên plan bằng OpenSpec

Mỗi yêu cầu thay đổi đáng kể (tính năng mới, báo cáo mới có logic phức tạp, nguồn dữ liệu mới) nên đi qua OpenSpec trước khi code, để plan được review và lưu lại trong repo.

## Vòng đời một change

| Bước | Lệnh trong Claude Code | Kết quả |
|------|------------------------|---------|
| Suy nghĩ / làm rõ | `/opsx:explore <ý tưởng>` | Thảo luận, không sửa file |
| Lên plan | `/opsx:propose <mô tả>` | `openspec/changes/<tên>/` gồm `proposal.md`, `specs/**/spec.md`, `design.md`, `tasks.md` |
| Sửa plan | `/opsx:update <tên>` | Cập nhật các artifact cho nhất quán |
| Triển khai | `/opsx:apply <tên>` | Code theo `tasks.md`, tick từng task |
| Đồng bộ spec | `/opsx:sync <tên>` | Gộp delta spec vào `openspec/specs/` |
| Kết thúc | `/opsx:archive <tên>` | Chuyển change vào `openspec/changes/archive/` |

`/opsx:propose` chỉ tạo plan, không code; chỉ triển khai khi chạy `/opsx:apply`.

## CLI hữu ích

```bash
openspec list                         # các change đang mở
openspec list --specs                 # các capability đã có spec
openspec show <change>                # xem một change
openspec status --change <change>     # tiến độ artifact
openspec validate <change> --strict   # kiểm tra định dạng
```

## Cấu hình dự án

`openspec/config.yaml` chứa `context` (domain, tech stack, quy ước) và `rules` cho từng artifact (proposal tiếng Việt, luôn có Non-goals; task ≤ 2 giờ; task thêm công cụ phải cập nhật `instruction/`). Sửa file này khi quy ước dự án thay đổi.

## Change hiện có

- `setup-report-platform` — thiết kế nền tảng sinh báo cáo (`reportkit`: khai báo YAML → nguồn dữ liệu → render HTML → CLI). Chạy `/opsx:apply setup-report-platform` để bắt đầu triển khai.
