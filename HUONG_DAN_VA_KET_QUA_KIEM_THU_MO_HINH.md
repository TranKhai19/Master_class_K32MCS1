# BÁO CÁO VÀ HƯỚNG DẪN KIỂM THỬ TÍNH ĐÚNG ĐẮN CỦA MÔ HÌNH CSDL (GIAI ĐOẠN 1)
## Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1
**Học viên thực hiện:** Trần Duy Khải  
**Đề tài:** Hệ thống Giám sát & Quản lý tiêu thụ điện các thiết bị IoT Nhà thông minh  
**Tài liệu tham chiếu:** `CSDLNC_G1.docx`

---

## 1. TỔNG QUAN VỀ SỰ THAY ĐỔI VÀ ĐỒNG BỘ HÓA MÔ HÌNH

Sau khi cập nhật tài liệu `CSDLNC_G1.docx`, mô hình cơ sở dữ liệu quan hệ (RDBMS) đã được chuẩn hóa và mở rộng từ 7 bảng lên **9 bảng thực thể** nhằm giải quyết trọn vẹn bài toán quản lý phân tầng và đạt chuẩn **3NF**:

| STT | Bảng (Entity) | Vai trò trong Hệ thống IoT | Chuẩn hóa / Quan hệ |
|---|---|---|---|
| 1 | **User** | Chủ tài khoản / Người dùng hệ thống | 1NF, PK `user_id`, Email UNIQUE |
| 2 | **Home** | Ngôi nhà / Biệt thự / Căn hộ | N:1 với User (`owner_id`), CASCADE |
| 3 | **HomeMember** *(Mới)* | Quản lý chia sẻ quyền truy cập nhà (N:N) | **2NF**: PK phức hợp `(home_id, user_id)`, `role` phụ thuộc đầy đủ vào cả cặp khóa |
| 4 | **Room** | Phòng / Khu vực chức năng trong nhà | N:1 với Home, CASCADE |
| 5 | **DeviceType** | Danh mục quy chuẩn loại thiết bị & công suất | **3NF**: Tách khỏi Device; chuẩn hóa `rated_power_watts` |
| 6 | **Device** | Thiết bị IoT vật lý thực tế | Bổ sung `home_id` (NOT NULL, CASCADE); `room_id` (NULL, SET NULL); `type_id` (RESTRICT) |
| 7 | **SubscriptionPlan** | Gói dịch vụ lưu trữ viễn thám & phân tích điện năng | Quản lý `price`, `retention_days` |
| 8 | **HomeSubscription** | Hợp đồng thuê bao của căn nhà | N:N giữa Home và SubscriptionPlan |
| 9 | **Invoice** *(Mới)* | Hóa đơn thanh toán thuê bao | **3NF**: Tách riêng khỏi HomeSubscription để gắn trực tiếp với người chi trả (`user_id`) |

---

## 2. DANH MỤC CÁC TẬP TIN ĐÃ ĐƯỢC XÂY DỰNG & CẬP NHẬT

1. **`script_create_table_management_smart_home.sql`**:
   - DDL khởi tạo toàn bộ 9 bảng kèm đầy đủ ràng buộc khóa chính, khóa ngoại, hành vi (`CASCADE`, `SET NULL`, `RESTRICT`) và kiểu dữ liệu chuẩn (`utf8mb4`).
   - Nạp sẵn bộ dữ liệu mẫu thực tế và đa dạng cho toàn bộ 9 bảng.
2. **`check_data_integrity.sql`**:
   - Truy vấn đối soát nhanh số lượng bản ghi của toàn bộ 9 bảng.
3. **`test_model_integrity.sql`**:
   - Bộ kịch bản kiểm thử bằng SQL thuần chạy trực tiếp trong MySQL Workbench / CLI.
   - Ứng dụng `START TRANSACTION` và `ROLLBACK` để thử nghiệm các trường hợp chặn khóa, vi phạm ràng buộc và hành vi CASCADE/SET NULL mà không làm hỏng dữ liệu gốc.
