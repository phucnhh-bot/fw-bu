# Design

## Context

Repo đang trống (xem proposal.md – Why). Máy dev đã có Python 3.12, `uv`, Node 24 (chỉ dùng cho OpenSpec). Báo cáo sẽ được sinh chủ yếu qua Claude Code: người dùng mô tả báo cáo, Claude tạo/sửa khai báo và chạy CLI. Vì vậy khai báo phải dễ đọc/sửa bởi cả người và AI, và bộ render phải cho kết quả đẹp mà không cần chỉnh CSS mỗi lần.

## Goals / Non-Goals

**Goals:**
- Một pipeline rõ ràng: khai báo → lấy dữ liệu → biến đổi → render → một file HTML.
- Thêm nguồn dữ liệu/loại section mới mà không sửa lõi pipeline.
- Chạy lại được, kiểm thử được mà không cần gọi API thật (cache + fixture).

**Non-Goals:**
- Không có ngôn ngữ biểu thức riêng cho transform; logic phức tạp viết bằng Python.
- Không tối ưu cho dataset lớn (> vài trăm nghìn dòng); báo cáo dùng dữ liệu đã tổng hợp.

## Decisions

### 1. Python + uv, package `reportkit` dạng src-layout
Python có hệ sinh thái xử lý dữ liệu tốt nhất (pandas, openpyxl) và dễ cho người làm số liệu đọc. `uv` cho cài đặt nhanh, lock file tái lập được.
*Phương án khác:* Node/TypeScript (thống nhất với OpenSpec) — bị loại vì xử lý bảng/Excel kém tiện hơn.

### 2. Cấu trúc thư mục
```
src/reportkit/
  cli.py            # lệnh list/validate/build/new (Typer)
  config.py         # model pydantic cho report.yaml, nạp & validate
  period.py         # tính kỳ mặc định, kỳ so sánh, múi giờ VN
  sources/          # registry connector: base.py, http.py, file.py
  cache.py          # cache dữ liệu thô: data/cache/<report>/<source>/<from>_<to>.json|parquet
  pipeline.py       # điều phối: fetch → transform → build context → render
  render/
    formatters.py   # định dạng số vi-VN, VND, %, ngày
    sections/       # registry section: kpis, chart, table, text
    engine.py       # Jinja2 + inline CSS/JS
templates/
  base.html.j2      # khung báo cáo theo design system
  sections/*.html.j2
  assets/report.css # design tokens (light/dark, print)
  vendor/chart.umd.min.js  # Chart.js vendor, nhúng inline khi render
reports/<id>/report.yaml (+ transforms.py tùy chọn)
output/  data/cache/  data/input/   # gitignore (trừ data/input/.gitkeep)
tests/ (fixtures/, test_*.py)
instruction/        # tài liệu cài đặt/sử dụng
```

### 3. Registry cho connector và section
Mỗi connector là class có `type` và `fetch(spec, period) -> DataFrame`; mỗi section có `type`, model pydantic cho cấu hình và template riêng. Đăng ký qua dict registry (không dùng plugin entry-points) — đủ đơn giản cho một repo.
*Phương án khác:* một hàm lớn `if type == ...` — khó mở rộng, bị loại.

### 4. Transform bằng Python, tham chiếu từ YAML
`report.yaml` khai báo `transforms: [{name: doanh-thu-theo-ngay, fn: revenue_by_day}]`; hàm nằm trong `reports/<id>/transforms.py` với chữ ký `fn(datasets: dict[str, DataFrame], period: Period) -> DataFrame`. KPI đơn giản khai báo trực tiếp (`dataset`, `column`, `agg: sum|mean|count|last`, `format`).
*Phương án khác:* DSL biến đổi trong YAML — tốn công, kém linh hoạt; SQL qua DuckDB — cân nhắc sau nếu dữ liệu lớn.

### 5. So sánh kỳ
Khi KPI có `compare: previous_period|same_period_last_year`, pipeline tính kỳ so sánh bằng `period.py` và chạy lại fetch + transform cho kỳ đó (hưởng cache). Không cần API hỗ trợ so sánh riêng.

### 6. Render: Jinja2 + CSS tokens + Chart.js inline
Template dùng design tokens (biến CSS trên `:root`, override cho `prefers-color-scheme: dark`, `@media print`). Chart.js được vendor vào repo và nhúng inline để file chạy offline; dữ liệu biểu đồ nhúng dạng `<script type="application/json">`. Cùng design system này được mô tả trong skill `business-report-html` để báo cáo Claude sinh tay (không qua CLI) trông giống báo cáo sinh bằng pipeline.
*Phương án khác:* ECharts (mạnh hơn nhưng ~1MB), Plotly (~3MB) — nặng cho file gửi email; có thể thêm sau như loại chart khác.

### 7. Secret và cấu hình
`python-dotenv` nạp `.env`; chuỗi `${VAR}` trong YAML được thay khi chạy. Logger có bộ lọc che giá trị của mọi biến đã thay. Cache chỉ lưu body response, không lưu header request.

### 8. Kiểm thử
pytest với `httpx.MockTransport` cho API, fixture CSV nhỏ trong `tests/fixtures/`, và test render bằng cách parse HTML đầu ra (kiểm tra không có `<script src=` / `<link href=http`, định dạng số, trạng thái rỗng). Một báo cáo mẫu `reports/mau-doanh-thu/` chạy hoàn toàn trên dữ liệu CSV mẫu để làm smoke test và ví dụ.

## Risks / Trade-offs

- [API nội bộ chưa biết định dạng] → connector `http` tổng quát (records_path, phân trang page/cursor); API đặc thù có thể viết connector riêng dựa trên base class.
- [File HTML nặng khi nhúng dữ liệu lớn] → chỉ nhúng dữ liệu đã tổng hợp; cảnh báo khi file > 5MB.
- [Cache cũ gây số liệu sai] → cache theo kỳ; kỳ chứa ngày hôm nay luôn bỏ qua cache; `--refresh` để ép làm mới.
- [transforms.py là code tùy ý] → chỉ nạp từ thư mục `reports/` trong repo, review như code thường.

## Migration Plan

Repo mới, không có migration. Rollback = revert commit.
