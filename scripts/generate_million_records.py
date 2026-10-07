#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOOL SINH 1 TRIỆU BẢN GHI (1,000,000 RECORDS) CHO MỖI BẢNG CƠ SỞ DỮ LIỆU SMART HOME
Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1 | Học viên: Trần Duy Khải
Tham chiếu mô hình: CSDLNC_G1.docx (9 Bảng quan hệ chuẩn 3NF)

Kỹ thuật & Khắc phục chuẩn:
- Mở file với newline='' và xuất ký tự xuống dòng thuần '\n' (triệt tiêu hoàn toàn warning Delimiter '\r').
- Bao chuỗi ký tự chứa dấu phẩy bằng dấu ngoặc kép '"' (OPTIONALLY ENCLOSED BY '"') để loại bỏ triệt để lỗi 1292.
- Tự động đồng bộ file CSV vào thư mục an toàn của MySQL Server:
  C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/
"""

import os
import sys
import time
import argparse
import random
import shutil
from datetime import datetime, timedelta

# Cấu hình UTF-8 an toàn cho console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

FIRST_NAMES = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan", "Vu", "Vo", "Dang", "Bui", "Do", "Ho", "Ngo", "Duong"]
MIDDLE_NAMES = ["Van", "Thi", "Quoc", "Minh", "Ngoc", "Thanh", "Huu", "Dinh", "Gia", "Hong", "Duc", "Tuan", "My"]
LAST_NAMES = ["An", "Binh", "Cuong", "Duc", "Dung", "Giang", "Hoa", "Huy", "Khanh", "Long", "Linh", "Kiet", "Nam", "Oanh", "Phuc", "Quan", "Son", "Thao", "Tung", "Vy"]

CITIES = ["Da Nang", "Ha Noi", "TP.HCM", "Hoi An", "Can Tho", "Hai Phong", "Nha Trang", "Hue"]
STREETS = ["Nguyen Hue", "Le Duan", "Dien Bien Phu", "Tran Phu", "Hai Ba Trung", "Nguyen Van Linh", "Pham Van Dong", "Vo Nguyen Giap"]
ROOM_TYPES = ["Phòng Khách", "Phòng Bếp", "Phòng Ngủ Master", "Phòng Làm Việc", "Sảnh Chính", "Ban Công", "Phòng Giải Trí", "Sân Thượng"]

MYSQL_UPLOADS_DIR = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data"

def generate_users(output_file, count, batch_size=50000):
    print(f"[*] Đang sinh {BOLD}{count:,}{RESET} bản ghi cho bảng {CYAN}User{RESET}...")
    start_time = time.time()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8', newline='', buffering=1024*1024*16) as f:
        f.write("user_id,full_name,email,phone,password_hash,created_at,updated_at\n")
        
        base_date = datetime(2025, 1, 1, 8, 0, 0)
        lines = []
        for i in range(1, count + 1):
            fn = random.choice(FIRST_NAMES)
            mn = random.choice(MIDDLE_NAMES)
            ln = random.choice(LAST_NAMES)
            full_name = f"{fn} {mn} {ln}"
            email = f"user_{i}_{ln.lower()}@smarthome.io"
            phone = f"09{random.randint(10000000, 99999999)}"
            pwd_hash = "$2a$12$e8Y7z6aK.d0bQ...sample_hash"
            created_at = (base_date + timedelta(seconds=i * 15)).strftime("%Y-%m-%d %H:%M:%S")
            updated_at = created_at
            
            lines.append(f"{i},\"{full_name}\",\"{email}\",\"{phone}\",\"{pwd_hash}\",{created_at},{updated_at}\n")
            
            if i % batch_size == 0:
                f.writelines(lines)
                lines.clear()
                sys.stdout.write(f"\r    -> Đã tạo: {i:,} / {count:,} ({i*100//count}%)")
                sys.stdout.flush()
                
        if lines:
            f.writelines(lines)
            
    print(f"\r    -> Hoàn tất: {count:,} bản ghi User ({time.time() - start_time:.2f}s) -> {output_file}")


def generate_homes(output_file, count, user_count, batch_size=50000):
    print(f"[*] Đang sinh {BOLD}{count:,}{RESET} bản ghi cho bảng {CYAN}Home{RESET}...")
    start_time = time.time()
    
    with open(output_file, 'w', encoding='utf-8', newline='', buffering=1024*1024*16) as f:
        f.write("home_id,user_id,home_name,address,created_at,updated_at\n")
        
        base_date = datetime(2025, 1, 2, 9, 0, 0)
        lines = []
        for i in range(1, count + 1):
            user_id = ((i - 1) % user_count) + 1
            city = random.choice(CITIES)
            street = random.choice(STREETS)
            home_name = f"Smart Home #{i} ({city})"
            # Đảm bảo bao ngoặc kép an toàn cho địa chỉ chứa dấu phẩy
            address = f"Số {random.randint(1, 999)} {street} - {city}"
            created_at = (base_date + timedelta(seconds=i * 20)).strftime("%Y-%m-%d %H:%M:%S")
            updated_at = created_at
            
            lines.append(f"{i},{user_id},\"{home_name}\",\"{address}\",{created_at},{updated_at}\n")
            
            if i % batch_size == 0:
                f.writelines(lines)
                lines.clear()
                sys.stdout.write(f"\r    -> Đã tạo: {i:,} / {count:,} ({i*100//count}%)")
                sys.stdout.flush()
                
        if lines:
            f.writelines(lines)
            
    print(f"\r    -> Hoàn tất: {count:,} bản ghi Home ({time.time() - start_time:.2f}s) -> {output_file}")


def generate_home_members(output_file, count, home_count, user_count, batch_size=50000):
    print(f"[*] Đang sinh {BOLD}{count:,}{RESET} bản ghi cho bảng {CYAN}HomeMember{RESET} (2NF - Composite PK)...")
    start_time = time.time()
    
    with open(output_file, 'w', encoding='utf-8', newline='', buffering=1024*1024*16) as f:
        f.write("home_id,user_id,role,joined_at\n")
        
        base_date = datetime(2025, 1, 3, 10, 0, 0)
        lines = []
        roles = ["ADMIN", "MEMBER", "MEMBER", "GUEST"]
        
        for i in range(1, count + 1):
            home_id = ((i - 1) % home_count) + 1
            user_id = ((i - 1) % user_count) + 1
            role = "ADMIN" if (i <= home_count) else random.choice(roles)
            joined_at = (base_date + timedelta(seconds=i * 12)).strftime("%Y-%m-%d %H:%M:%S")
            
            lines.append(f"{home_id},{user_id},\"{role}\",{joined_at}\n")
            
            if i % batch_size == 0:
                f.writelines(lines)
                lines.clear()
                sys.stdout.write(f"\r    -> Đã tạo: {i:,} / {count:,} ({i*100//count}%)")
                sys.stdout.flush()
                
        if lines:
            f.writelines(lines)
            
    print(f"\r    -> Hoàn tất: {count:,} bản ghi HomeMember ({time.time() - start_time:.2f}s) -> {output_file}")


STANDARD_ROOMS = [
    ("Phòng Khách", 1),
    ("Bếp & Phòng Ăn", 1),
    ("Phòng Ngủ Master", 2),
    ("Ban Công & Sân Phơi", 2),
]

def generate_rooms(output_file, count, home_count, batch_size=50000):
    print(f"[*] Đang sinh {BOLD}{count:,}{RESET} bản ghi cho bảng {CYAN}Room{RESET} (Nhiều phòng/nhà)...")
    start_time = time.time()
    
    with open(output_file, 'w', encoding='utf-8', newline='', buffering=1024*1024*16) as f:
        f.write("room_id,home_id,room_name,floor\n")
        
        lines = []
        num_rooms_per_home = len(STANDARD_ROOMS)
        for i in range(1, count + 1):
            home_id = ((i - 1) // num_rooms_per_home) % home_count + 1
            r_idx = (i - 1) % num_rooms_per_home
            r_name, floor = STANDARD_ROOMS[r_idx]
            
            lines.append(f"{i},{home_id},\"{r_name}\",{floor}\n")
            
            if i % batch_size == 0:
                f.writelines(lines)
                lines.clear()
                sys.stdout.write(f"\r    -> Đã tạo: {i:,} / {count:,} ({i*100//count}%)")
                sys.stdout.flush()
                
        if lines:
            f.writelines(lines)
            
    print(f"\r    -> Hoàn tất: {count:,} bản ghi Room ({time.time() - start_time:.2f}s) -> {output_file}")


DEVICE_TEMPLATES = [
    # Căn hộ 6 thiết bị
    [
        ("Công tắc đèn trần PK", 1, 0),         # Room 0: Phòng Khách
        ("Điều hòa Daikin Inverter PK", 3, 0),   # Room 0: Phòng Khách
        ("Camera an ninh AI PK", 8, 0),         # Room 0: Phòng Khách
        ("Cảm biến nhiệt ẩm Bếp", 5, 1),        # Room 1: Bếp
        ("Công tắc thông minh Bếp", 1, 1),      # Room 1: Bếp
        ("Điều hòa Inverter PN Master", 3, 2),  # Room 2: PN Master
    ],
    # Căn hộ 4 thiết bị
    [
        ("Công tắc thông minh 4 nút PK", 2, 0), # Room 0: Phòng Khách
        ("Điều hòa Panasonic 2.0HP PK", 4, 0),  # Room 0: Phòng Khách
        ("Cảm biến chuyển động PN Master", 6, 2), # Room 2: PN Master
        ("Khóa cửa thông minh FaceID", 7, -1),   # Cửa chính (room_id = NULL)
    ],
    # Căn hộ 7 thiết bị
    [
        ("Công tắc đèn trần PK", 1, 0),         # Room 0: Phòng Khách
        ("Điều hòa Inverter 1.5HP PK", 3, 0),   # Room 0: Phòng Khách
        ("Camera an ninh AI PK", 8, 0),         # Room 0: Phòng Khách
        ("Cảm biến nhiệt ẩm Bếp", 5, 1),        # Room 1: Bếp
        ("Cảm biến khói & khí gas Bếp", 11, 1),  # Room 1: Bếp
        ("Điều hòa Inverter PN Master", 3, 2),  # Room 2: PN Master
        ("Khóa cửa thông minh FaceID", 7, -1),   # Cửa chính ngoài trời
    ],
    # Căn hộ 5 thiết bị
    [
        ("Công tắc thông minh 2 nút PK", 1, 0), # Room 0: Phòng Khách
        ("Điều hòa Daikin 1.5HP PK", 3, 0),     # Room 0: Phòng Khách
        ("Công tắc thông minh Bếp", 1, 1),      # Room 1: Bếp
        ("Cảm biến nhiệt ẩm Bếp", 5, 1),        # Room 1: Bếp
        ("Ổ cắm thông minh đo điện Ban công", 9, 3), # Room 3: Ban công
    ]
]

def generate_devices(output_file, count, home_count, room_count, type_count=8, batch_size=50000):
    print(f"[*] Đang sinh {BOLD}{count:,}{RESET} bản ghi cho bảng {CYAN}Device{RESET} (Mỗi nhà nhiều thiết bị)...")
    start_time = time.time()
    
    statuses = ["ACTIVE", "ACTIVE", "ACTIVE", "OFFLINE", "MAINTENANCE"]
    base_date = datetime(2025, 1, 5, 8, 0, 0)
    
    with open(output_file, 'w', encoding='utf-8', newline='', buffering=1024*1024*16) as f:
        f.write("device_id,home_id,room_id,type_id,device_name,serial_number,mac_address,firmware_version,status,installed_at\n")
        
        lines = []
        dev_id = 1
        h = 1
        num_rooms_per_home = len(STANDARD_ROOMS)
        
        while dev_id <= count:
            home_id = ((h - 1) % home_count) + 1
            tmpl = DEVICE_TEMPLATES[(h - 1) % len(DEVICE_TEMPLATES)]
            
            for item in tmpl:
                if dev_id > count:
                    break
                
                d_name, type_id, r_idx = item
                
                # Tính room_id đảm bảo room thuộc chính home_id này
                if r_idx >= 0:
                    calculated_room_id = (h - 1) * num_rooms_per_home + 1 + r_idx
                    if calculated_room_id <= room_count:
                        room_id = str(calculated_room_id)
                    else:
                        room_id = "\\N"
                else:
                    room_id = "\\N"
                
                device_name = f"{d_name} #{dev_id}"
                serial_number = f"SN-IOT-{dev_id:08d}"
                
                mac_int = 0x001122000000 + dev_id
                mac_hex = f"{mac_int:012X}"
                mac_address = ":".join([mac_hex[j:j+2] for j in range(0, 12, 2)])
                
                firmware = f"v{1 + (dev_id % 3)}.{dev_id % 5}.{dev_id % 10}"
                status = random.choice(statuses)
                installed_at = (base_date + timedelta(seconds=dev_id * 10)).strftime("%Y-%m-%d %H:%M:%S")
                
                lines.append(f"{dev_id},{home_id},{room_id},{type_id},\"{device_name}\",\"{serial_number}\",\"{mac_address}\",\"{firmware}\",\"{status}\",{installed_at}\n")
                
                if dev_id % batch_size == 0:
                    f.writelines(lines)
                    lines.clear()
                    sys.stdout.write(f"\r    -> Đã tạo: {dev_id:,} / {count:,} ({dev_id*100//count}%)")
                    sys.stdout.flush()
                    
                dev_id += 1
            h += 1
            
        if lines:
            f.writelines(lines)
            
    print(f"\r    -> Hoàn tất: {count:,} bản ghi Device ({time.time() - start_time:.2f}s) -> {output_file}")


def generate_home_subscriptions(output_file, count, home_count, plan_count=4, batch_size=50000):
    print(f"[*] Đang sinh {BOLD}{count:,}{RESET} bản ghi cho bảng {CYAN}HomeSubscription{RESET}...")
    start_time = time.time()
    
    pay_statuses = ["PAID", "PAID", "EXPIRED", "PENDING"]
    
    with open(output_file, 'w', encoding='utf-8', newline='', buffering=1024*1024*16) as f:
        f.write("subscription_id,home_id,plan_id,start_date,end_date,payment_status\n")
        
        base_date = datetime(2025, 1, 10)
        lines = []
        for i in range(1, count + 1):
            home_id = ((i - 1) % home_count) + 1
            plan_id = ((i - 1) % plan_count) + 1
            s_date = base_date + timedelta(days=(i % 180))
            e_date = s_date + timedelta(days=30 * (plan_id))
            status = random.choice(pay_statuses)
            
            lines.append(f"{i},{home_id},{plan_id},{s_date.strftime('%Y-%m-%d')},{e_date.strftime('%Y-%m-%d')},\"{status}\"\n")
            
            if i % batch_size == 0:
                f.writelines(lines)
                lines.clear()
                sys.stdout.write(f"\r    -> Đã tạo: {i:,} / {count:,} ({i*100//count}%)")
                sys.stdout.flush()
                
        if lines:
            f.writelines(lines)
            
    print(f"\r    -> Hoàn tất: {count:,} bản ghi HomeSubscription ({time.time() - start_time:.2f}s) -> {output_file}")


def generate_invoices(output_file, count, sub_count, user_count, batch_size=50000):
    print(f"[*] Đang sinh {BOLD}{count:,}{RESET} bản ghi cho bảng {CYAN}Invoice{RESET} (3NF - Tách thanh toán)...")
    start_time = time.time()
    
    methods = ["VNPAY", "MOMO", "CREDIT_CARD", "BANK_TRANSFER"]
    amounts = [0.00, 99000.00, 199000.00, 499000.00]
    
    with open(output_file, 'w', encoding='utf-8', newline='', buffering=1024*1024*16) as f:
        f.write("invoice_id,subscription_id,user_id,amount,payment_method,payment_status,paid_at\n")
        
        base_date = datetime(2025, 1, 10, 8, 0, 0)
        lines = []
        for i in range(1, count + 1):
            sub_id = ((i - 1) % sub_count) + 1
            user_id = ((i - 1) % user_count) + 1
            amount = amounts[i % len(amounts)]
            method = random.choice(methods)
            status = "SUCCESS"
            paid_at = (base_date + timedelta(seconds=i * 25)).strftime("%Y-%m-%d %H:%M:%S")
            
            lines.append(f"{i},{sub_id},{user_id},{amount:.2f},\"{method}\",\"{status}\",{paid_at}\n")
            
            if i % batch_size == 0:
                f.writelines(lines)
                lines.clear()
                sys.stdout.write(f"\r    -> Đã tạo: {i:,} / {count:,} ({i*100//count}%)")
                sys.stdout.flush()
                
        if lines:
            f.writelines(lines)
            
    print(f"\r    -> Hoàn tất: {count:,} bản ghi Invoice ({time.time() - start_time:.2f}s) -> {output_file}")


def generate_device_types(output_file):
    print(f"[*] Đang xuất danh mục cho bảng {CYAN}DeviceType{RESET}...")
    types = [
        (1, "Công tắc thông minh 2 nút (Smart Switch 2-Gang)", "Lighting", 10.00, "Tuya Smart"),
        (2, "Công tắc thông minh 4 nút (Smart Switch 4-Gang)", "Lighting", 15.00, "Aqara"),
        (3, "Điều hòa không khí Inverter 1.5HP", "Climate", 1200.00, "Daikin"),
        (4, "Điều hòa không khí Inverter 2.0HP", "Climate", 1800.00, "Panasonic"),
        (5, "Cảm biến nhiệt độ & độ ẩm không dây", "Sensor", 2.50, "Xiaomi"),
        (6, "Cảm biến chuyển động & ánh sáng (Motion/Lux)", "Sensor", 1.50, "Philips Hue"),
        (7, "Khóa cửa thông minh FaceID & Vân tay", "Security", 25.00, "Yale"),
        (8, "Camera an ninh AI 2K góc rộng", "Security", 12.00, "Ezviz"),
        (9, "Ổ cắm thông minh đo điện năng tiêu thụ", "Power", 5.00, "Sonoff"),
        (10, "Bộ điều khiển bình nóng lạnh thông minh", "Power", 2500.00, "Ariston"),
        (11, "Cảm biến khói và khí gas thông minh", "Sensor", 3.00, "Honeywell"),
        (12, "Động cơ rèm thông minh tự động", "Lighting", 45.00, "Somfy")
    ]
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        f.write("type_id,type_name,category,rated_power_watts,manufacturer\n")
        for tid, name, cat, watt, mf in types:
            f.write(f'{tid},"{name}","{cat}",{watt:.2f},"{mf}"\n')
    print(f"    -> Hoàn tất: {len(types)} danh mục DeviceType -> {output_file}")


def generate_subscription_plans(output_file):
    print(f"[*] Đang xuất danh mục cho bảng {CYAN}SubscriptionPlan{RESET}...")
    plans = [
        (1, "Gói Miễn phí (Free Tier)", 0.00, 7),
        (2, "Gói Cơ bản (Standard Cloud)", 99000.00, 30),
        (3, "Gói Nâng cao (Premium Pro)", 199000.00, 90),
        (4, "Gói Doanh nghiệp (Enterprise Lifetime)", 499000.00, 365),
        (5, "Gói Chuyên gia Năng lượng (Energy Saver AI)", 149000.00, 60)
    ]
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        f.write("plan_id,plan_name,price,retention_days\n")
        for pid, name, price, ret in plans:
            f.write(f'{pid},"{name}",{price:.2f},{ret}\n')
    print(f"    -> Hoàn tất: {len(plans)} danh mục SubscriptionPlan -> {output_file}")


def copy_to_mysql_uploads(bulk_dir):
    """Tự động đồng bộ các file CSV vào thư mục an toàn của MySQL Server"""
    if os.path.exists("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads"):
        try:
            os.makedirs(MYSQL_UPLOADS_DIR, exist_ok=True)
            print(f"\n[*] Đang đồng bộ file sang thư mục an toàn của MySQL Server:")
            print(f"    -> {MYSQL_UPLOADS_DIR}")
            for fname in os.listdir(bulk_dir):
                if fname.endswith(".csv"):
                    src = os.path.join(bulk_dir, fname)
                    dst = os.path.join(MYSQL_UPLOADS_DIR, fname)
                    shutil.copy2(src, dst)
                    print(f"    [+] Đã copy: {fname}")
            print(f"{GREEN}[+] Đồng bộ hoàn tất!{RESET}")
        except Exception as e:
            print(f"{YELLOW}[!] Không thể tự copy (Cần quyền Admin): {e}{RESET}")


def update_load_script(count):
    """Cập nhật file load_million_records.sql chuẩn xác tuyệt đối"""
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "load_million_records.sql")
    
    content = f"""-- ==========================================================
