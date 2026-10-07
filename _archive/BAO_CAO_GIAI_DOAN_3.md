# BÁO CÁO BÀI TẬP LỚN (CAPSTONE PROJECT) — GIAI ĐOẠN 3 (CUỐI KHÓA)
## Môn học: Cơ sở Dữ liệu Nâng cao
**Học viên thực hiện:** Trần Duy Khải  
**Mã lớp:** K32MCS1  
**Đề tài:** Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh (Smart Home IoT System)  

---

## 1. TỔNG QUAN HỆ THỐNG VÀ BỐI CẢNH DỮ LIỆU

### 1.1. Kế thừa từ Giai đoạn 1 & Giai đoạn 2
Trong hai giai đoạn trước, hệ thống đã hoàn thành trọn vẹn phần thiết kế và cài đặt cơ sở dữ liệu quan hệ (RDBMS MySQL `smart_home_info`):
- **Giai đoạn 1**: Khảo sát nghiệp vụ, thiết kế mô hình thực thể liên kết (ERD) và chuẩn hóa dữ liệu đạt chuẩn **3NF** nhằm loại bỏ triệt để hiện tượng trùng lặp và dị thường cập nhật.
- **Giai đoạn 2**: Cài đặt script DDL/DML trên MySQL gồm 7 bảng nghiệp vụ lõi:
  1. `User`: Quản lý 15 tài khoản khách hàng sở hữu hệ thống.
  2. `Home`: Quản lý 16 bất động sản / biệt thự / căn hộ tại Đà Nẵng, Hà Nội, TP.HCM, Hội An.
  3. `Room`: Quản lý 25 phân khu chức năng (Phòng khách, Phòng bếp, Phòng ngủ master, Sảnh...).
  4. `DeviceType`: Danh mục quy chuẩn 8 chủng loại thiết bị (Tuya, Aqara, Daikin, Panasonic, Xiaomi, Ezviz, Yale).
  5. `Device`: 30 thiết bị vật lý hoạt động trong các căn hộ kèm Serial Number, MAC address.
  6. `SubscriptionPlan`: 4 gói dịch vụ lưu trữ đám mây (Free Tier 7 ngày, Standard 30 ngày, Premium 90 ngày, Enterprise 365 ngày).
  7. `HomeSubscription`: 18 hợp đồng thuê bao gắn liền với các căn hộ.

### 1.2. Thách thức Dữ liệu & Mục tiêu của Giai đoạn 3
Hệ thống IoT phát sinh khối lượng dữ liệu khổng lồ với đặc tính **3V của Big Data**:
- **Volume (Dung lượng lớn)**: Hàng chục nghìn log viễn thám chuỗi thời gian mỗi ngày từ các cảm biến nhiệt ẩm, công tắc, điều hòa, camera.
- **Velocity (Tốc độ phát sinh cao)**: Cảm biến gửi dữ liệu liên tục theo chu kỳ vài phút hoặc theo sự kiện.
- **Variety (Đa dạng cấu trúc)**: Dữ liệu đo lường viễn thám (nhiệt độ, công suất, điện áp, wifi RSSI) và nhật ký thao tác lệnh (Action, Payload JSON, Status) có cấu trúc bán cấu trúc, không phù hợp lưu trữ trực tiếp trong bảng RDBMS truyền thống do nghẽn I/O và chi phí mở rộng lớn.

**Mục tiêu Giai đoạn 3:**
1. Thiết kế và cài đặt cấu trúc lưu trữ **NoSQL (MongoDB)** cho dữ liệu phi cấu trúc và chuỗi thời gian.
2. Xây dựng quy trình xử lý dữ liệu lớn trên **Hệ sinh thái Hadoop (HDFS / Parquet) & Apache Spark (PySpark Engine)**.
3. Trực quan hóa kết quả phân tích trên **Web Dashboard tương tác (IoT Command Center)** để phát hiện bất thường, tối ưu năng lượng và quản trị thuê bao.

---

## 2. THIẾT KẾ CƠ SỞ DỮ LIỆU NOSQL (MONGODB)

### 2.1. Thiết kế Collections và Schema Validation
Hệ thống sử dụng MongoDB với 2 Collections tối ưu:

