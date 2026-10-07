# HỆ THỐNG QUẢN LÝ VÀ GIÁM SÁT THIẾT BỊ IOT NHÀ THÔNG MINH
## BÀI TẬP CÁ NHÂN MÔN HỌC: CƠ SỞ DỮ LIỆU NÂNG CAO

- **Học viên thực hiện:** Trần Duy Khải
- **Lớp / Khóa học:** K32MCS1 (Khoa học Máy tính)
- **Hệ thống CSDL:** MySQL 8.0 (Chuẩn 3NF, 9 Bảng) & MongoDB (NoSQL) & Apache Spark Engine
- **File Báo cáo Word Chính thức:** [`Bao_Cao_Bai_Tap_Ca_Nhan_CSDLNC.docx`](./Bao_Cao_Bai_Tap_Ca_Nhan_CSDLNC.docx)

---

## 1. CẤU TRÚC THƯ MỤC DỰ ÁN NỘP BÀI

```text
d:\Master_class_K32MCS1\
│
├── 📄 Bao_Cao_Bai_Tap_Ca_Nhan_CSDLNC.docx  <-- BÁO CÁO WORD HOÀN CHỈNH NỘP CHO GIẢNG VIÊN
├── 📄 NGHIEP_VU_VA_TRUY_VAN.md            <-- Chi tiết 10 nghiệp vụ & 41 truy vấn SQL nâng cao
├── 📄 HUONG_DAN_VA_KET_QUA_KIEM_THU_MO_HINH.md <-- Hướng dẫn và kết quả kiểm thử toàn vẹn
├── 🚀 run_demo.py                          <-- 1-Click khởi chạy Web Dashboard Demo (Port 8050)
│
├── 📁 sql/                                  <-- TOÀN BỘ SCRIPT CƠ SỞ DỮ LIỆU MYSQL & WORKBENCH
│   ├── script_create_table_management_smart_home.sql  <-- DDL 9 bảng chuẩn 3NF
│   ├── script_create_table_management_smart_home.mwb  <-- File mô hình MySQL Workbench
│   ├── seed_data_devicetype_and_subscription.sql      <-- Dữ liệu mẫu danh mục chuẩn
│   ├── check_data_integrity.sql                       <-- Kiểm tra ràng buộc khóa & tính toàn vẹn
│   ├── test_model_integrity.sql                      <-- Kịch bản SQL kiểm thử mô hình
│   ├── procedure_generate_million_records.sql         <-- Stored Procedure sinh 1M bản ghi
│   └── load_million_records.sql                       <-- Script LOAD DATA INFILE tốc độ cao
│
├── 📁 scripts/                              <-- TOÀN BỘ SCRIPT PYTHON KIỂM THỬ, TIỆN ÍCH & NẠP DATA
│   ├── test_model_integrity.py              <-- Kiểm thử tự động 100% tính đúng đắn mô hình
│   ├── fast_load_to_mysql.py                <-- Nạp nhanh 1 triệu bản ghi vào MySQL Server
│   ├── generate_million_records.py          <-- Sinh 1 triệu bản ghi viễn thám thực nghiệm
│   ├── build_academic_report.py             <-- Script tự động sinh tài liệu báo cáo Word
│   └── capture_screenshots.py               <-- Script tự động chụp màn hình Dashboard
│
├── 📁 dashboard/                            <-- Web Dashboard IoT Command Center (Flask, Chart.js)
│   ├── app.py                              <-- REST API Backend & Real-time Stream Controller
│   ├── db_manager.py                       <-- Quản lý kết nối đa hệ CSDL MySQL & Big Data
│   └── templates/index.html                <-- Giao diện Dashboard Dark Mode tương tác
│
├── 📁 bigdata/                              <-- Module NoSQL MongoDB & Apache Spark Analytics
│   ├── data/                               <-- Dữ liệu viễn thám chuỗi thời gian & kết quả Spark
│   ├── generate_iot_data.py                <-- Sinh dữ liệu telemetry & nhật ký lệnh điều khiển
│   ├── spark_analytics_jobs.py             <-- Batch processing jobs tính kWh & Z-score Anomaly
│   ├── hadoop_stream_engine.py             <-- Động cơ mô phỏng luồng viễn thám phân tán
│   └── nosql_schema_and_queries.js         <-- Schema validation & Aggregation Pipelines MongoDB
│
├── 📁 phụ lục/                              <-- Biểu mẫu kỹ thuật chuẩn hóa IoT
│   ├── BM_IOT_02_Commissioning_Form.pdf    <-- Biểu mẫu nghiệm thu kỹ thuật thiết bị
│   ├── BM_IOT_03_Commissioning_Test_Record.pdf <-- Biên bản thử tải và đo kiểm
│   ├── BM_IOT_04_Maintenance_Log.pdf      <-- Nhật ký bảo trì, bảo dưỡng thiết bị
│   └── mau-bien-ban-ban-giao-thiet-bi-3.doc <-- Biên bản bàn giao thiết bị hoàn thiện
│
├── 📁 images/                               <-- Hình ảnh sơ đồ ERD, kiến trúc và ảnh chụp giao diện
└── 📁 _archive/                             <-- Lưu trữ đề bài và các bản nháp giai đoạn trước
```

