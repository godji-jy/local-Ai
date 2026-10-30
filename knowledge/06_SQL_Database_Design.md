# SQL และการออกแบบฐานข้อมูลสำหรับโปรเจกต์

## 1. ออกแบบตารางจากสิ่งที่ระบบต้องเก็บ

ตัวอย่างระบบมอนิเตอร์: - `devices`: ข้อมูลอุปกรณ์ - `readings`: ค่าที่วัดได้ -
`alerts`: เหตุการณ์แจ้งเตือน - `users`: ผู้ใช้และสิทธิ์

ออกแบบให้แต่ละตารางมี primary key และกำหนด foreign key เพื่อรักษาความสัมพันธ์

## 2. ตัวอย่าง SQLite schema

``` sql
PRAGMA foreign_keys = ON;

CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE readings (
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    rpm REAL CHECK (rpm >= 0),
    temperature_c REAL,
    current_a REAL CHECK (current_a >= 0),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

CREATE INDEX idx_readings_device_time
ON readings(device_id, recorded_at);
```

ดัชนีช่วยให้ค้นหาตามอุปกรณ์และเวลาเร็วขึ้น แต่เพิ่มพื้นที่และต้นทุนการเขียน จึงควรสร้างตาม
query ที่ใช้จริง

## 3. CRUD พื้นฐาน

``` sql
INSERT INTO devices (device_id, name, location)
VALUES ('motor-01', 'Motor 1', 'Lab');

SELECT recorded_at, rpm, temperature_c
FROM readings
WHERE device_id = ?
ORDER BY recorded_at DESC
LIMIT 100;

UPDATE devices SET location = ?
WHERE device_id = ?;

DELETE FROM readings
WHERE recorded_at < ?;
```

เครื่องหมาย `?` เป็น placeholder ใน SQLite Python ห้ามต่อ string จาก input
ของผู้ใช้เข้ากับ SQL โดยตรง

## 4. ใช้ parameterized query ใน Python

``` python
import sqlite3

with sqlite3.connect("motor.db") as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        "INSERT INTO readings(device_id, recorded_at, rpm) VALUES (?, ?, ?)",
        ("motor-01", "2026-10-29T10:30:00Z", 1480)
    )
```

การใช้ `with` ช่วยจัดการ connection/transaction เบื้องต้น หากข้อมูลมีความสำคัญ
ควรออกแบบ backup และการกู้คืนด้วย

## 5. การรวมข้อมูล

``` sql
SELECT device_id,
       COUNT(*) AS sample_count,
       AVG(temperature_c) AS avg_temp,
       MAX(temperature_c) AS max_temp
FROM readings
WHERE recorded_at >= ?
GROUP BY device_id;
```

ใช้ `GROUP BY` สำหรับสรุป และ `JOIN` เมื่อต้องดึงข้อมูลจากหลายตาราง
อย่าเก็บค่าที่คำนวณซ้ำได้โดยไม่จำเป็น เว้นแต่มีเหตุผลด้านประสิทธิภาพ

## 6. Transaction และความถูกต้อง

Transaction ช่วยให้หลายคำสั่งสำเร็จหรือย้อนกลับร่วมกัน
ใช้กับงานที่ต้องเปลี่ยนข้อมูลหลายตารางพร้อมกัน ทดสอบกรณี error และ rollback

## 7. ออกแบบข้อมูลเวลา

-   เลือก timezone และรูปแบบเวลาให้ชัดเจน
-   สำหรับระบบกระจาย แนะนำเก็บเวลาอ้างอิง UTC และแปลงเป็นเวลาท้องถิ่นตอนแสดง
-   เก็บเวลาที่วัดจริงแยกจากเวลาที่ server ได้รับ หากจำเป็น
-   กำหนดนโยบายลบ/เก็บข้อมูลเก่า

## 8. โปรเจกต์จบ

สร้างฐานข้อมูลสำหรับ dashboard: 1. เก็บอุปกรณ์และ telemetry 2. ทำ query
ค่าล่าสุดต่ออุปกรณ์ 3. ทำ query ค่าเฉลี่ยรายชั่วโมง 4. เพิ่ม index
และวัดเวลาค้นหาก่อน/หลัง 5. เขียนแผน backup/restore

## แบบฝึกหัด

1.  เพิ่มตาราง alerts ที่เชื่อมกับ devices
2.  เขียน query หาอุณหภูมิสูงสุดรายวัน
3.  อธิบายความแตกต่าง primary key กับ foreign key
4.  แก้ query ที่เสี่ยง SQL injection ให้เป็น parameterized query
