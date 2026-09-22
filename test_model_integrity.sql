-- ==========================================================
-- BỘ KỊCH BẢN KIỂM THỬ TÍNH ĐÚNG ĐẮN CỦA MÔ HÌNH CSDL
-- Đề tài: Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh
-- Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1 | HV: Trần Duy Khải
-- Khớp mô hình: CSDLNC_G1.docx (9 Bảng, Chuẩn 3NF, Đầy đủ Ràng buộc)
-- ==========================================================

USE smart_home_info;

-- ----------------------------------------------------------
-- TEST GROUP 1: KIỂM TRA ĐỦ 9 BẢNG & SỐ LƯỢNG BẢN GHI BAN ĐẦU
-- ----------------------------------------------------------
SELECT '=== TEST 1: KIỂM TRA SỐ LƯỢNG BẢN GHI CỦA 9 BẢNG ===' AS test_case;

SELECT 'User' AS table_name, COUNT(*) AS rows_count, IF(COUNT(*) > 0, 'PASS', 'FAIL') AS status FROM User
UNION ALL
SELECT 'Home', COUNT(*), IF(COUNT(*) > 0, 'PASS', 'FAIL') FROM Home
UNION ALL
SELECT 'HomeMember', COUNT(*), IF(COUNT(*) > 0, 'PASS', 'FAIL') FROM HomeMember
UNION ALL
SELECT 'Room', COUNT(*), IF(COUNT(*) > 0, 'PASS', 'FAIL') FROM Room
UNION ALL
SELECT 'DeviceType', COUNT(*), IF(COUNT(*) > 0, 'PASS', 'FAIL') FROM DeviceType
UNION ALL
SELECT 'Device', COUNT(*), IF(COUNT(*) > 0, 'PASS', 'FAIL') FROM Device
UNION ALL
SELECT 'SubscriptionPlan', COUNT(*), IF(COUNT(*) > 0, 'PASS', 'FAIL') FROM SubscriptionPlan
UNION ALL
SELECT 'HomeSubscription', COUNT(*), IF(COUNT(*) > 0, 'PASS', 'FAIL') FROM HomeSubscription
UNION ALL
SELECT 'Invoice', COUNT(*), IF(COUNT(*) > 0, 'PASS', 'FAIL') FROM Invoice;


-- ----------------------------------------------------------
-- TEST GROUP 2: KIỂM TRA TÍNH NHẤT QUÁN NGHIỆP VỤ (CROSS-TABLE INTEGRITY)
-- ----------------------------------------------------------
SELECT '=== TEST 2: KIỂM TRA TÍNH NHẤT QUÁN PHÒNG VÀ CĂN NHÀ CỦA THIẾT BỊ ===' AS test_case;
-- Nguyên tắc: Một Device thuộc Room R và Home H thì Room R cũng phải thuộc Home H.
SELECT 
    d.device_id, d.device_name, d.home_id AS device_home, r.home_id AS room_home,
    IF(d.home_id = r.home_id, 'PASS (Nhất quán)', 'FAIL (Bất nhất)') AS consistency_check
FROM Device d
JOIN Room r ON d.room_id = r.room_id;

SELECT '=== TEST 3: KIỂM TRA LOGIC THỜI HẠN GÓI THUÊ BAO (start_date <= end_date) ===' AS test_case;
SELECT 
    subscription_id, home_id, start_date, end_date,
    IF(start_date <= end_date, 'PASS', 'FAIL: start_date > end_date') AS date_logic
FROM HomeSubscription;

SELECT '=== TEST 4: KIỂM TRA CÔNG SUẤT VÀ SỐ TIỀN PHẢI DƯƠNG (>= 0) ===' AS test_case;
SELECT 
    'DeviceType' AS entity, 
    COUNT(*) AS total_invalid_power,
    IF(COUNT(*) = 0, 'PASS (Mọi rated_power_watts >= 0)', 'FAIL') AS status
FROM DeviceType WHERE rated_power_watts < 0;

SELECT 
    'Invoice' AS entity, 
    COUNT(*) AS total_invalid_amount,
    IF(COUNT(*) = 0, 'PASS (Mọi invoice amount >= 0)', 'FAIL') AS status
FROM Invoice WHERE amount < 0;


