# TÀI LIỆU 10 NGHIỆP VỤ HỆ THỐNG SMART HOME IOT
## Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1
**Học viên:** Trần Duy Khải  
**Đề tài:** Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh  
**Database:** `smart_home_info` (MySQL - Chuẩn 3NF, 9 bảng)

---

## SƠ ĐỒ QUAN HỆ BẢNG (THAM CHIẾU NHANH)

```
User ──(1:N)──► Home ──(1:N)──► Room ──(1:N)──► Device ◄──(N:1)── DeviceType
 │               │
 │               └──(1:N)──► HomeMember ◄──(N:1)── User
 │               └──(1:N)──► HomeSubscription ◄──(N:1)── SubscriptionPlan
 │                                │
 └──────────────────────────────► Invoice ◄──(N:1)── HomeSubscription
```

---

## NGHIỆP VỤ 1: ĐĂNG KÝ TÀI KHOẢN & QUẢN LÝ NGƯỜI DÙNG

### 1.1. Mô tả nghiệp vụ
Người dùng tạo tài khoản trên hệ thống Smart Home. Mỗi tài khoản đại diện cho **một chủ sở hữu** có thể sở hữu nhiều bất động sản. Thông tin đăng nhập (email, mật khẩu hash) được bảo mật. Hệ thống đảm bảo **email là duy nhất** trên toàn hệ thống (UNIQUE constraint).

### 1.2. Cách quản trị
| Thao tác | Bảng liên quan | Ràng buộc áp dụng |
|---|---|---|
| Tạo tài khoản mới | `User` | `email` UNIQUE — chặn trùng email |
| Cập nhật thông tin | `User` | `updated_at` tự cập nhật (ON UPDATE CURRENT_TIMESTAMP) |
| Xóa tài khoản | `User` → cascade | ON DELETE CASCADE → tự động xóa `Home`, `HomeMember`, `Invoice` |
| Tra cứu người dùng | `User` | Tìm theo `email` hoặc `user_id` |

### 1.3. Truy vấn SQL

```sql
-- [NV1-Q1] Đăng ký tài khoản mới
INSERT INTO User (full_name, email, phone, password_hash)
VALUES ('Trần Duy Khải', 'khai.tran@smarthome.vn',
        '0901234567', SHA2('MatKhauBiMat@2025', 256));

-- [NV1-Q2] Tra cứu thông tin người dùng theo email
SELECT user_id, full_name, email, phone, created_at
FROM User
WHERE email = 'khai.tran@smarthome.vn';

-- [NV1-Q3] Thống kê số lượng nhà và thiết bị của từng người dùng
SELECT
    u.user_id,
    u.full_name,
    u.email,
    COUNT(DISTINCT h.home_id)   AS tong_so_nha,
    COUNT(DISTINCT d.device_id) AS tong_thiet_bi
FROM User u
LEFT JOIN Home h    ON h.user_id = u.user_id
LEFT JOIN Device d  ON d.home_id = h.home_id
GROUP BY u.user_id, u.full_name, u.email
ORDER BY tong_thiet_bi DESC;

-- [NV1-Q4] Tìm người dùng chưa có nhà nào (LEFT JOIN + IS NULL)
SELECT u.user_id, u.full_name, u.email
FROM User u
LEFT JOIN Home h ON h.user_id = u.user_id
WHERE h.home_id IS NULL;
```

---

## NGHIỆP VỤ 2: THÊM NHÀ & PHÂN BỔ CÁC PHÒNG CHỨC NĂNG

### 2.1. Mô tả nghiệp vụ
Chủ sở hữu đăng ký **ngôi nhà / căn hộ / biệt thự** vào hệ thống. Mỗi nhà được phân chia thành các **phòng chức năng** (phòng khách, phòng bếp, phòng ngủ, sảnh…) tương ứng với từng tầng. Phòng là đơn vị vị trí để gắn thiết bị IoT.

### 2.2. Cách quản trị
| Thao tác | Bảng liên quan | Ràng buộc áp dụng |
|---|---|---|
| Thêm nhà mới | `Home` | FK `user_id` → `User` — chủ nhà phải tồn tại |
| Thêm phòng vào nhà | `Room` | FK `home_id` → `Home` — nhà phải tồn tại |
| Xóa nhà | `Home` | CASCADE → tự xóa `Room`, `Device`, `HomeSubscription` |
| Xóa phòng | `Room` | SET NULL trên `Device.room_id` — thiết bị không bị mất |

### 2.3. Truy vấn SQL

