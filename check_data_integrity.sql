USE smart_home_info;

SELECT 'User' AS table_name, COUNT(*) AS total_rows FROM User
UNION ALL
SELECT 'Home', COUNT(*) FROM Home
UNION ALL
SELECT 'Room', COUNT(*) FROM Room
UNION ALL
SELECT 'DeviceType', COUNT(*) FROM DeviceType
UNION ALL
SELECT 'Device', COUNT(*) FROM Device
UNION ALL
SELECT 'SubscriptionPlan', COUNT(*) FROM SubscriptionPlan
UNION ALL
SELECT 'HomeSubscription', COUNT(*) FROM HomeSubscription;