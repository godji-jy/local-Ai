# Defensive Cybersecurity สำหรับเว็บแอปและโปรเจกต์นักศึกษา

**หมวด:** Cybersecurity / Secure Software  
**คำค้น:** secure coding, authentication, authorization, SQL injection, XSS, CSRF, secrets, dependency, logging
**ขอบเขต:** เน้นการป้องกันและทดสอบระบบที่ผู้พัฒนามีสิทธิ์ดูแลเท่านั้น

## 1. Authentication และ Authorization

- Authentication: ตรวจว่าผู้ใช้เป็นใคร
- Authorization: ผู้ใช้นั้นทำอะไรได้บ้าง

การ login สำเร็จไม่ได้แปลว่าผู้ใช้มีสิทธิ์เข้าถึงทุก resource ต้องตรวจ authorization ทุก request โดยใช้หลัก least privilege

## 2. Secrets management

ห้ามฝัง password, API key, database credentials หรือ token ใน source code, public repository, screenshot หรือ log ใช้ environment variables หรือ secret manager ตามขนาดระบบ หาก secret รั่ว ให้ revoke/rotate ไม่ใช่แค่ลบออกจากไฟล์ล่าสุด

## 3. Input validation

ตรวจชนิด ความยาว รูปแบบ และช่วงค่าของ input ฝั่ง server เสมอ UI validation เพียงอย่างเดียวป้องกันการส่ง request ที่สร้างขึ้นเองไม่ได้ ใช้ allowlist ตามความเหมาะสมและแยกการ validate ออกจาก output encoding

## 4. SQL Injection

หลีกเลี่ยงการประกอบ SQL ด้วย string interpolation จาก input ผู้ใช้ ใช้ parameterized query และ account ที่มีสิทธิ์เท่าที่จำเป็น

## 5. Cross-Site Scripting (XSS)

XSS เกิดเมื่อข้อมูลที่ไม่น่าเชื่อถือถูกแสดงเป็น HTML/JavaScript โดยไม่ encode อย่างเหมาะสม ใช้ output encoding ตาม context และหลีกเลี่ยงการ render HTML ที่ผู้ใช้ควบคุมโดยตรง

## 6. Cross-Site Request Forgery (CSRF)

ในระบบที่ใช้ cookie-based authentication ต้องออกแบบ CSRF protection ให้เหมาะกับ framework และ SameSite cookie settings อย่าสันนิษฐานว่า CORS เป็นกลไกป้องกัน CSRF

## 7. Access control สำหรับ IoT

แยกสิทธิ์ device, dashboard และ administrator เช่น device หนึ่งตัว publish ได้เฉพาะ telemetry topic ของตัวเอง และ dashboard ที่ไม่มีสิทธิ์ไม่ควรส่ง command ไปยังอุปกรณ์

## 8. Logging และการจัดการ error

บันทึกเหตุการณ์สำคัญ เช่น login failure, permission denied, configuration change และ alert state โดยไม่ log password/token ข้อความ error ที่ส่งผู้ใช้ไม่ควรเผย stack trace, filesystem path หรือ credential

## 9. Dependency และ supply chain

ใช้ package จากแหล่งที่เชื่อถือได้ pin เวอร์ชันที่ผ่านการทดสอบ ตรวจ dependency vulnerability และอัปเดตอย่างมีแผน อย่าติดตั้ง package ชื่อคล้าย library ที่ต้องการโดยไม่ตรวจเจ้าของและแหล่งที่มา

## 10. Secure development checklist

- ใช้ HTTPS/TLS เมื่อสื่อสารผ่านเครือข่ายที่ไม่เชื่อถือ
- มี authentication และ authorization แยกกัน
- ป้องกัน SQL injection และ XSS
- เก็บ secrets นอก source code
- จำกัดสิทธิ์ broker/database
- ตรวจ input ที่ server
- มี backup และการกู้คืน
- มี audit log สำหรับ action สำคัญ
- ทดสอบเฉพาะระบบที่ได้รับอนุญาต

## 11. OWASP Top 10

OWASP Top 10 เป็นเอกสารสร้างความตระหนักเกี่ยวกับความเสี่ยงเว็บแอป รุ่น 2025 มีหัวข้อ เช่น Broken Access Control, Security Misconfiguration, Software Supply Chain Failures, Cryptographic Failures และ Injection ควรตรวจรายละเอียดจากรุ่นล่าสุดเมื่อใช้ในรายงานหรือออกแบบระบบจริง

## แหล่งอ้างอิง

- OWASP Top 10:2025: https://top10.owasp.org/2025/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- Python secrets module: https://docs.python.org/3/library/secrets.html
