-- ==========================================================
-- BỘ DỮ LIỆU CHUẨN CHO BẢNG DeviceType VÀ SubscriptionPlan / HomeSubscription
-- Đề tài: Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh
-- Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1 | Học viên: Trần Duy Khải
-- Khớp hoàn toàn với dải khóa ngoại trong:
--   - Bảng Device (type_id từ 1 đến 8)
--   - Bảng HomeSubscription (plan_id từ 1 đến 4)
-- ==========================================================

USE smart_home_info;

-- 1. NẠP DỮ LIỆU DANH MỤC DeviceType (Chủng loại thiết bị chuẩn 3NF)
-- Đảm bảo có đủ type_id từ 1 đến 8 để khớp với 1,000,000 thiết bị trong bảng Device
INSERT INTO DeviceType (type_id, type_name, category, rated_power_watts, manufacturer)
VALUES
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
    (12, 'Động cơ rèm thông minh tự động', 'Lighting', 45.00, 'Somfy')
ON DUPLICATE KEY UPDATE
    type_name = VALUES(type_name),
    category = VALUES(category),
    rated_power_watts = VALUES(rated_power_watts),
    manufacturer = VALUES(manufacturer);


-- 2. NẠP DỮ LIỆU BẢNG SubscriptionPlan (Các gói cước dịch vụ IoT Cloud)
-- Đảm bảo có đủ plan_id từ 1 đến 4 để khớp với bảng HomeSubscription
INSERT INTO SubscriptionPlan (plan_id, plan_name, price, retention_days)
VALUES
    (1, 'Gói Miễn phí (Free Tier)', 0.00, 7),
    (2, 'Gói Cơ bản (Standard Cloud)', 99000.00, 30),
    (3, 'Gói Nâng cao (Premium Pro)', 199000.00, 90),
    (4, 'Gói Doanh nghiệp (Enterprise Lifetime)', 499000.00, 365),
    (5, 'Gói Chuyên gia Năng lượng (Energy Saver AI)', 149000.00, 60)
ON DUPLICATE KEY UPDATE
    plan_name = VALUES(plan_name),
    price = VALUES(price),
    retention_days = VALUES(retention_days);


-- 3. DỮ LIỆU MẪU CHO BẢNG HomeSubscription (Dành cho kiểm thử mẫu nếu chưa nạp file lớn)
-- Ghi chú: Nếu đã nạp file lớn bulk_data/home_subscriptions.csv (1,000,000 dòng),
-- đoạn script này sử dụng INSERT IGNORE để không gây lỗi duplicate key.
INSERT IGNORE INTO HomeSubscription (subscription_id, home_id, plan_id, start_date, end_date, payment_status)
VALUES
    (1, 1, 2, '2025-01-10', '2025-02-10', 'PAID'),
    (2, 2, 3, '2025-01-15', '2025-04-15', 'PAID'),
    (3, 3, 1, '2025-02-01', '2025-03-01', 'EXPIRED'),
    (4, 4, 4, '2025-01-01', '2026-01-01', 'PAID'),
    (5, 5, 2, '2025-02-15', '2025-03-15', 'PENDING');


-- ==========================================================
-- ĐỐI SOÁT DỮ LIỆU SAU KHI NẠP:
-- ==========================================================
SELECT 'DeviceType' AS TableName, COUNT(*) AS TotalRows FROM DeviceType
UNION ALL
SELECT 'SubscriptionPlan', COUNT(*) FROM SubscriptionPlan
UNION ALL
SELECT 'HomeSubscription', COUNT(*) FROM HomeSubscription;

SELECT * FROM DeviceType;
SELECT * FROM SubscriptionPlan;
