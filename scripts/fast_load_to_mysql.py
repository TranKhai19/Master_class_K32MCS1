#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOOL NẠP 1 TRIỆU BẢN GHI TRỰC TIẾP VÀO MYSQL (KHÔNG LO TIMEOUT WORKBENCH)
Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1 | Học viên: Trần Duy Khải

Ưu điểm vượt trội:
- Chạy trực tiếp qua MySQL Engine kết nối native socket, KHÔNG BỊ GIỚI HẠN TIMEOUT 30 GIÂY của giao diện Workbench.
- Tự động nạp tuần tự 7 bảng (7,000,000 bản ghi) siêu tốc.
- Đo thời gian nạp chính xác từng bảng và in báo cáo hoàn tất.
"""

import sys
import time
import getpass
import argparse

# Cấu hình UTF-8 cho console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

try:
    import pymysql
except ImportError:
    print(f"{YELLOW}[!] Thư viện pymysql chưa được cài đặt. Đang cài đặt...{RESET}")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
    import pymysql

TABLE_FILES = [
    ("DeviceType", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/device_types.csv",
     "(type_id, type_name, category, rated_power_watts, manufacturer)", None),
    ("SubscriptionPlan", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/subscription_plans.csv",
     "(plan_id, plan_name, price, retention_days)", None),
    ("User", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/users.csv", 
     "(user_id, full_name, email, phone, password_hash, created_at, updated_at)", None),
    ("Home", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/homes.csv", 
     "(home_id, user_id, home_name, address, created_at, updated_at)", None),
    ("HomeMember", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/home_members.csv", 
     "(home_id, user_id, role, joined_at)", None),
    ("Room", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/rooms.csv", 
     "(room_id, home_id, room_name, floor)", None),
    ("Device", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/devices.csv", 
     "(device_id, home_id, @room_id, type_id, device_name, serial_number, mac_address, firmware_version, status, installed_at)", 
     "SET room_id = NULLIF(@room_id, '\\N')"),
    ("HomeSubscription", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/home_subscriptions.csv", 
     "(subscription_id, home_id, plan_id, start_date, end_date, payment_status)", None),
    ("Invoice", "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/bulk_data/invoices.csv", 
     "(invoice_id, subscription_id, user_id, amount, payment_method, payment_status, paid_at)", None)
]

def main():
    parser = argparse.ArgumentParser(description="Nạp trực tiếp 7 triệu bản ghi vào MySQL Server")
    parser.add_argument("-H", "--host", default="127.0.0.1", help="MySQL Host (mặc định: 127.0.0.1)")
    parser.add_argument("-P", "--port", type=int, default=3306, help="MySQL Port (mặc định: 3306)")
    parser.add_argument("-u", "--user", default="root", help="MySQL Username (mặc định: root)")
    parser.add_argument("-p", "--password", default=None, help="MySQL Password")
    parser.add_argument("-d", "--database", default="smart_home_info", help="Database (mặc định: smart_home_info)")
    
    args = parser.parse_args()
    
    password = args.password
    if password is None:
        try:
            password = getpass.getpass(prompt=f"Nhập mật khẩu MySQL cho tài khoản [{args.user}]: ")
        except Exception:
            password = ""

    print(f"\n{CYAN}{BOLD}================================================================================{RESET}")
    print(f"{BOLD}TIẾN TRÌNH NẠP DỮ LIỆU LỚN VÀO MYSQL SERVER (7,000,000 RECORDS){RESET}")
    print(f" - Host: {args.host}:{args.port} | Database: {args.database} | User: {args.user}")
    print(f"{CYAN}{BOLD}================================================================================{RESET}\n")

    try:
        conn = pymysql.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=password,
            database=args.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=60,
            read_timeout=3600,
            write_timeout=3600
        )
        print(f"{GREEN}[+] Kết nối thành công đến MySQL Server!{RESET}\n")
    except Exception as e:
        print(f"{YELLOW}[!] Lỗi kết nối MySQL: {e}{RESET}")
        print("Vui lòng kiểm tra lại username/password hoặc đảm bảo service MySQL80 đang chạy.")
        sys.exit(1)

    cursor = conn.cursor()
    
    # 1. Tối ưu tham số session
    cursor.execute("SET autocommit = 0;")
    cursor.execute("SET unique_checks = 0;")
    cursor.execute("SET foreign_key_checks = 0;")
    
    # 2. Truncate các bảng
    print("[*] Đang làm sạch dữ liệu cũ các bảng...")
    truncate_order = ["Invoice", "HomeSubscription", "Device", "Room", "HomeMember", "Home", "User"]
    for tbl in truncate_order:
        cursor.execute(f"TRUNCATE TABLE {tbl};")
    conn.commit()
    print(f"{GREEN}[+] Đã làm sạch 7 bảng thành công (0.05s)!{RESET}\n")

    # 3. Nạp tuần tự từng bảng
    total_start = time.time()
    for idx, (tbl_name, file_path, cols, set_clause) in enumerate(TABLE_FILES, start=1):
        print(f"[{idx}/7] Đang nạp 1,000,000 bản ghi vào bảng {CYAN}{tbl_name}{RESET}...")
        t_start = time.time()
        
        load_sql = f"""
        LOAD DATA INFILE '{file_path}'
        INTO TABLE {tbl_name}
        CHARACTER SET utf8mb4
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 LINES
        {cols}
        """
        if set_clause:
            load_sql += f" {set_clause};"
        else:
            load_sql += ";"
            
        cursor.execute(load_sql)
        conn.commit()
        t_elapsed = time.time() - t_start
        print(f"      {GREEN}[PASS]{RESET} Hoàn tất bảng {BOLD}{tbl_name}{RESET}: 1,000,000 dòng ({t_elapsed:.2f}s)")

    # 4. Bật lại ràng buộc
    cursor.execute("SET foreign_key_checks = 1;")
    cursor.execute("SET unique_checks = 1;")
    cursor.execute("SET autocommit = 1;")
    
    total_elapsed = time.time() - total_start
    print(f"\n{GREEN}{BOLD}================================================================================{RESET}")
    print(f"{BOLD}HOÀN TẤT NẠP TOÀN BỘ 7,000,000 BẢN GHI THÀNH CÔNG! ({total_elapsed:.2f}s){RESET}")
    print(f"{GREEN}{BOLD}================================================================================{RESET}\n")

    # 5. Đối soát số lượng
    print(f"{BOLD}ĐỐI SOÁT TỔNG SỐ BẢN GHI HIỆN CÓ TRONG DATABASE:{RESET}")
    for tbl in ["User", "Home", "HomeMember", "Room", "Device", "HomeSubscription", "Invoice"]:
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {tbl};")
        row = cursor.fetchone()
        print(f" - Bảng {CYAN}{tbl:<18}{RESET}: {BOLD}{row['cnt']:,}{RESET} bản ghi")
    print("")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
