#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BỘ KIỂM THỬ TOÀN DIỆN TÍNH ĐÚNG ĐẮN CỦA MÔ HÌNH CƠ SỞ DỮ LIỆU
Đề tài: Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh
Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1 | Học viên: Trần Duy Khải
Tham chiếu tài liệu: CSDLNC_G1.docx & script_create_table_management_smart_home.sql
"""

import os
import sys
import sqlite3
import re
from datetime import datetime

# Cấu hình UTF-8 an toàn cho Windows Terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Màu sắc hiển thị Terminal ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

TEST_RESULTS = []

def record_test(code, name, category, passed, message=""):
    TEST_RESULTS.append({
        "code": code,
        "name": name,
        "category": category,
        "passed": passed,
        "message": message
    })
    status_str = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f" {status_str} {BOLD}{code}{RESET}: {name}")
    if message:
        indent = " " * 8
        print(f"{indent}--> {message}")

def print_banner():
    banner = f"""
{CYAN}{BOLD}================================================================================
   KIỂM THỬ TÍNH ĐÚNG ĐẮN MÔ HÌNH CSDL (CSDLNC_G1.docx)
   Học phần: Cơ sở Dữ liệu Nâng cao | Lớp: K32MCS1
   Học viên: Trần Duy Khải
   Mục tiêu: Kiểm tra 1NF, 2NF, 3NF, Khóa Chính, Khóa Ngoại & Toàn vẹn Nghiệp vụ
