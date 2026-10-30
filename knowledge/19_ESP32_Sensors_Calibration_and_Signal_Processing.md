# ESP32 Sensors, Calibration และ Signal Processing สำหรับระบบ Monitoring

**หมวด:** Automation / Embedded Systems / IoT  
**คำค้น:** ESP32, ADC, calibration, Hall sensor, RPM, DS18B20, ACS712, ADXL345, sampling, filtering

## 1. แยกค่าที่วัดได้จากค่าที่คำนวณ

ระบบ monitoring ควรเก็บทั้ง raw reading, calibrated reading และ derived metric แยกจากกัน เช่น:

- ADC raw count
- voltage หลัง calibration
- current ที่คำนวณจาก ACS712
- RPM ที่คำนวณจาก pulse count
- vibration feature ที่คำนวณจาก accelerometer

หากเก็บแต่ค่าที่คำนวณแล้ว จะย้อนตรวจไม่ได้ว่าปัญหาเกิดจาก sensor, calibration หรือสูตรคำนวณ

## 2. ADC และ Calibration

ADC แปลงแรงดัน analog เป็นค่าดิจิทัล ค่า raw ไม่ใช่แรงดันที่แม่นยำโดยตรง ความคลาดเคลื่อนอาจมาจาก reference voltage, attenuation, non-linearity, noise และอุณหภูมิของวงจร

แนวทาง:

1. ตรวจขอบเขตแรงดันสูงสุดของ pin ตาม datasheet ของชิป/บอร์ด
2. ห้ามป้อนแรงดันเกินขีดจำกัด ADC โดยตรง
3. ใช้ calibration API หรือวัดเทียบกับเครื่องมืออ้างอิง
4. เก็บค่า raw และ calibrated voltage
5. ใช้ multisampling/low-pass filter เมื่อเหมาะสม
6. ทดสอบกับหลายจุดตลอดช่วงใช้งาน ไม่ใช่เทียบเพียงจุดเดียว

หมายเหตุ: ADC2 ของ ESP32 รุ่นดั้งเดิมมีการใช้งานร่วมกับ Wi-Fi ในบางโหมด/driver ควรตรวจข้อจำกัดของชิปและ ESP-IDF/Arduino core version ที่ใช้งานจริง อย่าเหมารวมทุกชิปรุ่น ESP32 ว่าเหมือนกัน

## 3. Hall sensor และ RPM

หากเซนเซอร์สร้าง P pulses ต่อรอบ และนับได้ N pulses ภายในช่วงเวลา Δt วินาที:

`RPM = (N / P) × (60 / Δt)`

ถ้านับ pulse ด้วย interrupt ในช่วง 1 วินาที สูตรลดรูปเป็น `RPM = N × 60 / P`

ตัวอย่าง: แม่เหล็ก 3 จุดทำให้ได้ 3 pulses ต่อรอบ เมื่อวัด 75 pulses ใน 1 วินาที:

`RPM = (75 / 3) × 60 = 1500 RPM`

ต้องยืนยันว่า sensor ให้หนึ่ง pulse ต่อแม่เหล็กจริง ไม่มีการนับซ้ำจากสัญญาณสั่นหรือ noise ควรใช้ debounce ตามลักษณะสัญญาณและทดสอบด้วย tachometer อ้างอิง

## 4. วัด pulse แบบ interval และ count window

- Fixed time window: นับ pulses ในช่วงเวลาคงที่ เหมาะกับความเร็วสูง แต่ความละเอียดรอบต่ำอาจหยาบ
- Pulse period: วัดเวลาระหว่าง pulses เหมาะกับความเร็วต่ำ แต่ควรจัดการกรณีหยุดหมุนและ timeout
- Hybrid: เปลี่ยนวิธีตามช่วง RPM เพื่อให้ค่าครอบคลุมกว้างขึ้น

ใช้ตัวแปรที่เกี่ยวกับ ISR เป็น `volatile` ตามความจำเป็น และหากต้องอ่าน/รีเซ็ต counter บน MCU แบบ multicore ให้ใช้ critical section หรือ atomic-safe method ตาม framework หลีกเลี่ยงการทำงานหนักใน ISR

## 5. Current sensor ACS712

หลักการทั่วไปคือวัดแรงดันเอาต์พุตที่เปลี่ยนตามกระแส ความสัมพันธ์พื้นฐาน:

`I = (Vout - Vzero) / Sensitivity`

โดย `Vzero` คือ offset เมื่อกระแสเป็นศูนย์ และ sensitivity ขึ้นกับรุ่น/ช่วงกระแสและเงื่อนไขการใช้งาน ต้อง calibrate zero offset, ตรวจทิศทางกระแส, วัด noise และเทียบกับมิเตอร์ที่เหมาะสม

ไม่ควรใช้ sensitivity จากรุ่น 5A, 20A และ 30A สลับกัน และไม่ควรเชื่อค่า offset 2.5V แบบตายตัวโดยไม่วัดบนอุปกรณ์จริง

## 6. อุณหภูมิ DS18B20

ควรตรวจสถานะการอ่าน, CRC, timeout และค่า sentinel ที่ไลบรารีอาจใช้เมื่ออ่านผิดพลาด อย่านำค่า error ไปคำนวณค่าเฉลี่ยหรือสั่ง safety logic ราวกับเป็นอุณหภูมิจริง

## 7. Accelerometer และ Vibration

ก่อนวิเคราะห์ vibration ต้องรู้ sampling rate, range, axis orientation, mounting position และหน่วย ใช้ baseline จากเครื่องปกติภายใต้ load/speed เดียวกัน

Feature ที่ใช้ได้:

- Mean และ standard deviation
- RMS = sqrt(mean(x²))
- Peak-to-peak
- Crest factor = peak / RMS
- FFT spectrum เพื่อดู frequency components

RMS สูงขึ้นไม่ได้ระบุสาเหตุชำรุดได้แน่นอน การวิเคราะห์ต้องควบคุม RPM, load, mounting และ noise

## 8. Filtering และ sampling

- Moving average ช่วยลด noise แบบสั้นแต่ทำให้ response ช้าลง
- Median filter เหมาะกับ spike บางประเภท
- Low-pass filter ลดความถี่สูง แต่ต้องเลือก cutoff ตามสัญญาณเป้าหมาย
- Sampling rate ต้องมากพอสำหรับความถี่ที่ต้องการวิเคราะห์ และต้องพิจารณา aliasing

อย่าใช้ filter ที่ทำให้ safety trip ล่าช้าโดยไม่ประเมินความเสี่ยง

## 9. Safety logic

ระบบหยุดฉุกเฉินหรือ overcurrent protection ไม่ควรพึ่ง AI prediction เพียงอย่างเดียว ให้ใช้ threshold/hardware protection ที่ผ่านการทดสอบเป็นชั้นป้องกันอิสระ พร้อม fail-safe state เมื่อ sensor ขาด, data stale หรือ network หาย การทดสอบกับมอเตอร์จริงควรมีผู้ดูแลและชุดป้องกันที่เหมาะสม

## แหล่งอ้างอิง

- Espressif ESP32 ADC guide: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/adc/
- ADC calibration: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/adc/adc_calibration.html
- DS18B20 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ds18b20.pdf
- ACS712 datasheet: https://www.allegromicro.com/-/media/files/datasheets/acs712-datasheet.ashx
