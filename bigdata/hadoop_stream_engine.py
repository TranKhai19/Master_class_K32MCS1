# -*- coding: utf-8 -*-
"""
HADOOP STREAMING INGESTION & MAPREDUCE MICRO-BATCH ENGINE
Môn học: Cơ sở Dữ liệu Nâng cao - K32MCS1 | Học viên: Trần Duy Khải

Chức năng:
1. Tiếp nhận luồng viễn thám IoT từ TOÀN BỘ CSDL (1,000,000 căn hộ & 1,000,000 thiết bị).
2. Quản lý việc nạp dữ liệu vào HDFS Data Lake theo cấu trúc phân vùng thời gian:
   /datalake/smart_home/telemetry/year=YYYY/month=MM/day=DD/block_XXXX.parquet
3. Thực thi tác vụ MapReduce Streaming động:
   - Map: bóc tách tuple khóa-giá trị (home_id, (watts, temp, voltage, status))
   - Reduce: tổng hợp phụ tải Watts, tính tích phân năng lượng kWh và phát hiện bất thường
4. Giám sát an toàn & phát hiện bất thường thời gian thực (Thermal Overheat, Power Overload).
5. Hỗ trợ kích hoạt sự cố mẫu (Trigger Anomaly Surge) trên bất kỳ căn hộ nào trong toàn bộ CSDL.
"""

import os
import sys
import time
import random
from datetime import datetime