```sql
-- [NV2-Q1] Thêm một ngôi nhà mới cho người dùng user_id = 1
INSERT INTO Home (user_id, home_name, address)
VALUES (1, 'Biệt thự Đà Nẵng - An Thượng',
           '15 Nguyễn Đình Chiểu, Mỹ An, Ngũ Hành Sơn, Đà Nẵng');

-- [NV2-Q2] Thêm các phòng chức năng cho nhà home_id = 1
INSERT INTO Room (home_id, room_name, floor) VALUES
(1, 'Sảnh đón khách',    1),
(1, 'Phòng bếp & ăn',   1),
(1, 'Phòng khách lớn',  1),
(1, 'Phòng ngủ Master', 2),
(1, 'Phòng ngủ con 1',  2),
(1, 'Phòng làm việc',   2);

-- [NV2-Q3] Xem toàn bộ nhà và số phòng của từng nhà
SELECT
    h.home_id,
    u.full_name        AS chu_so_huu,
    h.home_name,
    h.address,
    COUNT(r.room_id)   AS so_phong,
    h.created_at
FROM Home h
JOIN User u ON u.user_id = h.user_id
LEFT JOIN Room r ON r.home_id = h.home_id
GROUP BY h.home_id, u.full_name, h.home_name, h.address, h.created_at
ORDER BY so_phong DESC;

-- [NV2-Q4] Liệt kê toàn bộ phòng theo tầng của một ngôi nhà
SELECT room_id, room_name, floor
FROM Room
WHERE home_id = 1
ORDER BY floor ASC, room_name ASC;
```

---

## NGHIỆP VỤ 3: CHIA SẺ QUYỀN TRUY CẬP NHÀ CHO THÀNH VIÊN

### 3.1. Mô tả nghiệp vụ
Chủ nhà (ADMIN) có thể **chia sẻ quyền điều khiển** cho các thành viên gia đình hoặc người thuê. Mỗi thành viên được gán vai trò: `ADMIN` (toàn quyền), `MEMBER` (điều khiển thiết bị), hoặc `GUEST` (chỉ xem). Đây là quan hệ **N:N** giữa `User` và `Home`, được chuẩn hóa qua bảng `HomeMember` (đạt chuẩn **2NF** với Composite PK).

### 3.2. Cách quản trị
| Thao tác | Bảng liên quan | Ràng buộc áp dụng |
|---|---|---|
| Thêm thành viên vào nhà | `HomeMember` | PK phức hợp `(home_id, user_id)` — không trùng lặp |
| Cập nhật vai trò | `HomeMember` | UPDATE `role` theo `(home_id, user_id)` |
| Xóa thành viên | `HomeMember` | DELETE theo `(home_id, user_id)` |
| Xóa user | `User` | CASCADE → tự xóa hàng trong `HomeMember` |

### 3.3. Truy vấn SQL

```sql
-- [NV3-Q1] Thêm thành viên gia đình vào nhà home_id = 1
INSERT INTO HomeMember (home_id, user_id, role) VALUES
(1, 2, 'MEMBER'),
(1, 3, 'GUEST');

-- [NV3-Q2] Liệt kê tất cả thành viên của một ngôi nhà
SELECT
    hm.home_id,
    h.home_name,
    u.full_name     AS ten_thanh_vien,
    u.email,
    u.phone,
    hm.role,
    hm.joined_at
FROM HomeMember hm
JOIN Home h ON h.home_id = hm.home_id
JOIN User u ON u.user_id = hm.user_id
WHERE hm.home_id = 1
ORDER BY FIELD(hm.role, 'ADMIN', 'MEMBER', 'GUEST');

-- [NV3-Q3] Tìm tất cả nhà mà một người dùng có quyền truy cập
SELECT
    h.home_id,
    h.home_name,
    h.address,
    hm.role,
    u_owner.full_name AS chu_nha
FROM HomeMember hm
JOIN Home h         ON h.home_id  = hm.home_id
JOIN User u_owner   ON u_owner.user_id = h.user_id
WHERE hm.user_id = 2;

-- [NV3-Q4] Cập nhật vai trò thành viên
UPDATE HomeMember
SET role = 'MEMBER'
WHERE home_id = 1 AND user_id = 3;
```

---

## NGHIỆP VỤ 4: LẮP ĐẶT VÀ QUẢN LÝ THIẾT BỊ IOT

