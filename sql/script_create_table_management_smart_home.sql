-- ==========================================================
-- BÀI TẬP CÁ NHÂN: HỆ THỐNG GIÁM SÁT & QUẢN LÝ THIẾT BỊ IoT NHÀ THÔNG MINH
-- Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1
-- Học viên: Trần Duy Khải
-- Mô hình Cơ sở Dữ liệu Quan hệ (RDBMS MySQL) - Chuẩn 3NF
-- Phiên bản cập nhật theo tài liệu CSDLNC_G1.docx
-- ==========================================================

DROP DATABASE IF EXISTS smart_home_info;
CREATE DATABASE smart_home_info CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_home_info;

-- ==========================================================
-- 1. BẢNG User (Người dùng / Chủ tài khoản)
-- ==========================================================
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==========================================================
-- 2. BẢNG Home (Ngôi nhà / Bất động sản / Căn hộ)
-- Mối quan hệ: User — Home (1:N): Một chủ sở hữu (user_id) có nhiều nhà.
-- ==========================================================
CREATE TABLE Home (
    home_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    home_name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- ==========================================================
-- 3. BẢNG HomeMember (Quan hệ N:N giữa User và Home)
-- Đạt chuẩn 2NF: Khóa chính phức hợp (home_id, user_id).
-- Các thuộc tính role, joined_at phụ thuộc vào cả cặp khóa.
-- ==========================================================
CREATE TABLE HomeMember (
    home_id INT NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'MEMBER' COMMENT 'ADMIN, MEMBER, GUEST',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (home_id, user_id),
    FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- ==========================================================
-- 4. BẢNG Room (Khu vực / Phòng chức năng trong nhà)
-- Mối quan hệ: Home — Room (1:N): Mỗi phòng thuộc về một căn nhà duy nhất.
-- ==========================================================
CREATE TABLE Room (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    home_id INT NOT NULL,
    room_name VARCHAR(100) NOT NULL,
    floor INT DEFAULT 1,
    FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE
);

-- ==========================================================
-- 5. BẢNG DeviceType (Danh mục quy chuẩn chủng loại thiết bị)
-- Đạt chuẩn 3NF: Tách riêng ra khỏi Device để loại bỏ phụ thuộc bắc cầu
-- (Công suất danh định và hãng sản xuất phụ thuộc vào loại thiết bị).
-- ==========================================================
CREATE TABLE DeviceType (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL COMMENT 'Lighting, Climate, Sensor, Security, Power',
    rated_power_watts DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    manufacturer VARCHAR(100) NOT NULL
);

-- ==========================================================
-- 6. BẢNG Device (Thiết bị IoT vật lý cụ thể)
-- Mối quan hệ:
--   - Home — Device (1:N): Mỗi thiết bị bắt buộc thuộc 1 nhà (ON DELETE CASCADE)
--   - Room — Device (1:N, tùy chọn): Cho phép NULL nếu là thiết bị ngoài trời / chưa phân bổ (ON DELETE SET NULL)
--   - DeviceType — Device (1:N): Mỗi thiết bị thuộc 1 chủng loại chuẩn (ON DELETE RESTRICT)
-- ==========================================================
CREATE TABLE Device (
    device_id INT PRIMARY KEY AUTO_INCREMENT,
    home_id INT NOT NULL,
    room_id INT NULL,
    type_id INT NOT NULL,
    device_name VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    mac_address VARCHAR(50) NOT NULL UNIQUE,
    firmware_version VARCHAR(30) DEFAULT 'v1.0.0',
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT 'ACTIVE, OFFLINE, MAINTENANCE',
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE SET NULL,
    FOREIGN KEY (type_id) REFERENCES DeviceType(type_id) ON DELETE RESTRICT
);

-- ==========================================================
-- 7. BẢNG SubscriptionPlan (Các gói dịch vụ lưu trữ / phân tích dữ liệu)
-- ==========================================================
CREATE TABLE SubscriptionPlan (
    plan_id INT PRIMARY KEY AUTO_INCREMENT,
    plan_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    retention_days INT NOT NULL DEFAULT 7
);

-- ==========================================================
-- 8. BẢNG HomeSubscription (Hợp đồng thuê bao gói dịch vụ của từng ngôi nhà)
-- Mối quan hệ N:N giữa Home và SubscriptionPlan
-- ==========================================================
CREATE TABLE HomeSubscription (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    home_id INT NOT NULL,
    plan_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING, PAID, EXPIRED, CANCELLED',
    FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES SubscriptionPlan(plan_id) ON DELETE RESTRICT
);

-- ==========================================================
-- 9. BẢNG Invoice (Hóa đơn thanh toán thuê bao)
-- Đạt chuẩn 3NF: Tách riêng khỏi HomeSubscription vì thông tin giao dịch
-- thanh toán phụ thuộc vào người chi trả cụ thể (user_id) và thời điểm phát sinh.
-- ==========================================================
CREATE TABLE Invoice (
    invoice_id INT PRIMARY KEY AUTO_INCREMENT,
    subscription_id INT NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'VNPAY' COMMENT 'VNPAY, MOMO, CREDIT_CARD, BANK_TRANSFER',
    payment_status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS' COMMENT 'SUCCESS, FAILED, REFUNDED',
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES HomeSubscription(subscription_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- ==========================================================
-- 10. DỮ LIỆU DANH MỤC QUY CHUẨN BAN ĐẦU (SEED REFERENCE DATA)
-- Khớp hoàn toàn với dải khóa ngoại của Device và HomeSubscription
-- ==========================================================

-- 10.1. Dữ liệu chuẩn cho DeviceType (type_id từ 1 đến 8 được Device tham chiếu)
INSERT INTO DeviceType (type_id, type_name, category, rated_power_watts, manufacturer) VALUES
(1, 'Công tắc thông minh 2 nút (Smart Switch 2-Gang)', 'Lighting', 10.00, 'Tuya Smart'),
(2, 'Công tắc thông minh 4 nút (Smart Switch 4-Gang)', 'Lighting', 15.00, 'Aqara'),
(3, 'Điều hòa không khí Inverter 1.5HP', 'Climate', 1200.00, 'Daikin'),
(4, 'Điều hòa không khí Inverter 2.0HP', 'Climate', 1800.00, 'Panasonic'),
(5, 'Cảm biến nhiệt độ & độ ẩm không dây', 'Sensor', 2.50, 'Xiaomi'),
(6, 'Cảm biến chuyển động & ánh sáng (Motion/Lux)', 'Sensor', 1.50, 'Philips Hue'),
(7, 'Khóa cửa thông minh FaceID & Vân tay', 'Security', 25.00, 'Yale'),
(8, 'Camera an ninh AI 2K góc rộng', 'Security', 12.00, 'Ezviz'),
(9, 'Ổ cắm thông minh đo điện năng tiêu thụ', 'Power', 5.00, 'Sonoff'),
(10, 'Bộ điều khiển bình nóng lạnh thông minh', 'Power', 2500.00, 'Ariston'),
(11, 'Cảm biến khói và khí gas thông minh', 'Sensor', 3.00, 'Honeywell'),
(12, 'Động cơ rèm thông minh tự động', 'Lighting', 45.00, 'Somfy');

-- 10.2. Dữ liệu chuẩn cho SubscriptionPlan (plan_id từ 1 đến 4 được HomeSubscription tham chiếu)
INSERT INTO SubscriptionPlan (plan_id, plan_name, price, retention_days) VALUES
(1, 'Gói Miễn phí (Free Tier)', 0.00, 7),
(2, 'Gói Cơ bản (Standard Cloud)', 99000.00, 30),
(3, 'Gói Nâng cao (Premium Pro)', 199000.00, 90),
(4, 'Gói Doanh nghiệp (Enterprise Lifetime)', 499000.00, 365),
(5, 'Gói Chuyên gia Năng lượng (Energy Saver AI)', 149000.00, 60);