4. **`test_model_integrity.py`**:
   - Script tự động hóa kiểm thử toàn diện 20 ca kiểm thử (Test Cases), in kết quả trực quan với màu sắc, thời gian thực thi và tỷ lệ đạt chuẩn.

---

## 3. KẾT QUẢ THỰC THI KIỂM THỬ TÍNH ĐÚNG ĐẮN (TEST REPORT)

Chạy lệnh kiểm thử tự động:
```bash
python test_model_integrity.py
```

### Bảng tổng hợp 20 Test Cases:

| Mã TC | Nhóm kiểm thử | Tên ca kiểm thử | Kết quả | Ghi chú kỹ thuật |
|---|---|---|:---:|---|
| **TC-01** | Schema | Kiểm tra sự hiện diện đầy đủ của 9 bảng | **PASS** | Đủ 9/9 bảng thực thể |
| **TC-02** | Schema | HomeMember có Khóa chính phức hợp `(home_id, user_id)` | **PASS** | Composite PK đúng chuẩn |
| **TC-03** | Schema | Device có `home_id` (NOT NULL) và `room_id` (Nullable) | **PASS** | Thiết bị gắn với nhà, linh hoạt vị trí |
| **TC-04** | Schema | DeviceType chuẩn hóa thuộc tính `rated_power_watts` | **PASS** | Thay thế tên cũ, định nghĩa chuẩn |
| **TC-05** | Schema | Invoice có FK trỏ đến `HomeSubscription` và `User` | **PASS** | Đúng quan hệ thanh toán |
| **TC-06** | Chuẩn hóa | Kiểm tra Chuẩn 1NF (Tính nguyên tử, PK cho mọi bảng) | **PASS** | Không có mảng lặp, dữ liệu atomic |
| **TC-07** | Chuẩn hóa | Kiểm tra Chuẩn 2NF (HomeMember Full Functional Dependency) | **PASS** | `role`, `joined_at` phụ thuộc cả cặp PK |
| **TC-08** | Chuẩn hóa | Kiểm tra Chuẩn 3NF (Tách DeviceType khỏi Device) | **PASS** | Loại bỏ phụ thuộc bắc cầu công suất |
| **TC-09** | Chuẩn hóa | Kiểm tra Chuẩn 3NF (Tách Invoice khỏi HomeSubscription) | **PASS** | Loại bỏ phụ thuộc bắc cầu hóa đơn |
| **TC-10** | Ràng buộc | [Positive] Nạp thành công dữ liệu mẫu ban đầu | **PASS** | Khởi tạo trơn tru dữ liệu 9 bảng |
| **TC-11** | Ràng buộc | [Negative] Chặn trùng lặp Email ở bảng User | **PASS** | Bắt lỗi `IntegrityError` (UNIQUE) |
| **TC-12** | Ràng buộc | [Negative] Chặn trùng Serial Number / MAC Address ở Device | **PASS** | Bắt lỗi `IntegrityError` (UNIQUE) |
| **TC-13** | Ràng buộc | [Negative] Chặn chèn dữ liệu mồ côi (Orphan Record FK) | **PASS** | Bắt lỗi Foreign Key Constraint |
| **TC-14** | Hành vi FK | [ON DELETE SET NULL] Xóa Room -> `Device.room_id` = NULL | **PASS** | Thiết bị không bị xóa mất khi xóa phòng |
| **TC-15** | Hành vi FK | [ON DELETE RESTRICT] Chặn xóa DeviceType đang dùng | **PASS** | Không cho phép xóa danh mục khi có thiết bị |
| **TC-16** | Hành vi FK | [ON DELETE RESTRICT] Chặn xóa Plan đang có thuê bao | **PASS** | Không cho phép xóa gói cước đang phục vụ |
| **TC-17** | Hành vi FK | [ON DELETE CASCADE] Xóa User -> Xóa sạch tài nguyên con | **PASS** | Tự động dọn dẹp sạch sẽ Home, Device, Inv |
| **TC-18** | Nghiệp vụ | Room của Device phải thuộc cùng Home với Device | **PASS** | 0 bản ghi vi phạm cross-table |
| **TC-19** | Nghiệp vụ | Thời hạn hợp đồng thuê bao (`start_date <= end_date`) | **PASS** | 0 bản ghi vi phạm chuỗi thời gian |
| **TC-20** | Nghiệp vụ | Giá trị không âm (`rated_power_watts >= 0`, `amount >= 0`) | **PASS** | Dữ liệu số học hoàn toàn hợp lệ |