### 4.1. Mô tả nghiệp vụ
Kỹ thuật viên hoặc chủ nhà đăng ký thiết bị IoT vật lý (điều hòa, khóa thông minh, camera, cảm biến…) vào một phòng cụ thể. Mỗi thiết bị được nhận dạng duy nhất bằng **Serial Number** và **MAC Address**. Trạng thái thiết bị (`ACTIVE`, `OFFLINE`, `MAINTENANCE`) được theo dõi liên tục.

### 4.2. Cách quản trị
| Thao tác | Bảng liên quan | Ràng buộc áp dụng |
|---|---|---|
| Lắp đặt thiết bị mới | `Device` | FK `home_id` (NOT NULL), `room_id` (NULL cho phép), `type_id` (RESTRICT) |
| Chuyển thiết bị sang phòng khác | `Device` | UPDATE `room_id` (phòng mới phải cùng `home_id`) |
| Cập nhật firmware | `Device` | UPDATE `firmware_version` |
| Gửi thiết bị bảo trì | `Device` | UPDATE `status = 'MAINTENANCE'` |
| Xóa phòng | `Room` | SET NULL trên `Device.room_id` — thiết bị vẫn còn |

### 4.3. Truy vấn SQL

```sql
-- [NV4-Q1] Lắp đặt thiết bị mới vào phòng
INSERT INTO Device (home_id, room_id, type_id, device_name,
                    serial_number, mac_address, firmware_version, status)
VALUES (1, 4, 3, 'Điều hòa Daikin Phòng ngủ Master',
        'DAK-SH-2025-001', 'A4:C3:F0:85:7E:01', 'v3.2.1', 'ACTIVE');

-- [NV4-Q2] Xem toàn bộ thiết bị trong một ngôi nhà (JOIN 3 bảng)
SELECT
    d.device_id,
    dt.category          AS loai,
    dt.manufacturer      AS hang_sx,
    d.device_name,
    r.room_name          AS vi_tri_phong,
    r.floor              AS tang,
    d.status,
    dt.rated_power_watts AS cong_suat_W,
    d.firmware_version,
    d.installed_at
FROM Device d
JOIN DeviceType dt    ON dt.type_id  = d.type_id
LEFT JOIN Room r      ON r.room_id   = d.room_id
WHERE d.home_id = 1
ORDER BY r.floor ASC, dt.category ASC;

-- [NV4-Q3] Thống kê số lượng thiết bị theo loại và hãng sản xuất
SELECT
    dt.category,
    dt.manufacturer,
    COUNT(d.device_id)          AS so_luong,
    SUM(dt.rated_power_watts)   AS tong_cong_suat_W,
    AVG(dt.rated_power_watts)   AS tb_cong_suat_W
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
GROUP BY dt.category, dt.manufacturer
ORDER BY so_luong DESC;

-- [NV4-Q4] Chuyển thiết bị sang phòng khác (cùng ngôi nhà)
UPDATE Device
SET room_id = 5
WHERE device_id = 1 AND home_id = 1;

-- [NV4-Q5] Cập nhật trạng thái bảo trì hàng loạt
UPDATE Device
SET status = 'MAINTENANCE'
WHERE home_id = 1 AND status = 'OFFLINE';
```

---

## NGHIỆP VỤ 5: TRA CỨU & BÁO CÁO THIẾT BỊ THEO TẦNG / PHÒNG

### 5.1. Mô tả nghiệp vụ
Chủ nhà cần **xem bản đồ thiết bị** bố trí trong toàn ngôi nhà, phân loại theo tầng và phòng. Dashboard hiển thị tổng công suất định mức mỗi phòng để hỗ trợ lập kế hoạch tiết kiệm điện. Các thiết bị **chưa được phân bổ phòng** (room_id = NULL) cần được liệt kê riêng để xử lý.

### 5.2. Cách quản trị
| Thao tác | Bảng liên quan | Kỹ thuật SQL |
|---|---|---|
| Xem thiết bị theo tầng | `Device` + `Room` + `DeviceType` | JOIN + GROUP BY `floor` |
| Xem thiết bị chưa phân phòng | `Device` | WHERE `room_id IS NULL` |
| Tính tổng công suất mỗi phòng | `Device` + `DeviceType` | SUM(`rated_power_watts`) GROUP BY `room_id` |
| Xếp hạng phòng tiêu thụ nhiều nhất | Subquery + ORDER BY | ORDER BY tổng_cong_suat DESC |

### 5.3. Truy vấn SQL