-- SCRIPT NẠP 1 TRIỆU BẢN GHI (1,000,000 ROWS) TỐC ĐỘ CAO VÀO MYSQL
-- Đề tài: Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh
-- Môn học: Cơ sở Dữ liệu Nâng cao | Học viên: Trần Duy Khải
-- 
-- SỬ DỤNG THƯ MỤC AN TOÀN CHUẨN CỦA MYSQL SERVER:
-- C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/
-- (Tránh hoàn toàn lỗi Error Code 2068 & 1292 & Warning '\\r')
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
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(type_id, type_name, category, rated_power_watts, manufacturer);
COMMIT;
SELECT '-> Đã nạp xong bảng DeviceType' AS progress;

-- 0.2 Nạp bảng quy chuẩn SubscriptionPlan
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/subscription_plans.csv'
REPLACE INTO TABLE SubscriptionPlan
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(plan_id, plan_name, price, retention_days);
COMMIT;
SELECT '-> Đã nạp xong bảng SubscriptionPlan' AS progress;

-- 1. Nạp bảng User ({count:,} dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/users.csv'
INTO TABLE User
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(user_id, full_name, email, phone, password_hash, created_at, updated_at);
COMMIT;
SELECT '-> Đã nạp xong bảng User' AS progress;

-- 2. Nạp bảng Home ({count:,} dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/homes.csv'
INTO TABLE Home
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(home_id, user_id, home_name, address, created_at, updated_at);
COMMIT;
SELECT '-> Đã nạp xong bảng Home' AS progress;

-- 3. Nạp bảng HomeMember ({count:,} dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/home_members.csv'
INTO TABLE HomeMember
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(home_id, user_id, role, joined_at);
COMMIT;
SELECT '-> Đã nạp xong bảng HomeMember' AS progress;

-- 4. Nạp bảng Room ({count:,} dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/rooms.csv'
INTO TABLE Room
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(room_id, home_id, room_name, floor);
COMMIT;
SELECT '-> Đã nạp xong bảng Room' AS progress;

-- 5. Nạp bảng Device ({count:,} dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/devices.csv'
INTO TABLE Device
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(device_id, home_id, @room_id, type_id, device_name, serial_number, mac_address, firmware_version, status, installed_at)
SET room_id = NULLIF(@room_id, '\\\\N');
COMMIT;
SELECT '-> Đã nạp xong bảng Device' AS progress;

-- 6. Nạp bảng HomeSubscription ({count:,} dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/home_subscriptions.csv'
INTO TABLE HomeSubscription
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 LINES
(subscription_id, home_id, plan_id, start_date, end_date, payment_status);
COMMIT;
SELECT '-> Đã nạp xong bảng HomeSubscription' AS progress;

-- 7. Nạp bảng Invoice ({count:,} dòng)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/invoices.csv'
INTO TABLE Invoice
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
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
"""
    with open(sql_path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    print(f"\n[+] Đã cập nhật script nạp MySQL: {BOLD}{sql_path}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Sinh 1 triệu bản ghi cho CSDL Smart Home")
    parser.add_argument("--count", type=int, default=1000000, help="Số lượng bản ghi mỗi bảng (Mặc định: 1,000,000)")
    parser.add_argument("--batch-size", type=int, default=50000, help="Kích thước batch ghi buffer (Mặc định: 50,000)")
    parser.add_argument("--output-dir", type=str, default="bulk_data", help="Thư mục xuất CSV")
    
    args = parser.parse_args()
    count = args.count
    batch_size = args.batch_size
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bulk_dir = os.path.join(base_dir, args.output_dir)
    os.makedirs(bulk_dir, exist_ok=True)
    
    print(f"{CYAN}{BOLD}================================================================================{RESET}")
    print(f"{BOLD}CHƯƠNG TRÌNH SINH DỮ LIỆU QUY MÔ LỚN (BIG DATA GENERATOR V2){RESET}")
    print(f" - Số bản ghi mỗi bảng lớn: {GREEN}{BOLD}{count:,}{RESET}")
    print(f" - Danh mục quy chuẩn (3NF): {BOLD}DeviceType (12 chủng loại), SubscriptionPlan (5 gói cước){RESET}")
    print(f" - Số lượng bảng chính     : {BOLD}9 bảng (Đầy đủ mô hình chuẩn 3NF){RESET}")
    print(f" - Tổng số bản ghi sinh    : {GREEN}{BOLD}{(count * 7) + 17:,} records{RESET}")
    print(f" - Thư mục xuất file       : {bulk_dir}")
    print(f"{CYAN}{BOLD}================================================================================{RESET}\n")
    
    total_start = time.time()
    
    devtypes_csv = os.path.join(bulk_dir, "device_types.csv")
    plans_csv = os.path.join(bulk_dir, "subscription_plans.csv")
    users_csv = os.path.join(bulk_dir, "users.csv")
    homes_csv = os.path.join(bulk_dir, "homes.csv")
    members_csv = os.path.join(bulk_dir, "home_members.csv")
    rooms_csv = os.path.join(bulk_dir, "rooms.csv")
    devices_csv = os.path.join(bulk_dir, "devices.csv")
    subs_csv = os.path.join(bulk_dir, "home_subscriptions.csv")
    invoices_csv = os.path.join(bulk_dir, "invoices.csv")
    
    generate_device_types(devtypes_csv)
    generate_subscription_plans(plans_csv)
    generate_users(users_csv, count, batch_size)
    generate_homes(homes_csv, count, count, batch_size)
    generate_home_members(members_csv, count, count, count, batch_size)
    generate_rooms(rooms_csv, count, count, batch_size)
    generate_devices(devices_csv, count, count, count, 8, batch_size)
    generate_home_subscriptions(subs_csv, count, count, 4, batch_size)
    generate_invoices(invoices_csv, count, count, count, batch_size)
    
    update_load_script(count)
    copy_to_mysql_uploads(bulk_dir)
    
    total_time = time.time() - total_start
    print(f"\n{GREEN}{BOLD}================================================================================{RESET}")
    print(f"{BOLD}ĐÃ SINH VÀ ĐỒNG BỘ THÀNH CÔNG ĐẦY ĐỦ 9 BẢNG DỮ LIỆU! ({total_time:.2f}s){RESET}")
    print(f"{GREEN}{BOLD}================================================================================{RESET}\n")

if __name__ == "__main__":
    main()