---

## 2. PHÂN NHÓM CÁC MỤC SQL VÀ PYTHON

### A. Nhóm Script SQL (`sql/`):
- `sql/script_create_table_management_smart_home.sql`: Script DDL tạo cấu trúc cơ sở dữ liệu quan hệ gồm 9 bảng chuẩn **3NF** (`User`, `Home`, `HomeMember`, `Room`, `DeviceType`, `Device`, `SubscriptionPlan`, `HomeSubscription`, `Invoice`).
- `sql/script_create_table_management_smart_home.mwb`: Tệp thiết kế trực quan trên MySQL Workbench.
- `sql/seed_data_devicetype_and_subscription.sql`: Dữ liệu quy chuẩn danh mục chủng loại thiết bị và gói cước.
- `sql/check_data_integrity.sql`: Truy vấn kiểm tra ràng buộc khóa chính, khóa ngoại và tính nhất quán.
- `sql/test_model_integrity.sql`: Script kiểm thử toàn vẹn trên hệ quản trị CSDL.
- `sql/procedure_generate_million_records.sql`: Stored Procedure sinh 1.000.000 bản ghi.
- `sql/load_million_records.sql`: Nạp nhanh dữ liệu lớn qua lệnh LOAD DATA INFILE.

### B. Nhóm Script Python (`scripts/`):
- `scripts/test_model_integrity.py`: Bộ kiểm thử toàn diện tự động 100% tính hợp lệ tham chiếu và dạng chuẩn 3NF.
- `scripts/fast_load_to_mysql.py`: Nạp nhanh 1 triệu bản ghi vào MySQL qua socket trực tiếp (không bị timeout).
- `scripts/generate_million_records.py`: Sinh dữ liệu viễn thám và bảng giao dịch thực nghiệm.
- `scripts/build_academic_report.py`: Script tự động xuất báo cáo học thuật định dạng Word (.docx).
- `scripts/capture_screenshots.py`: Script tự động chụp ảnh màn hình giao diện Dashboard.

---

## 3. HƯỚNG DẪN KHỞI CHẠY DEMO HỆ THỐNG (1-CLICK RUN)

### Yêu cầu môi trường:
- Python 3.8+ (đã có thư viện `flask`, `requests`).

### Lệnh chạy demo:
Mở cửa sổ dòng lệnh (Terminal / PowerShell) tại thư mục dự án và thực thi lệnh:

```powershell
python run_demo.py
```

### Hệ thống sẽ tự động:
1. Kiểm tra tập dữ liệu chuỗi thời gian viễn thám trong `bigdata/data/`.
2. Chạy các Batch Processing Jobs tổng hợp điện năng và phát hiện bất thường.
3. Khởi động Web Server tại địa chỉ `http://localhost:8050` và tự động mở trình duyệt hiển thị Dashboard giám sát thời gian thực.