```sql
-- [NV5-Q1] Bản đồ thiết bị toàn nhà — phân cấp theo Tầng → Phòng
SELECT
    COALESCE(r.floor, 0)       AS tang,
    COALESCE(r.room_name, '⚠ Chưa phân phòng') AS phong,
    dt.category                AS loai_thiet_bi,
    d.device_name,
    d.status,
    dt.rated_power_watts       AS cong_suat_W
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
LEFT JOIN Room r   ON r.room_id  = d.room_id
WHERE d.home_id = 1
ORDER BY tang ASC, phong ASC, loai_thiet_bi ASC;

-- [NV5-Q2] Tổng công suất định mức theo từng phòng
SELECT
    r.floor                        AS tang,
    r.room_name,
    COUNT(d.device_id)             AS so_thiet_bi,
    SUM(dt.rated_power_watts)      AS tong_cong_suat_W,
    ROUND(SUM(dt.rated_power_watts) / 1000, 3) AS cong_suat_kW
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
JOIN Room r        ON r.room_id  = d.room_id
WHERE d.home_id = 1
GROUP BY r.room_id, r.floor, r.room_name
ORDER BY tong_cong_suat_W DESC;

-- [NV5-Q3] Liệt kê thiết bị chưa được gắn phòng
SELECT
    d.device_id,
    d.device_name,
    dt.category,
    d.status,
    d.installed_at
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
WHERE d.room_id IS NULL
ORDER BY d.home_id, d.installed_at;

-- [NV5-Q4] Tìm phòng có nhiều thiết bị OFFLINE nhất (cần bảo trì)
SELECT
    r.room_name,
    h.home_name,
    COUNT(d.device_id) AS so_thiet_bi_offline
FROM Device d
JOIN Room r ON r.room_id = d.room_id
JOIN Home h ON h.home_id = d.home_id
WHERE d.status = 'OFFLINE'
GROUP BY r.room_id, r.room_name, h.home_name
ORDER BY so_thiet_bi_offline DESC
LIMIT 10;
```

---

## NGHIỆP VỤ 6: ĐĂNG KÝ & GIA HẠN GÓI THUÊ BAO DỊCH VỤ

### 6.1. Mô tả nghiệp vụ
Mỗi ngôi nhà cần **đăng ký một gói cước** để lưu trữ dữ liệu viễn thám từ thiết bị IoT trên đám mây. Có 5 gói: Free (7 ngày), Standard (30 ngày), Premium (90 ngày), Enterprise (365 ngày), Energy Saver AI (60 ngày). Hệ thống theo dõi **ngày bắt đầu / kết thúc** và **trạng thái thanh toán**. Một nhà có thể gia hạn nhiều lần.

### 6.2. Cách quản trị
| Thao tác | Bảng liên quan | Ràng buộc áp dụng |
|---|---|---|
| Đăng ký gói mới | `HomeSubscription` | FK `home_id` + `plan_id`; `start_date <= end_date` |
| Kiểm tra hết hạn | `HomeSubscription` | WHERE `end_date < CURDATE()` |
| Gia hạn thuê bao | `HomeSubscription` | INSERT bản ghi mới với `start_date` tiếp nối |
| Hủy thuê bao | `HomeSubscription` | UPDATE `payment_status = 'CANCELLED'` |
| Xóa gói cước | `SubscriptionPlan` | RESTRICT — không xóa khi đang có hợp đồng |

### 6.3. Truy vấn SQL

```sql
-- [NV6-Q1] Đăng ký gói Premium Pro cho nhà home_id = 1
INSERT INTO HomeSubscription (home_id, plan_id, start_date, end_date, payment_status)
VALUES (1, 3, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 90 DAY), 'PAID');

-- [NV6-Q2] Xem tất cả hợp đồng thuê bao của một ngôi nhà
SELECT
    hs.subscription_id,
    h.home_name,
    sp.plan_name,
    sp.price              AS gia_thang,
    sp.retention_days     AS luu_tru_ngay,
    hs.start_date,
    hs.end_date,
    DATEDIFF(hs.end_date, CURDATE()) AS ngay_con_lai,
    hs.payment_status
FROM HomeSubscription hs
JOIN Home h              ON h.home_id  = hs.home_id
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
WHERE hs.home_id = 1
ORDER BY hs.start_date DESC;

-- [NV6-Q3] Cảnh báo hợp đồng sắp hết hạn trong 7 ngày tới
SELECT
    h.home_name,
    u.full_name    AS chu_nha,
    u.email,
    u.phone,
    sp.plan_name,
    hs.end_date,
    DATEDIFF(hs.end_date, CURDATE()) AS ngay_con_lai
FROM HomeSubscription hs
JOIN Home h              ON h.home_id  = hs.home_id
JOIN User u              ON u.user_id  = h.user_id
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
WHERE hs.payment_status = 'PAID'
  AND hs.end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
ORDER BY hs.end_date ASC;

-- [NV6-Q4] Thống kê số hợp đồng theo từng gói cước
SELECT
    sp.plan_name,
    sp.price,
    sp.retention_days,
    COUNT(hs.subscription_id)                                    AS tong_hop_dong,
    SUM(CASE WHEN hs.payment_status='PAID'    THEN 1 ELSE 0 END) AS da_thanh_toan,
    SUM(CASE WHEN hs.payment_status='EXPIRED' THEN 1 ELSE 0 END) AS het_han
FROM SubscriptionPlan sp
LEFT JOIN HomeSubscription hs ON hs.plan_id = sp.plan_id
GROUP BY sp.plan_id, sp.plan_name, sp.price, sp.retention_days
ORDER BY tong_hop_dong DESC;
```

