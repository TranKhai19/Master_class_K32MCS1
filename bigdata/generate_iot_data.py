"""
Module: generate_iot_data.py
Mục đích: Giả lập sinh luồng dữ liệu lớn (Big Data) chuỗi thời gian cho 30 thiết bị IoT
thuộc 16 căn hộ trong hệ thống Smart Home (dựa trên script_create_table_management_smart_home.sql).
Dữ liệu sinh ra bao gồm:
1. device_telemetry (Time-series log cảm biến viễn thám: nhiệt độ, độ ẩm, công suất Watts, điện áp, wifi RSSI)
2. command_logs (Lịch sử thao tác điều khiển thiết bị: ON, OFF, SET_TEMP, LOCK, ...)
3. dimension_metadata (Bảng chiều đồng bộ từ RDBMS MySQL)
"""

import os
import json
import random
from datetime import datetime, timedelta

# Định nghĩa Metadata chuẩn từ SQL script
DEVICE_TYPES = {
    1: {"name": "Smart Switch 2-Gang", "category": "Lighting", "power": 10.0, "mfr": "Tuya Smart"},
    2: {"name": "Smart Switch 4-Gang", "category": "Lighting", "power": 15.0, "mfr": "Aqara"},
    3: {"name": "Air Conditioner Inverter 1.5HP", "category": "Climate", "power": 1200.0, "mfr": "Daikin"},
    4: {"name": "Air Conditioner Inverter 2.0HP", "category": "Climate", "power": 1800.0, "mfr": "Panasonic"},
    5: {"name": "Smart Thermostat & Humidity", "category": "Sensor", "power": 2.5, "mfr": "Xiaomi"},
    6: {"name": "Motion & Lux Sensor", "category": "Sensor", "power": 1.5, "mfr": "Philips Hue"},
    7: {"name": "Smart Door Lock FaceID", "category": "Security", "power": 25.0, "mfr": "Yale"},
    8: {"name": "Smart IP Camera 2K AI", "category": "Security", "power": 12.0, "mfr": "Ezviz"},
}

