# Proposal

## Why

Báo cáo số liệu kinh doanh (doanh thu, đơn hàng, KPI vận hành) hiện chưa có quy trình chung: mỗi lần cần báo cáo phải tự lấy dữ liệu, tự tính toán và tự dàn trang, nên kết quả không nhất quán và khó lặp lại. Repo `fw-bu` đang trống, nên đây là lúc dựng một nền tảng sinh báo cáo HTML thống nhất để người dùng (và Claude Code) có thể sinh báo cáo đẹp, đúng số liệu, lặp lại được theo kỳ.

## What Changes

- Dựng project Python (quản lý bằng `uv`) với package `reportkit` trong `src/`, kèm pytest và ruff.
- Thêm cơ chế **định nghĩa báo cáo** bằng file khai báo (`reports/<tên>/report.yaml`): nguồn dữ liệu, tham số kỳ báo cáo, KPI, bảng và biểu đồ.
- Thêm lớp **nguồn dữ liệu** có thể mở rộng: REST API (xác thực bằng key trong `.env`), CSV/Excel, có cache dữ liệu thô để chạy lại không phải gọi API.
- Thêm bộ **render HTML** tạo một file duy nhất, tự chứa (CSS, dữ liệu, thư viện biểu đồ đều nhúng inline), mở được offline, hỗ trợ light/dark và in ra PDF.
- Thêm **CLI** `reportkit` để liệt kê, kiểm tra và build báo cáo theo kỳ.
- Thêm skill Claude Code để sinh báo cáo HTML đẹp theo design system chung, và tài liệu cài đặt/sử dụng trong `instruction/`.

## Capabilities

### New Capabilities
- `report-definition`: Khai báo một báo cáo (metadata, tham số kỳ, nguồn dữ liệu, KPI, bảng, biểu đồ) và kiểm tra tính hợp lệ của khai báo.
- `data-sources`: Lấy dữ liệu từ REST API và file CSV/Excel theo khai báo, quản lý thông tin xác thực và cache dữ liệu thô.
- `report-rendering`: Sinh file HTML tự chứa từ dữ liệu đã xử lý theo design system chung (định dạng số vi-VN, VND, light/dark, in ấn).
- `report-cli`: Giao diện dòng lệnh để liệt kê, validate và build báo cáo cho một kỳ cụ thể.

### Modified Capabilities
<!-- Không có: repo chưa có spec nào. -->

## Non-goals

- Không xây web server/dashboard realtime; đầu ra là file HTML tĩnh.
- Không lập lịch chạy tự động (cron/CI) trong change này.
- Không kết nối trực tiếp cơ sở dữ liệu SQL; có thể bổ sung connector sau.
- Không tích hợp một API cụ thể nào; connector REST là loại chung, API thật được khai báo khi có nhu cầu.

## Impact

- Code mới: `src/reportkit/`, `reports/`, `templates/`, `tests/`, `pyproject.toml`.
- Phụ thuộc mới: pandas, Jinja2, httpx, pydantic, PyYAML, python-dotenv, openpyxl; dev: pytest, ruff. Chart.js được vendor vào repo để nhúng inline.
- Secrets: API key đọc từ `.env` (có `.env.example`), `.env` và `output/`, `data/cache/` được gitignore.
- Tài liệu: `instruction/` và `CLAUDE.md`.
