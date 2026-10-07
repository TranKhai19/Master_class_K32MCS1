-- ==========================================================
-- THỦ TỤC LƯU TRỮ (STORED PROCEDURE) SINH DỮ LIỆU LỚN THUẦN MYSQL
-- Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1 | Học viên: Trần Duy Khải
-- Kỹ thuật: Sử dụng WHILE LOOP, Prepared Batch Inserts, Commit ngắt quãng
-- Mục đích: Sinh dữ liệu tự động bên trong MySQL Server
-- ==========================================================

USE smart_home_info;

DELIMITER //

DROP PROCEDURE IF EXISTS sp_generate_bulk_data //

CREATE PROCEDURE sp_generate_bulk_data(
    IN p_num_records INT,    -- Số lượng bản ghi muốn sinh (ví dụ: 100000, 1000000)
    IN p_batch_size INT      -- Kích thước mỗi đợt commit (khuyên dùng: 5000 đến 10000)
)
BEGIN
    DECLARE v_counter INT DEFAULT 1;
    DECLARE v_batch_count INT DEFAULT 0;
    
    -- Tắt kiểm tra ràng buộc tạm thời để tối ưu tốc độ ghi I/O
    SET autocommit = 0;
    SET unique_checks = 0;
    SET foreign_key_checks = 0;

    -- 1. SINH DỮ LIỆU USER
    WHILE v_counter <= p_num_records DO
        INSERT INTO User (user_id, full_name, email, phone, password_hash, created_at, updated_at)
        VALUES (
            v_counter,
            CONCAT('User Fullname ', v_counter),
            CONCAT('user_', v_counter, '@smarthome.io'),
            CONCAT('09', LPAD(FLOOR(RAND() * 99999999), 8, '0')),
            '$2a$12$e8Y7z6aK.d0bQ...sample_hash',
            NOW() - INTERVAL (p_num_records - v_counter) SECOND,
            NOW()
        );
        
        SET v_counter = v_counter + 1;
        SET v_batch_count = v_batch_count + 1;
        
        -- Commit theo từng lô batch
        IF v_batch_count >= p_batch_size THEN
            COMMIT;
            SET v_batch_count = 0;
        END IF;
    END WHILE;
    COMMIT;
    
    -- Bật lại kiểm tra ràng buộc
    SET foreign_key_checks = 1;
    SET unique_checks = 1;
    SET autocommit = 1;
    
    SELECT CONCAT('Hoàn tất sinh ', p_num_records, ' bản ghi thành công!') AS result;
END //

DELIMITER ;

-- ==========================================================
-- HƯỚNG DẪN THỰC THI THỦ TỤC:
-- CALL sp_generate_bulk_data(10000, 5000);   -- Sinh thử nghiệm 10.000 bản ghi
-- CALL sp_generate_bulk_data(1000000, 10000); -- Sinh 1.000.000 bản ghi
-- ==========================================================