#### Collection 1: `device_telemetry` (Log Viễn thám Chuỗi thời gian)
Lưu trữ định kỳ trạng thái hoạt động và các chỉ số đo lường môi trường / điện năng:
```json
{
  "_id": ObjectId("66da1f8b89e3a102c9a10001"),
  "timestamp": "2025-07-28 13:30:00",
  "device_id": 2,
  "device_name": "Điều hòa Daikin PK",
  "room_id": 1,
  "home_id": 1,
  "category": "Climate",
  "status": "ACTIVE",
  "metrics": {
    "temperature": 24.2,
    "humidity": 52.0,
    "power_watts": 1210.5,
    "voltage": 220.4,
    "rssi_dbm": -58
  },
  "is_anomaly": false,
  "anomaly_reason": "NORMAL"
}
```

#### Collection 2: `command_logs` (Nhật ký Thao tác Điều khiển)
Lưu trữ lịch sử thực thi các lệnh từ người dùng hoặc hệ thống tự động:
```json
{
  "_id": ObjectId("66da1f8b89e3a102c9a10500"),
  "timestamp": "2025-07-28 18:45:10",
  "log_id": "CMD-202507281845-02",
  "device_id": 2,
  "device_name": "Điều hòa Daikin PK",
  "home_id": 1,
  "action": "SET_TEMPERATURE",
  "source": "MOBILE_APP",
  "status": "SUCCESS",
  "latency_ms": 142
}
```

### 2.2. Chiến lược Đánh chỉ mục (Indexing Strategy)
Để đảm bảo tốc độ truy vấn thời gian thực dưới 10ms trên tập dữ liệu hàng triệu bản ghi, hệ thống thiết lập các Compound Indexes:
1. `db.device_telemetry.createIndex({ "device_id": 1, "timestamp": -1 })`: Tối ưu truy vấn vẽ biểu đồ chuỗi thời gian cho từng thiết bị trên Mobile App.
2. `db.device_telemetry.createIndex({ "home_id": 1, "timestamp": -1 })`: Tối ưu truy vấn tổng hợp phụ tải điện cho từng căn hộ.
3. `db.device_telemetry.createIndex({ "is_anomaly": 1, "anomaly_reason": 1 })`: Tối ưu quét nhanh các sự cố bất thường (quá nhiệt, quá tải).
4. `db.command_logs.createIndex({ "source": 1, "status": 1 })`: Phục vụ đối soát độ tin cậy của các kênh điều khiển (Mobile vs Schedule vs Voice).

### 2.3. Các Truy vấn Phân tích Nâng cao (Aggregation Pipelines)
Trong tệp `bigdata/nosql_schema_and_queries.js`, các Aggregation Pipelines mẫu đã được cài đặt:
- **Pipeline 1**: Tính tổng công suất và trung bình Watts theo từng chủng loại thiết bị (`$group` by `$category`).
- **Pipeline 2**: Lọc và cảnh báo tức thời các sự cố quá nhiệt (`metrics.temperature >= 45.0°C`) phục vụ hệ thống báo cháy.
- **Pipeline 3**: Thống kê tỷ lệ thành công và độ trễ trung bình của các kênh gửi lệnh (`$avg: "$latency_ms"`).
- **Pipeline 4**: Tính toán tổng điện năng tiêu thụ (kWh) theo từng căn hộ thông qua tích phân công suất theo thời gian.

---

## 3. KIẾN TRÚC HỆ SINH THÁI BIG DATA (HADOOP / SPARK PIPELINE)

### 3.1. Sơ đồ Luồng Dữ liệu Đa tầng (Multi-tier Architecture)

```
[IoT Sensors & Devices] (30 thiết bị)
        │
        ▼ (MQTT / HTTP JSON Stream)
[NoSQL Hot Storage] (MongoDB: device_telemetry, command_logs)
        │
        ├─────────────────────────────────────────┐
        ▼ (Batch Ingestion & Parquet Compression)   ▼ (Realtime Query)
[Hadoop Data Lake] (HDFS: Cold Storage Parquet)   [Web Dashboard UI]
        │
        ▼ (Distributed Processing)
[Apache Spark / Hadoop MapReduce Engine]
  ├── Job 1: Energy & Power Consumption Aggregation (kWh)
  ├── Job 2: Anomaly Detection & Thermal/Overload Alerts
  ├── Job 3: Command Usage & Latency Profiling
  └── Job 4: Subscription & Retention Compliance Check
        │
        ▼
[Business Intelligence & Dashboard Serving] (Flask REST API + Chart.js)
```

