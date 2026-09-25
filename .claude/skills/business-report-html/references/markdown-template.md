# Cú pháp template Markdown (`templates/reports/<report-id>.md`)

Mỗi loại báo cáo một file. Build: `uv run scripts/build_report.py --md <template> --values <values.json> --out <file>.html`.

Thứ tự xử lý: **Jinja2** (điền giá trị từ `values.json`) → tách **frontmatter** → **Markdown** + các **khối component** → HTML theo design system chung.

## 1. Frontmatter (tuỳ chọn) → phần đầu báo cáo

```yaml
---
eyebrow: Báo cáo kinh doanh
subtitle: Mô tả ngắn
owner: Phòng Kinh doanh
period: { from: "{{ period.from }}", to: "{{ period.to }}" }   # hiển thị dd/mm/yyyy
compare_label: so với {{ previous_label }}                      # nhãn delta mặc định của KPI
sources: {{ sources | tojson }}
title: ...            # nếu bỏ trống, dùng dòng "# ..." đầu tiên của file
---
```
`generated_at` tự điền giờ Việt Nam lúc build.

## 2. Chỗ điền giá trị (Jinja2)

- `{{ ten_bien }}` — giá trị lấy từ `values.json`. Thiếu biến → build báo lỗi (không bao giờ in rỗng).
- Bộ lọc định dạng vi-VN:

| Bộ lọc | Ví dụ | Kết quả |
|---|---|---|
| `number` | `{{ 184230 \| number }}` | 184.230 |
| `number(1)` | `{{ 3.14159 \| number(1) }}` | 3,1 |
| `number(compact=true)` | `{{ 2500000 \| number(compact=true) }}` | 2,5 triệu |
| `currency` | `{{ 12845000000 \| currency }}` | 12.845.000.000 ₫ |
| `currency(true)` | `{{ 12845000000 \| currency(true) }}` | 12,85 tỷ ₫ |
| `percent` | `{{ 0.042 \| percent }}` | 4,2% |
| `delta` | `{{ 0.096 \| delta }}` | +9,6% |
| `pp` | `{{ -0.005 \| pp }}` | -0,5 điểm % |
| `date` | `{{ "2026-08-31" \| date }}` | 31/08/2026 |
| `tojson` | `{{ list \| tojson }}` | dùng trong khối component |

- Điều khiển: `{% for r in regions %}…{% endfor %}`, `{% if … %}…{% endif %}`, biểu thức `{{ (a - b) / b | delta }}` (bọc ngoặc trước khi lọc).
- `values.json` chứa **số thô** (0.042, không phải "4,2%"); định dạng để template lo.

## 3. Markdown

CommonMark + bảng GFM. Heading `##`, `###`, đoạn văn, **đậm**, danh sách, link, `---`.
- Bảng: cột số dùng căn phải `---:`. Bảng tự nằm trong card, cuộn ngang trên mobile.
- Callout: `> [!good] …`, `> [!warn] …`, `> [!bad] …`, `> [!note] …`.
- HTML thô trong template **không** được render (bị escape).

## 4. Khối component (fenced code, nội dung YAML/JSON)

Các trường giống `data-schema.md` (bỏ `type`). Heading `##`/`###` đứng ngay trên khối sẽ thành tiêu đề của component.

````markdown
## Chỉ số chính
```kpis
- { label: Doanh thu, value: {{ revenue }}, previous: {{ revenue_prev }}, format: currency, compact: true }
- { label: Tỷ lệ hoàn hàng, value: {{ return_rate }}, previous: {{ return_rate_prev }}, format: percent, invert: true }
```

## Doanh thu theo tuần
```chart
chart: line            # line | area | bar | pie | doughnut
format: currency
compact: true
labels: {{ weekly.labels | tojson }}
series:
  - { name: T8/2026, data: {{ weekly.current | tojson }} }
  - { name: T7/2026, data: {{ weekly.previous | tojson }}, dashed: true }
```

```table
columns: [ { key: region, label: Khu vực }, { key: revenue, label: Doanh thu, format: currency } ]
rows: {{ regions | tojson }}
totals: { region: Tổng, revenue: {{ revenue }} }
```
````

Khối `table` (khác bảng Markdown) có sắp xếp theo cột và tự định dạng số — dùng khi bảng lấy thẳng từ dữ liệu. Khối code với ngôn ngữ khác (` ```sql `…) hiển thị như code bình thường.

Ví dụ đầy đủ: `templates/reports/mau-doanh-thu.md` + `examples/mau-doanh-thu.values.json`.