DEVICES = [
    {"device_id": 1, "room_id": 1, "home_id": 1, "type_id": 1, "name": "Công tắc đèn trần PK", "mac": "AA:BB:CC:11:22:01", "status": "ACTIVE"},
    {"device_id": 2, "room_id": 1, "home_id": 1, "type_id": 3, "name": "Điều hòa Daikin PK", "mac": "AA:BB:CC:11:22:02", "status": "ACTIVE"},
    {"device_id": 3, "room_id": 1, "home_id": 1, "type_id": 8, "name": "Camera an ninh PK", "mac": "AA:BB:CC:11:22:03", "status": "ACTIVE"},
    {"device_id": 4, "room_id": 2, "home_id": 1, "type_id": 5, "name": "Cảm biến nhiệt ẩm Bếp", "mac": "AA:BB:CC:11:22:04", "status": "ACTIVE"},
    {"device_id": 5, "room_id": 2, "home_id": 1, "type_id": 1, "name": "Công tắc đèn bếp", "mac": "AA:BB:CC:11:22:05", "status": "ACTIVE"},
    {"device_id": 6, "room_id": 3, "home_id": 1, "type_id": 3, "name": "Điều hòa PN Master", "mac": "AA:BB:CC:11:22:06", "status": "ACTIVE"},
    {"device_id": 7, "room_id": 3, "home_id": 1, "type_id": 6, "name": "Cảm biến chuyển động PN", "mac": "AA:BB:CC:11:22:07", "status": "OFFLINE"},
    {"device_id": 8, "room_id": 4, "home_id": 2, "type_id": 2, "name": "Công tắc 4 nút Villa", "mac": "AA:BB:CC:11:22:08", "status": "ACTIVE"},
    {"device_id": 9, "room_id": 4, "home_id": 2, "type_id": 7, "name": "Khóa thông minh cửa chính", "mac": "AA:BB:CC:11:22:09", "status": "ACTIVE"},
    {"device_id": 10, "room_id": 5, "home_id": 2, "type_id": 4, "name": "Điều hòa Panasonic Bungalow", "mac": "AA:BB:CC:11:22:10", "status": "ACTIVE"},
    {"device_id": 11, "room_id": 6, "home_id": 3, "type_id": 1, "name": "Công tắc PK HAGL", "mac": "AA:BB:CC:11:22:11", "status": "ACTIVE"},
    {"device_id": 12, "room_id": 6, "home_id": 3, "type_id": 8, "name": "Ezviz Camera Cửa Ra Vào", "mac": "AA:BB:CC:11:22:12", "status": "ACTIVE"},
    {"device_id": 13, "room_id": 7, "home_id": 3, "type_id": 3, "name": "Điều hòa Daikin PN HAGL", "mac": "AA:BB:CC:11:22:13", "status": "ACTIVE"},
    {"device_id": 14, "room_id": 8, "home_id": 4, "type_id": 2, "name": "Aqara Switch Sảnh VIP", "mac": "AA:BB:CC:11:22:14", "status": "ACTIVE"},
    {"device_id": 15, "room_id": 8, "home_id": 4, "type_id": 4, "name": "Điều hòa Panasonic PK VIP", "mac": "AA:BB:CC:11:22:15", "status": "ACTIVE"},
    {"device_id": 16, "room_id": 8, "home_id": 4, "type_id": 7, "name": "Khóa cửa vân tay Yale Đảo KC", "mac": "AA:BB:CC:11:22:16", "status": "ACTIVE"},
    {"device_id": 17, "room_id": 9, "home_id": 4, "type_id": 5, "name": "Cảm biến môi trường Bếp VIP", "mac": "AA:BB:CC:11:22:17", "status": "ACTIVE"},
    {"device_id": 18, "room_id": 10, "home_id": 4, "type_id": 4, "name": "Điều hòa 2.0HP PN VIP", "mac": "AA:BB:CC:11:22:18", "status": "MAINTENANCE"},
    {"device_id": 19, "room_id": 11, "home_id": 5, "type_id": 1, "name": "Công tắc Vinhomes CP", "mac": "AA:BB:CC:11:22:19", "status": "ACTIVE"},
    {"device_id": 20, "room_id": 12, "home_id": 5, "type_id": 6, "name": "Cảm biến chuyển động P.Làm việc", "mac": "AA:BB:CC:11:22:20", "status": "ACTIVE"},
    {"device_id": 21, "room_id": 13, "home_id": 6, "type_id": 8, "name": "Ezviz Camera Hà Nội", "mac": "AA:BB:CC:11:22:21", "status": "ACTIVE"},
    {"device_id": 22, "room_id": 14, "home_id": 7, "type_id": 2, "name": "Công tắc Aqara The Manor", "mac": "AA:BB:CC:11:22:22", "status": "ACTIVE"},
    {"device_id": 23, "room_id": 16, "home_id": 9, "type_id": 1, "name": "Công tắc Nhà Vườn Cẩm Lệ", "mac": "AA:BB:CC:11:22:23", "status": "OFFLINE"},
    {"device_id": 24, "room_id": 18, "home_id": 11, "type_id": 3, "name": "Điều hòa Daikin Hồ Tây", "mac": "AA:BB:CC:11:22:24", "status": "ACTIVE"},
    {"device_id": 25, "room_id": 19, "home_id": 12, "type_id": 7, "name": "Khóa vân tay Căn hộ Sơn Trà", "mac": "AA:BB:CC:11:22:25", "status": "ACTIVE"},
    {"device_id": 26, "room_id": 19, "home_id": 12, "type_id": 8, "name": "Camera Ezviz View Biển", "mac": "AA:BB:CC:11:22:26", "status": "ACTIVE"},
    {"device_id": 27, "room_id": 21, "home_id": 13, "type_id": 1, "name": "Công tắc Hải Châu", "mac": "AA:BB:CC:11:22:27", "status": "ACTIVE"},
    {"device_id": 28, "room_id": 23, "home_id": 15, "type_id": 1, "name": "Công tắc Gò Vấp", "mac": "AA:BB:CC:11:22:28", "status": "ACTIVE"},
    {"device_id": 29, "room_id": 24, "home_id": 16, "type_id": 2, "name": "Aqara Switch Riverside", "mac": "AA:BB:CC:11:22:29", "status": "ACTIVE"},
    {"device_id": 30, "room_id": 25, "home_id": 16, "type_id": 8, "name": "Camera Hầm Rượu Riverside", "mac": "AA:BB:CC:11:22:30", "status": "ACTIVE"},
]

