# Spec Delta

## Purpose

Sinh báo cáo thành một file HTML duy nhất, tự chứa, trình bày đẹp và nhất quán theo design system chung để gửi, lưu trữ và mở offline.

## ADDED Requirements

### Requirement: File HTML tự chứa
Mỗi lần build SHALL tạo đúng một file HTML trong đó CSS, dữ liệu biểu đồ và thư viện biểu đồ được nhúng inline; file SHALL mở được đúng khi không có mạng.

#### Scenario: Mở báo cáo offline
- **WHEN** mở file HTML đầu ra trên máy không có kết nối mạng
- **THEN** mọi KPI, bảng và biểu đồ hiển thị đầy đủ và không có request mạng nào

### Requirement: Bố cục báo cáo chuẩn
Báo cáo SHALL có phần đầu (tiêu đề, kỳ báo cáo, thời điểm sinh, nguồn dữ liệu), sau đó là các section theo thứ tự khai báo, và phần chân ghi nguồn dữ liệu cùng phiên bản công cụ.

#### Scenario: Phần đầu hiển thị kỳ báo cáo
- **WHEN** build báo cáo cho kỳ 2026-08-01 đến 2026-08-31
- **THEN** phần đầu hiển thị "01/08/2026 – 31/08/2026" và thời điểm sinh theo giờ Việt Nam

### Requirement: Định dạng số và KPI
Số liệu SHALL được định dạng theo chuẩn vi-VN (dấu chấm phân cách hàng nghìn, dấu phẩy thập phân); tiền tệ hiển thị theo VND; thẻ KPI SHALL hiển thị giá trị kỳ hiện tại và chênh lệch so với kỳ so sánh (nếu khai báo) kèm dấu tăng/giảm.

#### Scenario: Định dạng tiền tệ
- **WHEN** KPI doanh thu có giá trị 1234567890 và định dạng `currency`
- **THEN** thẻ KPI hiển thị "1.234.567.890 ₫" (hoặc dạng rút gọn "1,23 tỷ ₫" nếu khai báo `compact: true`)

#### Scenario: So sánh với kỳ trước
- **WHEN** KPI khai báo so sánh với kỳ trước, giá trị kỳ này 120 và kỳ trước 100
- **THEN** thẻ KPI hiển thị "+20,0%" với màu và mũi tên biểu thị tăng

### Requirement: Giao diện light/dark, di động và in ấn
Báo cáo SHALL hiển thị đúng ở chế độ sáng và tối theo cài đặt hệ thống, đọc được trên màn hình rộng 360px mà không cuộn ngang toàn trang, và khi in (hoặc lưu PDF) SHALL ẩn phần điều khiển tương tác và không cắt ngang biểu đồ giữa hai trang.

#### Scenario: In ra PDF
- **WHEN** người dùng in báo cáo ra PDF khổ A4
- **THEN** mỗi biểu đồ và thẻ KPI nằm trọn trong một trang

### Requirement: Trạng thái dữ liệu rỗng
Khi một dataset không có bản ghi trong kỳ, section tương ứng SHALL hiển thị thông báo "Không có dữ liệu trong kỳ" thay vì biểu đồ/bảng trống hoặc lỗi.

#### Scenario: Dataset rỗng
- **WHEN** dataset của một biểu đồ không có bản ghi
- **THEN** section hiển thị thông báo không có dữ liệu và các section khác vẫn render bình thường
