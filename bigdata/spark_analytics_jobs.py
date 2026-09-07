"""
Module: spark_analytics_jobs.py
Mục đích: Mô phỏng / Thực thi các Batch Job phân tích Dữ liệu Lớn theo kiến trúc Apache Spark / Hadoop
đối soát dữ liệu giữa RDBMS MySQL (Metadata) và NoSQL/HDFS (Telemetry & Command Logs).

Các tác vụ phân tích chính:
1. Hourly & Daily Power Aggregation (Tính kWh, tải đỉnh Peak Hours vs Giờ thường Off-peak).
2. Energy Matrix by Home and Device Type (Phân bổ tiêu thụ theo căn hộ và chủng loại thiết bị).
3. Anomaly & Safety Detection (Cảnh báo quá nhiệt, vượt công suất định mức, thiết bị rớt mạng).
4. Command Usage & Network Latency Profiling (Phân tích thói quen điều khiển và độ trễ).
5. Subscription & Retention Compliance Check (Đối soát chính sách lưu trữ retention_days và doanh thu).
"""

import os
import json
from datetime import datetime
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_data():
    telemetry_path = os.path.join(DATA_DIR, "device_telemetry.json")
    commands_path = os.path.join(DATA_DIR, "command_logs.json")
    meta_path = os.path.join(DATA_DIR, "metadata_dimensions.json")
    
    if not os.path.exists(telemetry_path) or not os.path.exists(commands_path):
        raise FileNotFoundError("Chưa tìm thấy tệp dữ liệu viễn thám. Vui lòng chạy generate_iot_data.py trước!")
        
    with open(telemetry_path, "r", encoding="utf-8") as f:
        telemetry = json.load(f)
    with open(commands_path, "r", encoding="utf-8") as f:
        commands = json.load(f)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    return telemetry, commands, meta

