# MQTT Reliable IoT Architecture: Topic, QoS, Retain และการกู้คืนการเชื่อมต่อ

**หมวด:** IoT / Networking / Automation  
**คำค้น:** MQTT, broker, publisher, subscriber, topic, QoS, retained, last will, reconnect, message schema

## 1. แนวคิด Publish/Subscribe

MQTT เป็น protocol แบบ client-server และ publish/subscribe:

- Publisher ส่งข้อความไปยัง topic
- Broker รับและส่งต่อให้ subscriber ที่ subscribe topic ตรงกัน
- Publisher และ subscriber ไม่จำเป็นต้องรู้จักกันโดยตรง

รูปแบบนี้ช่วยแยก ESP32, dashboard และ data logger ออกจากกัน

## 2. ออกแบบ topic hierarchy

ตัวอย่าง:

```text
factory/motor-01/telemetry
factory/motor-01/status
factory/motor-01/event
factory/motor-01/command
factory/motor-01/config
```

แนวทาง:

- `telemetry`: ค่าที่วัดต่อเนื่อง
- `status`: สถานะ online/offline และสุขภาพระบบ
- `event`: เหตุการณ์ เช่น over-temperature warning
- `command`: คำสั่งจากผู้ควบคุม
- `config`: การตั้งค่าที่มีการควบคุมสิทธิ์

อย่า publish password หรือข้อมูลลับใน topic/payload

## 3. QoS 0, 1 และ 2

- QoS 0: at most once; ไม่มีการยืนยันรับและอาจสูญหาย เหมาะกับ telemetry ที่มีข้อมูลใหม่มาทดแทนเร็ว
- QoS 1: at least once; ผู้รับอาจได้รับซ้ำ ผู้บริโภคควรจัดการ duplicate
- QoS 2: exactly once ในขอบเขต delivery protocol ของ MQTT; มี overhead สูงกว่า ไม่ได้แปลว่าระบบปลายทางทำธุรกรรมทางธุรกิจ exactly-once โดยอัตโนมัติ

เลือก QoS ตามผลกระทบเมื่อข้อความหายหรือซ้ำ ไม่ใช่ตั้ง QoS 2 ทุก topic

## 4. Retained message

Retained message ทำให้ subscriber ใหม่ได้รับค่าล่าสุดที่ broker เก็บไว้สำหรับ topic นั้น เหมาะกับ state/config บางประเภท แต่ต้องระวัง retained command ที่อาจถูกนำกลับมาใช้เมื่อ client reconnect โดยไม่ตั้งใจ อย่าใช้ retained กับคำสั่งที่เป็น one-time action โดยไม่ออกแบบ semantics ให้ชัดเจน

## 5. Last Will and Testament

LWT ช่วยให้ broker publish สถานะ offline เมื่อ client ตัดการเชื่อมต่อผิดปกติ ออกแบบ status topic และ retained status ให้ dashboard เห็นสถานะล่าสุด แต่ควรมี heartbeat/last-seen เพราะการเชื่อมต่ออาจค้างก่อน broker ตรวจพบ

## 6. Payload schema

ส่ง JSON ที่มี version, timestamp, device ID และหน่วยชัดเจน:

```json
{
  "schema_version": 1,
  "device_id": "motor-01",
  "timestamp_ms": 1793350000000,
  "rpm": 1480.0,
  "temperature_c": 42.5,
  "current_a": 1.25,
  "vibration_rms_g": 0.08
}
```

ตัวเลขต้องเป็น number ไม่ใช่ string หากต้องคำนวณต่อ ค่าที่ไม่มี sensor reading ต้องใช้ null หรือสถานะ invalid พร้อม reason ไม่ควรแทนด้วยศูนย์ เพราะศูนย์อาจเป็นค่าจริง

## 7. Reconnect และ duplicate handling

- ใช้ reconnect delay แบบเพิ่มขึ้นเป็นช่วง (backoff) และมีเพดาน
- กำหนด client ID ให้ไม่ชนกัน
- ตรวจ return code ของ publish/subscribe
- เก็บ sequence number หรือ message ID หากต้องตรวจ duplicate
- ใส่ timestamp และแยก event time ออกจาก receive time
- หากข้อมูลเก่าเกิน TTL อย่านำมาใช้เป็นสถานะปัจจุบัน

## 8. ความปลอดภัย

- ใช้ authentication แยกอุปกรณ์
- ใช้ TLS เมื่อข้ามเครือข่ายที่ไม่เชื่อถือ
- จำกัด ACL ให้ device publish/subscribe เฉพาะ topic ที่ต้องใช้
- แยก topic telemetry กับ command
- ตรวจ schema และช่วงค่าที่รับได้
- ห้ามเปิด broker แบบ anonymous บนเครือข่ายที่ผู้อื่นเข้าถึงได้
- คำสั่งสำคัญต้องมี authorization, expiry, audit และ state confirmation

## 9. MQTT ไม่ใช่ safety controller

MQTT อาศัยเครือข่ายและ broker ซึ่งอาจล่าช้าหรือขาดการเชื่อมต่อ การป้องกันอันตรายของเครื่องจักรต้องมี local interlock หรือ hardware protection ตามความเหมาะสม อย่าใช้ dashboard/AI/MQTT เป็นชั้นป้องกันเพียงชั้นเดียว

## แหล่งอ้างอิง

- OASIS MQTT Version 5.0 Standard: https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html
- MQTT Version 3.1.1: https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html
