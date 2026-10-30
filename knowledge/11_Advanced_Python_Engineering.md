# Advanced Python Engineering: โครงสร้างโปรแกรม การจัดการข้อผิดพลาด และการทดสอบ

**หมวด:** Programming / Software Engineering  
**คำค้น:** Python, functions, modules, exceptions, logging, testing, type hints, virtual environment, debugging  
**ขอบเขต:** แนวทางสร้างโปรแกรม Python ที่อ่านง่าย ตรวจสอบได้ และดูแลต่อได้ เหมาะกับโปรเจกต์นักศึกษาและแอป Local AI

## 1. คิดเป็นส่วนประกอบก่อนเขียนโค้ด

โปรแกรมที่ดูแลได้ควรแบ่งหน้าที่ชัดเจน ไม่ควรรวมการรับข้อมูล ประมวลผล ติดต่อฐานข้อมูล และแสดงผลไว้ในฟังก์ชันเดียวทั้งหมด ตัวอย่างการแบ่งชั้นงาน:

1. **Interface layer:** รับค่าจากผู้ใช้ เช่น Gradio textbox และ dropdown
2. **Application/service layer:** ตัดสินใจว่าจะเรียกขั้นตอนใด เช่น ค้นเอกสารก่อนตอบ
3. **Data access layer:** อ่าน/เขียน ChromaDB หรือไฟล์
4. **Model/client layer:** ติดต่อ Ollama หรือโมเดล embedding
5. **Observability layer:** บันทึกเวลา สถานะ และข้อผิดพลาด

หลักสำคัญคือแต่ละชั้นควรมีหน้าที่เดียวและสื่อสารผ่านข้อมูลที่มีรูปแบบชัดเจน ตัวอย่างเช่น `retrieve_context(query) -> list[Document]` ไม่ควรแสดง HTML เอง และ `format_answer(text) -> str` ไม่ควรเรียกฐานข้อมูล

## 2. แยกฟังก์ชันและกำหนดสัญญาข้อมูล

ฟังก์ชันที่ดีควรมีชื่อสื่อความหมาย รับค่าที่จำเป็น และคืนค่าที่คาดเดาได้ ควรระบุ type hints เพื่อช่วยผู้พัฒนาและเครื่องมือตรวจโค้ด

```python
from typing import Any

def normalize_query(query: str) -> str:
    """Normalize whitespace without changing the query's meaning."""
    return " ".join(query.strip().split())

def safe_get_text(record: dict[str, Any]) -> str:
    value = record.get("text", "")
    return value.strip() if isinstance(value, str) else ""
```

อย่าทำ normalization แบบลบอักขระทุกชนิดโดยไม่เข้าใจภาษา เพราะอาจทำลายคำภาษาไทย เครื่องหมายในโค้ด หรือชื่อไฟล์ได้ ควรเก็บ `raw_query` และ `normalized_query` แยกกันเมื่อการแปลงมีผลต่อการค้นหา

## 3. จัดการข้อผิดพลาดเป็นประเภท

ข้อผิดพลาดมีหลายชนิดและควรตอบสนองต่างกัน:

- `ConnectionError`: บริการ Ollama หรือฐานข้อมูลเข้าถึงไม่ได้
- `Timeout`: บริการตอบช้าเกินกำหนด ควรแจ้งว่าคำขอหมดเวลา ไม่ควรแสร้งว่าค้นพบข้อมูลแล้ว
- `HTTPError`: API ตอบสถานะผิดพลาด ควรบันทึก status code และรายละเอียดที่ไม่เป็นความลับ
- `JSONDecodeError`: ข้อมูลตอบกลับไม่ใช่ JSON ที่ถูกต้อง
- `FileNotFoundError`: เส้นทางไฟล์ไม่ถูกต้องหรือไฟล์ถูกย้าย
- `KeyError` / `TypeError`: โครงสร้างข้อมูลไม่ตรงกับที่โปรแกรมคาดหวัง

จับ exception ที่ขอบเขตการทำงานซึ่งสามารถกู้คืนได้ อย่าใช้ `except Exception: pass` เพราะจะซ่อนสาเหตุจริง ควร log รายละเอียดทางเทคนิคใน terminal และส่งข้อความที่เข้าใจง่ายให้ผู้ใช้

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("local_ai")

