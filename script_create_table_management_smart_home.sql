CREATE DATABASE if not exists smart_home_info;
USE smart_home_info;
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Home (
    home_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    home_name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Room (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    home_id INT NOT NULL,
    room_name VARCHAR(100) NOT NULL,
    floor INT DEFAULT 1,
    FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE
);

CREATE TABLE DeviceType (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    default_power_rating DECIMAL(6,2),
    manufacturer VARCHAR(100)
);

CREATE TABLE Device (
    device_id INT PRIMARY KEY AUTO_INCREMENT,
    room_id INT NOT NULL,
    type_id INT NOT NULL,
    device_name VARCHAR(100) NOT NULL,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    mac_address VARCHAR(50) NOT NULL UNIQUE,
    firmware_version VARCHAR(30),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES DeviceType(type_id) ON DELETE RESTRICT
);

CREATE TABLE SubscriptionPlan (
    plan_id INT PRIMARY KEY AUTO_INCREMENT,
    plan_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    retention_days INT NOT NULL
);

CREATE TABLE HomeSubscription (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    home_id INT NOT NULL,
    plan_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'PENDING',
    FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES SubscriptionPlan(plan_id) ON DELETE RESTRICT
);
device
-- ==========================================================
-- 1. BẢNG User (15 người dùng)
-- ==========================================================
INSERT INTO User (user_id, full_name, email, password_hash, phone, created_at) VALUES
(1, 'Nguyen Van An', 'an.nguyen@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash1', '0905123456', '2025-01-10 08:30:00'),
(2, 'Tran Thi Binh', 'binh.tran@yahoo.com', '$2a$12$e8Y7z6aK.d0bQ...hash2', '0914234567', '2025-01-15 09:15:00'),
(3, 'Le Quoc Cuong', 'cuong.le@outlook.com', '$2a$12$e8Y7z6aK.d0bQ...hash3', '0988345678', '2025-02-01 10:00:00'),
(4, 'Pham Minh Duc', 'duc.pham@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash4', '0935456789', '2025-02-12 11:20:00'),
(5, 'Hoang Ngoc Dung', 'dung.hoang@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash5', '0903567890', '2025-02-20 14:05:00'),
(6, 'Vo Thanh Giang', 'giang.vo@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash6', '0977678901', '2025-03-05 16:45:00'),
(7, 'Dang Thi Hoa', 'hoa.dang@hotmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash7', '0918789012', '2025-03-18 08:10:00'),
(8, 'Bui Quang Huy', 'huy.bui@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash8', '0945890123', '2025-04-02 13:30:00'),
(9, 'Doan Hong Khanh', 'khanh.doan@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash9', '0908901234', '2025-04-15 15:20:00'),
(10, 'Ngo Gia Long', 'long.ngo@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash10', '0932012345', '2025-05-01 09:00:00'),
(11, 'Duong My Linh', 'linh.duong@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash11', '0961123456', '2025-05-20 10:40:00'),
(12, 'Phan Tuan Kiet', 'kiet.phan@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash12', '0983234567', '2025-06-02 17:15:00'),
(13, 'Vu Dinh Nam', 'nam.vu@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash13', '0919345678', '2025-06-18 12:00:00'),
(14, 'Dinh Thi Oanh', 'oanh.dinh@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash14', '0909456789', '2025-07-04 14:25:00'),
(15, 'Truong Minh Phuc', 'phuc.truong@gmail.com', '$2a$12$e8Y7z6aK.d0bQ...hash15', '0975567890', '2025-07-22 18:30:00');

-- ==========================================================
-- 2. BẢNG DeviceType (8 chủng loại thiết bị)
-- ==========================================================
INSERT INTO DeviceType (type_id, type_name, category, default_power_rating, manufacturer) VALUES
(1, 'Smart Switch 2-Gang', 'Lighting', 10.00, 'Tuya Smart'),
(2, 'Smart Switch 4-Gang', 'Lighting', 15.00, 'Aqara'),
(3, 'Air Conditioner Inverter 1.5HP', 'Climate', 1200.00, 'Daikin'),
(4, 'Air Conditioner Inverter 2.0HP', 'Climate', 1800.00, 'Panasonic'),
(5, 'Smart Thermostat & Humidity', 'Sensor', 2.50, 'Xiaomi'),
(6, 'Motion & Lux Sensor', 'Sensor', 1.50, 'Philips Hue'),
(7, 'Smart Door Lock FaceID', 'Security', 25.00, 'Yale'),
(8, 'Smart IP Camera 2K AI', 'Security', 12.00, 'Ezviz');

-- ==========================================================
-- 3. BẢNG SubscriptionPlan (4 gói cước)
-- ==========================================================
INSERT INTO SubscriptionPlan (plan_id, plan_name, price, retention_days) VALUES
(1, 'Gói Miễn phí (Free Tier)', 0.00, 7),
(2, 'Gói Cơ bản (Standard Cloud)', 99000.00, 30),
(3, 'Gói Nâng cao (Premium Pro)', 199000.00, 90),
(4, 'Gói Doanh nghiệp (Enterprise Lifetime)', 499000.00, 365);

-- ==========================================================
-- 4. BẢNG Home (16 căn nhà/căn hộ)
-- ==========================================================
INSERT INTO Home (home_id, user_id, home_name, address, created_at) VALUES
(1, 1, 'Nhà phố Thanh Khê', '105 Dien Bien Phu, Thanh Khe, Da Nang', '2025-01-11 10:00:00'),
(2, 1, 'Villa nghỉ dưỡng Hội An', '48 Cua Dai, Cam Chau, Hoi An', '2025-03-01 14:00:00'),
(3, 2, 'Căn hộ HAGL Danang', '72 Ham Nghi, Thanh Khe, Da Nang', '2025-01-16 09:30:00'),
(4, 3, 'Biệt thự Đảo Kim Cương', 'Số 1 Duong 104, BTT, Quan 2, TP.HCM', '2025-02-02 11:00:00'),
(5, 4, 'Chung cư Vinhomes Central Park', '208 Nguyen Huu Canh, Binh Thanh, TP.HCM', '2025-02-13 14:20:00'),
(6, 5, 'Nhà phố Ba Đình', '14 Doi Can, Ba Dinh, Ha Noi', '2025-02-21 16:10:00'),
(7, 6, 'Penthouse The Manor', 'Me Tri, Nam Tu Liem, Ha Noi', '2025-03-06 17:00:00'),
(8, 7, 'Căn hộ Masteri Thảo Điền', '159 Xa Lo Ha Noi, Quan 2, TP.HCM', '2025-03-19 09:15:00'),
(9, 8, 'Nhà vườn Cẩm Lệ', '22 CMT8, Cam Le, Da Nang', '2025-04-03 15:40:00'),
(10, 9, 'Chung cư Sunrise City', '23 Nguyen Huu Tho, Tan Hung, Quan 7, TP.HCM', '2025-04-16 10:30:00'),
(11, 10, 'Nhà phố Tây Hồ', '88 Xuan Dieu, Tay Ho, Ha Noi', '2025-05-02 11:45:00'),
(12, 11, 'Căn hộ Sơn Trà Ocean View', '95 Ngo Quyen, Son Tra, Da Nang', '2025-05-21 13:00:00'),
(13, 12, 'Nhà riêng Hải Châu', '12 Tran Phu, Hai Chau, Da Nang', '2025-06-03 18:00:00'),
(14, 13, 'Căn hộ Ecopark Sky Oasis', 'Van Giang, Hung Yen', '2025-06-19 14:10:00'),
(15, 14, 'Nhà phố Gò Vấp', '55 Quang Trung, Go Vap, TP.HCM', '2025-07-05 16:30:00'),
(16, 15, 'Biệt thự Vinhome Riverside', 'Hoa Lan 2, Long Bien, Ha Noi', '2025-07-23 19:00:00');

-- ==========================================================
-- 5. BẢNG Room (25 phòng)
-- ==========================================================
INSERT INTO Room (room_id, home_id, room_name, floor) VALUES
(1, 1, 'Phòng Khách T1', 1),
(2, 1, 'Bếp & Phòng Ăn', 1),
(3, 1, 'Phòng Ngủ Master', 2),
(4, 2, 'Sảnh Tiếp Khách', 1),
(5, 2, 'Phòng Ngủ Bungalow', 1),
(6, 3, 'Living Room', 1),
(7, 3, 'Master Bedroom', 1),
(8, 4, 'Phòng Khách Sang Trọng', 1),
(9, 4, 'Bếp Hiện Đại', 1),
(10, 4, 'Phòng Ngủ VIP', 2),
(11, 5, 'Phòng Sinh Hoạt Chung', 1),
(12, 5, 'Phòng Làm Việc', 1),
(13, 6, 'Phòng Khách Tầng Trệt', 1),
(14, 7, 'Khu Vực Giải Trí', 1),
(15, 8, 'Phòng Khách Studio', 1),
(16, 9, 'Gian Nhà Chính', 1),
(17, 10, 'Phòng Sinh Hoạt', 1),
(18, 11, 'Phòng Khách Hồ Tây', 1),
(19, 12, 'Phòng Khách View Biển', 1),
(20, 12, 'Phòng Ngủ 01', 1),
(21, 13, 'Phòng Khách Lớn', 1),
(22, 14, 'Phòng Khách Ban Công', 1),
(23, 15, 'Phòng Khách Trước', 1),
(24, 16, 'Đại Sảnh', 1),
(25, 16, 'Phòng Rượu & Thư Viện', 2);

-- ==========================================================
-- 6. BẢNG HomeSubscription (18 giao dịch thuê bao)
-- ==========================================================
INSERT INTO HomeSubscription (subscription_id, home_id, plan_id, start_date, end_date, payment_status) VALUES
(1, 1, 2, '2025-01-15', '2025-02-15', 'PAID'),
(2, 1, 3, '2025-02-15', '2025-05-15', 'PAID'),
(3, 2, 3, '2025-03-05', '2025-06-05', 'PAID'),
(4, 3, 1, '2025-01-20', '2025-02-20', 'EXPIRED'),
(5, 3, 2, '2025-02-21', '2025-03-21', 'PAID'),
(6, 4, 4, '2025-02-05', '2026-02-05', 'PAID'),
(7, 5, 2, '2025-02-15', '2025-03-15', 'PAID'),
(8, 6, 2, '2025-02-25', '2025-03-25', 'EXPIRED'),
(9, 7, 3, '2025-03-10', '2025-06-10', 'PAID'),
(10, 8, 1, '2025-03-20', '2025-04-20', 'EXPIRED'),
(11, 9, 2, '2025-04-05', '2025-05-05', 'PAID'),
(12, 10, 2, '2025-04-20', '2025-05-20', 'PENDING'),
(13, 11, 3, '2025-05-05', '2025-08-05', 'PAID'),
(14, 12, 2, '2025-05-25', '2025-06-25', 'PAID'),
(15, 13, 1, '2025-06-05', '2025-07-05', 'EXPIRED'),
(16, 14, 2, '2025-06-20', '2025-07-20', 'PAID'),
(17, 15, 2, '2025-07-10', '2025-08-10', 'PENDING'),
(18, 16, 4, '2025-07-25', '2026-07-25', 'PAID');

-- ==========================================================
-- 7. BẢNG Device (30 thiết bị vật lý đa dạng chủng loại)
-- ==========================================================
INSERT INTO Device (device_id, room_id, type_id, device_name, serial_number, mac_address, firmware_version, status, installed_at) VALUES
(1, 1, 1, 'Công tắc đèn trần PK', 'SN-TY-00101', 'AA:BB:CC:11:22:01', 'v2.1.0', 'ACTIVE', '2025-01-12 10:00:00'),
(2, 1, 3, 'Điều hòa Daikin PK', 'SN-DK-00201', 'AA:BB:CC:11:22:02', 'v1.4.2', 'ACTIVE', '2025-01-12 11:30:00'),
(3, 1, 8, 'Camera an ninh PK', 'SN-EZ-00301', 'AA:BB:CC:11:22:03', 'v5.0.1', 'ACTIVE', '2025-01-12 14:00:00'),
(4, 2, 5, 'Cảm biến nhiệt ẩm Bếp', 'SN-XM-00401', 'AA:BB:CC:11:22:04', 'v1.0.8', 'ACTIVE', '2025-01-13 09:00:00'),
(5, 2, 1, 'Công tắc đèn bếp', 'SN-TY-00102', 'AA:BB:CC:11:22:05', 'v2.1.0', 'ACTIVE', '2025-01-13 09:30:00'),
(6, 3, 3, 'Điều hòa PN Master', 'SN-DK-00202', 'AA:BB:CC:11:22:06', 'v1.4.2', 'ACTIVE', '2025-01-14 15:00:00'),
(7, 3, 6, 'Cảm biến chuyển động PN', 'SN-PH-00501', 'AA:BB:CC:11:22:07', 'v3.2.0', 'OFFLINE', '2025-01-14 16:20:00'),
(8, 4, 2, 'Công tắc 4 nút Villa', 'SN-AQ-00601', 'AA:BB:CC:11:22:08', 'v2.0.4', 'ACTIVE', '2025-03-02 08:30:00'),
(9, 4, 7, 'Khóa thông minh cửa chính', 'SN-YL-00701', 'AA:BB:CC:11:22:09', 'v4.1.2', 'ACTIVE', '2025-03-02 09:45:00'),
(10, 5, 4, 'Điều hòa Panasonic Bungalow', 'SN-PN-00801', 'AA:BB:CC:11:22:10', 'v2.0.0', 'ACTIVE', '2025-03-02 11:00:00'),
(11, 6, 1, 'Công tắc PK HAGL', 'SN-TY-00103', 'AA:BB:CC:11:22:11', 'v2.1.0', 'ACTIVE', '2025-01-17 10:00:00'),
(12, 6, 8, 'Ezviz Camera Cửa Ra Vào', 'SN-EZ-00302', 'AA:BB:CC:11:22:12', 'v5.0.1', 'ACTIVE', '2025-01-17 11:15:00'),
(13, 7, 3, 'Điều hòa Daikin PN HAGL', 'SN-DK-00203', 'AA:BB:CC:11:22:13', 'v1.4.2', 'ACTIVE', '2025-01-18 14:00:00'),
(14, 8, 2, 'Aqara Switch Sảnh VIP', 'SN-AQ-00602', 'AA:BB:CC:11:22:14', 'v2.0.4', 'ACTIVE', '2025-02-03 09:00:00'),
(15, 8, 4, 'Điều hòa Panasonic PK VIP', 'SN-PN-00802', 'AA:BB:CC:11:22:15', 'v2.0.0', 'ACTIVE', '2025-02-03 10:30:00'),
(16, 8, 7, 'Khóa cửa vân tay Yale Đảo KC', 'SN-YL-00702', 'AA:BB:CC:11:22:16', 'v4.1.2', 'ACTIVE', '2025-02-03 14:00:00'),
(17, 9, 5, 'Cảm biến môi trường Bếp VIP', 'SN-XM-00402', 'AA:BB:CC:11:22:17', 'v1.0.8', 'ACTIVE', '2025-02-04 15:00:00'),
(18, 10, 4, 'Điều hòa 2.0HP PN VIP', 'SN-PN-00803', 'AA:BB:CC:11:22:18', 'v2.0.0', 'MAINTENANCE', '2025-02-04 16:30:00'),
(19, 11, 1, 'Công tắc Vinhomes CP', 'SN-TY-00104', 'AA:BB:CC:11:22:19', 'v2.1.0', 'ACTIVE', '2025-02-14 10:00:00'),
(20, 12, 6, 'Cảm biến chuyển động P.Làm việc', 'SN-PH-00502', 'AA:BB:CC:11:22:20', 'v3.2.0', 'ACTIVE', '2025-02-14 14:00:00'),
(21, 13, 8, 'Ezviz Camera Hà Nội', 'SN-EZ-00303', 'AA:BB:CC:11:22:21', 'v5.0.1', 'ACTIVE', '2025-02-22 11:00:00'),
(22, 14, 2, 'Công tắc Aqara The Manor', 'SN-AQ-00603', 'AA:BB:CC:11:22:22', 'v2.0.4', 'ACTIVE', '2025-03-07 15:30:00'),
(23, 16, 1, 'Công tắc Nhà Vườn Cẩm Lệ', 'SN-TY-00105', 'AA:BB:CC:11:22:23', 'v2.1.0', 'OFFLINE', '2025-04-04 09:30:00'),
(24, 18, 3, 'Điều hòa Daikin Hồ Tây', 'SN-DK-00204', 'AA:BB:CC:11:22:24', 'v1.4.2', 'ACTIVE', '2025-05-03 10:00:00'),
(25, 19, 7, 'Khóa vân tay Căn hộ Sơn Trà', 'SN-YL-00703', 'AA:BB:CC:11:22:25', 'v4.1.2', 'ACTIVE', '2025-05-22 14:00:00'),
(26, 19, 8, 'Camera Ezviz View Biển', 'SN-EZ-00304', 'AA:BB:CC:11:22:26', 'v5.0.1', 'ACTIVE', '2025-05-22 15:00:00'),
(27, 21, 1, 'Công tắc Hải Châu', 'SN-TY-00106', 'AA:BB:CC:11:22:27', 'v2.1.0', 'ACTIVE', '2025-06-04 11:00:00'),
(28, 23, 1, 'Công tắc Gò Vấp', 'SN-TY-00107', 'AA:BB:CC:11:22:28', 'v2.1.0', 'ACTIVE', '2025-07-06 10:30:00'),
(29, 24, 2, 'Aqara Switch Riverside', 'SN-AQ-00604', 'AA:BB:CC:11:22:29', 'v2.0.4', 'ACTIVE', '2025-07-24 14:30:00'),
(30, 25, 8, 'Camera Hầm Rượu Riverside', 'SN-EZ-00305', 'AA:BB:CC:11:22:30', 'v5.0.1', 'ACTIVE', '2025-07-24 16:00:00');