/**
 * SCRIPT KHỞI TẠO VÀ TRUY VẤN NỀN TẢNG NOSQL MONGODB
 * Đề tài: Hệ thống Giám sát & Quản lý Thiết bị IoT Nhà Thông Minh
 * Học viên: Trần Duy Khải - K32MCS1 - CSDL Nâng Cao
 *
 * File này chứa:
 * 1. Khởi tạo Database và Collections với JSON Schema Validation.
 * 2. Thiết lập Index tối ưu truy vấn thời gian thực và chuỗi thời gian (Time-series Indexes).
 * 3. Các Aggregation Pipelines mẫu phục vụ phân tích dữ liệu lớn.
 */

// 1. Chuyển sang database smart_home_nosql
use smart_home_nosql;

// ============================================================================
// 2. KHỞI TẠO VÀ THIẾT LẬP SCHEMA VALIDATION CHO CÁC COLLECTIONS
// ============================================================================

// 2.1. Collection: device_telemetry (Log cảm biến viễn thám chuỗi thời gian)
db.createCollection("device_telemetry", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "device_id", "home_id", "category", "metrics"],
      properties: {
        timestamp: {
          bsonType: "string", // hoặc date nếu dùng ISODate
          description: "Thời điểm ghi nhận tín hiệu viễn thám (ISO8601)"
        },
        device_id: {
          bsonType: "int",
          description: "Mã định danh thiết bị vật lý từ RDBMS Device(device_id)"
        },
        device_name: {
          bsonType: "string"
        },
        room_id: {
          bsonType: "int"
        },
        home_id: {
          bsonType: "int",
          description: "Mã căn hộ từ RDBMS Home(home_id)"
        },
        category: {
          enum: ["Lighting", "Climate", "Sensor", "Security"],
          description: "Chủng loại thiết bị phân cấp"
        },
        status: {
          enum: ["ACTIVE", "OFFLINE", "MAINTENANCE"],
          description: "Trạng thái hoạt động tức thời"
        },
        metrics: {
          bsonType: "object",
          required: ["power_watts"],
          properties: {
            temperature: { bsonType: ["double", "int", "null"] },
            humidity: { bsonType: ["double", "int", "null"] },
            power_watts: { bsonType: ["double", "int"] },
            voltage: { bsonType: ["double", "int"] },
            rssi_dbm: { bsonType: ["int", "null"] }
          }
        },
        is_anomaly: {
          bsonType: "bool",
          description: "Cờ đánh dấu bất thường (quá nhiệt, quá tải, offline)"
        },
        anomaly_reason: {
          bsonType: "string"
        }
      }
    }
  }
});

// 2.2. Collection: command_logs (Nhật ký thao tác điều khiển thiết bị)
db.createCollection("command_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "log_id", "device_id", "home_id", "action", "status"],
      properties: {
        timestamp: { bsonType: "string" },
        log_id: { bsonType: "string" },
        device_id: { bsonType: "int" },
        home_id: { bsonType: "int" },
        action: { bsonType: "string" },
        source: {
          enum: ["MOBILE_APP", "AUTOMATION_SCHEDULE", "VOICE_ASSISTANT"],
          description: "Nguồn kích hoạt lệnh"
        },
        status: {
          enum: ["SUCCESS", "TIMEOUT", "FAILED", "PENDING"],
          description: "Kết quả thực thi lệnh"
        },
        latency_ms: {
          bsonType: "int",
          description: "Thời gian đáp ứng từ cloud đến thiết bị (ms)"
        }
      }
    }
  }
});

// ============================================================================
// 3. THIẾT LẬP CHỈ MỤC (INDEXING STRATEGY) CHO NOSQL MONGODB
// ============================================================================

// Index phục vụ truy vấn chuỗi thời gian theo từng thiết bị (Compound Index)
db.device_telemetry.createIndex({ "device_id": 1, "timestamp": -1 }, { name: "idx_device_time" });

// Index phục vụ tổng hợp năng lượng theo từng căn hộ
db.device_telemetry.createIndex({ "home_id": 1, "timestamp": -1 }, { name: "idx_home_time" });