HOMES = [
    {"home_id": 1, "user_id": 1, "name": "Nhà phố Thanh Khê", "city": "Da Nang"},
    {"home_id": 2, "user_id": 1, "name": "Villa nghỉ dưỡng Hội An", "city": "Hoi An"},
    {"home_id": 3, "user_id": 2, "name": "Căn hộ HAGL Danang", "city": "Da Nang"},
    {"home_id": 4, "user_id": 3, "name": "Biệt thự Đảo Kim Cương", "city": "TP.HCM"},
    {"home_id": 5, "user_id": 4, "name": "Chung cư Vinhomes Central Park", "city": "TP.HCM"},
    {"home_id": 6, "user_id": 5, "name": "Nhà phố Ba Đình", "city": "Ha Noi"},
    {"home_id": 7, "user_id": 6, "name": "Penthouse The Manor", "city": "Ha Noi"},
    {"home_id": 8, "user_id": 7, "name": "Căn hộ Masteri Thảo Điền", "city": "TP.HCM"},
    {"home_id": 9, "user_id": 8, "name": "Nhà vườn Cẩm Lệ", "city": "Da Nang"},
    {"home_id": 10, "user_id": 9, "name": "Chung cư Sunrise City", "city": "TP.HCM"},
    {"home_id": 11, "user_id": 10, "name": "Nhà phố Tây Hồ", "city": "Ha Noi"},
    {"home_id": 12, "user_id": 11, "name": "Căn hộ Sơn Trà Ocean View", "city": "Da Nang"},
    {"home_id": 13, "user_id": 12, "name": "Nhà riêng Hải Châu", "city": "Da Nang"},
    {"home_id": 14, "user_id": 13, "name": "Căn hộ Ecopark Sky Oasis", "city": "Hung Yen"},
    {"home_id": 15, "user_id": 14, "name": "Nhà phố Gò Vấp", "city": "TP.HCM"},
    {"home_id": 16, "user_id": 15, "name": "Biệt thự Vinhome Riverside", "city": "Ha Noi"},
]

SUBSCRIPTIONS = [
    {"sub_id": 1, "home_id": 1, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "PAID"},
    {"sub_id": 2, "home_id": 1, "plan_id": 3, "plan_name": "Premium Pro", "price": 199000, "retention_days": 90, "status": "PAID"},
    {"sub_id": 3, "home_id": 2, "plan_id": 3, "plan_name": "Premium Pro", "price": 199000, "retention_days": 90, "status": "PAID"},
    {"sub_id": 4, "home_id": 3, "plan_id": 1, "plan_name": "Free Tier", "price": 0, "retention_days": 7, "status": "EXPIRED"},
    {"sub_id": 5, "home_id": 3, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "PAID"},
    {"sub_id": 6, "home_id": 4, "plan_id": 4, "plan_name": "Enterprise Lifetime", "price": 499000, "retention_days": 365, "status": "PAID"},
    {"sub_id": 7, "home_id": 5, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "PAID"},
    {"sub_id": 8, "home_id": 6, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "EXPIRED"},
    {"sub_id": 9, "home_id": 7, "plan_id": 3, "plan_name": "Premium Pro", "price": 199000, "retention_days": 90, "status": "PAID"},
    {"sub_id": 10, "home_id": 8, "plan_id": 1, "plan_name": "Free Tier", "price": 0, "retention_days": 7, "status": "EXPIRED"},
    {"sub_id": 11, "home_id": 9, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "PAID"},
    {"sub_id": 12, "home_id": 10, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "PENDING"},
    {"sub_id": 13, "home_id": 11, "plan_id": 3, "plan_name": "Premium Pro", "price": 199000, "retention_days": 90, "status": "PAID"},
    {"sub_id": 14, "home_id": 12, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "PAID"},
    {"sub_id": 15, "home_id": 13, "plan_id": 1, "plan_name": "Free Tier", "price": 0, "retention_days": 7, "status": "EXPIRED"},
    {"sub_id": 16, "home_id": 14, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "PAID"},
    {"sub_id": 17, "home_id": 15, "plan_id": 2, "plan_name": "Standard Cloud", "price": 99000, "retention_days": 30, "status": "PENDING"},
    {"sub_id": 18, "home_id": 16, "plan_id": 4, "plan_name": "Enterprise Lifetime", "price": 499000, "retention_days": 365, "status": "PAID"},
]