### 3.2. Cấu trúc Phân vùng HDFS & Quản trị Vòng đời Dữ liệu (DLM)
- Dữ liệu viễn thám lưu trữ dài hạn trên HDFS được nén bằng định dạng **Apache Parquet (Snappy)** theo mô hình phân vùng thời gian:
  ```
  /datalake/smart_home/telemetry/year=2025/month=07/day=28/part-00000.parquet
  ```
- **Đối soát Chính sách Lưu trữ theo Gói cước (Data Retention Policy)**:
  Tích hợp bảng `SubscriptionPlan` từ MySQL:
  + Gói Miễn phí (Free Tier): Dữ liệu được lưu trữ tối đa **7 ngày**, sau 7 ngày hệ thống tự động xóa bản ghi (TTL hoặc HDFS cleanup script).
  + Gói Cơ bản (Standard Cloud): Lưu trữ **30 ngày**.
  + Gói Nâng cao (Premium Pro): Lưu trữ **90 ngày**.
  + Gói Doanh nghiệp (Enterprise Lifetime): Lưu trữ **365 ngày**.

---

## 4. CÁC MÔ HÌNH PHÂN TÍCH DỮ LIỆU LỚN & KẾT QUẢ RÚT RA

### 4.1. Phân tích Tiêu thụ Điện năng (Energy Analytics)
- **Công thức tính điện năng tiêu thụ**:
  $$\text{Energy (kWh)} = \sum_{i=1}^{N} \frac{P_i \times \Delta t_i}{1000}$$
  *(với $P_i$ là công suất đo bằng Watts, $\Delta t_i$ là khoảng thời gian lấy mẫu = 0.5 giờ).*
- **Kết quả thu được**:
  1. **Nhóm thiết bị ngốn điện nhất**: Nhóm **Climate (Điều hòa nhiệt độ Daikin, Panasonic)** chiếm tới **~88.5%** tổng điện năng toàn hệ thống, tiếp theo là nhóm **Lighting** (~6.8%), **Security** (~3.7%) và **Sensor** (~1.0%).
  2. **Phân tích Phụ tải Giờ Cao Điểm (Peak vs Off-Peak)**:
     - Giờ cao điểm (11h-13h buổi trưa và 18h-22h buổi tối) chiếm tới **54.2%** lượng điện tiêu thụ trong ngày.
     - **Giá trị kinh doanh**: Hệ thống có thể gửi thông báo gợi ý hoặc kích hoạt chế độ "Eco-Smart" trên ứng dụng, tự động tăng điều hòa lên 1°C hoặc tắt các đèn không cần thiết vào khung giờ cao điểm để tiết kiệm 15-25% hóa đơn tiền điện EVN cho khách hàng.

