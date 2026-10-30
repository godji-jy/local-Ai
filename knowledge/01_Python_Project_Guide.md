# คู่มือ Python สำหรับโปรเจกต์จริง

> สำหรับนำเข้า Local AI ผ่านโฟลเดอร์ `knowledge/` --- เน้นโครงสร้างโปรเจกต์
> การจัดการข้อผิดพลาด การทดสอบ และการบำรุงรักษา ไม่ใช่แค่ไวยากรณ์พื้นฐาน

## 1. วางโครงสร้างโปรเจกต์

``` text
my_project/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── services.py
│   └── utils.py
├── tests/
│   └── test_services.py
├── data/
├── .env.example
├── requirements.txt
├── README.md
└── main.py
```

หลักการ: แยกส่วนตั้งค่าระบบ (`config.py`), กฎการทำงาน (`services.py`),
ฟังก์ชันช่วย (`utils.py`) และส่วนเริ่มโปรแกรม (`main.py`)
เพื่อให้แก้ไขและทดสอบง่ายขึ้น อย่าเก็บรหัสผ่านหรือ token ไว้ใน Git

## 2. จัดการข้อผิดพลาดอย่างเหมาะสม

``` python
import json
from pathlib import Path

def load_json(path: str) -> dict:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"ไม่พบไฟล์ข้อมูล: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"ไฟล์ JSON ไม่ถูกต้อง: {file_path}") from exc

    if not isinstance(data, dict):
        raise ValueError("ข้อมูลระดับบนสุดต้องเป็น JSON object")
    return data
```

แนวทาง: จับข้อผิดพลาดที่คาดการณ์ได้ ระบุข้อความที่ช่วยแก้ปัญหา และอย่าใช้
`except Exception: pass` เพราะจะซ่อนต้นเหตุ

## 3. ใช้ logging แทน print ในแอปจริง

``` python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("เริ่มระบบ")
logger.warning("พบข้อมูลที่ไม่สมบูรณ์")
```

อย่าบันทึกรหัสผ่าน ข้อมูลส่วนตัว หรือ secret ลง log

## 4. อ่านข้อมูลแบบปลอดภัยและรองรับภาษาไทย

``` python
from pathlib import Path

def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
```

หากเปิดไฟล์ภาษาไทยแล้วเป็นตัวอักษรเพี้ยน ให้ตรวจ encoding
ของไฟล์และโปรแกรมต้นทางก่อนเปลี่ยน encoding แบบสุ่ม

## 5. การทดสอบด้วย pytest

ติดตั้ง: `python -m pip install pytest`

``` python
def average(values):
    if not values:
        raise ValueError("ต้องมีข้อมูลอย่างน้อยหนึ่งค่า")
    return sum(values) / len(values)

def test_average():
    assert average([2, 4, 6]) == 4

def test_average_empty():
    try:
        average([])
    except ValueError:
        return
    assert False, "ควรเกิด ValueError"
```

รันด้วย `python -m pytest -q` จากโฟลเดอร์โปรเจกต์

## 6. การจัดการ dependency

สร้าง virtual environment: - Windows: `py -m venv .venv` - PowerShell:
`.\.venv\Scripts\Activate.ps1` - ติดตั้ง:
`python -m pip install -r requirements.txt` - บันทึกรายการ:
`python -m pip freeze > requirements.txt`

หาก PowerShell บล็อกสคริปต์ ให้ใช้ `.\.venv\Scripts\python.exe`
โดยตรงแทนการเปลี่ยนนโยบายระบบโดยไม่เข้าใจผลกระทบ

## 7. โปรเจกต์ฝึกทำ

สร้างโปรแกรมจัดการไฟล์ความรู้: 1. รับโฟลเดอร์จากผู้ใช้ 2. ตรวจนามสกุล `.txt`,
`.md`, `.pdf` 3. สร้างรายการไฟล์พร้อมขนาดและเวลาแก้ไข 4. บันทึกรายการเป็น JSON
5. จัดการกรณีโฟลเดอร์ไม่มีอยู่และไฟล์อ่านไม่ได้ 6. เขียน unit test
สำหรับการกรองนามสกุล

## 8. Checklist ก่อนส่งโปรเจกต์

-   [ ] เริ่มโปรแกรมจากคำสั่งใน README ได้
-   [ ] มีไฟล์ `requirements.txt`
-   [ ] ไม่มี API key หรือรหัสผ่านใน source code
-   [ ] มีข้อความ error ที่เข้าใจได้
-   [ ] มี test อย่างน้อยสำหรับฟังก์ชันหลัก
-   [ ] ระบุข้อจำกัดและวิธีทดลองซ้ำได้

## แบบฝึกหัด

1.  เพิ่มฟังก์ชันค้นหาไฟล์ตามคำในชื่อ
2.  ให้โปรแกรมข้ามไฟล์ขนาดเกิน 20 MB และแจ้งเหตุผล
3.  เขียน test เมื่อไฟล์ไม่มีอยู่
4.  อธิบายว่าเหตุใดการแยก logic ออกจาก UI จึงช่วยดูแลโปรเจกต์ระยะยาว