---

## NGHIỆP VỤ 7: THANH TOÁN HÓA ĐƠN & TRUY VẾT GIAO DỊCH

### 7.1. Mô tả nghiệp vụ
Sau khi đăng ký gói thuê bao, chủ nhà thực hiện **thanh toán** qua các kênh: VNPay, MoMo, thẻ tín dụng, chuyển khoản. Mỗi lần thanh toán tạo ra một **hóa đơn độc lập** trong bảng `Invoice`. Tách bảng này khỏi `HomeSubscription` là yêu cầu của **chuẩn 3NF** — thông tin thanh toán phụ thuộc vào người trả tiền cụ thể (`user_id`), không chỉ vào hợp đồng.

### 7.2. Cách quản trị
| Thao tác | Bảng liên quan | Ràng buộc áp dụng |
|---|---|---|
| Ghi nhận thanh toán | `Invoice` | FK `subscription_id` + `user_id`; `amount >= 0` |
| Xử lý hoàn tiền | `Invoice` | UPDATE `payment_status = 'REFUNDED'` |
| Tra cứu lịch sử theo người dùng | `Invoice` JOIN `User` | Lọc theo `user_id` và khoảng thời gian |
| Đối soát doanh thu | `Invoice` JOIN `SubscriptionPlan` | SUM(`amount`) GROUP BY tháng |

### 7.3. Truy vấn SQL

```sql
-- [NV7-Q1] Ghi nhận thanh toán hóa đơn thuê bao
INSERT INTO Invoice (subscription_id, user_id, amount, payment_method, payment_status)
VALUES (1, 1, 199000.00, 'MOMO', 'SUCCESS');

-- [NV7-Q2] Lịch sử thanh toán đầy đủ của một người dùng (JOIN 4 bảng)
SELECT
    i.invoice_id,
    i.paid_at,
    h.home_name,
    sp.plan_name,
    i.amount,
    i.payment_method,
    i.payment_status
FROM Invoice i
JOIN HomeSubscription hs ON hs.subscription_id = i.subscription_id
JOIN Home h              ON h.home_id  = hs.home_id
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
WHERE i.user_id = 1
ORDER BY i.paid_at DESC;

-- [NV7-Q3] Báo cáo doanh thu theo tháng
SELECT
    DATE_FORMAT(i.paid_at, '%Y-%m') AS thang,
    COUNT(i.invoice_id)             AS so_hoa_don,
    SUM(i.amount)                   AS doanh_thu_VND,
    AVG(i.amount)                   AS gia_tri_tb
FROM Invoice i
WHERE i.payment_status = 'SUCCESS'
GROUP BY DATE_FORMAT(i.paid_at, '%Y-%m')
ORDER BY thang DESC;

-- [NV7-Q4] Doanh thu theo gói cước (gói nào bán chạy nhất)
SELECT
    sp.plan_name,
    COUNT(i.invoice_id)   AS so_giao_dich,
    SUM(i.amount)         AS tong_doanh_thu,
    ROUND(SUM(i.amount) * 100.0 /
        (SELECT SUM(amount) FROM Invoice WHERE payment_status = 'SUCCESS'), 2)
        AS ty_le_phan_tram
FROM Invoice i
JOIN HomeSubscription hs ON hs.subscription_id = i.subscription_id
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
WHERE i.payment_status = 'SUCCESS'
GROUP BY sp.plan_id, sp.plan_name
ORDER BY tong_doanh_thu DESC;
```

---

## NGHIỆP VỤ 8: GIÁM SÁT CÔNG SUẤT TIÊU THỤ ĐIỆN THEO NHÀ