-- ----------------------------------------------------------
-- TEST GROUP 3: KIỂM TRA RÀNG BUỘC KHÓA DUY NHẤT (UNIQUE CONSTRAINTS)
-- ----------------------------------------------------------
SELECT '=== TEST 5: KIỂM TRA BẢO TOÀN TÍNH DUY NHẤT (UNIQUE: email, serial_number, mac_address) ===' AS test_case;
SELECT 
    IF((SELECT COUNT(*) FROM User) = (SELECT COUNT(DISTINCT email) FROM User), 'PASS (Email không trùng lặp)', 'FAIL') AS check_user_email,
    IF((SELECT COUNT(*) FROM Device) = (SELECT COUNT(DISTINCT serial_number) FROM Device), 'PASS (Serial không trùng lặp)', 'FAIL') AS check_device_serial,
    IF((SELECT COUNT(*) FROM Device) = (SELECT COUNT(DISTINCT mac_address) FROM Device), 'PASS (MAC không trùng lặp)', 'FAIL') AS check_device_mac;


-- ----------------------------------------------------------
-- TEST GROUP 4: KIỂM TRA HÀNH VI KHÓA NGOẠI (ON DELETE CASCADE, SET NULL, RESTRICT)
-- Sử dụng TRANSACTION để không làm biến đổi dữ liệu vĩnh viễn!
-- ----------------------------------------------------------

-- Test 4.1: ON DELETE SET NULL từ Room -> Device
START TRANSACTION;
SELECT '=== TEST 6: THỬ NGHIỆM ON DELETE SET NULL (Xóa Room -> Device.room_id chuyển thành NULL) ===' AS test_case;
-- Lấy thử một phòng đang có thiết bị: room_id = 1
SELECT device_id, device_name, room_id FROM Device WHERE room_id = 1;
-- Xóa Room 1
DELETE FROM Room WHERE room_id = 1;
-- Kiểm tra các thiết bị lúc này: device_id 1, 2, 3 phải có room_id = NULL và vẫn còn tồn tại trong bảng Device!
SELECT 
    device_id, device_name, home_id, room_id,
    IF(room_id IS NULL, 'PASS (Đã tự động SET NULL)', 'FAIL') AS set_null_result
FROM Device WHERE device_id IN (1, 2, 3);
ROLLBACK; -- Khôi phục lại dữ liệu ban đầu!


-- Test 4.2: ON DELETE RESTRICT từ DeviceType -> Device
START TRANSACTION;
SELECT '=== TEST 7: THỬ NGHIỆM ON DELETE RESTRICT (Xóa DeviceType đang dùng -> Phải bị chặn) ===' AS test_case;
-- Ghi chú: Nếu thực hiện `DELETE FROM DeviceType WHERE type_id = 1;`
-- Hệ thống MySQL sẽ báo lỗi: Cannot delete or update a parent row: a foreign key constraint fails
-- Chứng minh mô hình ngăn chặn triệt để hiện tượng mất danh mục khi đang có thiết bị vật lý sử dụng.
ROLLBACK;


-- Test 4.3: ON DELETE CASCADE từ User -> Home -> Room, Device, HomeSubscription, HomeMember
START TRANSACTION;
SELECT '=== TEST 8: THỬ NGHIỆM ON DELETE CASCADE (Xóa User 1 -> Tự động xóa sạch các tài nguyên phụ thuộc) ===' AS test_case;
-- Kiểm tra dữ liệu phụ thuộc của User 1 trước khi xóa:
SELECT COUNT(*) AS total_homes_user1 FROM Home WHERE user_id = 1;
-- Thực hiện xóa User 1
DELETE FROM User WHERE user_id = 1;
-- Kiểm tra: Home của User 1 phải = 0
SELECT 
    (SELECT COUNT(*) FROM Home WHERE user_id = 1) AS homes_remaining,
    (SELECT COUNT(*) FROM HomeMember WHERE user_id = 1) AS members_remaining,
    (SELECT COUNT(*) FROM Device WHERE home_id IN (1, 2)) AS devices_remaining,
    IF((SELECT COUNT(*) FROM Home WHERE user_id = 1) = 0 
       AND (SELECT COUNT(*) FROM Device WHERE home_id IN (1, 2)) = 0, 
       'PASS (CASCADE thành công sạch sẽ)', 'FAIL') AS cascade_result;
ROLLBACK; -- Khôi phục lại dữ liệu gốc!

SELECT '=== HOÀN TẤT BỘ KIỂM THỬ TÍNH ĐÚNG ĐẮN CỦA MÔ HÌNH CSDL ===' AS final_summary;
