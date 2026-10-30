# การสร้างและดูแลระบบ AI แบบ Offline

## 1. คำว่า Offline หมายถึงอะไร

ระบบ offline ที่แท้จริงควรทำงานได้โดยไม่ส่ง prompt, เอกสาร หรือ telemetry
ไปยังบริการภายนอก ต้องตรวจทั้ง runtime, model, tokenizer, embedding model,
package และระบบ log ไม่ใช่แค่ปิด API key

## 2. องค์ประกอบระบบ Local AI

-   LLM: สร้างคำตอบ
-   Embedding model: แปลงข้อความเป็นเวกเตอร์
-   Vector store: ค้นหาส่วนเอกสารที่เกี่ยวข้อง
-   Parser: อ่าน PDF/TXT/MD/โค้ด
-   UI: รับคำถามและแสดงผล
-   Local storage: เก็บเอกสารและ index

หากใช้ RAG ให้แยก "ค้นเอกสาร" กับ "สร้างคำตอบ" ออกจากกันเพื่อวิเคราะห์ปัญหาได้ง่าย

## 3. เช็กลิสต์ก่อนตัดอินเทอร์เน็ต

1.  ดาวน์โหลดโมเดลและไฟล์ที่จำเป็นครบแล้ว
2.  ทดสอบการโหลด tokenizer/embedding แบบ local path
3.  ติดตั้ง dependency ไว้ใน virtual environment
4.  ทดลองถามคำถามจากเอกสารจริง
5.  ปิดเครือข่ายแล้วทดสอบซ้ำ
6.  ตรวจ network monitor หรือ firewall log ว่าไม่มี outbound connection
    ที่ไม่คาดคิด
7.  เตรียมสำรองโมเดลและ index

การตั้ง environment variable ให้ offline เป็นการช่วยป้องกันการดาวน์โหลดอัตโนมัติ
แต่ไม่ได้พิสูจน์ด้วยตัวเองว่าโปรแกรมไม่มีการเชื่อมต่อเครือข่าย

## 4. ตัวอย่างเรียก Ollama ผ่านเครื่องตัวเอง

``` python
import requests

def ask_local_model(prompt: str) -> str:
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "qwen3:4b",
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )
    response.raise_for_status()
    return response.json()["response"]

print(ask_local_model("อธิบาย MQTT แบบสั้น ๆ"))
```

คำสั่งนี้เรียก service บน localhost ไม่ใช่ API ภายนอก ชื่อโมเดลต้องตรงกับ
`ollama list` บนเครื่องนั้น

## 5. RAG pipeline ที่ตรวจสอบได้

1.  อ่านเอกสาร
2.  แบ่งเป็น chunks
3.  สร้าง embedding
4.  บันทึกพร้อม metadata
5.  ค้น top-k chunks
6.  ส่ง context และคำถามให้ LLM
7.  แสดงคำตอบพร้อมชื่อไฟล์/หน้าหรือหัวข้ออ้างอิง

เริ่ม chunk ขนาดประมาณ 400--800 tokens และ overlap 50--120 tokens
เป็นค่าทดลอง ไม่ใช่กฎตายตัว ควรปรับตามเอกสารและภาษาไทย

## 6. ป้องกัน embedding dimension mismatch

ข้อผิดพลาดเช่น `size 1024 is different from 384` มักเกิดเมื่อใช้ embedding model
คนละตัวกับที่สร้าง index ไว้ - บันทึกชื่อและเวอร์ชัน embedding model ใน metadata -
หากเปลี่ยน embedding model ให้สร้าง embeddings/index ใหม่ในตำแหน่งชั่วคราว -
ปิดโปรแกรมทุกตัวที่จับไฟล์ฐานข้อมูลอยู่ก่อนสลับ index - สำรองฐานข้อมูลก่อน migration -
ตรวจ dimension ของเวกเตอร์ใหม่ก่อนนำไปใช้งาน

อย่านำเวกเตอร์คนละโมเดลมาใช้ร่วมกันแม้จะเก็บในไฟล์ชนิดเดียวกัน

## 7. วัดคุณภาพ RAG

สร้างชุดคำถามทดสอบอย่างน้อย 20 ข้อ: - คำตอบอยู่ในเอกสารโดยตรง -
คำถามใช้คำพ้องหรือสะกดผิด - เอกสารไม่มีคำตอบ - มีหลายเอกสารที่คล้ายกัน -
คำถามเป็นภาษาไทยและอังกฤษ

ประเมิน retrieval: เอกสารที่ถูกต้องติด top-k หรือไม่; ประเมิน generation: คำตอบอิง
context หรือแต่งข้อมูลเพิ่ม; ประเมิน latency และ RAM/VRAM

## 8. การป้องกัน prompt injection ในเอกสาร

เอกสารที่ค้นเจออาจมีข้อความสั่งให้โมเดลเปิดเผยข้อมูลหรือเปลี่ยนกฎ ให้ถือเนื้อหาเอกสารเป็น
"ข้อมูล" ไม่ใช่คำสั่งระบบ จำกัดเครื่องมือที่ LLM เรียกได้ และไม่ให้ RAG
อ่านไฟล์นอกโฟลเดอร์ที่อนุญาต

## โปรเจกต์จบ

สร้าง Local Knowledge Assistant ที่รองรับ Markdown, TXT, PDF และโค้ด มี source
citation, โหมด offline, ประวัติการนำเข้าเอกสาร, การลบ/สร้าง index ใหม่
และชุดประเมินผล

## แบบฝึกหัด

1.  เขียนแผนทดสอบ offline โดยไม่อาศัยเพียง environment variable
2.  สร้างคำถามที่ไม่มีคำตอบในเอกสาร แล้วกำหนดพฤติกรรม "ไม่พบข้อมูล"
3.  ออกแบบ metadata สำหรับติดตาม embedding model
4.  เขียน test ป้องกันการนำไฟล์นอก `knowledge/` เข้า index
