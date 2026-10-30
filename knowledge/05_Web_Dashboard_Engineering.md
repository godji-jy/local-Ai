# Web Development และ Dashboard สำหรับระบบข้อมูล

## 1. สถาปัตยกรรมแนะนำ

-   Frontend: HTML/CSS/JavaScript หรือ framework ที่ถนัด
-   Backend: FastAPI/Flask/Node.js
-   Data layer: SQLite/PostgreSQL/Firebase
-   Telemetry: MQTT subscriber หรือ service รับข้อมูล
-   Charts: กราฟที่แสดง timestamp และหน่วยชัดเจน

แยก UI ออกจาก business logic และ database
เพื่อเปลี่ยนหน้าตาโดยไม่ต้องเขียนระบบข้อมูลใหม่

## 2. ออกแบบ API

ตัวอย่าง endpoint: - `GET /api/health` ตรวจสถานะ - `GET /api/devices`
รายชื่ออุปกรณ์ - `GET /api/devices/{id}/latest` ค่าล่าสุด -
`GET /api/devices/{id}/history?from=...&to=...` ประวัติ -
`POST /api/alerts/{id}/acknowledge` ยืนยันการรับทราบแจ้งเตือน

กำหนดรูปแบบ response, error code, authentication และ validation ให้ชัดเจน
อย่าส่ง stack trace ให้ผู้ใช้ปลายทาง

## 3. ตัวอย่าง FastAPI

ติดตั้ง `python -m pip install fastapi uvicorn`

``` python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Motor Dashboard API")

class Reading(BaseModel):
    rpm: float = Field(ge=0, le=10000)
    temperature_c: float = Field(ge=-40, le=200)
    current_a: float = Field(ge=0, le=100)

latest = {}

@app.post("/api/devices/{device_id}/latest")
def update_latest(device_id: str, reading: Reading):
    if not device_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="invalid device id")
    latest[device_id] = reading.model_dump()
    return {"ok": True, "device_id": device_id}

@app.get("/api/devices/{device_id}/latest")
def get_latest(device_id: str):
    if device_id not in latest:
        raise HTTPException(status_code=404, detail="device not found")
    return latest[device_id]
```

ตัวอย่างนี้เก็บใน RAM จึงหายเมื่อรีสตาร์ต และไม่ใช่ production database

รัน: `uvicorn main:app --reload` แล้วเปิด `/docs` เพื่อทดลอง API

## 4. Dashboard ที่อ่านง่าย

ทุกการ์ดควรมี: - ชื่อค่าพร้อมหน่วย เช่น Temperature (°C) - ค่าล่าสุดและเวลาที่รับข้อมูล -
สถานะ stale/offline หากไม่มีข้อมูลใหม่ - กราฟที่แกนเวลาอ่านได้ - สีเตือนพร้อมข้อความ
ไม่พึ่งสีอย่างเดียว - การแยกค่า sensor จริงกับค่าทำนายจาก AI

หลีกเลี่ยงการรีเฟรชทั้งหน้าเมื่อมีข้อมูลใหม่ ให้ปรับเฉพาะส่วนที่เปลี่ยนและระบุเวลาของข้อมูลล่าสุด

## 5. จัดการสถานะโหลดและข้อผิดพลาด

UI ควรแสดง loading, empty state, error state และ retry action
ตัวอย่างข้อความ: - "กำลังโหลดข้อมูล..." - "ยังไม่มีข้อมูลในช่วงเวลานี้" -
"เชื่อมต่ออุปกรณ์ไม่ได้ ข้อมูลล่าสุดเมื่อ 14:32" - "ลองใหม่"

## 6. ความปลอดภัยเว็บ

-   validate input ทั้ง frontend และ backend
-   ใช้ parameterized query
-   ตรวจสิทธิ์ทุก endpoint
-   จำกัด CORS ให้เฉพาะ origin ที่จำเป็น
-   ไม่ฝัง secret ใน JavaScript ที่ส่งให้ browser
-   ใช้ HTTPS เมื่อส่งข้อมูลผ่านเครือข่ายที่ไม่เชื่อถือ
-   เพิ่ม rate limit และ audit log ตามความเหมาะสม

## 7. โปรเจกต์จบ

ทำ dashboard มอนิเตอร์อุปกรณ์ IoT: backend รับค่าจาก MQTT, เก็บฐานข้อมูล, API
ส่งข้อมูลให้หน้าเว็บ และหน้าเว็บแสดงค่าปัจจุบัน กราฟย้อนหลัง และ alert history

## แบบฝึกหัด

1.  เพิ่ม endpoint สำหรับดึงข้อมูลย้อนหลัง
2.  ทำให้ UI แสดง offline เมื่อข้อมูลเก่ากว่าเกณฑ์
3.  เขียน validation สำหรับค่า RPM ที่ไม่สมเหตุสมผล
4.  อธิบายว่าทำไม secret ห้ามใส่ใน frontend
