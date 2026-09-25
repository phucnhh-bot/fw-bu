# Tasks

## 1. Khung project

- [ ] 1.1 Tạo `pyproject.toml` (uv, src-layout, package `reportkit`, entry point `reportkit`), thêm dependencies và dev-dependencies (pytest, ruff); verify `uv sync` thành công và `uv run reportkit --help` chạy
- [ ] 1.2 Tạo các thư mục `src/reportkit/`, `templates/`, `reports/`, `tests/`, `data/input/`, cập nhật `.gitignore` (`.env`, `output/`, `data/cache/`, `.venv/`) và `.env.example`; verify `git status` không hiện file bị ignore
- [ ] 1.3 Cấu hình ruff và pytest trong `pyproject.toml`; verify `uv run ruff check .` và `uv run pytest` chạy (0 test cũng được)
- [ ] 1.4 Cập nhật `instruction/setup.md` với lệnh cài đặt Python deps và `CLAUDE.md` với lệnh build/lint/test; verify làm theo tài liệu trên clone mới chạy được

## 2. Khai báo báo cáo và kỳ

- [ ] 2.1 Viết model pydantic cho `report.yaml` (report, source, transform, section) và hàm nạp; verify test nạp khai báo hợp lệ và báo lỗi thiếu trường (spec report-definition)
- [ ] 2.2 Viết `period.py`: kỳ mặc định theo `period`, kỳ so sánh, múi giờ Asia/Ho_Chi_Minh; verify test kỳ tháng ngày 2026-09-25 → 2026-08-01..2026-08-31 và lỗi from > to
- [ ] 2.3 Validate tham chiếu dataset giữa section/transform/source; verify test báo đúng tên section và dataset thiếu
- [ ] 2.4 Viết `instruction/report-definition.md` mô tả schema `report.yaml` kèm ví dụ; verify ví dụ trong tài liệu pass validate

## 3. Nguồn dữ liệu và cache

- [ ] 3.1 Tạo registry connector và connector `file` (CSV UTF-8, xlsx theo sheet); verify test đọc fixture CSV/xlsx
- [ ] 3.2 Tạo connector `http` với thay tham số kỳ, `records_path`, phân trang page/cursor, retry; verify test với `httpx.MockTransport` (3 trang, lỗi 5xx)
- [ ] 3.3 Thay `${VAR}` từ `.env`/môi trường và che secret trong log/lỗi; verify test thiếu biến và test token không xuất hiện trong log/cache
- [ ] 3.4 Cache dữ liệu thô theo (report, source, kỳ), bỏ qua khi kỳ chứa hôm nay hoặc `refresh`; verify test lần build thứ hai không gọi API
- [ ] 3.5 Viết `instruction/data-sources.md` (cách khai báo API, đặt token trong `.env`, cache); verify nội dung khớp với các trường model

## 4. Render HTML

- [ ] 4.1 Viết `formatters.py` (số vi-VN, VND đầy đủ/rút gọn, %, ngày dd/mm/yyyy); verify test "1.234.567.890 ₫", "1,23 tỷ ₫", "+20,0%"
- [ ] 4.2 Tạo `templates/base.html.j2` và `templates/assets/report.css` theo design system của skill `business-report-html` (light/dark, 360px, print); verify render báo cáo rỗng mở đúng ở cả hai chế độ
- [ ] 4.3 Vendor Chart.js vào `templates/vendor/` và cơ chế nhúng inline CSS/JS; verify test HTML đầu ra không chứa `<script src=` hay stylesheet ngoài
- [ ] 4.4 Section `kpis` (giá trị, so sánh kỳ, mũi tên tăng/giảm), `chart` (line/bar/pie/doughnut), `table` (sắp xếp, định dạng cột), `text` (markdown) và trạng thái rỗng; verify test render từng loại và dataset rỗng

## 5. Pipeline và CLI

- [ ] 5.1 Viết `pipeline.py`: fetch → transform (nạp `transforms.py`) → so sánh kỳ → render → ghi `output/<id>/<id>_<from>_<to>.html`; verify test pipeline end-to-end với fixture
- [ ] 5.2 Viết CLI `list`, `validate`, `build` (`--from/--to/--refresh/--open`), `new`; verify test CLI bằng Typer CliRunner theo các scenario của spec report-cli
- [ ] 5.3 Tạo báo cáo mẫu `reports/mau-doanh-thu/` dùng CSV mẫu trong `data/input/sample/`; verify `uv run reportkit build mau-doanh-thu --from 2026-08-01 --to 2026-08-31` tạo file HTML
- [ ] 5.4 Viết `instruction/usage.md` (quy trình tạo và build báo cáo, dùng qua Claude Code); verify các lệnh trong tài liệu chạy đúng

## 6. Kiểm tra tích hợp

- [ ] 6.1 Mở báo cáo mẫu offline, kiểm tra light/dark, màn hình 360px và in PDF A4; verify theo các scenario của spec report-rendering
- [ ] 6.2 Chạy `uv run ruff check .`, `uv run pytest` và `openspec validate setup-report-platform --strict`; verify tất cả pass