### 8.1. Mô tả nghiệp vụ
Hệ thống tính **tổng công suất định mức** (từ `DeviceType.rated_power_watts`) của tất cả thiết bị đang `ACTIVE` trong mỗi ngôi nhà để ước lượng chi phí điện tối đa. Kết hợp với dữ liệu viễn thám thực tế từ MongoDB (Giai đoạn 3), có thể cảnh báo khi phụ tải vượt ngưỡng an toàn. Nhóm thiết bị **Climate** (điều hòa) thường chiếm 80-90% tổng công suất.

### 8.2. Cách quản trị
| Thao tác | Bảng liên quan | Kỹ thuật SQL |
|---|---|---|
| Tính công suất mỗi nhà | `Device` + `DeviceType` + `Home` | SUM + JOIN + WHERE status='ACTIVE' |
| Xếp hạng nhà ngốn điện nhất | GROUP BY + ORDER BY | ORDER BY tổng công suất DESC |
| Phân tích theo danh mục | GROUP BY `category` | Climate vs Lighting vs Sensor… |
| Cảnh báo vượt ngưỡng | GROUP BY + HAVING | HAVING tổng > 5000W |

### 8.3. Truy vấn SQL

```sql
-- [NV8-Q1] Tổng công suất định mức theo từng ngôi nhà (xếp hạng)
SELECT
    h.home_id,
    u.full_name                          AS chu_so_huu,
    h.home_name,
    COUNT(d.device_id)                   AS so_thiet_bi_active,
    SUM(dt.rated_power_watts)            AS tong_cong_suat_W,
    ROUND(SUM(dt.rated_power_watts)/1000, 3) AS tong_cong_suat_kW,
    ROUND(SUM(dt.rated_power_watts) * 24 / 1000, 2) AS uoc_tinh_dien_ngay_kWh
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
JOIN Home h        ON h.home_id  = d.home_id
JOIN User u        ON u.user_id  = h.user_id
WHERE d.status = 'ACTIVE'
GROUP BY h.home_id, u.full_name, h.home_name
ORDER BY tong_cong_suat_W DESC;

-- [NV8-Q2] Phân bổ công suất theo danh mục thiết bị (toàn hệ thống)
SELECT
    dt.category,
    COUNT(d.device_id)                              AS so_thiet_bi,
    SUM(dt.rated_power_watts)                       AS tong_W,
    ROUND(SUM(dt.rated_power_watts) * 100.0 /
        (SELECT SUM(dt2.rated_power_watts)
         FROM Device d2 JOIN DeviceType dt2 ON dt2.type_id = d2.type_id
         WHERE d2.status = 'ACTIVE'), 2)            AS ty_le_phan_tram
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
WHERE d.status = 'ACTIVE'
GROUP BY dt.category
ORDER BY tong_W DESC;

-- [NV8-Q3] Cảnh báo nhà có tổng công suất vượt 5000W (nguy cơ quá tải)
SELECT
    h.home_name,
    u.full_name,
    u.phone                   AS lien_he_khan,
    SUM(dt.rated_power_watts) AS tong_cong_suat_W
FROM Device d
JOIN DeviceType dt ON dt.type_id = d.type_id
JOIN Home h        ON h.home_id  = d.home_id
JOIN User u        ON u.user_id  = h.user_id
WHERE d.status = 'ACTIVE'
GROUP BY h.home_id, h.home_name, u.full_name, u.phone
HAVING tong_cong_suat_W > 5000
ORDER BY tong_cong_suat_W DESC;
```

---

## NGHIỆP VỤ 9: PHÁT HIỆN THIẾT BỊ OFFLINE & LẬP KẾ HOẠCH BẢO TRÌ

### 9.1. Mô tả nghiệp vụ
Hệ thống **phát hiện sớm** các thiết bị bị ngắt kết nối (`OFFLINE`) hoặc đang bảo trì (`MAINTENANCE`). Từ đó gửi cảnh báo đến chủ nhà và lập danh sách ưu tiên bảo trì theo **mức độ quan trọng** của loại thiết bị. Thiết bị an ninh (Security) được ưu tiên xử lý trước Điều hòa (Climate), Điện năng (Power), Cảm biến (Sensor), rồi mới đến Đèn chiếu sáng (Lighting).

### 9.2. Cách quản trị
| Thao tác | Bảng liên quan | Kỹ thuật SQL |
|---|---|---|
| Liệt kê thiết bị OFFLINE | `Device` + `DeviceType` + `Home` | WHERE `status != 'ACTIVE'` |
| Ưu tiên bảo trì theo category | CASE WHEN ưu tiên | Security > Climate > Power > Sensor > Lighting |
| Thống kê tỷ lệ hoạt động | GROUP BY + CASE | COUNT theo status |
| Nhà cần hỗ trợ gấp nhất | GROUP BY `home_id` + HAVING | GROUP_CONCAT danh sách thiết bị |

