# Spec Delta

## Purpose

Cung cấp lệnh `reportkit` để liệt kê, kiểm tra và build báo cáo cho một kỳ cụ thể, dùng được cả bởi người và bởi Claude Code.

## ADDED Requirements

### Requirement: Liệt kê báo cáo
Lệnh `reportkit list` SHALL in ra id, tiêu đề và kiểu kỳ của mọi báo cáo trong `reports/`.

#### Scenario: Liệt kê
- **WHEN** chạy `reportkit list` khi có 2 báo cáo hợp lệ
- **THEN** in ra 2 dòng, mỗi dòng gồm id, tiêu đề, kiểu kỳ

### Requirement: Kiểm tra khai báo
Lệnh `reportkit validate [<report-id>]` SHALL kiểm tra khai báo (một hoặc tất cả báo cáo) mà không gọi nguồn dữ liệu, và trả mã thoát khác 0 nếu có lỗi.

#### Scenario: Validate có lỗi
- **WHEN** chạy `reportkit validate` và một báo cáo tham chiếu dataset không tồn tại
- **THEN** lệnh in lỗi của báo cáo đó và thoát với mã khác 0

### Requirement: Build báo cáo
Lệnh `reportkit build <report-id> [--from YYYY-MM-DD --to YYYY-MM-DD] [--refresh] [--open]` SHALL lấy dữ liệu, xử lý, render và ghi file tới `output/<report-id>/<report-id>_<from>_<to>.html`, rồi in đường dẫn file. `--refresh` bỏ qua cache; `--open` mở file bằng trình duyệt mặc định.

#### Scenario: Build thành công
- **WHEN** chạy `reportkit build doanh-thu-thang --from 2026-08-01 --to 2026-08-31`
- **THEN** file `output/doanh-thu-thang/doanh-thu-thang_2026-08-01_2026-08-31.html` được tạo và đường dẫn được in ra, mã thoát 0

#### Scenario: Báo cáo không tồn tại
- **WHEN** chạy `reportkit build khong-co`
- **THEN** lệnh báo không tìm thấy báo cáo, gợi ý chạy `reportkit list`, và thoát với mã khác 0

### Requirement: Tạo báo cáo mới từ mẫu
Lệnh `reportkit new <report-id>` SHALL tạo `reports/<report-id>/report.yaml` từ mẫu có sẵn, và từ chối nếu thư mục đã tồn tại.

#### Scenario: Tạo mới
- **WHEN** chạy `reportkit new kpi-van-hanh`
- **THEN** tạo `reports/kpi-van-hanh/report.yaml` hợp lệ theo `reportkit validate kpi-van-hanh`
