# Sinh báo cáo HTML

## Cách nhanh: nhờ Claude Code

Mô tả báo cáo bằng ngôn ngữ tự nhiên, ví dụ:

> Làm báo cáo doanh thu tháng 8/2026 so với tháng 7, lấy từ API đơn hàng, chia theo khu vực và kênh bán.

Claude sẽ dùng skill `fetch-business-data` để lấy dữ liệu và `business-report-html` để dựng file. Nếu loại báo cáo có template trong `templates/reports/<id>.md` thì báo cáo theo đúng template đó (xem [report-templates.md](report-templates.md)); nếu không thì dùng giao diện mặc định. Kết quả nằm trong `output/<report-id>/` (gitignore):

- `<id>_<from>_<to>.values.json` (có template) hoặc `<id>_<from>_<to>.json` (mặc định) — dữ liệu đã tổng hợp, sửa tay rồi build lại được
- `<id>_<from>_<to>.html` — báo cáo tự chứa, mở offline, gửi email được

## Build lại

```bash
# có template .md
uv run .claude/skills/business-report-html/scripts/build_report.py \
  --md templates/reports/<id>.md --values output/<id>/<id>_<from>_<to>.values.json --out output/<id>/<id>_<from>_<to>.html

# giao diện mặc định
python3 .claude/skills/business-report-html/scripts/build_report.py \
  --data output/<id>/<id>_<from>_<to>.json --out output/<id>/<id>_<from>_<to>.html

# chỉ kiểm tra một file HTML đã có
python3 .claude/skills/business-report-html/scripts/build_report.py --check output/<id>/<file>.html
```

Schema JSON: `.claude/skills/business-report-html/references/data-schema.md`. Ví dụ: `.claude/skills/business-report-html/examples/doanh-thu-mau.json`.

## Xem / in báo cáo

- Mở file `.html` bằng trình duyệt; nút "Đổi giao diện sáng/tối" ở góc phải; bấm tiêu đề cột để sắp xếp bảng.
- In PDF: Ctrl+P → khổ A4, hoặc
  ```bash
  google-chrome --headless=new --no-sandbox --no-pdf-header-footer \
    --print-to-pdf=output/<id>/<file>.pdf file://$PWD/output/<id>/<file>.html
  ```

## Đổi giao diện

Màu và kiểu chữ là biến CSS trong `.claude/skills/business-report-html/assets/report-template.html` (`--accent`, `--c1…--c6`, khối light và dark). Mọi báo cáo dùng chung template này.
