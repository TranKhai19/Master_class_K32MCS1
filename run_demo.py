"""
SCRIPT ĐIỀU PHỐI KHỞI CHẠY DEMO HỆ THỐNG (1-CLICK RUN DEMO)
Đề tài: Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh (Smart Home IoT System)
Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1
Học viên: Trần Duy Khải

Chức năng:
1. Tự động kiểm tra & nạp dữ liệu chuỗi thời gian NoSQL (Telemetry & Command Logs).
2. Tự động thực thi Spark/Hadoop Analytics Batch Processing Jobs.
3. Khởi động Web Dashboard Server trên port 8050 và tự động mở trình duyệt.
"""

import os
import sys
import time
import webbrowser
import threading

# Thêm thư mục hiện tại vào PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from bigdata.generate_iot_data import generate_telemetry_and_commands
from bigdata.spark_analytics_jobs import run_spark_analytics_jobs
from dashboard.app import app

def print_banner():
    banner = r"""
================================================================================
   SMART HOME IoT SYSTEM - BIG DATA & NoSQL ANALYTICS DASHBOARD
   Học phần: Cơ sở Dữ liệu Nâng cao | Lớp: K32MCS1
   Học viên: Trần Duy Khải
================================================================================
 [1] RDBMS MySQL:  smart_home_info (User, Home, Room, Device, Subscription)
 [2] NoSQL:        MongoDB Collections (device_telemetry, command_logs)
 [3] Big Data:     Hadoop HDFS Partitioning & PySpark Analytics Engine
 [4] Dashboard:    Interactive IoT Command Center (Port 8050)
================================================================================
"""
    print(banner)

def open_browser(url, delay=1.5):
    def _open():
        time.sleep(delay)
        print(f"[+] Automatically launching web browser: {url}")
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()

def main():
    print_banner()

    data_dir = os.path.join(ROOT_DIR, "bigdata", "data")
    telemetry_file = os.path.join(data_dir, "device_telemetry.json")
    analytics_file = os.path.join(data_dir, "analytics_results.json")

    # Bước 1: Kiểm tra & sinh dữ liệu nếu chưa có
    if not os.path.exists(telemetry_file):
        print("[*] Generating high-velocity IoT telemetry & command data...")
        generate_telemetry_and_commands(days=10, interval_minutes=30)
    else:
        print("[+] Telemetry & Command data already initialized in bigdata/data/")

    # Bước 2: Chạy Spark Analytics Jobs
    if not os.path.exists(analytics_file):
        print("[*] Running Spark / Hadoop Analytics Batch Processing Jobs...")
        run_spark_analytics_jobs()
    else:
        print("[+] Analytics results already processed.")

    # Bước 3: Mở trình duyệt và khởi chạy Dashboard
    port = 8050
    url = f"http://localhost:{port}"
    print(f"\n[>>>] Khởi chạy Dashboard tại: {url}")
    print("[>>>] Nhấn CTRL+C trong cửa sổ dòng lệnh để dừng server.\n")
    
    open_browser(url)
    
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