**Tổng kết:** **20 / 20 Test Cases PASSED (Tỷ lệ 100.0%)**

---

## 4. HƯỚNG DẪN THỰC THI

### Cách 1: Chạy script kiểm thử Python (Nhanh, độc lập, trực quan)
Mở Terminal / PowerShell tại thư mục dự án và gõ:
```powershell
python test_model_integrity.py
```

### Cách 2: Chạy trong MySQL Workbench
1. Mở **MySQL Workbench 8.0**.
2. Mở file `script_create_table_management_smart_home.sql` và nhấn biểu tượng tia sét ⚡ (Execute) để tạo database và nạp dữ liệu.
3. Mở file `test_model_integrity.sql` và nhấn Execute để chạy bộ test kịch bản SQL và xem kết quả trực tiếp trên lưới kết quả.

---

## 5. THỰC NGHIỆM VỚI DỮ LIỆU LỚN: 1 TRIỆU BẢN GHI (1,000,000 ROWS / TABLE)

Để phục vụ phân tích dữ liệu lớn và kiểm thử hiệu năng truy vấn nâng cao (Big Data & High-Velocity IoT Analytics), hệ thống đã tích hợp sẵn công cụ sinh dữ liệu tự động:

### 5.1. Công cụ sinh dữ liệu tự động ([generate_million_records.py](file:///d:/Master_Class/CSDLNC/generate_million_records.py))
- **Cơ chế:** I/O Buffer Streaming nạp trực tiếp ra file CSV chuẩn, bảo đảm 100% toàn vẹn ràng buộc khóa ngoại và khóa duy nhất.
- **Tốc độ sinh:** Đã sinh thành công **7.000.000 bản ghi** (1.000.000 bản ghi cho mỗi bảng trong 7 bảng chính) trong **44.96 giây**.
- **Dữ liệu xuất ra thư mục:** `d:/Master_Class/CSDLNC/bulk_data/` gồm:
  - `users.csv` (1.000.000 dòng, ~137 MB)
  - `homes.csv` (1.000.000 dòng, ~113 MB)
  - `devices.csv` (1.000.000 dòng, ~111 MB)
  - `invoices.csv` (1.000.000 dòng, ~67 MB)
  - `home_subscriptions.csv` (1.000.000 dòng, ~45 MB)
  - `home_members.csv` (1.000.000 dòng, ~40 MB)
  - `rooms.csv` (1.000.000 dòng, ~35 MB)

### 5.2. Cách nạp siêu tốc vào MySQL ([load_million_records.sql](file:///d:/Master_Class/CSDLNC/load_million_records.sql))
Mở file `load_million_records.sql` trong **MySQL Workbench** và thực thi:
- Tự động cấu hình `local_infile = 1`.
- Tắt tạm thời `autocommit`, `foreign_key_checks` và `unique_checks` trong lúc nạp để tối đa hóa tốc độ ghi đĩa I/O (chỉ mất khoảng 30-45 giây cho toàn bộ 7 triệu bản ghi).
- Tự động bật lại toàn vẹn và thực thi truy vấn đối soát số lượng.

### 5.3. Cách sinh thuần SQL qua Stored Procedure ([procedure_generate_million_records.sql](file:///d:/Master_Class/CSDLNC/procedure_generate_million_records.sql))
- Dành cho môi trường chỉ sử dụng MySQL Server:
```sql
CALL sp_generate_bulk_data(1000000, 10000);
```

