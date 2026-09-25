---
name: fetch-business-data
description: Lấy số liệu kinh doanh từ REST API (có token), CSV hoặc Excel để làm báo cáo — gọi API có phân trang, lưu cache dữ liệu thô, giữ bí mật token, rồi tổng hợp bằng pandas. Dùng khi báo cáo cần dữ liệu từ API/file, hoặc người dùng nói "lấy dữ liệu", "gọi API", "đọc file excel".
---

# Lấy dữ liệu kinh doanh

## Quy tắc bắt buộc

- **Secret chỉ nằm trong `.env`** (đã gitignore). Tham chiếu dạng `${TEN_BIEN}`; không bao giờ `cat .env`, `echo $TOKEN`, hay dán token vào lệnh/tệp/đầu ra. Thiếu biến → nhờ người dùng thêm vào `.env` (mẫu: `.env.example`), không tự bịa.
- **Dữ liệu thô lưu cache** tại `data/cache/<report-id>/<nguồn>/<from>_<to>.json`. Kỳ đã kết thúc thì dùng lại cache; kỳ chứa hôm nay thì gọi lại (`--refresh`).
- **Không sửa dữ liệu thô**; mọi làm sạch/tổng hợp làm trong script và có thể chạy lại.
- API mới hoặc chưa rõ: gọi thử 1 trang nhỏ, xem cấu trúc response (in vài bản ghi đầu, không in header) rồi mới lấy toàn bộ. Ghi lại cấu hình API vào `instruction/apis.md` để lần sau dùng lại.

## Gọi REST API

```bash
python3 .claude/skills/fetch-business-data/scripts/fetch_api.py \
  --url "https://api.example.com/v1/orders" \
  --header 'Authorization: Bearer ${ORDERS_API_TOKEN}' \
  --param from=2026-08-01 --param to=2026-08-31 \
  --records-path data.items --page-param page --page-size-param limit --page-size 500 \
  --out data/cache/doanh-thu-thang/orders/2026-08-01_2026-08-31.json
```

- Dùng **nháy đơn** quanh `${...}` để shell không tự thay biến; script tự đọc `.env`.
- Phân trang theo cursor: `--cursor-path meta.next_cursor --cursor-param cursor`.
- POST: `--method POST --json '{"from":"2026-08-01","to":"2026-08-31"}'`.
- Tự retry với 5xx/429, dừng và báo lỗi (đã che secret) với 4xx.
- Chạy `--help` để xem đủ tuỳ chọn. Danh sách API đã biết: `instruction/apis.md`.

## Đọc CSV / Excel và tổng hợp

Dùng pandas qua uv (không cần cài vào hệ thống):

```bash
uv run --with pandas --with openpyxl python - <<'EOF'
import pandas as pd, json
df = pd.read_json("data/cache/doanh-thu-thang/orders/2026-08-01_2026-08-31.json")
# df = pd.read_excel("data/input/kpi.xlsx", sheet_name="T8")   # Excel
# df = pd.read_csv("data/input/orders.csv")                     # CSV UTF-8
df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_convert("Asia/Ho_Chi_Minh")
by_region = df.groupby("region").agg(orders=("id", "count"), revenue=("amount", "sum")).reset_index()
print(by_region.to_string())
print("TỔNG", by_region[["orders", "revenue"]].sum().to_dict())
EOF
```

## Kiểm tra trước khi đưa vào báo cáo

- Số bản ghi hợp lý (so với kỳ trước), không trùng id, không có ngày ngoài kỳ.
- Tổng các nhóm = tổng KPI; đơn vị tiền (VND hay nghìn VND) thống nhất.
- Giá trị null/âm bất thường → nêu trong nhận định của báo cáo, không lặng lẽ bỏ.
- Múi giờ: quy đổi về `Asia/Ho_Chi_Minh` trước khi group theo ngày.

Sau khi có số liệu, chuyển sang skill `business-report-html` để dựng file HTML.