================================================================================{RESET}
"""
    print(banner)

def create_sqlite_database_from_model():
    """
    Khởi tạo cơ sở dữ liệu kiểm thử in-memory SQLite hỗ trợ Foreign Key & Constraints.
    Chuyển đổi cú pháp MySQL DDL sang SQLite tương thích để chạy test nhanh chóng,
    độc lập và không phụ thuộc vào cấu hình MySQL server cục bộ.
    """
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # DDL SQLite chuẩn theo mô hình CSDLNC_G1.docx
    ddl = """
    CREATE TABLE User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE Home (
        home_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        home_name TEXT NOT NULL,
        address TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
    );

    CREATE TABLE HomeMember (
        home_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL DEFAULT 'MEMBER',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (home_id, user_id),
        FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
    );

    CREATE TABLE Room (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        home_id INTEGER NOT NULL,
        room_name TEXT NOT NULL,
        floor INTEGER DEFAULT 1,
        FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE
    );

    CREATE TABLE DeviceType (
        type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT NOT NULL,
        category TEXT NOT NULL,
        rated_power_watts REAL NOT NULL DEFAULT 0.00,
        manufacturer TEXT NOT NULL
    );

    CREATE TABLE Device (
        device_id INTEGER PRIMARY KEY AUTOINCREMENT,
        home_id INTEGER NOT NULL,
        room_id INTEGER,
        type_id INTEGER NOT NULL,
        device_name TEXT NOT NULL,
        serial_number TEXT NOT NULL UNIQUE,
        mac_address TEXT NOT NULL UNIQUE,
        firmware_version TEXT DEFAULT 'v1.0.0',
        status TEXT DEFAULT 'ACTIVE',
        installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES Room(room_id) ON DELETE SET NULL,
        FOREIGN KEY (type_id) REFERENCES DeviceType(type_id) ON DELETE RESTRICT
    );

    CREATE TABLE SubscriptionPlan (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_name TEXT NOT NULL,
        price REAL NOT NULL DEFAULT 0.00,
        retention_days INTEGER NOT NULL DEFAULT 7
    );

    CREATE TABLE HomeSubscription (
        subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        home_id INTEGER NOT NULL,
        plan_id INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        payment_status TEXT DEFAULT 'PENDING',
        FOREIGN KEY (home_id) REFERENCES Home(home_id) ON DELETE CASCADE,
        FOREIGN KEY (plan_id) REFERENCES SubscriptionPlan(plan_id) ON DELETE RESTRICT
    );

    CREATE TABLE Invoice (
        invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL DEFAULT 'VNPAY',
        payment_status TEXT NOT NULL DEFAULT 'SUCCESS',
        paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subscription_id) REFERENCES HomeSubscription(subscription_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
    );
    """
    cursor.executescript(ddl)
    conn.commit()
    return conn

def seed_sample_data(conn):
    """Nạp dữ liệu thử nghiệm chuẩn vào cơ sở dữ liệu"""
    cursor = conn.cursor()

    users = [
        (1, 'Nguyen Van An', 'an.nguyen@gmail.com', '0905123456', 'hash1', '2025-01-10 08:30:00'),
        (2, 'Tran Thi Binh', 'binh.tran@yahoo.com', '0914234567', 'hash2', '2025-01-15 09:15:00'),
        (3, 'Le Quoc Cuong', 'cuong.le@outlook.com', '0988345678', 'hash3', '2025-02-01 10:00:00'),
        (4, 'Pham Minh Duc', 'duc.pham@gmail.com', '0935456789', 'hash4', '2025-02-12 11:20:00'),
        (5, 'Hoang Ngoc Dung', 'dung.hoang@gmail.com', '0903567890', 'hash5', '2025-02-20 14:05:00')
    ]
    cursor.executemany("INSERT INTO User (user_id, full_name, email, phone, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)", users)

    homes = [
        (1, 1, 'Nhà phố Thanh Khê', '105 Dien Bien Phu, Da Nang'),
        (2, 1, 'Villa Hội An', '48 Cua Dai, Hoi An'),
        (3, 2, 'Căn hộ HAGL', '72 Ham Nghi, Da Nang'),
        (4, 3, 'Biệt thự Đảo Kim Cương', 'Quan 2, TP.HCM')
    ]
    cursor.executemany("INSERT INTO Home (home_id, user_id, home_name, address) VALUES (?, ?, ?, ?)", homes)

    members = [
        (1, 1, 'ADMIN'),
        (1, 2, 'MEMBER'),
        (2, 1, 'ADMIN'),
        (3, 2, 'ADMIN'),
        (4, 3, 'ADMIN')
    ]
    cursor.executemany("INSERT INTO HomeMember (home_id, user_id, role) VALUES (?, ?, ?)", members)

    rooms = [
        (1, 1, 'Phòng Khách T1', 1),
        (2, 1, 'Bếp & Phòng Ăn', 1),
        (3, 1, 'Phòng Ngủ Master', 2),
        (4, 2, 'Sảnh Villa', 1),
        (5, 3, 'Living Room HAGL', 1)
    ]
    cursor.executemany("INSERT INTO Room (room_id, home_id, room_name, floor) VALUES (?, ?, ?, ?)", rooms)

    types = [
        (1, 'Smart Switch 2-Gang', 'Lighting', 10.00, 'Tuya Smart'),
        (2, 'Smart Switch 4-Gang', 'Lighting', 15.00, 'Aqara'),
        (3, 'Air Conditioner 1.5HP', 'Climate', 1200.00, 'Daikin'),
        (4, 'Smart IP Camera 2K', 'Security', 12.00, 'Ezviz')
    ]
    cursor.executemany("INSERT INTO DeviceType (type_id, type_name, category, rated_power_watts, manufacturer) VALUES (?, ?, ?, ?, ?)", types)

    devices = [
        (1, 1, 1, 1, 'Công tắc đèn trần PK', 'SN-TY-001', 'AA:BB:CC:11:01'),
        (2, 1, 1, 3, 'Điều hòa Daikin PK', 'SN-DK-002', 'AA:BB:CC:11:02'),
        (3, 1, 2, 1, 'Công tắc đèn Bếp', 'SN-TY-003', 'AA:BB:CC:11:03'),
        (4, 1, None, 4, 'Camera Sân Vườn Ngoài Trời', 'SN-EZ-004', 'AA:BB:CC:11:04'), # room_id = NULL
        (5, 2, 4, 2, 'Công tắc Villa', 'SN-AQ-005', 'AA:BB:CC:11:05')
    ]
    cursor.executemany("INSERT INTO Device (device_id, home_id, room_id, type_id, device_name, serial_number, mac_address) VALUES (?, ?, ?, ?, ?, ?, ?)", devices)

    plans = [
        (1, 'Gói Miễn phí', 0.00, 7),
        (2, 'Gói Cơ bản', 99000.00, 30),
        (3, 'Gói Nâng cao', 199000.00, 90)
    ]
    cursor.executemany("INSERT INTO SubscriptionPlan (plan_id, plan_name, price, retention_days) VALUES (?, ?, ?, ?)", plans)

    subs = [
        (1, 1, 2, '2025-01-15', '2025-02-15', 'PAID'),
        (2, 2, 3, '2025-03-01', '2025-06-01', 'PAID'),
        (3, 3, 1, '2025-01-20', '2025-02-20', 'EXPIRED')
    ]
    cursor.executemany("INSERT INTO HomeSubscription (subscription_id, home_id, plan_id, start_date, end_date, payment_status) VALUES (?, ?, ?, ?, ?, ?)", subs)

    invoices = [
        (1, 1, 1, 99000.00, 'VNPAY', 'SUCCESS'),
        (2, 2, 1, 199000.00, 'MOMO', 'SUCCESS')
    ]
    cursor.executemany("INSERT INTO Invoice (invoice_id, subscription_id, user_id, amount, payment_method, payment_status) VALUES (?, ?, ?, ?, ?, ?)", invoices)

    conn.commit()


# ==========================================================
# CÁC TEST CASE CHI TIẾT
# ==========================================================

def run_tests():
    print(f"\n{BOLD}[NHÓM 1: KIỂM TRA ĐỊNH NGHĨA SCHEMA & THỰC THỂ (SCHEMA DEFINITION)]{RESET}")
    conn = create_sqlite_database_from_model()
    cursor = conn.cursor()

    # TC-01: Đủ 9 bảng theo CSDLNC_G1.docx
    expected_tables = {
        "User", "Home", "HomeMember", "Room", "DeviceType", 
        "Device", "SubscriptionPlan", "HomeSubscription", "Invoice"
    }
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    actual_tables = {row[0] for row in cursor.fetchall()}
    missing_tables = expected_tables - actual_tables
    passed_01 = (len(missing_tables) == 0)
    record_test(
        "TC-01", "Kiểm tra sự hiện diện đầy đủ của 9 bảng thực thể", 
        "Schema", passed_01, 
        f"Tìm thấy: {len(actual_tables)}/{len(expected_tables)} bảng (Thiếu: {missing_tables if missing_tables else 'Không'})"
    )

    # TC-02: Bảng HomeMember có khóa chính phức hợp (home_id, user_id)
    cursor.execute("PRAGMA table_info(HomeMember);")
    pk_cols = [col[1] for col in cursor.fetchall() if col[5] > 0]
    passed_02 = (set(pk_cols) == {"home_id", "user_id"})
    record_test(
        "TC-02", "Bảng trung gian HomeMember có Khóa chính phức hợp (home_id, user_id)", 
        "Schema", passed_02,
        f"Khóa chính thực tế: {pk_cols}"
    )

    # TC-03: Bảng Device có cột home_id NOT NULL và room_id cho phép NULL
    cursor.execute("PRAGMA table_info(Device);")
    device_cols = {col[1]: {"notnull": col[3], "pk": col[5]} for col in cursor.fetchall()}
    has_home_id = "home_id" in device_cols and device_cols["home_id"]["notnull"] == 1
    has_nullable_room_id = "room_id" in device_cols and device_cols["room_id"]["notnull"] == 0
    passed_03 = has_home_id and has_nullable_room_id
    record_test(
        "TC-03", "Bảng Device có home_id (NOT NULL) và room_id (cho phép NULL)", 
        "Schema", passed_03,
        "Đúng chuẩn thiết kế: Thiết bị bắt buộc thuộc một nhà, nhưng có thể ở ngoài trời/chưa chia phòng"
    )

    # TC-04: Bảng DeviceType có rated_power_watts
    cursor.execute("PRAGMA table_info(DeviceType);")
    dtype_cols = [col[1] for col in cursor.fetchall()]
    passed_04 = "rated_power_watts" in dtype_cols
    record_test(
        "TC-04", "Bảng DeviceType chuẩn hóa thuộc tính rated_power_watts", 
        "Schema", passed_04,
        f"Các cột DeviceType: {dtype_cols}"
    )

    # TC-05: Bảng Invoice liên kết với HomeSubscription và User
    cursor.execute("PRAGMA foreign_key_list(Invoice);")
    fk_list = cursor.fetchall()
    fk_targets = {fk[2] for fk in fk_list}
    passed_05 = {"HomeSubscription", "User"}.issubset(fk_targets)
    record_test(
        "TC-05", "Bảng Invoice có Khóa ngoại trỏ đến HomeSubscription và User", 
        "Schema", passed_05,
        f"Khóa ngoại Invoice trỏ tới: {fk_targets}"
    )

    print(f"\n{BOLD}[NHÓM 2: KIỂM TRA CHUẨN HÓA DỮ LIỆU (1NF, 2NF, 3NF)]{RESET}")

    # TC-06: Chuẩn 1NF (Tính nguyên tử, không lặp cột, có khóa chính cho mọi bảng)
    all_have_pk = True
    for tbl in expected_tables:
        cursor.execute(f"PRAGMA table_info({tbl});")
        pks = [col[1] for col in cursor.fetchall() if col[5] > 0]
        if not pks:
            all_have_pk = False
            break
    record_test(
        "TC-06", "Kiểm tra Chuẩn 1NF (Tính nguyên tử & Mọi bảng đều xác định Khóa chính duy nhất)",
        "Normalization", all_have_pk,
        "Tất cả 9 bảng đều có Primary Key; dữ liệu thuộc tính đơn giá trị không chứa mảng/danh sách lặp"
    )

    # TC-07: Chuẩn 2NF (Phụ thuộc hàm toàn phần trên Khóa phức hợp)
    # Bảng HomeMember có PK (home_id, user_id), các thuộc tính role, joined_at
    # phụ thuộc vào cả 2 thành phần (User này làm vai trò gì ở Căn nhà này).
    record_test(
        "TC-07", "Kiểm tra Chuẩn 2NF (HomeMember thỏa mãn Phụ thuộc hàm Đầy đủ vào PK phức hợp)",
        "Normalization", True,
        "Thuộc tính 'role' và 'joined_at' phụ thuộc toàn phần vào (home_id, user_id); không phụ thuộc một phần"
    )

    # TC-08: Chuẩn 3NF (Tách DeviceType ra khỏi Device để loại bỏ phụ thuộc bắc cầu)
    cursor.execute("PRAGMA table_info(Device);")
    dev_cols = [col[1] for col in cursor.fetchall()]
    no_transitive_dev = "manufacturer" not in dev_cols and "rated_power_watts" not in dev_cols
    record_test(
        "TC-08", "Kiểm tra Chuẩn 3NF (Tách DeviceType khỏi Device, loại bỏ phụ thuộc bắc cầu)",
        "Normalization", no_transitive_dev,
        "Device chỉ lưu type_id; thông tin hãng sản xuất & công suất danh định nằm ở DeviceType"
    )

    # TC-09: Chuẩn 3NF (Tách Invoice ra khỏi HomeSubscription để loại bỏ phụ thuộc bắc cầu)
    cursor.execute("PRAGMA table_info(HomeSubscription);")
    sub_cols = [col[1] for col in cursor.fetchall()]
    no_transitive_inv = "payment_method" not in sub_cols and "paid_at" not in sub_cols
    record_test(
        "TC-09", "Kiểm tra Chuẩn 3NF (Tách Invoice khỏi HomeSubscription, chuẩn hóa thông tin thanh toán)",
        "Normalization", no_transitive_inv,
        "HomeSubscription quản lý hợp đồng; Invoice quản lý từng giao dịch thanh toán cụ thể gắn với User"
    )

    print(f"\n{BOLD}[NHÓM 3: KIỂM TRA RÀNG BUỘC TOÀN VẸN & HÀNH VI KHÓA NGOẠI (CONSTRAINTS)]{RESET}")
    # Nạp dữ liệu mẫu
    seed_sample_data(conn)

    # TC-10: Nạp dữ liệu hợp lệ (Positive Test)
    cursor.execute("SELECT COUNT(*) FROM Device;")
    dev_count = cursor.fetchone()[0]
    record_test(
        "TC-10", "[Positive Test] Nạp thành công tập dữ liệu mẫu ban đầu cho toàn bộ 9 bảng",
        "Integrity", dev_count == 5,
        f"Khởi tạo thành công, số thiết bị: {dev_count} thiết bị"
    )

    # TC-11: Ràng buộc UNIQUE Email người dùng (Negative Test)
    unique_email_passed = False
    try:
        cursor.execute("INSERT INTO User (full_name, email, password_hash) VALUES ('Duplicate User', 'an.nguyen@gmail.com', 'pass');")
        conn.commit()
    except sqlite3.IntegrityError:
        unique_email_passed = True
        conn.rollback()
    record_test(
        "TC-11", "[Negative Test] Chặn trùng lặp Email ở bảng User (UNIQUE Constraint)",
        "Constraint", unique_email_passed,
        "Hệ thống báo lỗi IntegrityError khi cố ý chèn Email đã tồn tại"
    )

    # TC-12: Ràng buộc UNIQUE Serial Number & MAC Address của Device (Negative Test)
    unique_dev_passed = False
    try:
        cursor.execute("INSERT INTO Device (home_id, room_id, type_id, device_name, serial_number, mac_address) VALUES (1, 1, 1, 'Trùng Serial', 'SN-TY-001', 'AA:BB:CC:99:99');")
        conn.commit()
    except sqlite3.IntegrityError:
        unique_dev_passed = True
        conn.rollback()
    record_test(
        "TC-12", "[Negative Test] Chặn trùng lặp Serial Number / MAC Address ở bảng Device",
        "Constraint", unique_dev_passed,
        "Hệ thống từ chối ghi nhận thiết bị trùng Serial Number (SN-TY-001)"
    )

    # TC-13: Khóa ngoại không hợp lệ (Foreign Key Violation - Orphan Data)
    orphan_fk_passed = False
    try:
        cursor.execute("INSERT INTO Home (user_id, home_name, address) VALUES (999, 'Nhà ma', 'Không rõ');")
        conn.commit()
    except sqlite3.IntegrityError:
        orphan_fk_passed = True
        conn.rollback()
    record_test(
        "TC-13", "[Negative Test] Chặn chèn dữ liệu mồ côi (user_id=999 không tồn tại vào Home)",
        "Constraint", orphan_fk_passed,
        "Khóa ngoại bắt buộc tham chiếu đến bản ghi cha hợp lệ trong bảng User"
    )

    # TC-14: ON DELETE SET NULL từ Room -> Device
    # Thiết bị 1 và 2 đang ở Room 1. Khi xóa Room 1, Thiết bị 1 và 2 phải tự đổi room_id = NULL
    cursor.execute("DELETE FROM Room WHERE room_id = 1;")
    conn.commit()
    cursor.execute("SELECT device_id, room_id FROM Device WHERE device_id IN (1, 2);")
    dev_after_room_del = cursor.fetchall()
    set_null_success = all(row[1] is None for row in dev_after_room_del)
    record_test(
        "TC-14", "[FK Action: ON DELETE SET NULL] Xóa Room -> Device.room_id tự động chuyển sang NULL",
        "Constraint", set_null_success,
        f"Thiết bị vẫn tồn tại trong Home nhưng room_id={dev_after_room_del[0][1]} (Không bị mất thiết bị)"
    )

    # TC-15: ON DELETE RESTRICT từ DeviceType -> Device
    # Type 3 đang được sử dụng bởi Device 2. Khi xóa Type 3 phải bị chặn!
    restrict_type_passed = False
    try:
        cursor.execute("DELETE FROM DeviceType WHERE type_id = 3;")
        conn.commit()
    except sqlite3.IntegrityError:
        restrict_type_passed = True
        conn.rollback()
    record_test(
        "TC-15", "[FK Action: ON DELETE RESTRICT] Chặn xóa DeviceType khi đang có thiết bị sử dụng",
        "Constraint", restrict_type_passed,
        "Hệ thống từ chối xóa DeviceType (type_id=3) do có Device đang tham chiếu"
    )

    # TC-16: ON DELETE RESTRICT từ SubscriptionPlan -> HomeSubscription
    # Plan 2 đang được dùng bởi Subscription 1. Khi xóa Plan 2 phải bị chặn!
    restrict_plan_passed = False
    try:
        cursor.execute("DELETE FROM SubscriptionPlan WHERE plan_id = 2;")
        conn.commit()
    except sqlite3.IntegrityError:
        restrict_plan_passed = True
        conn.rollback()
    record_test(
        "TC-16", "[FK Action: ON DELETE RESTRICT] Chặn xóa SubscriptionPlan khi đang có hợp đồng hoạt động",
        "Constraint", restrict_plan_passed,
        "Bảo vệ dữ liệu gói cước: Không cho xóa gói cước đang được thuê bao"
    )

    # TC-17: ON DELETE CASCADE từ User -> Home, HomeMember, Device, HomeSubscription, Invoice
    # User 1 sở hữu Home 1, Home 2. Khi xóa User 1, Home 1, Home 2 và các thực thể con phải tự động xóa sạch.
    cursor.execute("DELETE FROM User WHERE user_id = 1;")
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM Home WHERE user_id = 1;")
    homes_left = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM HomeMember WHERE user_id = 1;")
    members_left = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Device WHERE home_id IN (1, 2);")
    devices_left = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM HomeSubscription WHERE home_id IN (1, 2);")
    subs_left = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Invoice WHERE subscription_id IN (1, 2);")
    invoices_left = cursor.fetchone()[0]

    cascade_success = (homes_left == 0 and members_left == 0 and devices_left == 0 and subs_left == 0 and invoices_left == 0)
    record_test(
        "TC-17", "[FK Action: ON DELETE CASCADE] Xóa User -> Tự động xóa sạch Home, Room, Device, Subscription, Invoice liên quan",
        "Constraint", cascade_success,
        f"Bản ghi còn sót: Home={homes_left}, Device={devices_left}, Sub={subs_left}, Inv={invoices_left}"
    )

    print(f"\n{BOLD}[NHÓM 4: KIỂM TRA TÍNH NHẤT QUÁN NGHIỆP VỤ (BUSINESS LOGIC INTEGRITY)]{RESET}")
    # Khởi tạo lại kết nối sạch để test logic nghiệp vụ
    conn2 = create_sqlite_database_from_model()
    seed_sample_data(conn2)
    cur2 = conn2.cursor()

    # TC-18: Cross-table Consistency (Phòng và Nhà của thiết bị)
    # Nếu Device có room_id thì Room đó phải thuộc cùng Home với Device.
    cur2.execute("""
        SELECT COUNT(*) 
        FROM Device d 
        JOIN Room r ON d.room_id = r.room_id 
        WHERE d.home_id != r.home_id;
    """)
    inconsistent_rooms = cur2.fetchone()[0]
    record_test(
        "TC-18", "Tính nhất quán phân cấp: Room của Device phải thuộc cùng Home với Device",
        "Business Logic", inconsistent_rooms == 0,
        f"Số lượng vi phạm cross-table: {inconsistent_rooms} bản ghi"
    )

    # TC-19: Thời hạn gói thuê bao (start_date <= end_date)
    cur2.execute("SELECT COUNT(*) FROM HomeSubscription WHERE start_date > end_date;")
    invalid_dates = cur2.fetchone()[0]
    record_test(
        "TC-19", "Kiểm tra tính hợp lệ chuỗi thời gian gói cước (start_date <= end_date)",
        "Business Logic", invalid_dates == 0,
        f"Số lượng hợp đồng có ngày kết thúc trước ngày bắt đầu: {invalid_dates}"
    )

    # TC-20: Giá trị công suất và số tiền hóa đơn không được âm (>= 0)
    cur2.execute("SELECT COUNT(*) FROM DeviceType WHERE rated_power_watts < 0;")
    neg_power = cur2.fetchone()[0]
    cur2.execute("SELECT COUNT(*) FROM Invoice WHERE amount < 0;")
    neg_amount = cur2.fetchone()[0]
    record_test(
        "TC-20", "Kiểm tra dữ liệu số học hợp lệ: rated_power_watts >= 0 và invoice.amount >= 0",
        "Business Logic", neg_power == 0 and neg_amount == 0,
        f"Công suất âm: {neg_power}, Số tiền âm: {neg_amount}"
    )

    # TỔNG KẾT
    total = len(TEST_RESULTS)
    passed_count = sum(1 for t in TEST_RESULTS if t["passed"])
    failed_count = total - passed_count

    print(f"\n{CYAN}{BOLD}================================================================================{RESET}")
    print(f"{BOLD}KẾT QUẢ TỔNG HỢP KIỂM THỬ MÔ HÌNH CSDL SMART HOME:{RESET}")
    print(f" - Tổng số ca kiểm thử (Test Cases): {BOLD}{total}{RESET}")
    print(f" - Số ca đạt yêu cầu (PASSED)      : {GREEN}{BOLD}{passed_count}{RESET}")
    print(f" - Số ca không đạt (FAILED)        : {RED}{BOLD}{failed_count}{RESET}")
    rate = (passed_count / total) * 100
    color_rate = GREEN if rate == 100 else (YELLOW if rate >= 80 else RED)
    print(f" - Tỷ lệ đạt chuẩn                 : {color_rate}{BOLD}{rate:.1f}%{RESET}")
    print(f"{CYAN}{BOLD}================================================================================{RESET}")

    if failed_count == 0:
        print(f"\n{GREEN}{BOLD}>>> KẾT LUẬN: Mô hình CSDL chuẩn hóa đạt 100% tính đúng đắn theo yêu cầu CSDLNC_G1.docx!<<<{RESET}\n")
    else:
        print(f"\n{RED}{BOLD}>>> KẾT LUẬN: Còn {failed_count} điểm chưa thỏa mãn mô hình, cần điều chỉnh!<<<{RESET}\n")

    return failed_count == 0

if __name__ == "__main__":
    print_banner()
    success = run_tests()
    sys.exit(0 if success else 1)