try:
    result = call_service()
except TimeoutError:
    logger.warning("Service timed out")
    user_message = "บริการใช้เวลานานเกินไป กรุณาลองใหม่"
except Exception:
    logger.exception("Unexpected failure")
    user_message = "เกิดข้อผิดพลาดภายในระบบ กรุณาตรวจสอบ log"
```

ไม่ควรบันทึกรหัสผ่าน API key token หรือเนื้อหาส่วนตัวที่ไม่จำเป็นลง log

## 4. Logging ที่ช่วยหาสาเหตุจริง

การบันทึก log ควรมี timestamp, ระดับความรุนแรง, ชื่อ component, request ID และระยะเวลา เช่น:

`INFO retrieval query_id=abc retrieved=4 elapsed_ms=83`

`WARNING ollama timeout_ms=300000 model=qwen3:4b`

แยก `INFO` สำหรับเหตุการณ์ปกติ, `WARNING` สำหรับสิ่งผิดปกติที่ยังทำงานต่อได้, `ERROR` สำหรับงานล้มเหลว และ `DEBUG` สำหรับรายละเอียดเฉพาะตอนวิเคราะห์ปัญหา

## 5. ทดสอบเป็นชั้น

- **Unit test:** ทดสอบฟังก์ชันเดี่ยว เช่น การตัด chunk หรือแปลง metadata
- **Integration test:** ทดสอบการเชื่อม Python กับ ChromaDB หรือ Ollama
- **End-to-end test:** ทดสอบเส้นทางจริง ตั้งแต่ผู้ใช้ถามจนเห็นคำตอบ
- **Regression test:** เก็บกรณีที่เคยผิดพลาดไว้ทดสอบซ้ำทุกครั้งที่แก้โค้ด

ตัวอย่างกรณีทดสอบ `normalize_query`: ข้อความว่าง, ช่องว่างหลายตัว, ภาษาไทย, ภาษาอังกฤษ, code snippet และข้อความที่มี newline

## 6. Environment และ dependency

ใช้ virtual environment แยก dependency ระหว่างโปรเจกต์ และบันทึกเวอร์ชันที่ทดสอบจริงใน `requirements.txt` หรือ lock file อย่าคิดว่าโค้ดจาก Gradio คนละ major version จะใช้พารามิเตอร์เหมือนกัน ตรวจเวอร์ชันด้วย:

```powershell
python --version
python -m pip show gradio chromadb ollama requests
python -m pip freeze > requirements-lock.txt
```

เมื่อเกิดปัญหา API เปลี่ยน ให้ตรวจเอกสารของเวอร์ชันที่ติดตั้งก่อนแก้โค้ด

## 7. หลักการ Debugging อย่างเป็นระบบ

1. ทำซ้ำปัญหาด้วย input สั้นที่สุด
2. จด expected result และ actual result
3. อ่าน traceback จากล่างขึ้นบน โดยบรรทัดท้ายสุดมักระบุชนิด exception
4. ระบุ component ที่ผิด: UI, chat function, network, model หรือ database
5. แก้ทีละประเด็น อย่าเปลี่ยนหลายส่วนพร้อมกัน
6. เพิ่ม regression test เพื่อป้องกันปัญหาเดิม

## 8. เช็กลิสต์คุณภาพโค้ด

- ฟังก์ชันหนึ่งทำหน้าที่ชัดเจน
- ตรวจชนิดและค่าของ input
- ไม่กลืน exception
- มี timeout สำหรับการเรียกบริการ
- log เวลาและสถานะที่จำเป็น
- ไม่มี secret ฝังใน source code
- มีการทดสอบ input ว่าง input ผิดรูปแบบ และบริการไม่พร้อม
- ข้อความ error บอกแนวทางแก้โดยไม่เปิดเผยข้อมูลลับ

## แหล่งอ้างอิง

- Python Tutorial — Errors and Exceptions: https://docs.python.org/3/tutorial/errors.html
- Python Logging HOWTO: https://docs.python.org/3/howto/logging.html
- Python unittest: https://docs.python.org/3/library/unittest.html