### 9.3. Truy vấn SQL

```sql
-- [NV9-Q1] Danh sách thiết bị không hoạt động — ưu tiên bảo trì
SELECT
    d.device_id,
    h.home_name,
    u.phone                 AS lien_he_chu_nha,
    dt.category,
    d.device_name,
    r.room_name,
    d.status,
    d.firmware_version,
    CASE dt.category
        WHEN 'Security' THEN '1 - Khẩn cấp'
        WHEN 'Climate'  THEN '2 - Cao'
        WHEN 'Power'    THEN '3 - Trung bình'
        WHEN 'Sensor'   THEN '4 - Theo dõi'
        ELSE                 '5 - Thấp'
    END AS muc_uu_tien
FROM Device d
JOIN DeviceType dt  ON dt.type_id = d.type_id
JOIN Home h         ON h.home_id  = d.home_id
JOIN User u         ON u.user_id  = h.user_id
LEFT JOIN Room r    ON r.room_id  = d.room_id
WHERE d.status IN ('OFFLINE', 'MAINTENANCE')
ORDER BY
    FIELD(dt.category, 'Security', 'Climate', 'Power', 'Sensor', 'Lighting'),
    h.home_name;

-- [NV9-Q2] Báo cáo tỷ lệ sức khỏe thiết bị toàn hệ thống
SELECT
    d.status,
    COUNT(*)  AS so_luong,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Device), 2) AS ty_le_phan_tram
FROM Device d
GROUP BY d.status
ORDER BY so_luong DESC;

-- [NV9-Q3] Tìm ngôi nhà cần hỗ trợ kỹ thuật gấp nhất
SELECT
    h.home_name,
    u.full_name,
    u.email,
    u.phone,
    COUNT(d.device_id)    AS so_thiet_bi_hong,
    GROUP_CONCAT(d.device_name ORDER BY d.device_name SEPARATOR ', ')
                          AS danh_sach_hong
FROM Device d
JOIN Home h ON h.home_id = d.home_id
JOIN User u ON u.user_id = h.user_id
WHERE d.status IN ('OFFLINE', 'MAINTENANCE')
GROUP BY h.home_id, h.home_name, u.full_name, u.email, u.phone
ORDER BY so_thiet_bi_hong DESC
LIMIT 5;
```

---

## NGHIỆP VỤ 10: BÁO CÁO TỔNG HỢP KINH DOANH & ĐỐI SOÁT TUÂN THỦ SLA

### 10.1. Mô tả nghiệp vụ
Quản trị viên cần **báo cáo kinh doanh định kỳ**: tổng doanh thu, phân tích tỷ suất chuyển đổi gói cước, và **đối soát chính sách lưu trữ dữ liệu (Data Retention SLA)**. Cụ thể, kiểm tra xem mỗi hợp đồng có đang được lưu đúng số ngày theo gói cước đã mua hay không — yếu tố quan trọng về mặt **pháp lý và cam kết dịch vụ** với khách hàng doanh nghiệp. Áp dụng **Window Function** (`RANK()`) để xếp hạng khách hàng theo giá trị vòng đời.

### 10.2. Cách quản trị
| Thao tác | Bảng liên quan | Kỹ thuật SQL |
|---|---|---|
| KPI tổng quan hệ thống | Tất cả bảng | COUNT DISTINCT, SUM, COALESCE |
| Kiểm tra SLA lưu trữ | `HomeSubscription` + `SubscriptionPlan` | DATEDIFF so với `retention_days`, CASE WHEN |
| Khách hàng VIP theo doanh thu | `Invoice` + `User` | SUM + RANK() Window Function |
| Tỷ lệ gia hạn (Renewal Rate) | `HomeSubscription` | GROUP BY + HAVING `so_lan_mua >= 2` |

### 10.3. Truy vấn SQL

