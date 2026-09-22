-- ==========================================================
-- SCRIPT NẠP 1 TRIỆU BẢN GHI (1,000,000 ROWS) TỐC ĐỘ CAO VÀO MYSQL
-- Đề tài: Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh
-- Môn học: Cơ sở Dữ liệu Nâng cao | Học viên: Trần Duy Khải
-- 
-- SỬ DỤNG THƯ MỤC AN TOÀN CHUẨN CỦA MYSQL SERVER:
-- C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/
-- (Tránh hoàn toàn lỗi Error Code 2068 & 1292 & Warning '\r')
-- ==========================================================

USE smart_home_info;

-- TỐI ƯU HÓA HIỆU NĂNG CHO DỮ LIỆU LỚN (BIG DATA INGESTION)
COMMIT;
SET SESSION wait_timeout = 3600;
SET SESSION interactive_timeout = 3600;
SET SESSION net_read_timeout = 3600;
SET SESSION net_write_timeout = 3600;
SET autocommit = 0;
SET unique_checks = 0;
SET foreign_key_checks = 0;

-- LÀM SẠCH NHANH DỮ LIỆU CŨ TRONG 0.01 GIÂY (TRÁNH LỖI DUPLICATE & TRÁNH NGHẼN REPLACE)
TRUNCATE TABLE Invoice;
TRUNCATE TABLE HomeSubscription;
TRUNCATE TABLE Device;
TRUNCATE TABLE Room;
TRUNCATE TABLE HomeMember;
TRUNCATE TABLE Home;
TRUNCATE TABLE User;
TRUNCATE TABLE DeviceType;
TRUNCATE TABLE SubscriptionPlan;
COMMIT;

SELECT '=== BẮT ĐẦU NẠP DỮ LIỆU LỚN (ĐẦY ĐỦ 9 BẢNG) ===' AS status;

-- 0.1 Nạp bảng quy chuẩn DeviceType
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/device_types.csv'
REPLACE INTO TABLE DeviceType
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(type_id, type_name, category, rated_power_watts, manufacturer);
COMMIT;
SELECT '-> Đã nạp xong bảng DeviceType' AS progress;

-- 0.2 Nạp bảng quy chuẩn SubscriptionPlan
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/subscription_plans.csv'
REPLACE INTO TABLE SubscriptionPlan
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(plan_id, plan_name, price, retention_days);
COMMIT;
SELECT '-> Đã nạp xong bảng SubscriptionPlan' AS progress;

-- 1. Nạp bảng User (1,000,000 dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/users.csv'
INTO TABLE User
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(user_id, full_name, email, phone, password_hash, created_at, updated_at);
COMMIT;
SELECT '-> Đã nạp xong bảng User' AS progress;

-- 2. Nạp bảng Home (1,000,000 dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/homes.csv'
INTO TABLE Home
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(home_id, user_id, home_name, address, created_at, updated_at);
COMMIT;
SELECT '-> Đã nạp xong bảng Home' AS progress;

-- 3. Nạp bảng HomeMember (1,000,000 dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/home_members.csv'
INTO TABLE HomeMember
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(home_id, user_id, role, joined_at);
COMMIT;
SELECT '-> Đã nạp xong bảng HomeMember' AS progress;

-- 4. Nạp bảng Room (1,000,000 dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/rooms.csv'
INTO TABLE Room
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(room_id, home_id, room_name, floor);
COMMIT;
SELECT '-> Đã nạp xong bảng Room' AS progress;

-- 5. Nạp bảng Device (1,000,000 dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/devices.csv'
INTO TABLE Device
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(device_id, home_id, @room_id, type_id, device_name, serial_number, mac_address, firmware_version, status, installed_at)
SET room_id = NULLIF(@room_id, '\\N');
COMMIT;
SELECT '-> Đã nạp xong bảng Device' AS progress;

-- 6. Nạp bảng HomeSubscription (1,000,000 dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/home_subscriptions.csv'
INTO TABLE HomeSubscription
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(subscription_id, home_id, plan_id, start_date, end_date, payment_status);
COMMIT;
SELECT '-> Đã nạp xong bảng HomeSubscription' AS progress;

-- 7. Nạp bảng Invoice (1,000,000 dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/invoices.csv'
INTO TABLE Invoice
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(invoice_id, subscription_id, user_id, amount, payment_method, payment_status, paid_at);
COMMIT;
SELECT '-> Đã nạp xong bảng Invoice' AS progress;

-- BẬT LẠI CÁC RÀNG BUỘC TOÀN VẸN
SET foreign_key_checks = 1;
SET unique_checks = 1;
SET autocommit = 1;

SELECT '=== HOÀN TẤT QUÁ TRÌNH NẠP DỮ LIỆU LỚN THÀNH CÔNG ===' AS final_status;

-- KIỂM TRA ĐỐI SOÁT TỔNG SỐ BẢN GHI
SELECT 'User' AS table_name, COUNT(*) AS total_rows FROM User
UNION ALL SELECT 'Home', COUNT(*) FROM Home
UNION ALL SELECT 'HomeMember', COUNT(*) FROM HomeMember
UNION ALL SELECT 'Room', COUNT(*) FROM Room
UNION ALL SELECT 'DeviceType', COUNT(*) FROM DeviceType
UNION ALL SELECT 'Device', COUNT(*) FROM Device
UNION ALL SELECT 'SubscriptionPlan', COUNT(*) FROM SubscriptionPlan
UNION ALL SELECT 'HomeSubscription', COUNT(*) FROM HomeSubscription
UNION ALL SELECT 'Invoice', COUNT(*) FROM Invoice;
