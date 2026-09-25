# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Mục đích repo

Sinh báo cáo số liệu kinh doanh (doanh thu, đơn hàng, KPI vận hành) thành **file HTML tự chứa** — mở offline, light/dark, in PDF A4. Dữ liệu lấy từ REST API (token trong `.env`) hoặc CSV/Excel. Báo cáo mặc định tiếng Việt, số theo vi-VN, tiền VND, múi giờ `Asia/Ho_Chi_Minh`. Trả lời người dùng bằng tiếng Việt.

## Trạng thái hiện tại

- Chưa có code ứng dụng. Pipeline `reportkit` (Python + uv) mới ở dạng plan: `openspec/changes/setup-report-platform/` (proposal, specs, design, tasks). Triển khai bằng `/opsx:apply setup-report-platform`; khi đó cập nhật lại mục lệnh bên dưới.
- Báo cáo hiện được sinh qua hai skill trong `.claude/skills/`:
  - `fetch-business-data` → gọi API (`scripts/fetch_api.py`: phân trang, retry, cache, che secret) và tổng hợp bằng pandas.
  - `business-report-html` → một design system duy nhất `assets/report-template.html` tự render từ một khối JSON (`<script id="report-data">`); `scripts/build_report.py` validate, nhúng Chart.js (vendor trong `assets/vendor/`) inline và chặn tài nguyên ngoài.
- **Template theo loại báo cáo**: `templates/reports/<report-id>.md` do người dùng cung cấp (Jinja2 `{{ biến | currency }}` + Markdown + khối ```kpis/```chart/```table). `build_report.py --md ... --values ...` render template → sections markdown/component → cùng design system. Có template thì phải dùng template; không có thì dùng JSON section mặc định. Không sửa template của người dùng để lách lỗi thiếu biến.
- **Second brain**: `second-brain/` là vault Obsidian (PARA). Định nghĩa KPI ở `second-brain/30-resources/kpi/` — đọc trước khi tính số liệu báo cáo. Chỉ ghi vào vault khi người dùng yêu cầu; ghi chú mới mặc định vào `00-inbox/`, dùng template trong `_templates/`, link dạng `[[...]]`.

## Lệnh thường dùng

```bash
# build báo cáo từ template .md (cú pháp: .claude/skills/business-report-html/references/markdown-template.md)
uv run .claude/skills/business-report-html/scripts/build_report.py --md templates/reports/<id>.md --values <values>.json --out output/<id>/<file>.html
# build báo cáo mặc định từ JSON (schema: .claude/skills/business-report-html/references/data-schema.md)
python3 .claude/skills/business-report-html/scripts/build_report.py --data <file>.json --out output/<id>/<file>.html
python3 .claude/skills/business-report-html/scripts/build_report.py --check output/<id>/<file>.html

# lấy dữ liệu API (xem --help)
python3 .claude/skills/fetch-business-data/scripts/fetch_api.py --url ... --out data/cache/<id>/<nguồn>/<from>_<to>.json

# kiểm tra trực quan (đọc ảnh chụp để tự review)
google-chrome --headless=new --no-sandbox --hide-scrollbars --window-size=1200,2400 --screenshot=/tmp/r.png file://$PWD/<file>.html

# OpenSpec
openspec list | openspec status --change <tên> | openspec validate <tên> --strict
```

## Quy ước

- **Plan trước khi code** cho thay đổi đáng kể: `/opsx:propose` (chỉ tạo plan, không code) → review → `/opsx:apply` → `/opsx:archive`. Quy tắc viết artifact nằm trong `openspec/config.yaml` (proposal tiếng Việt có Non-goals; task ≤ 2 giờ; task thêm công cụ phải cập nhật `instruction/`).
- **Mọi hướng dẫn cài đặt/sử dụng nằm trong `instruction/`**; thêm công cụ hoặc API mới thì cập nhật file tương ứng (API ghi vào `instruction/apis.md`, chỉ ghi tên biến môi trường).
- **Không tạo template HTML thứ hai**: khác biệt giữa các loại báo cáo nằm trong template `.md`; đổi giao diện qua biến CSS của template chung; thêm loại component thì sửa template HTML + `SECTION_TYPES`/`COMPONENT_FENCES` trong `build_report.py` + `data-schema.md` + `markdown-template.md` cùng lúc. Pipeline `reportkit` sau này phải dùng cùng design system.
- **Số liệu tính bằng code**, không tính nhẩm; đối chiếu tổng nhóm với KPI tổng; thiếu dữ liệu thì để section rỗng và nói rõ, không bịa.
- **Secret**: chỉ tham chiếu `${TEN_BIEN}`; không đọc/in `.env`. `output/`, `data/cache/`, `.env` đã gitignore.
