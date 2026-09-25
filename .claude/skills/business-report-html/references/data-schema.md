# Schema dữ liệu báo cáo (JSON)

```jsonc
{
  "meta": {
    "title": "Báo cáo doanh thu tháng 8/2026",   // bắt buộc
    "eyebrow": "Báo cáo kinh doanh",              // dòng nhỏ phía trên tiêu đề
    "subtitle": "Mô tả ngắn phạm vi báo cáo",
    "period": { "from": "2026-08-01", "to": "2026-08-31" },  // ISO, hiển thị dd/mm/yyyy
    "compare_label": "so với T7/2026",            // nhãn mặc định cho delta KPI
    "owner": "Phòng Kinh doanh",
    "generated_at": "2026-09-25T09:00:00+07:00",  // ISO có múi giờ
    "sources": ["API đơn hàng", "kpi.xlsx"]
  },
  "sections": [ /* các section, render theo thứ tự */ ]
}
```

Mọi section có thể có: `title`, `description` (dòng phụ dưới tiêu đề), `note` (chú thích nhỏ phía dưới).

## `format` dùng chung

| format     | ví dụ giá trị | hiển thị            |
|------------|---------------|---------------------|
| `number` (mặc định) | 184230 | 184.230          |
| `currency` | 12845000000   | 12.845.000.000 ₫ (hoặc 12,85 tỷ ₫ với `compact: true`) |
| `percent`  | 0.042         | 4,2%                |
| `delta`    | 0.096         | +9,6%               |
| `decimal`  | 3.14159       | 3,14                |
| `text`     | "Miền Bắc"    | giữ nguyên          |

`compact: true` rút gọn thành nghìn / triệu / tỷ.

## `kpis`

```json
{ "type": "kpis", "title": "Chỉ số chính", "items": [
  { "label": "Doanh thu", "value": 12845000000, "previous": 11720000000, "format": "currency", "compact": true },
  { "label": "Tỷ lệ hoàn hàng", "value": 0.042, "previous": 0.047, "format": "percent", "invert": true,
    "compare_label": "so với cùng kỳ", "note": "Tính trên đơn đã giao" }
]}
```
- `previous` (tuỳ chọn) → hiện ▲/▼ và %; với `percent` hiện chênh lệch điểm %.
- `invert: true` khi giảm là tốt (màu xanh khi giảm).

## `chart`

```json
{ "type": "chart", "title": "Doanh thu theo tuần", "chart": "line", "format": "currency", "compact": true,
  "labels": ["Tuần 1", "Tuần 2"],
  "series": [ { "name": "T8/2026", "data": [2810000000, 3050000000] },
              { "name": "T7/2026", "data": [2650000000, 2780000000], "dashed": true } ] }
```
- `chart`: `line` | `area` | `bar` | `pie` | `doughnut`
- `bar`: thêm `"horizontal": true`, `"stacked": true` khi cần.
- Số phần tử mỗi `series[].data` phải bằng số `labels`. `pie`/`doughnut` chỉ dùng 1 series.

## `table`

```json
{ "type": "table", "title": "Chi tiết theo khu vực",
  "columns": [ { "key": "region", "label": "Khu vực" },
               { "key": "revenue", "label": "Doanh thu", "format": "currency" } ],
  "rows":    [ { "region": "Miền Bắc", "revenue": 4960000000 } ],
  "totals":  { "region": "Tổng", "revenue": 12845000000 } }
```
- Cột có `format` (khác `text`) được căn phải. Bấm tiêu đề cột để sắp xếp.
- Mỗi row phải có đủ mọi `key` của `columns` (giá trị `null` hiển thị "—").

## `text`

```json
{ "type": "text", "title": "Nhận định", "tone": "warn",
  "paragraphs": ["Doanh thu tăng 9,6%..."], "bullets": ["Việc cần làm 1", "Việc cần làm 2"] }
```
- `tone`: `good` | `warn` | `bad` | bỏ trống. Nội dung là text thuần (không HTML).
