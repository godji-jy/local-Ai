# การออกแบบและตรวจสอบโปรเจกต์ AI/Automation เชิงวิศวกรรม

**หมวด:** Engineering / Automation / Research Methodology  
**คำค้น:** requirement, architecture, acceptance criteria, calibration, validation, baseline, risk assessment, experiment design

## 1. เริ่มจากปัญหา ไม่เริ่มจากชื่อ AI

เขียน problem statement ให้ตอบว่า:

- ใครเป็นผู้ใช้
- ปัญหาที่เกิดขึ้นคืออะไร
- ปัจจุบันแก้ปัญหาอย่างไร
- ข้อจำกัดของวิธีเดิมคืออะไร
- ระบบใหม่ต้องส่งผลลัพธ์อะไร
- จะวัดได้อย่างไรว่าดีขึ้น

หากกฎ threshold แบบปกติแก้ปัญหาได้เพียงพอ การใส่ AI อาจไม่คุ้มกับความซับซ้อน

## 2. Requirement และ acceptance criteria

แยก:

- Functional requirements: ระบบต้องทำอะไร
- Non-functional requirements: latency, reliability, maintainability, security
- Safety requirements: เงื่อนไขหยุด/ป้องกันอันตราย

ตัวอย่าง acceptance criteria ที่วัดได้:

- อ่าน RPM ได้ภายในช่วง tolerance ที่กำหนดเมื่อเทียบเครื่องมืออ้างอิง
- แสดงสถานะ stale เมื่อไม่มีข้อมูลใหม่เกินเวลาที่กำหนด
- บันทึก event พร้อม timestamp และ device ID
- หาก sensor invalid จะไม่แสดงค่าปลอมเป็นค่าปกติ

ตัวเลข tolerance ต้องกำหนดจาก sensor datasheet, เครื่องมืออ้างอิง และความต้องการของโครงงาน ไม่ควรตั้งตัวเลขโดยไม่มีเหตุผล

## 3. Architecture และ data flow

วาด flow ตั้งแต่ sensor → microcontroller → transport → backend → database → dashboard → alert ระบุ:

- protocol และ payload
- sampling/update rate
- หน่วยและ timestamp
- จุดที่มี buffer/retry
- failure modes
- จุดที่ตัดสินใจ safety

## 4. Calibration และ ground truth

การอ้างว่าระบบแม่นต้องมีเครื่องมืออ้างอิงหรือ ground truth วิธีทดสอบต้องครอบคลุมช่วงใช้งานหลายจุดและทำซ้ำได้ รายงาน mean error, MAE, maximum absolute error และเงื่อนไขการทดลองตามความเหมาะสม

## 5. AI ต้องเทียบกับ baseline

ตัวอย่าง motor monitoring:

- Baseline A: fixed threshold
- Baseline B: moving average + threshold
- Model C: supervised classifier

ประเมินด้วย dataset split ที่ป้องกัน temporal/group leakage และรายงาน precision/recall ของ class fault แต่ละประเภท พร้อม false alarm และ missed detection

## 6. Data collection protocol

บันทึก operating condition เช่น speed, load, temperature, sensor location, sampling frequency, firmware version และวันที่ทดลอง ห้ามใช้ข้อมูล test ในการปรับ threshold หรือ train model

## 7. Reliability และ fault handling

ทดสอบกรณี:

- sensor disconnected
- sensor stuck at constant value
- impossible reading
- network disconnect
- broker unavailable
- database full/unavailable
- power interruption
- duplicate/out-of-order message

ระบบควรแสดงสถานะ degraded/fault แทนการแสดงค่าเก่าราวกับยังสดใหม่

## 8. Safety by design

AI prediction เป็นข้อมูลช่วยตัดสินใจ ไม่ใช่กลไกป้องกันอันตรายเพียงอย่างเดียว ใช้ interlock, emergency stop และ overcurrent/overtemperature protection ที่เหมาะสมและผ่านการตรวจสอบโดยผู้มีความรู้ ออกแบบให้เมื่อข้อมูลไม่แน่ใจ ระบบเข้าสู่สถานะปลอดภัยตาม risk assessment

## 9. รายงานโครงงาน

โครงสร้างแนะนำ:

1. บทนำและ problem statement
2. วัตถุประสงค์และขอบเขต
3. ทฤษฎีและงานที่เกี่ยวข้อง
4. การออกแบบระบบและอุปกรณ์
5. วิธีดำเนินงานและการเก็บข้อมูล
6. การทดลองและเกณฑ์ประเมิน
7. ผลการทดลองพร้อมตาราง/กราฟ
8. วิเคราะห์ข้อผิดพลาดและข้อจำกัด
9. สรุปและแนวทางพัฒนาต่อ

ระบุผลที่วัดได้จริง แยกจากผลที่คาดหวัง และไม่แต่งผลทดลอง

## แหล่งอ้างอิง

- NIST Engineering Statistics Handbook: https://www.itl.nist.gov/div898/handbook/
- Espressif ESP-IDF documentation: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/
- scikit-learn model evaluation: https://scikit-learn.org/stable/modules/model_evaluation.html