```sql
-- [NV10-Q1] Báo cáo KPI kinh doanh tổng quan (một truy vấn duy nhất)
SELECT
    COUNT(DISTINCT u.user_id)                       AS tong_nguoi_dung,
    COUNT(DISTINCT h.home_id)                       AS tong_nha,
    COUNT(DISTINCT d.device_id)                     AS tong_thiet_bi,
    COUNT(DISTINCT hs.subscription_id)              AS tong_hop_dong,
    COALESCE(SUM(CASE WHEN i.payment_status='SUCCESS'
                      THEN i.amount END), 0)        AS tong_doanh_thu_VND,
    COUNT(DISTINCT CASE WHEN hs.payment_status='PAID'
                        THEN hs.subscription_id END) AS hop_dong_con_hieu_luc
FROM User u
LEFT JOIN Home h              ON h.user_id  = u.user_id
LEFT JOIN Device d            ON d.home_id  = h.home_id
LEFT JOIN HomeSubscription hs ON hs.home_id = h.home_id
LEFT JOIN Invoice i           ON i.subscription_id = hs.subscription_id;

-- [NV10-Q2] Đối soát tuân thủ chính sách lưu trữ (SLA Compliance Check)
SELECT
    hs.subscription_id,
    h.home_name,
    sp.plan_name,
    sp.retention_days              AS cam_ket_luu_tru_ngay,
    DATEDIFF(hs.end_date, hs.start_date) AS thoi_han_thuc_te_ngay,
    hs.payment_status,
    CASE
        WHEN DATEDIFF(hs.end_date, hs.start_date) >= sp.retention_days
        THEN 'TUAN_THU'
        ELSE 'VI_PHAM_SLA'
    END AS ket_qua_kiem_tra
FROM HomeSubscription hs
JOIN Home h              ON h.home_id  = hs.home_id
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
ORDER BY ket_qua_kiem_tra ASC, h.home_name ASC;

-- [NV10-Q3] Top 5 khách hàng đóng góp doanh thu cao nhất (Window Function RANK)
SELECT
    u.full_name,
    u.email,
    SUM(i.amount)        AS tong_chi_tieu,
    COUNT(i.invoice_id)  AS so_lan_thanh_toan,
    RANK() OVER (ORDER BY SUM(i.amount) DESC) AS xep_hang
FROM Invoice i
JOIN User u ON u.user_id = i.user_id
WHERE i.payment_status = 'SUCCESS'
GROUP BY u.user_id, u.full_name, u.email
ORDER BY xep_hang
LIMIT 5;

-- [NV10-Q4] Tỷ lệ gia hạn (Renewal Rate) — nhà đã mua gói từ 2 lần trở lên
SELECT
    h.home_name,
    u.full_name,
    COUNT(hs.subscription_id)  AS so_lan_mua,
    MIN(hs.start_date)         AS lan_dau_dang_ky,
    MAX(hs.end_date)           AS het_han_cuoi,
    SUM(sp.price)              AS tong_gia_tri_khach_hang
FROM HomeSubscription hs
JOIN Home h              ON h.home_id  = hs.home_id
JOIN User u              ON u.user_id  = h.user_id
JOIN SubscriptionPlan sp ON sp.plan_id = hs.plan_id
GROUP BY h.home_id, h.home_name, u.full_name
HAVING so_lan_mua >= 2
ORDER BY tong_gia_tri_khach_hang DESC;
```

---

## TỔNG KẾT 10 NGHIỆP VỤ

| # | Tên nghiệp vụ | Bảng chính | Kỹ thuật SQL nổi bật |
|:---:|---|---|---|
| 1 | Đăng ký & quản lý người dùng | `User` | INSERT, UNIQUE, LEFT JOIN IS NULL |
| 2 | Thêm nhà & phân bổ phòng | `Home`, `Room` | INSERT, CASCADE, GROUP BY |
| 3 | Chia sẻ quyền truy cập nhà | `HomeMember` | Composite PK, FIELD() sort |
| 4 | Lắp đặt & quản lý thiết bị IoT | `Device`, `DeviceType` | JOIN 3 bảng, UPDATE, SET NULL |
| 5 | Tra cứu thiết bị theo tầng/phòng | `Device`, `Room` | COALESCE, LEFT JOIN, SUM |
| 6 | Đăng ký & gia hạn thuê bao | `HomeSubscription` | DATE_ADD, DATEDIFF, BETWEEN |
| 7 | Thanh toán & truy vết hóa đơn | `Invoice` | JOIN 4 bảng, DATE_FORMAT, GROUP BY |
| 8 | Giám sát công suất tiêu thụ điện | `Device`, `DeviceType` | SUM, HAVING, Subquery tỷ lệ % |
| 9 | Phát hiện thiết bị offline & bảo trì | `Device` | CASE WHEN, FIELD(), GROUP_CONCAT |
| 10 | Báo cáo kinh doanh & đối soát SLA | `Invoice`, `HomeSubscription` | RANK() Window Function, COALESCE |
