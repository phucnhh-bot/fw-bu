# Spec Delta

## Purpose

Cho phép khai báo một báo cáo kinh doanh bằng file cấu hình (nguồn dữ liệu, tham số kỳ, KPI, bảng, biểu đồ) để báo cáo có thể build lặp lại mà không phải sửa code.

## ADDED Requirements

### Requirement: Báo cáo được khai báo bằng file YAML
Mỗi báo cáo SHALL nằm trong thư mục `reports/<report-id>/` và có file `report.yaml` chứa: `id`, `title`, `description`, `owner`, `period` (kiểu kỳ: `day`, `week`, `month`, `quarter`, `custom`), `sources` (danh sách nguồn dữ liệu), và `sections` (danh sách phần nội dung: `kpis`, `chart`, `table`, `text`).

#### Scenario: Khai báo hợp lệ được nạp
- **WHEN** `reports/doanh-thu-thang/report.yaml` có đủ các trường bắt buộc
- **THEN** hệ thống nạp được báo cáo với `id` là `doanh-thu-thang` và danh sách section theo đúng thứ tự khai báo

#### Scenario: Thiếu trường bắt buộc
- **WHEN** file `report.yaml` thiếu trường `sources`
- **THEN** hệ thống báo lỗi nêu rõ tên file và tên trường bị thiếu, và không sinh file HTML

### Requirement: Tham số kỳ báo cáo
Báo cáo SHALL nhận khoảng thời gian `from`/`to` (ngày, định dạng ISO `YYYY-MM-DD`); nếu không truyền, hệ thống SHALL tính kỳ gần nhất đã kết thúc theo `period` và múi giờ `Asia/Ho_Chi_Minh`.

#### Scenario: Kỳ mặc định theo tháng
- **WHEN** build báo cáo có `period: month` vào ngày 2026-09-25 mà không truyền `from`/`to`
- **THEN** kỳ báo cáo là 2026-08-01 đến 2026-08-31

#### Scenario: Khoảng ngày không hợp lệ
- **WHEN** truyền `from` lớn hơn `to`
- **THEN** hệ thống báo lỗi và không gọi bất kỳ nguồn dữ liệu nào

### Requirement: Tham chiếu dữ liệu giữa các phần
Mỗi section SHALL tham chiếu dữ liệu qua tên dataset (`dataset: <tên>`), trong đó tên dataset là tên một nguồn trong `sources` hoặc một dataset dẫn xuất được khai báo trong `transforms`.

#### Scenario: Tham chiếu dataset không tồn tại
- **WHEN** một section khai báo `dataset: don-hang` nhưng không có nguồn hay transform nào tên `don-hang`
- **THEN** bước validate báo lỗi nêu tên section và tên dataset không tìm thấy