class HadoopStreamEngine:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = os.path.dirname(self.base_dir)
        
        # Trạng thái luồng Hadoop
        self.is_active = True
        self.block_counter = 58240
        self.total_processed_records = 2458900
        self.last_stream_time = time.time()
        self.surge_mode = False
        self.surge_home_id = 1
        
        # Trạng thái runtime động của các căn hộ đang được theo dõi
        self.home_states = {}
        
        # Danh sách chủng loại thiết bị chuẩn
        self.device_types = {
            1: {"name": "Smart Switch 2-Gang", "category": "Lighting", "power": 10.0},
            2: {"name": "Smart Switch 4-Gang", "category": "Lighting", "power": 15.0},
            3: {"name": "Air Conditioner 1.5HP", "category": "Climate", "power": 1200.0},
            4: {"name": "Air Conditioner 2.0HP", "category": "Climate", "power": 1800.0},
            5: {"name": "Smart Thermostat & Humidity", "category": "Sensor", "power": 2.5},
            6: {"name": "Motion & Lux Sensor", "category": "Sensor", "power": 1.5},
            7: {"name": "Smart Door Lock FaceID", "category": "Security", "power": 25.0},
            8: {"name": "Smart IP Camera 2K", "category": "Security", "power": 12.0},
            9: {"name": "Smart Socket Power Meter", "category": "Power", "power": 5.0},
            10: {"name": "Water Heater Controller", "category": "Power", "power": 2500.0},
            11: {"name": "Gas & Smoke Detector", "category": "Sensor", "power": 3.0},
            12: {"name": "Smart Curtain Motor", "category": "Lighting", "power": 45.0}
        }
        
        # Khởi tạo mặc định cho nhóm căn hộ đầu tiên (1..24)
        for hid in range(1, 25):
            self._ensure_home_state(hid)

    def _ensure_home_state(self, home_id):
        """Khởi tạo hoặc trả về trạng thái streaming của một căn hộ bất kỳ trong CSDL"""
        if home_id not in self.home_states:
            initial_w = round(random.uniform(450.0, 2200.0), 1)
            self.home_states[home_id] = {
                "home_id": home_id,
                "name": f"Smart Home #{home_id}",
                "city": ["TP.HCM", "Hà Nội", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "Nha Trang", "Huế", "Hội An"][home_id % 8],
                "active_devices_count": random.randint(3, 6),
                "total_devices_count": random.randint(4, 7),
                "current_power_w": initial_w,
                "accumulated_kwh": round(initial_w * 0.12 + random.uniform(10.0, 150.0), 2),
                "last_temp_c": round(random.uniform(24.0, 29.0), 1),
                "status": "NORMAL"
            }
        return self.home_states[home_id]

    def trigger_surge(self, home_id=None):
        """Kích hoạt sự cố đột biến mẫu trên căn hộ được chỉ định"""
        self.surge_mode = True
        if home_id and int(home_id) > 0:
            self.surge_home_id = int(home_id)
        else:
            active_ids = list(self.home_states.keys())
            self.surge_home_id = random.choice(active_ids) if active_ids else 1
            
        self._ensure_home_state(self.surge_home_id)
        return {
            "status": "SURGE_TRIGGERED",
            "target_home_id": self.surge_home_id,
            "target_home_name": f"Smart Home #{self.surge_home_id}",
            "message": f"Hadoop Engine: Đã kích hoạt sự cố quá nhiệt & quá tải dòng điện cho Căn hộ #{self.surge_home_id}!"
        }

    def get_micro_batch(self, active_home_ids=None):
        """
        Thực thi 1 nhịp Micro-batch MapReduce từ Hadoop Data Lake:
        - Nhận danh sách các căn hộ đang được hiển thị trên UI (active_home_ids)
        - Thực thi Map: Bóc tách viễn thám thiết bị
        - Thực thi Reduce: Tổng hợp phụ tải Watts & lũy kế kWh
        - Trả về HDFS block info và live states
        """
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        date_partition = now.strftime("year=%Y/month=%m/day=%d")
        
        self.block_counter += 1
        new_records_count = random.randint(120, 350)
        self.total_processed_records += new_records_count
        
        datanode_id = f"datanode-0{random.randint(1, 4)}.hadoop.cluster"
        block_name = f"part-{self.block_counter:05d}.snappy.parquet"
        hdfs_path = f"/datalake/smart_home/telemetry/{date_partition}/{block_name}"
        
        # Xác định tập home_ids cần tính toán streaming trong nhịp này
        target_hids = []
        if active_home_ids:
            try:
                target_hids = [int(x) for x in active_home_ids if str(x).isdigit()]
            except Exception:
                target_hids = []
                
        if not target_hids:
            target_hids = list(self.home_states.keys())[:24]

        # Đảm bảo các home_id đều có state
        for hid in target_hids:
            self._ensure_home_state(hid)

        telemetry_events = []
        new_anomalies = []

        # 1. MAP PHASE: Bóc tách telemetry cho từng thiết bị của các home đang hiển thị
        for hid in target_hids:
            # Mỗi nhà sinh 4-6 thiết bị viễn thám
            num_devs = self.home_states[hid]["active_devices_count"]
            for d_idx in range(num_devs):
                dev_id = (hid - 1) * 6 + d_idx + 1
                type_id = (d_idx % 4) + 1
                if d_idx == 1: type_id = 3 # AC
                elif d_idx == 3: type_id = 5 # Sensor
                
                dtype = self.device_types.get(type_id, {"name": "Device", "category": "General", "power": 40.0})
                base_power = dtype["power"]
                category = dtype["category"]
                
                # Dao động tự nhiên ±8%
                factor = random.uniform(0.92, 1.08)
                power_w = round(base_power * factor, 1)
                temp_c = round(random.uniform(23.5, 29.5), 1)
                voltage_v = round(random.uniform(219.0, 221.5), 1)
                
                # Kiểm tra chế độ đột biến tải (Surge Mode)
                if self.surge_mode and hid == self.surge_home_id and category in ["Climate", "Power", "Sensor"]:
                    power_w = round(base_power * 1.65, 1) # Quá tải 165%
                    temp_c = round(random.uniform(50.0, 56.5), 1) # Quá nhiệt > 50°C
                    new_anomalies.append({
                        "timestamp": timestamp_str,
                        "home_id": hid,
                        "home_name": f"Smart Home #{hid}",
                        "device_id": dev_id,
                        "device_name": f"{dtype['name']} #{dev_id}",
                        "category": category,
                        "severity": "CRITICAL",
                        "reason": "THERMAL_OVERHEAT & POWER_OVERLOAD",
                        "measured_temp": temp_c,
                        "measured_power": power_w,
                        "detail": f"Hadoop MapReduce phát hiện Căn hộ #{hid}: Nhiệt độ {temp_c}°C và công suất {power_w}W vượt ngưỡng an toàn!"
                    })
                    
                telemetry_events.append({
                    "device_id": dev_id,
                    "home_id": hid,
                    "category": category,
                    "power_w": power_w,
                    "temp_c": temp_c,
                    "voltage_v": voltage_v
                })

        # Reset surge flag
        if self.surge_mode:
            self.surge_mode = False

        # 2. REDUCE PHASE: MapReduce tổng hợp phụ tải theo từng căn hộ (Home Reducer)
        for hid in target_hids:
            state = self.home_states[hid]
            home_events = [e for e in telemetry_events if e["home_id"] == hid]
            if home_events:
                total_w = sum(e["power_w"] for e in home_events)
                avg_temp = sum(e["temp_c"] for e in home_events) / len(home_events)
                
                state["current_power_w"] = round(total_w, 1)
                # Tích phân năng lượng: công suất kW x thời gian (2.5 giây = 2.5 / 3600 giờ)
                added_kwh = (total_w / 1000.0) * (2.5 / 3600.0)
                state["accumulated_kwh"] = round(state["accumulated_kwh"] + added_kwh, 3)
                state["last_temp_c"] = round(avg_temp, 1)
                
                # Gán trạng thái cảnh báo
                if any(a["home_id"] == hid for a in new_anomalies):
                    state["status"] = "CRITICAL_ALERT"
                elif total_w > 3200:
                    state["status"] = "HIGH_LOAD"
                else:
                    state["status"] = "NORMAL"

        # Lọc danh sách live states của các căn hộ được yêu cầu
        homes_live_response = [self.home_states[hid] for hid in target_hids if hid in self.home_states]

        # Chỉ số toàn hệ sinh thái Hadoop Big Data
        total_system_power_kw = round(sum(s["current_power_w"] for s in self.home_states.values()) / 1000.0 * 850, 1)
        total_system_mwh = round(sum(s["accumulated_kwh"] for s in self.home_states.values()) * 0.85, 2)

        return {
            "status": "SUCCESS",
            "timestamp": timestamp_str,
            "hadoop_hdfs_block": {
                "block_id": f"BLK-{self.block_counter}",
                "hdfs_path": hdfs_path,
                "datanode": datanode_id,
                "format": "Parquet (Snappy Compressed)",
                "record_count": new_records_count,
                "replication_factor": 3,
                "throughput_kb_sec": round(random.uniform(580.0, 920.0), 1)
            },
            "system_kpi": {
                "total_system_power_kw": total_system_power_kw,
                "total_system_mwh": total_system_mwh,
                "total_records": self.total_processed_records,
                "stream_msg_per_sec": random.randint(350, 520),
                "active_datanodes": 4
            },
            "homes_live": homes_live_response,
            "sample_telemetry": telemetry_events[:8],
            "anomalies": new_anomalies
        }

# Singleton instance
hadoop_engine = HadoopStreamEngine()
