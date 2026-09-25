---
name: business-report-html
description: Sinh báo cáo số liệu kinh doanh dạng file HTML đẹp, tự chứa (mở offline, light/dark, in PDF) theo design system chung của repo. Dùng khi người dùng yêu cầu tạo/cập nhật báo cáo, dashboard tĩnh, tổng hợp KPI, doanh thu, đơn hàng, vận hành... thành file HTML, hoặc hỏi "làm báo cáo", "xuất report", "report html".
---

# Báo cáo kinh doanh HTML

Mọi báo cáo HTML dùng chung **một design system** (`assets/report-template.html`: header, thẻ KPI, biểu đồ Chart.js, bảng, callout, light/dark, in A4). Nội dung đến từ một trong hai nguồn:

1. **Template Markdown của loại báo cáo** — `templates/reports/<report-id>.md`, do người dùng cung cấp. **Ưu tiên nếu có.** Template quyết định cấu trúc, thứ tự, câu chữ; bạn chỉ tính số liệu và điền giá trị.
2. **Template mặc định (JSON section)** — dự phòng khi loại báo cáo chưa có template `.md`.

## Quy trình

1. **Xác định loại báo cáo** và kiểm tra `templates/reports/` (`ls templates/reports/`). Có template khớp → đọc toàn bộ file đó trước khi làm gì khác. Chỉ hỏi người dùng khi thiếu thật sự: kỳ báo cáo, kỳ so sánh, nguồn dữ liệu.
2. **Lấy dữ liệu** — cần gọi API hoặc đọc file thì dùng skill `fetch-business-data`. Không in token.
3. **Tính toán bằng code**, không tính nhẩm (script Python / `uv run --with pandas`); đối chiếu tổng nhóm với KPI tổng. Công thức KPI lấy theo ghi chú trong `second-brain/30-resources/kpi/` nếu có (vd cách tính tỷ lệ hoàn); chưa có định nghĩa thì nêu công thức đã dùng khi báo lại.
4. **Build**
   - *Có template `.md`*: viết file giá trị `output/<id>/<id>_<from>_<to>.values.json` chứa **số thô** (chưa định dạng) cho mọi `{{ biến }}` trong template, rồi:
     ```bash
     uv run .claude/skills/business-report-html/scripts/build_report.py \
       --md templates/reports/<id>.md --values output/<id>/<id>_<from>_<to>.values.json \
       --out output/<id>/<id>_<from>_<to>.html
     ```
     Thiếu biến → script dừng và nêu tên biến. **Không sửa template của người dùng** để lách lỗi; bổ sung giá trị, hoặc hỏi người dùng nếu template cần đổi. Template dùng cú pháp chỗ điền khác (`[Doanh thu]`, `<<x>>`…) → hỏi trước khi chuyển sang `{{ }}`. Cú pháp template: `references/markdown-template.md`.
   - *Không có template*: viết JSON section theo `references/data-schema.md` (ví dụ `examples/doanh-thu-mau.json`) → `output/<id>/<id>_<from>_<to>.json`, rồi:
     ```bash
     python3 .claude/skills/business-report-html/scripts/build_report.py \
       --data output/<id>/<id>_<from>_<to>.json --out output/<id>/<id>_<from>_<to>.html
     ```
     Nếu loại báo cáo này sẽ lặp lại, đề xuất người dùng tạo template `.md` cho nó.
   Script validate, nhúng Chart.js inline và từ chối nếu file còn tài nguyên ngoài.
5. **Kiểm tra trực quan** (nên làm với báo cáo mới): chụp ảnh headless rồi đọc ảnh
   ```bash
   google-chrome --headless=new --no-sandbox --hide-scrollbars --window-size=1200,2400 \
     --screenshot=/tmp/report.png file://$PWD/output/<id>/<file>.html
   ```
   Thêm `--window-size=360,3200` để kiểm tra mobile, `--blink-settings=preferredColorScheme=0` cho dark mode.
6. Báo lại cho người dùng: đường dẫn file, template đã dùng, kỳ báo cáo, nguồn dữ liệu, các giả định/chỗ số liệu thiếu.

## Nguyên tắc trình bày

Áp dụng cho template mặc định; với template `.md` thì template của người dùng quyết định, chỉ áp dụng phần định dạng số.

- **Thứ tự**: KPI chính → xu hướng theo thời gian → phân rã (khu vực/kênh/sản phẩm) → bảng chi tiết → nhận định & đề xuất.
- **Tối đa 4–6 KPI** ở phần đầu; mỗi KPI nên có `previous` để hiện tăng/giảm. Chỉ số "càng thấp càng tốt" (chi phí, tỷ lệ hoàn, thời gian giao) đặt `"invert": true`.
- **Chọn biểu đồ**:
  - Theo thời gian → `line` (kỳ so sánh đặt `"dashed": true`), khối lượng tích luỹ → `area`.
  - So sánh giữa nhóm → `bar`; tên nhóm dài hoặc > 8 nhóm → `"horizontal": true`; cấu thành → `"stacked": true`.
  - Tỷ trọng ≤ 5 phần → `doughnut`; nhiều hơn thì dùng `bar` ngang, gộp phần nhỏ thành "Khác".
  - Không quá 6 series trên một biểu đồ.
- **Tiền lớn** dùng `"compact": true` ở KPI/biểu đồ (12,85 tỷ ₫); bảng chi tiết để số đầy đủ.
- **Tỷ lệ** truyền dạng thập phân (0.042 → 4,2%); tăng trưởng trong bảng dùng format `delta`.
- **Nhận định** (`text`) viết ngắn, có số cụ thể, nêu nguyên nhân chính và việc cần làm; `tone`: `good` / `warn` / `bad` hoặc bỏ trống.
- Ghi rõ nguồn trong `meta.sources`, đơn vị trong `description` của section khi không hiển nhiên.
- Không bịa số: thiếu dữ liệu thì để section trống (hiện "Không có dữ liệu trong kỳ") và nói rõ trong nhận định.

## Khi cần tuỳ biến

- Đổi màu thương hiệu: sửa biến CSS `--accent`, `--c1…--c6` trong template (cả khối light và dark). Giữ tương phản đủ ở cả hai chế độ.
- Cần loại component mới: thêm hàm `renderXxx` trong template HTML, thêm type vào `SECTION_TYPES` (và `COMPONENT_FENCES` nếu dùng trong `.md`) của `scripts/build_report.py`, cập nhật `references/data-schema.md` và `references/markdown-template.md`. Không tạo template HTML thứ hai — khác biệt giữa các loại báo cáo nằm trong template `.md`.
- Khi pipeline `reportkit` (xem `openspec/changes/`) đã có, ưu tiên `uv run reportkit build <id>`; template Jinja của pipeline dùng cùng design system này.
