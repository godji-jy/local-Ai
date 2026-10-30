# SQL Data Modeling และ Query Performance

**หมวด:** Database / Backend  
**คำค้น:** relational database, primary key, foreign key, normalization, index, join, transaction, ACID, query plan

## 1. ตารางและความสัมพันธ์

Relational database เก็บข้อมูลในตาราง โดย:

- Primary key ระบุแถวไม่ซ้ำ
- Foreign key เชื่อมความสัมพันธ์และรักษา referential integrity
- Unique constraint ป้องกันค่าซ้ำใน field ที่ต้องไม่ซ้ำ
- Check constraint จำกัดค่าตามกฎ
- NOT NULL บังคับว่าต้องมีค่า

ตัวอย่างระบบมอเตอร์อาจมี `devices`, `sensor_readings`, `alerts` และ `maintenance_events` แยกกันเพื่อไม่เก็บข้อมูลซ้ำซ้อน

## 2. Normalization

- 1NF: คอลัมน์เก็บค่า atomic ไม่เก็บรายการหลายค่าไว้ในช่องเดียว
- 2NF: non-key attributes ขึ้นกับ primary key ทั้งชุด ไม่ใช่เพียงบางส่วนของ composite key
- 3NF: ลด transitive dependency ของ non-key attributes

Normalization ช่วยลด update anomaly แต่ระบบวิเคราะห์ข้อมูลบางแบบอาจใช้ denormalization เพื่ออ่านเร็วขึ้น ต้องแลกกับความเสี่ยงข้อมูลไม่ตรงกัน

## 3. JOIN

- INNER JOIN: เฉพาะแถวที่ match กัน
- LEFT JOIN: เก็บทุกแถวฝั่งซ้าย แม้ไม่มีค่าฝั่งขวา
- RIGHT JOIN: เก็บทุกแถวฝั่งขวา
- FULL OUTER JOIN: เก็บแถวทั้งสองฝั่ง รวมที่ไม่ match

ก่อน join ให้ตรวจ cardinality เพราะ join แบบ one-to-many อาจทำให้จำนวนแถวเพิ่มขึ้นและทำให้ผลรวมสูงเกินจริง

## 4. Index

Index ช่วยลดเวลาค้นบาง query แต่กินพื้นที่และเพิ่มภาระตอน INSERT/UPDATE/DELETE ควรสร้างตามรูปแบบ query จริง เช่น filter ด้วย `device_id` และเรียงตาม `timestamp` อาจพิจารณา composite index ตาม database engine และ query plan

อย่าสร้าง index ทุกคอลัมน์โดยไม่วัดผล ใช้ `EXPLAIN` หรือเครื่องมือ query plan ของฐานข้อมูลนั้น

## 5. Transaction และ ACID

- Atomicity: งานทั้งหมดสำเร็จหรือ rollback ตามขอบเขต transaction
- Consistency: รักษากฎและ constraint
- Isolation: ควบคุมผลจาก transaction ที่ทำพร้อมกัน
- Durability: เมื่อ commit แล้วข้อมูลต้องคงอยู่ตามคุณสมบัติของระบบ

การบันทึก alert ที่เกี่ยวข้องหลายตารางควรพิจารณา transaction เพื่อไม่ให้เกิดข้อมูลครึ่งชุด

## 6. Time-series sensor data

เก็บ timestamp พร้อม timezone/มาตรฐาน UTC, device ID, sensor type, value, unit, quality flag และ sequence number ถ้าจำเป็น แยกค่า null, missing, invalid และ zero ให้ชัด

## 7. SQL safety

ใช้ parameterized queries แทนการต่อ string จาก input ผู้ใช้โดยตรง ลดความเสี่ยง SQL injection จำกัดสิทธิ์ database account และไม่ให้ UI ใช้บัญชี admin

ตัวอย่างแนวคิด:

```python
cursor.execute(
    "SELECT rpm FROM readings WHERE device_id = ? AND timestamp >= ?",
    (device_id, start_time)
)
```

placeholder แตกต่างกันตาม database driver เช่น SQLite, PostgreSQL หรือ MySQL ต้องใช้รูปแบบที่ driver ระบุ

## 8. Backup และ migration

ก่อนเปลี่ยน schema ให้สำรองข้อมูล ทดสอบ migration บนสำเนา วางแผน rollback และตรวจจำนวนแถวหลัง migrate อย่าแก้ฐานข้อมูลจริงโดยไม่ทดสอบ

## แหล่งอ้างอิง

- SQLite documentation: https://www.sqlite.org/docs.html
- PostgreSQL documentation: https://www.postgresql.org/docs/current/
- OWASP SQL Injection Prevention: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