def generate_telemetry_and_commands(days=14, interval_minutes=15):
    """
    Tạo dữ liệu viễn thám chuỗi thời gian cho các thiết bị
    - Tạo chu kỳ ngày/đêm thực tế
    - Thêm các sự kiện bất thường (Anomalies):
      + Quá nhiệt (Thermal Alert > 45°C tại Bếp/PK)
      + Quá tải (Power Overload > default_power * 1.25)
      + Thiết bị rớt mạng (Offline)
    """
    print(f"[*] Generating telemetry data for {len(DEVICES)} devices across {days} days...")
    
    end_time = datetime(2025, 7, 31, 23, 45, 0)
    start_time = end_time - timedelta(days=days)
    
    telemetry_records = []
    command_records = []
    
    cmd_actions = {
        "Lighting": ["TURN_ON", "TURN_OFF", "DIM_BRIGHTNESS", "SET_COLOR_TEMP"],
        "Climate": ["TURN_ON", "TURN_OFF", "SET_TEMPERATURE", "CHANGE_FAN_SPEED", "SET_ECO_MODE"],
        "Security": ["LOCK_DOOR", "UNLOCK_DOOR", "ARM_SECURITY", "CAPTURE_SNAPSHOT", "TRIGGER_SIREN"],
        "Sensor": ["SYNC_BATTERY", "CALIBRATE_SENSOR", "READ_INSTANT_TELEMETRY"]
    }
    
    current_time = start_time
    total_steps = int((end_time - start_time).total_seconds() / (interval_minutes * 60))
    step = 0
    
    while current_time <= end_time:
        hour = current_time.hour
        is_daytime = 6 <= hour <= 18
        is_peak_hour = (11 <= hour <= 13) or (18 <= hour <= 22)
        
        # Nhiệt độ nền môi trường tự nhiên (mùa hè miền Trung/Bắc: 26°C - 36°C)
        ambient_temp = 27.0 + 7.0 * (1.0 if 12 <= hour <= 15 else (0.3 if 0 <= hour <= 5 else 0.7)) + random.uniform(-1.0, 1.0)
        ambient_humidity = 60.0 - 15.0 * (1.0 if 12 <= hour <= 15 else 0.0) + random.uniform(-4.0, 4.0)

        for dev in DEVICES:
            dev_id = dev["device_id"]
            dev_type = DEVICE_TYPES[dev["type_id"]]
            category = dev_type["category"]
            default_pwr = dev_type["power"]
            
            # Nếu thiết bị trong SQL bị OFFLINE
            if dev["status"] == "OFFLINE":
                # Vẫn ghi nhận log mất tín hiệu định kỳ
                if random.random() < 0.05:
                    telemetry_records.append({
                        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "device_id": dev_id,
                        "device_name": dev["name"],
                        "room_id": dev["room_id"],
                        "home_id": dev["home_id"],
                        "category": category,
                        "status": "OFFLINE",
                        "metrics": {
                            "temperature": None,
                            "humidity": None,
                            "power_watts": 0.0,
                            "voltage": 0.0,
                            "rssi_dbm": None
                        },
                        "is_anomaly": True,
                        "anomaly_reason": "DEVICE_OFFLINE"
                    })
                continue
            
            # Tính toán tải tiêu thụ công suất thực tế
            power_watts = 0.0
            temp = ambient_temp
            humidity = ambient_humidity
            is_anomaly = False
            anomaly_reason = "NORMAL"
            
            if category == "Climate":
                # Điều hòa hoạt động mạnh vào giờ cao điểm
                if is_peak_hour or (is_daytime and random.random() < 0.75):
                    # Đang bật làm lạnh
                    power_watts = default_pwr * random.uniform(0.75, 1.05)
                    temp = random.uniform(22.0, 26.0) # Nhiệt độ trong phòng điều hòa
                    humidity = random.uniform(45.0, 58.0)
                else:
                    # Chế độ chờ standby
                    power_watts = random.uniform(3.0, 8.0)
                    temp = ambient_temp - 1.5
                    
                # Kịch bản Anomaly: Thiết bị #15 (Điều hòa Panasonic VIP) có lúc quá tải
                if dev_id == 15 and current_time.day in [25, 28] and hour in [13, 14]:
                    power_watts = default_pwr * random.uniform(1.30, 1.45) # Quá tải > 2400W
                    is_anomaly = True
                    anomaly_reason = "POWER_OVERLOAD"
                    
            elif category == "Lighting":
                # Chiếu sáng bật vào buổi tối (18h - 23h)
                if 18 <= hour <= 23:
                    power_watts = default_pwr * random.uniform(0.8, 1.0)
                elif 5 <= hour <= 7 and random.random() < 0.4:
                    power_watts = default_pwr * 0.5
                else:
                    power_watts = 0.5 # Standby MCU
                    
            elif category == "Sensor":
                power_watts = default_pwr * random.uniform(0.9, 1.0)
                # Kịch bản Anomaly: Quá nhiệt phòng bếp (Thiết bị #4: Cảm biến nhiệt ẩm Bếp)
                if dev_id == 4 and current_time.day == 26 and 11 <= hour <= 12:
                    temp = random.uniform(46.5, 52.0) # Quá nhiệt > 45°C cảnh báo cháy
                    is_anomaly = True
                    anomaly_reason = "HIGH_TEMPERATURE_ALERT"
                # Thiết bị #17 (Cảm biến Bếp VIP)
                elif dev_id == 17 and current_time.day == 29 and hour == 19:
                    temp = random.uniform(47.0, 49.5)
                    is_anomaly = True
                    anomaly_reason = "HIGH_TEMPERATURE_ALERT"
                    
            elif category == "Security":
                # Camera & Khóa thông minh hoạt động 24/7
                power_watts = default_pwr * random.uniform(0.85, 1.1)

            # Tạo bản ghi viễn thám Telemetry
            voltage = round(random.uniform(218.0, 224.5), 1)
            rssi = random.randint(-75, -45) # Cường độ tín hiệu Wi-Fi
            
            telemetry_records.append({
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "device_id": dev_id,
                "device_name": dev["name"],
                "room_id": dev["room_id"],
                "home_id": dev["home_id"],
                "category": category,
                "status": "ACTIVE",
                "metrics": {
                    "temperature": round(temp, 1),
                    "humidity": round(humidity, 1),
                    "power_watts": round(power_watts, 2),
                    "voltage": voltage,
                    "rssi_dbm": rssi
                },
                "is_anomaly": is_anomaly,
                "anomaly_reason": anomaly_reason
            })
            
            # Thỉnh thoảng phát sinh Command Log (Lệnh điều khiển)
            if random.random() < 0.04:
                action = random.choice(cmd_actions[category])
                source = random.choice(["MOBILE_APP", "AUTOMATION_SCHEDULE", "VOICE_ASSISTANT"])
                status = "SUCCESS" if random.random() > 0.05 else "TIMEOUT"
                latency = random.randint(45, 380) if status == "SUCCESS" else random.randint(3000, 5000)
                
                command_records.append({
                    "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "log_id": f"CMD-{current_time.strftime('%Y%m%d%H%M')}-{dev_id:02d}",
                    "device_id": dev_id,
                    "device_name": dev["name"],
                    "home_id": dev["home_id"],
                    "action": action,
                    "source": source,
                    "status": status,
                    "latency_ms": latency
                })
                
        current_time += timedelta(minutes=interval_minutes)
        step += 1
        if step % 200 == 0:
            print(f"   Progress: {step}/{total_steps} time steps ({len(telemetry_records)} records)...")
            
    print(f"[+] Total Telemetry Records generated: {len(telemetry_records)}")
    print(f"[+] Total Command Records generated: {len(command_records)}")
    
    # Xuất ra thư mục bigdata/data
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    
    # Lưu JSON cho NoSQL / MongoDB
    with open(os.path.join(out_dir, "device_telemetry.json"), "w", encoding="utf-8") as f:
        json.dump(telemetry_records, f, ensure_ascii=False)
        
    with open(os.path.join(out_dir, "command_logs.json"), "w", encoding="utf-8") as f:
        json.dump(command_records, f, ensure_ascii=False)
        
    # Lưu metadata kích thước & bảng chiều
    metadata = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_devices": len(DEVICES),
        "total_homes": len(HOMES),
        "total_telemetry": len(telemetry_records),
        "total_commands": len(command_records),
        "devices": DEVICES,
        "device_types": DEVICE_TYPES,
        "homes": HOMES,
        "subscriptions": SUBSCRIPTIONS
    }
    with open(os.path.join(out_dir, "metadata_dimensions.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Successfully saved datasets to {out_dir}")
    return telemetry_records, command_records, metadata

if __name__ == "__main__":
    generate_telemetry_and_commands(days=10, interval_minutes=30)
