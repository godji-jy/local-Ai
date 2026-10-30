# Automation, IoT, ESP32, MQTT และ Firebase

## 1. โครงสร้างระบบ

ระบบมอนิเตอร์เครื่องจักรขนาดเล็กอาจประกอบด้วย: 1. Sensors: อุณหภูมิ กระแส การสั่น
และรอบหมุน 2. ESP32: อ่านค่าและตรวจความสมเหตุสมผล 3. MQTT broker:
ส่งข้อมูลไปยังผู้รับ 4. Dashboard: แสดงค่าปัจจุบันและกราฟย้อนหลัง 5. Database:
เก็บประวัติและเหตุการณ์ 6. Safety controller: ตัดการทำงานเมื่อเงื่อนไขอันตราย

**ข้อสำคัญ:** การป้องกันอันตรายต้องทำในวงจร/ตัวควบคุมที่เหมาะสม
ไม่ควรฝากการตัดไฟไว้กับ cloud, Wi-Fi หรือ AI เพียงอย่างเดียว

## 2. MQTT topics และ payload

ตัวอย่าง topic: - `factory/motor1/telemetry` - `factory/motor1/status` -
`factory/motor1/command` - `factory/motor1/alert`

ตัวอย่าง JSON:

``` json
{
  "device_id": "motor1",
  "timestamp": "2026-10-29T10:30:00Z",
  "rpm": 1480,
  "temperature_c": 42.6,
  "current_a": 1.2,
  "vibration_rms": 0.18
}
```

ควรมี `device_id`, timestamp, หน่วยวัด และ schema version
หากมีการเปลี่ยนรูปแบบข้อมูล

## 3. QoS และ retained message

-   QoS 0: ส่งแบบ best effort; อาจหายได้
-   QoS 1: อย่างน้อยหนึ่งครั้ง; อาจซ้ำ จึงต้องรองรับข้อความซ้ำ
-   QoS 2: ส่งครั้งเดียวตาม protocol แต่มี overhead มากกว่า
-   Retained message: broker เก็บข้อความล่าสุดของ topic ไว้ให้ subscriber ใหม่

อย่าใช้ retained command
ที่อาจสั่งให้เครื่องจักรเริ่มทำงานโดยอัตโนมัติเมื่ออุปกรณ์กลับมาออนไลน์
คำสั่งควรมีอายุหมดอายุและตรวจสถานะความปลอดภัยก่อนเสมอ

## 4. ตัวอย่าง Python subscriber สำหรับทดลอง

ติดตั้ง `python -m pip install paho-mqtt`

``` python
import json
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
TOPIC = "factory/motor1/telemetry"

def on_connect(client, userdata, flags, reason_code, properties):
    print("connect result:", reason_code)
    client.subscribe(TOPIC, qos=1)

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        rpm = float(payload["rpm"])
        temp = float(payload["temperature_c"])
        print(f"RPM={rpm:.0f}, Temp={temp:.1f} C")
    except (ValueError, KeyError, UnicodeDecodeError) as exc:
        print("Invalid payload:", exc)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_forever()
```

เปลี่ยน broker ให้ตรงกับระบบจริง และอย่าเปิด broker สู่ internet โดยไม่มี
authentication/TLS

## 5. การคำนวณ RPM จาก Hall sensor

ถ้ามีแม่เหล็ก `P` จุดต่อรอบ และนับพัลส์ `N` ครั้งในช่วง `T` วินาที:

`RPM = (N / P) × (60 / T)`

ตัวอย่าง: ติดแม่เหล็ก 3 จุด นับได้ 75 พัลส์ใน 1 วินาที จะได้
`(75 / 3) × 60 = 1500 RPM` โดยสมมติว่าแต่ละแม่เหล็กให้หนึ่งพัลส์และไม่มีพัลส์หลุด/ซ้ำ

ใช้ interrupt ที่สั้น ไม่ทำ `Serial.print()` หนัก ๆ ใน ISR และใช้ตัวแปรที่แชร์กับ ISR
อย่างถูกต้อง เช่น critical section หรือ atomic ตามแพลตฟอร์ม

## 6. Firebase และการออกแบบข้อมูล

ตัวอย่าง path: - `/devices/motor1/telemetry/latest` -
`/devices/motor1/telemetry_history/{push_id}` -
`/devices/motor1/alerts/{alert_id}` - `/devices/motor1/config`

แยกข้อมูลล่าสุดออกจากประวัติ เพื่อให้ dashboard อ่านข้อมูลปัจจุบันได้เร็ว ตั้ง Security
Rules ให้แต่ละอุปกรณ์/ผู้ใช้เข้าถึงเฉพาะข้อมูลที่จำเป็น ห้ามใช้ database rules
แบบเปิดอ่านเขียนทุกคนในระบบจริง

## 7. Safety state machine

ออกแบบสถานะอย่างชัดเจน: - `NORMAL` - `WARNING` - `TRIPPED` -
`RESET_REQUIRED`

แนวทาง: 1. ตรวจเซนเซอร์ขาด/ค่าผิดช่วง 2. กำหนด threshold และเวลา debounce 3.
เมื่อ trip ให้หยุดด้วยวงจรควบคุมที่เหมาะสม 4. บันทึกเหตุผลและ timestamp 5. อนุญาต
reset เฉพาะเมื่อเงื่อนไขปลอดภัย 6. ไม่ให้ระบบเริ่มเองหลังไฟดับหรือเน็ตกลับมา

## 8. โปรเจกต์จบ

ทำ dashboard ติดตามมอเตอร์พร้อม RPM, อุณหภูมิ, กระแส, vibration, power
estimate, alert history และสถานะ AI
โดยแสดงความแตกต่างระหว่างค่าที่วัดจริงกับค่าที่โมเดลทำนาย

## แบบฝึกหัด

1.  ออกแบบ MQTT topic tree สำหรับมอเตอร์ 3 ตัว
2.  เพิ่มการตรวจสอบ payload ว่ามีฟิลด์ครบและชนิดถูกต้อง
3.  จำลอง broker หลุดแล้ววางแผน reconnect
4.  เขียน state diagram ของระบบ safety
5.  อธิบายว่าทำไม AI ไม่ควรเป็นกลไกตัดไฟหลัก