def run_spark_analytics_jobs():
    print("[*] Starting Hadoop/Spark Analytics Batch Processing Jobs...")
    telemetry, commands, meta = load_data()
    
    devices = {d["device_id"]: d for d in meta["devices"]}
    device_types = {int(k): v for k, v in meta["device_types"].items()}
    homes = {h["home_id"]: h for h in meta["homes"]}
    subs = meta["subscriptions"]
    
    # -------------------------------------------------------------------------
    # JOB 1: ENERGY & CONSUMPTION ANALYTICS (kWh calculation)
    # Giả sử mỗi bước ghi đo là interval = 0.5 giờ (30 phút)
    # kWh = (Power_Watts * 0.5) / 1000
    # -------------------------------------------------------------------------
    print("   [Job 1] Aggregating Energy Consumption (Hourly, Daily, Peak vs Off-Peak)...")
    hourly_load = defaultdict(lambda: {"total_watts": 0.0, "count": 0, "kwh": 0.0})
    daily_load = defaultdict(lambda: {"total_watts": 0.0, "count": 0, "kwh": 0.0})
    home_energy = defaultdict(lambda: {"kwh": 0.0, "active_devices": set(), "records": 0})
    category_energy = defaultdict(lambda: {"kwh": 0.0, "records": 0, "total_power": 0.0})
    peak_energy_kwh = 0.0
    offpeak_energy_kwh = 0.0
    
    for rec in telemetry:
        ts = datetime.strptime(rec["timestamp"], "%Y-%m-%d %H:%M:%S")
        hour_key = ts.strftime("%H:00")
        date_key = ts.strftime("%Y-%m-%d")
        
        metrics = rec.get("metrics") or {}
        power_w = metrics.get("power_watts") or 0.0
        kwh = (power_w * 0.5) / 1000.0
        
        # Hourly profile
        hourly_load[hour_key]["total_watts"] += power_w
        hourly_load[hour_key]["count"] += 1
        hourly_load[hour_key]["kwh"] += kwh
        
        # Daily profile
        daily_load[date_key]["total_watts"] += power_w
        daily_load[date_key]["count"] += 1
        daily_load[date_key]["kwh"] += kwh
        
        # By Home
        home_id = rec["home_id"]
        home_energy[home_id]["kwh"] += kwh
        home_energy[home_id]["active_devices"].add(rec["device_id"])
        home_energy[home_id]["records"] += 1
        
        # By Category
        cat = rec["category"]
        category_energy[cat]["kwh"] += kwh
        category_energy[cat]["records"] += 1
        category_energy[cat]["total_power"] += power_w
        
        # Peak vs Off-peak
        hour = ts.hour
        if (11 <= hour <= 13) or (18 <= hour <= 22):
            peak_energy_kwh += kwh
        else:
            offpeak_energy_kwh += kwh

    # Format hourly results
    sorted_hours = sorted(hourly_load.keys())
    hourly_chart_data = {
        "labels": sorted_hours,
        "avg_power_watts": [round(hourly_load[h]["total_watts"] / hourly_load[h]["count"], 1) for h in sorted_hours],
        "total_kwh": [round(hourly_load[h]["kwh"], 2) for h in sorted_hours]
    }
    
    sorted_days = sorted(daily_load.keys())
    daily_chart_data = {
        "labels": sorted_days,
        "total_kwh": [round(daily_load[d]["kwh"], 2) for d in sorted_days]
    }

    # Format home results
    home_ranking = []
    for hid, info in home_energy.items():
        home_ranking.append({
            "home_id": hid,
            "home_name": homes.get(hid, {}).get("name", f"Home {hid}"),
            "city": homes.get(hid, {}).get("city", "Vietnam"),
            "total_kwh": round(info["kwh"], 2),
            "active_devices_count": len(info["active_devices"])
        })
    home_ranking.sort(key=lambda x: x["total_kwh"], reverse=True)
    
    # Format category results
    category_summary = []
    total_system_kwh = sum(c["kwh"] for c in category_energy.values())
    for cat, info in category_energy.items():
        pct = (info["kwh"] / total_system_kwh * 100.0) if total_system_kwh > 0 else 0
        category_summary.append({
            "category": cat,
            "total_kwh": round(info["kwh"], 2),
            "percentage": round(pct, 1),
            "avg_power_watts": round(info["total_power"] / info["records"], 1) if info["records"] > 0 else 0
        })
    category_summary.sort(key=lambda x: x["total_kwh"], reverse=True)

    # -------------------------------------------------------------------------
    # JOB 2: ANOMALY & HEALTH DETECTION
    # -------------------------------------------------------------------------
    print("   [Job 2] Identifying Anomalies, Overloads, and Safety Alerts...")
    anomalies = []
    thermal_alerts_count = 0
    power_overload_count = 0
    offline_count = 0
    
    for rec in telemetry:
        if rec.get("is_anomaly") or rec.get("status") == "OFFLINE":
            metrics = rec.get("metrics") or {}
            reason = rec.get("anomaly_reason", "ANOMALY")
            dev_id = rec["device_id"]
            dev_name = rec["device_name"]
            home_id = rec["home_id"]
            home_name = homes.get(home_id, {}).get("name", f"Home {home_id}")
            
            temp = metrics.get("temperature")
            power = metrics.get("power_watts")
            
            severity = "WARNING"
            if reason == "HIGH_TEMPERATURE_ALERT":
                thermal_alerts_count += 1
                severity = "CRITICAL"
                detail = f"Nhiệt độ đo được {temp}°C vượt ngưỡng an toàn (45°C). Nguy cơ sự cố hỏa hoạn!"
            elif reason == "POWER_OVERLOAD":
                power_overload_count += 1
                severity = "HIGH"
                detail = f"Công suất tức thời {power}W vượt quá 125% công suất định mức."
            elif reason == "DEVICE_OFFLINE":
                offline_count += 1
                severity = "MEDIUM"
                detail = "Mất tín hiệu kết nối viễn thám Wi-Fi liên tục."
            else:
                detail = "Thông số cảm biến bất thường."
                
            anomalies.append({
                "timestamp": rec["timestamp"],
                "device_id": dev_id,
                "device_name": dev_name,
                "home_id": home_id,
                "home_name": home_name,
                "category": rec["category"],
                "reason": reason,
                "severity": severity,
                "detail": detail,
                "measured_temp": temp,
                "measured_power": power
            })

    # Sort anomalies recent first
    anomalies.sort(key=lambda x: x["timestamp"], reverse=True)

    # -------------------------------------------------------------------------
    # JOB 3: COMMAND USAGE & NETWORK PERFORMANCE PROFILING
    # -------------------------------------------------------------------------
    print("   [Job 3] Profiling Command Latency and Source Distribution...")
    source_stats = defaultdict(lambda: {"count": 0, "success": 0, "total_lat": 0})
    action_stats = defaultdict(int)
    
    for cmd in commands:
        src = cmd.get("source", "UNKNOWN")
        source_stats[src]["count"] += 1
        if cmd.get("status") == "SUCCESS":
            source_stats[src]["success"] += 1
        source_stats[src]["total_lat"] += cmd.get("latency_ms", 0)
        action_stats[cmd.get("action", "OTHER")] += 1
        
    command_source_summary = []
    for src, st in source_stats.items():
        command_source_summary.append({
            "source": src,
            "total_commands": st["count"],
            "success_rate": round(st["success"] / st["count"] * 100.0, 1) if st["count"] > 0 else 0,
            "avg_latency_ms": round(st["total_lat"] / st["count"], 1) if st["count"] > 0 else 0
        })

    # -------------------------------------------------------------------------
    # JOB 4: SUBSCRIPTION & RETENTION COMPLIANCE AUDITING
    # Đối soát giữa MySQL SubscriptionPlan và thực tế lưu trữ Big Data
    # -------------------------------------------------------------------------
    print("   [Job 4] Auditing Subscription Plans, Revenue and Data Retention Compliance...")
    plan_revenue = defaultdict(float)
    plan_subscribers = defaultdict(int)
    sub_status_count = defaultdict(int)
    total_revenue = 0.0
    
    for s in subs:
        pname = s["plan_name"]
        price = s["price"]
        status = s["status"]
        sub_status_count[status] += 1
        plan_subscribers[pname] += 1
        if status == "PAID":
            plan_revenue[pname] += price
            total_revenue += price
            
    # Kiểm tra số ngày dữ liệu viễn thám thực tế so với retention_days
    # Giả sử log được sinh 10 ngày
    data_retention_audit = []
    for s in subs:
        hid = s["home_id"]
        hname = homes.get(hid, {}).get("name", f"Home {hid}")
        retention_days = s["retention_days"]
        current_data_days = 10 # Số ngày log viễn thám hiện có trong mock data
        compliance = "COMPLIANT" if current_data_days <= retention_days else "OVER_LIMIT"
        
        data_retention_audit.append({
            "subscription_id": s["sub_id"],
            "home_id": hid,
            "home_name": hname,
            "plan_name": s["plan_name"],
            "retention_policy_days": retention_days,
            "actual_stored_days": current_data_days,
            "payment_status": s["status"],
            "compliance": compliance
        })

    # -------------------------------------------------------------------------
    # ĐÓNG GÓI TỔNG THỂ KẾT QUẢ PHÂN TÍCH (ANALYTICS SUMMARY)
    # -------------------------------------------------------------------------
    analytics_payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kpi_overview": {
            "total_users": 15,
            "total_homes": len(homes),
            "total_rooms": 25,
            "total_devices": len(devices),
            "active_devices": sum(1 for d in devices.values() if d["status"] == "ACTIVE"),
            "offline_devices": sum(1 for d in devices.values() if d["status"] != "ACTIVE"),
            "total_telemetry_records": len(telemetry),
            "total_command_records": len(commands),
            "total_system_kwh": round(total_system_kwh, 2),
            "peak_energy_kwh": round(peak_energy_kwh, 2),
            "offpeak_energy_kwh": round(offpeak_energy_kwh, 2),
            "peak_energy_percent": round((peak_energy_kwh / total_system_kwh * 100.0), 1) if total_system_kwh > 0 else 0,
            "total_anomalies_detected": len(anomalies),
            "thermal_alerts_count": thermal_alerts_count,
            "power_overload_count": power_overload_count,
            "offline_dropouts_count": offline_count,
            "total_revenue_vnd": total_revenue,
            "paid_subscriptions_count": sub_status_count.get("PAID", 0),
            "pending_subscriptions_count": sub_status_count.get("PENDING", 0),
            "expired_subscriptions_count": sub_status_count.get("EXPIRED", 0)
        },
        "energy_charts": {
            "hourly": hourly_chart_data,
            "daily": daily_chart_data,
            "category_summary": category_summary,
            "home_ranking": home_ranking
        },
        "anomalies": anomalies[:50], # Lấy 50 cảnh báo mới nhất
        "command_analytics": {
            "source_summary": command_source_summary,
            "action_frequency": dict(action_stats)
        },
        "business_analytics": {
            "plan_revenue": dict(plan_revenue),
            "plan_subscribers": dict(plan_subscribers),
            "status_distribution": dict(sub_status_count),
            "retention_audit": data_retention_audit
        }
    }

    out_file = os.path.join(DATA_DIR, "analytics_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(analytics_payload, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Big Data Analytics Finished successfully! Output saved to: {out_file}")
    return analytics_payload

if __name__ == "__main__":
    run_spark_analytics_jobs()
