USE smart_home_info;

-- ==========================================================
-- KIỂM TRA TỔNG SỐ BẢN GHI CỦA TẤT CẢ 9 BẢNG TRONG MÔ HÌNH
-- ==========================================================
SELECT 'User' AS table_name, COUNT(*) AS total_rows FROM User
UNION ALL
SELECT 'Home', COUNT(*) FROM Home
UNION ALL
SELECT 'HomeMember', COUNT(*) FROM HomeMember
UNION ALL
SELECT 'Room', COUNT(*) FROM Room
UNION ALL
SELECT 'DeviceType', COUNT(*) FROM DeviceType
UNION ALL
SELECT 'Device', COUNT(*) FROM Device
UNION ALL
SELECT 'SubscriptionPlan', COUNT(*) FROM SubscriptionPlan
UNION ALL
SELECT 'HomeSubscription', COUNT(*) FROM HomeSubscription
UNION ALL
SELECT 'Invoice', COUNT(*) FROM Invoice;