### 4.2. Giám sát An toàn & Phát hiện Bất thường (Anomaly Detection)
Thuật toán đối soát dữ liệu viễn thám với bảng quy chuẩn `DeviceType` trong MySQL:
1. **Cảnh báo Quá nhiệt (Thermal Alert - Mức CRITICAL)**:
   - Phát hiện cảm biến nhiệt ẩm tại phòng bếp của *Nhà phố Thanh Khê* (#4) và *Biệt thự Đảo Kim Cương* (#17) đo được nhiệt độ đạt tới **48°C - 52°C**.
   - **Ứng dụng**: Kích hoạt còi hú báo cháy tức thời và gửi cảnh báo đỏ khẩn cấp đến điện thoại chủ nhà.
2. **Cảnh báo Vượt công suất Định mức (Power Overload - Mức HIGH)**:
   - Thiết bị #15 (Điều hòa Panasonic 2.0HP tại Đảo Kim Cương có định mức 1800W) có thời điểm tiêu thụ lên tới **2450W** (vượt > 135% định mức).
   - **Ứng dụng**: Cảnh báo nguy cơ chập cháy aptomat, khuyến cáo gia chủ bảo trì máy lạnh định kỳ.
3. **Cảnh báo Thiết bị Rớt mạng (Offline Dropouts - Mức MEDIUM)**:
   - Phát hiện cảm biến chuyển động #7 và công tắc #23 mất tín hiệu Wi-Fi kéo dài.

### 4.3. Phân tích Thói quen Điều khiển (Command Behavior)
- Tỷ lệ kích hoạt qua **Mobile App chiếm 48.3%**, qua **Kịch bản Tự động hóa (Automation Schedule) chiếm 32.5%**, qua **Trợ lý Giọng nói (Voice Assistant) chiếm 19.2%**.
- Tỷ lệ thực thi lệnh thành công đạt **95.2%** với độ trễ trung bình rất thấp (**184ms** đối với Mobile App).

### 4.4. Phân tích Kinh doanh & Hợp đồng Thuê bao (Subscription Business Insights)
- Doanh thu từ các hợp đồng thuê bao đã thanh toán (`PAID`) đạt **1,891,000 VNĐ** (trong đó gói Enterprise Lifetime và Premium Pro chiếm 85% tổng doanh thu).
- Đạt tỷ lệ tuân thủ chính sách lưu trữ dữ liệu (SLA Data Retention Compliance) **100%** đối với tất cả 18 hợp đồng.

---

## 5. WEB DASHBOARD TRỰC QUAN HÓA (IOT COMMAND CENTER)

Dashboard được xây dựng tại thư mục `dashboard/` với backend Flask và frontend Dark Mode ứng dụng Tailwind CSS & Chart.js:
- **Tab 1: Tổng quan Hệ thống (Executive Overview)**: Hiển thị 5 thẻ KPI đầu bảng, biểu đồ đường biến thiên công suất 24h, biểu đồ tròn cơ cấu tiêu thụ và bảng xếp hạng tiêu thụ của các căn hộ.
- **Tab 2: Luồng Dữ liệu NoSQL & Hadoop (Data Pipeline Explorer)**: Sơ đồ tương tác giải thích 5 tầng kiến trúc dữ liệu, tích hợp trình xem JSON document thực tế của `device_telemetry` và `command_logs`.
- **Tab 3: Phân tích Năng lượng (Energy & Load Analytics)**: Biểu đồ cột tiêu thụ theo ngày, biểu đồ phân bổ giờ cao điểm EVN và bảng chi tiết sản lượng điện kèm ước tính cước phí của 16 căn hộ.
- **Tab 4: Giám sát An toàn & Bất thường (Anomaly & Health Center)**: Bảng nhật ký sự cố thời gian thực kèm bộ lọc phân loại mức độ nguy hiểm (Critical, High, Medium).
- **Tab 5: Kinh doanh & Thuê bao (Subscription & Retention)**: Biểu đồ doanh thu từng gói cước và bảng kiểm toán tuân thủ `retention_days`.
- **Bộ lọc Dropdown Căn hộ**: Cho phép lọc số liệu chi tiết cho bất kỳ căn hộ nào trong 16 căn nhà.

---

## 6. HƯỚNG DẪN KHỞI CHẠY VÀ THUYẾT TRÌNH DEMO (1-CLICK RUN)

### 6.1. Yêu cầu Môi trường
- Python 3.8+ (đã có sẵn trong môi trường của máy).
- Các thư viện chuẩn: `flask`, `requests` (đã cài đặt).

### 6.2. Lệnh khởi chạy duy nhất
Tại cửa sổ dòng lệnh PowerShell hoặc Terminal trong thư mục dự án:
```powershell
python run_demo.py
```

### 6.3. Chu trình Tự động của Script:
1. Tự động kiểm tra dữ liệu lớn viễn thám trong thư mục `bigdata/data/`. Nếu chưa có, script tự động sinh hơn 13,500+ bản ghi đo lường thực tế.
2. Tự động thực thi 4 Batch Jobs phân tích dữ liệu lớn (`spark_analytics_jobs.py`).
3. Khởi động Web Server tại địa chỉ `http://localhost:8050` và tự động mở trình duyệt web hiển thị Dashboard trực quan hóa.

---

## 7. KẾT LUẬN

Bài tập lớn đã hoàn thành trọn vẹn mục tiêu của cả 3 giai đoạn:
1. **Thiết kế CSDL Quan hệ chuẩn mực (MySQL - 3NF)**: Đảm bảo tính toàn vẹn và nhất quán cho các dữ liệu giao dịch cốt lõi (Người dùng, Căn hộ, Thiết bị, Hợp đồng).
2. **Triển khai Big Data & NoSQL (MongoDB + Hadoop/Spark Paradigm)**: Giải quyết triệt để bài toán lưu trữ luồng dữ liệu IoT tốc độ cao, chuỗi thời gian và dung lượng lớn.
3. **Phân tích & Trực quan hóa Nghiệp vụ**: Cung cấp các insight kinh doanh thực tế, kịch bản cảnh báo an toàn hỏa hoạn/quá tải và công cụ quản trị hiện đại cho hệ sinh thái Nhà thông minh.
