# Spec Delta

## Purpose

Lấy dữ liệu kinh doanh từ REST API và file CSV/Excel theo khai báo của báo cáo, giữ bí mật thông tin xác thực và cho phép chạy lại nhờ cache dữ liệu thô.

## ADDED Requirements

### Requirement: Nguồn dữ liệu REST API
Hệ thống SHALL hỗ trợ nguồn `type: http` với `url`, `method`, `params`, `headers`, đường dẫn tới mảng bản ghi trong response (`records_path`), và phân trang theo trang hoặc cursor. Tham số kỳ báo cáo (`{from}`, `{to}`) SHALL được thay vào `url`/`params`.

#### Scenario: Gọi API có phân trang
- **WHEN** nguồn http khai báo phân trang theo trang và API trả 3 trang dữ liệu
- **THEN** dataset chứa bản ghi của cả 3 trang theo đúng thứ tự

#### Scenario: API trả lỗi
- **WHEN** API trả mã HTTP 5xx sau số lần thử lại cấu hình
- **THEN** build dừng lại, báo lỗi nêu tên nguồn, URL (không kèm secret) và mã lỗi, và không sinh file HTML thiếu số liệu

### Requirement: Nguồn dữ liệu file
Hệ thống SHALL hỗ trợ nguồn `type: file` đọc CSV (UTF-8) và Excel (`.xlsx`, chọn sheet) từ đường dẫn tương đối trong repo.

#### Scenario: Đọc file Excel theo sheet
- **WHEN** nguồn file khai báo `path: data/input/kpi.xlsx` và `sheet: T8`
- **THEN** dataset chứa các dòng của sheet `T8` với tên cột lấy từ dòng tiêu đề

### Requirement: Bảo mật thông tin xác thực
Secret (API key, token) SHALL chỉ được tham chiếu qua biến môi trường dạng `${ENV_NAME}` trong khai báo, được nạp từ `.env` hoặc môi trường, và SHALL NOT xuất hiện trong log, thông báo lỗi, cache hay file HTML đầu ra.

#### Scenario: Thiếu biến môi trường
- **WHEN** khai báo dùng `${GHN_API_TOKEN}` nhưng biến này không được đặt
- **THEN** hệ thống báo lỗi nêu tên biến bị thiếu trước khi gọi API

#### Scenario: Secret không lộ ra đầu ra
- **WHEN** build thành công một báo cáo dùng header chứa token
- **THEN** giá trị token không xuất hiện trong file HTML, file cache hay log

### Requirement: Cache dữ liệu thô
Dữ liệu thô của mỗi nguồn SHALL được lưu cache theo (báo cáo, nguồn, kỳ). Khi build lại cùng kỳ, hệ thống SHALL dùng cache trừ khi người dùng yêu cầu làm mới.

#### Scenario: Build lại dùng cache
- **WHEN** build cùng báo cáo và cùng kỳ lần thứ hai
- **THEN** không có request nào tới API và kết quả giống lần đầu

#### Scenario: Yêu cầu làm mới
- **WHEN** build với tùy chọn làm mới
- **THEN** hệ thống gọi lại API và ghi đè cache của kỳ đó
