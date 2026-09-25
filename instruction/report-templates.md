# Template báo cáo (.md)

Mỗi loại báo cáo có một template Markdown trong `templates/reports/<report-id>.md`. Khi được yêu cầu làm báo cáo loại đó, Claude đọc template, lấy và tính số liệu, ghi vào file giá trị JSON, rồi build ra HTML theo giao diện chung. Loại báo cáo chưa có template thì dùng giao diện mặc định.

## Thêm template mới

1. Tạo `templates/reports/<report-id>.md` (id viết thường, gạch nối, không dấu).
2. Viết nội dung như một báo cáo Markdown bình thường; chỗ nào là số liệu thì đặt `{{ ten_bien }}` kèm bộ lọc định dạng, vd `{{ doanh_thu | currency }}`, `{{ tang_truong | delta }}`.
3. Chỗ cần thẻ KPI / biểu đồ / bảng sắp xếp được → dùng khối ```kpis, ```chart, ```table.
4. Ghi chú ở đầu file (trong comment `<!-- -->` hoặc frontmatter) nguồn dữ liệu và cách tính cho từng biến, để Claude tính đúng.

Cú pháp đầy đủ và bảng bộ lọc: `.claude/skills/business-report-html/references/markdown-template.md`. Ví dụ: `templates/reports/mau-doanh-thu.md`.

Nếu template dùng cú pháp chỗ điền khác (`[Doanh thu]`, `<<x>>`, …), Claude sẽ hỏi trước khi chuyển sang `{{ }}`.

## Build tay

```bash
uv run .claude/skills/business-report-html/scripts/build_report.py \
  --md templates/reports/<id>.md --values output/<id>/<id>_<from>_<to>.values.json \
  --out output/<id>/<id>_<from>_<to>.html
```

Lần đầu `uv run` tự cài jinja2, markdown-it-py, pyyaml vào môi trường tạm (khai báo ở đầu script). Thiếu biến trong `values.json` thì build dừng và nêu tên biến.
