"""
Web Dashboard Application: Smart Home IoT Big Data Analytics
Backend: Flask
Mục đích: Cung cấp API và giao diện Dashboard trực quan hóa kết quả phân tích dữ liệu lớn
từ luồng NoSQL MongoDB & Hadoop / Spark cho hệ thống Smart Home.
"""

import os
import json
from flask import Flask, render_template, jsonify, request

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "bigdata", "data")

def get_analytics_data():
    results_path = os.path.join(DATA_DIR, "analytics_results.json")
    if not os.path.exists(results_path):
        # Tự động tính toán nếu chưa có
        from bigdata.spark_analytics_jobs import run_spark_analytics_jobs
        return run_spark_analytics_jobs()
    with open(results_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_metadata():
    meta_path = os.path.join(DATA_DIR, "metadata_dimensions.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/overview")
def api_overview():
    data = get_analytics_data()
    return jsonify(data.get("kpi_overview", {}))

@app.route("/api/homes")
def api_homes():
    meta = get_metadata()
    return jsonify(meta.get("homes", []))

@app.route("/api/energy-analytics")
def api_energy():
    data = get_analytics_data()
    home_id = request.args.get("home_id")
    energy_data = data.get("energy_charts", {})
    
    if home_id and home_id != "all":
        try:
            hid = int(home_id)
            filtered_ranking = [h for h in energy_data.get("home_ranking", []) if h["home_id"] == hid]
            return jsonify({
                "hourly": energy_data.get("hourly", {}),
                "daily": energy_data.get("daily", {}),
                "category_summary": energy_data.get("category_summary", []),
                "home_ranking": filtered_ranking
            })
        except ValueError:
            pass
            
    return jsonify(energy_data)

@app.route("/api/anomalies")
def api_anomalies():
    data = get_analytics_data()
    anomalies = data.get("anomalies", [])
    home_id = request.args.get("home_id")
    severity = request.args.get("severity")
    
    filtered = anomalies
    if home_id and home_id != "all":
        try:
            hid = int(home_id)
            filtered = [a for a in filtered if a["home_id"] == hid]
        except ValueError:
            pass
            
    if severity and severity != "all":
        filtered = [a for a in filtered if a["severity"].upper() == severity.upper()]
        
    return jsonify(filtered)

@app.route("/api/commands")
def api_commands():
    data = get_analytics_data()
    return jsonify(data.get("command_analytics", {}))

@app.route("/api/business")
def api_business():
    data = get_analytics_data()
    return jsonify(data.get("business_analytics", {}))

@app.route("/api/pipeline-info")
def api_pipeline_info():
    """
    Thông tin chi tiết về kiến trúc luồng dữ liệu NoSQL/Hadoop và dữ liệu mẫu
    """
    sample_telemetry = {}
    sample_command = {}
    
    telemetry_path = os.path.join(DATA_DIR, "device_telemetry.json")
    if os.path.exists(telemetry_path):
        with open(telemetry_path, "r", encoding="utf-8") as f:
            records = json.load(f)
            if records:
                sample_telemetry = records[0]
                
    cmd_path = os.path.join(DATA_DIR, "command_logs.json")
    if os.path.exists(cmd_path):
        with open(cmd_path, "r", encoding="utf-8") as f:
            records = json.load(f)
            if records:
                sample_command = records[0]
                
    pipeline_details = {
        "architecture_layers": [
            {
                "layer": "1. Ingestion Layer",
                "tech": "MQTT / Kafka Broker",
                "description": "Tiếp nhận 30 luồng viễn thám chuỗi thời gian từ 30 thiết bị IoT (Daikin, Tuya, Aqara, Ezviz...) với độ trễ thấp < 200ms."
            },
            {
                "layer": "2. NoSQL Operational Store (Hot Tier)",
                "tech": "MongoDB Time-Series Collections",
                "description": "Lưu trữ realtime 2 collections: 'device_telemetry' và 'command_logs'. Compound index {device_id: 1, timestamp: -1} phục vụ truy vấn tức thời trên app."
            },
            {
                "layer": "3. Data Lake & Archival (Cold Tier)",
                "tech": "Hadoop HDFS / Parquet Partitioning",
                "description": "Định kỳ nén dữ liệu sang Parquet phân vùng theo /year=2025/month=07/day=... Giảm 70% dung lượng lưu trữ dài hạn so với JSON thô."
            },
            {
                "layer": "4. Distributed Analytics Engine",
                "tech": "Apache Spark (PySpark) / MapReduce",
                "description": "Thực thi 4 Batch Jobs: Tính điện năng kWh, phát hiện bất thường quá nhiệt/quá tải, đánh giá độ trễ mạng, và đối soát retention_days của gói cước."
            },
            {
                "layer": "5. Business Intelligence & Serving",
                "tech": "FastAPI/Flask + Chart.js Dashboard",
                "description": "Trực quan hóa kết quả phân tích phục vụ người dùng cuối quản lý tiêu thụ điện và nhà cung cấp giám sát doanh thu thuê bao."
            }
        ],
        "sample_telemetry": sample_telemetry,
        "sample_command": sample_command,
        "nosql_stats": {
            "database": "smart_home_nosql",
            "collections": ["device_telemetry", "command_logs"],
            "indexes_count": 5
        },
        "hadoop_stats": {
            "hdfs_path": "/datalake/smart_home/telemetry/year=2025/month=07/",
            "storage_format": "Parquet (Snappy Compressed)",
            "retention_policy_active": True
        }
    }
    return jsonify(pipeline_details)

if __name__ == "__main__":
    print("[*] Starting Smart Home IoT Analytics Dashboard on http://localhost:8050")
    app.run(host="0.0.0.0", port=8050, debug=False)