// Index phục vụ lọc nhanh các bất thường quá nhiệt / quá tải
db.device_telemetry.createIndex({ "is_anomaly": 1, "anomaly_reason": 1 }, { name: "idx_anomaly" });
db.device_telemetry.createIndex({ "metrics.temperature": -1 }, { name: "idx_temperature_desc" });

// Index phục vụ phân tích nhật ký thao tác điều khiển
db.command_logs.createIndex({ "device_id": 1, "timestamp": -1 }, { name: "idx_cmd_dev_time" });
db.command_logs.createIndex({ "source": 1, "status": 1 }, { name: "idx_cmd_src_status" });


// ============================================================================
// 4. CÁC MẪU TRUY VẤN PHÂN TÍCH NÂNG CAO (AGGREGATION PIPELINES)
// ============================================================================

// ----------------------------------------------------------------------------
// PIPELINE 1: Thống kê tổng công suất tiêu thụ trung bình theo Chủng loại thiết bị
// ----------------------------------------------------------------------------
print("--- PIPELINE 1: Avg Power by Category ---");
db.device_telemetry.aggregate([
  { $match: { "status": "ACTIVE" } },
  {
    $group: {
      _id: "$category",
      avg_power_watts: { $avg: "$metrics.power_watts" },
      max_power_watts: { $max: "$metrics.power_watts" },
      total_records: { $sum: 1 }
    }
  },
  { $sort: { avg_power_watts: -1 } }
]);

// ----------------------------------------------------------------------------
// PIPELINE 2: Phát hiện các sự cố bất thường (Thermal & Power Anomaly Detection)
// ----------------------------------------------------------------------------
print("--- PIPELINE 2: Detect Active Anomalies ---");
db.device_telemetry.aggregate([
  {
    $match: {
      $or: [
        { "metrics.temperature": { $gte: 45.0 } },
        { "is_anomaly": true }
      ]
    }
  },
  {
    $project: {
      _id: 0,
      timestamp: 1,
      device_id: 1,
      device_name: 1,
      home_id: 1,
      category: 1,
      anomaly_reason: 1,
      measured_temp: "$metrics.temperature",
      measured_power: "$metrics.power_watts"
    }
  },
  { $sort: { timestamp: -1 } },
  { $limit: 10 }
]);

// ----------------------------------------------------------------------------
// PIPELINE 3: Phân tích độ trễ và tỷ lệ thành công của các nguồn kích hoạt lệnh
// ----------------------------------------------------------------------------
print("--- PIPELINE 3: Command Source Latency and Reliability ---");
db.command_logs.aggregate([
  {
    $group: {
      _id: "$source",
      total_commands: { $sum: 1 },
      success_count: {
        $sum: { $cond: [{ $eq: ["$status", "SUCCESS"] }, 1, 0] }
      },
      avg_latency_ms: { $avg: "$latency_ms" },
      max_latency_ms: { $max: "$latency_ms" }
    }
  },
  {
    $project: {
      source: "$_id",
      total_commands: 1,
      avg_latency_ms: { $round: ["$avg_latency_ms", 1] },
      max_latency_ms: 1,
      success_rate_percent: {
        $round: [
          { $multiply: [{ $divide: ["$success_count", "$total_commands"] }, 100] },
          2
        ]
      }
    }
  },
  { $sort: { total_commands: -1 } }
]);

// ----------------------------------------------------------------------------
// PIPELINE 4: Ước tính điện năng tiêu thụ (kWh) theo từng Căn hộ (Home)
// Giả định chu kỳ gửi mẫu là 0.5 giờ (30 phút)
// ----------------------------------------------------------------------------
print("--- PIPELINE 4: Estimated kWh per Home ---");
db.device_telemetry.aggregate([
  {
    $group: {
      _id: "$home_id",
      avg_power_w: { $avg: "$metrics.power_watts" },
      sample_count: { $sum: 1 },
      // kWh = sum(watts * 0.5h) / 1000
      total_kwh: {
        $sum: {
          $divide: [{ $multiply: ["$metrics.power_watts", 0.5] }, 1000]
        }
      }
    }
  },
  {
    $project: {
      home_id: "$_id",
      sample_count: 1,
      total_kwh: { $round: ["$total_kwh", 2] }
    }
  },
  { $sort: { total_kwh: -1 } }
]);
