# Ollama Local Model Operations: API, Performance และการตรวจสอบผลลัพธ์

**หมวด:** Local AI / Model Serving  
**คำค้น:** Ollama, /api/chat, stream, keep_alive, context length, num_predict, latency, GPU, model loading

## 1. บทบาทของ Ollama

Ollama เป็น runtime สำหรับเรียกใช้งานโมเดลภาษาในเครื่อง แอป Python ติดต่อ runtime ผ่าน HTTP API โดยทั่วไป local endpoint คือ `http://127.0.0.1:11434` เมื่อ Ollama เปิดทำงาน

แยกเวลาประมวลผลเป็น:

- Model load time: โหลด weights เข้าหน่วยความจำ
- Prompt processing / prefill: ประมวลผล prompt และประวัติ
- Generation time: สร้าง token คำตอบ
- Network/UI overhead: รับส่งข้อมูลและ render หน้าเว็บ

ถ้าทดสอบ chat สั้นเร็ว แต่หน้าเว็บช้า ให้ตรวจ prompt length, history length, retrieval, จำนวนรอบ LLM และการแสดงผล ไม่ควรสรุปว่า GPU ช้าอย่างเดียว

## 2. API chat

รูปแบบพื้นฐาน:

```python
payload = {
    "model": "qwen3:4b",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain embeddings."}
    ],
    "stream": False,
    "options": {
        "temperature": 0.2,
        "num_ctx": 4096,
        "num_predict": 384
    }
}
```

`stream=False` ให้รอผลลัพธ์จนเสร็จ เหมาะกับการประมวลผลก่อนแสดงคำตอบ ส่วน `stream=True` เหมาะกับการทยอยแสดง token เมื่อ UI และ backend จัดการ stream อย่างถูกต้อง

## 3. Context window และ token

Context window ครอบคลุม system prompt, ประวัติแชต, คำถาม, retrieved context และส่วนที่โมเดลต้องสร้าง การเพิ่มประวัติและเอกสารยาวอาจทำให้ prefill ช้าลงและใช้ memory มากขึ้น

ควรจำกัด:

- จำนวนข้อความเก่า
- ความยาวต่อข้อความ
- จำนวน chunk ที่นำมาแนบ
- ขนาด chunk
- `num_predict` สำหรับผลลัพธ์

อย่าตัดข้อความอย่างเดียวจนทำให้โค้ดหรือข้อมูลสำคัญขาดกลางประโยค ควรตัดตามขอบเขต message/section

## 4. Temperature และการตั้งค่า

Temperature สูงขึ้นโดยทั่วไปทำให้การสุ่มหลากหลายขึ้น; ต่ำลงช่วยให้คำตอบมีความสม่ำเสมอขึ้น แต่ไม่ได้รับประกันความถูกต้อง สำหรับงานตอบจากเอกสารควรเริ่มจากค่าต่ำถึงปานกลางและประเมินด้วยชุดคำถามจริง

`num_predict` คือเพดานจำนวน token ที่สร้าง ไม่ได้บอกจำนวน token ที่จะได้แน่นอน `num_ctx` กำหนดบริบทที่ runtime รองรับตามความสามารถของโมเดลและ runtime

ตรวจ option ที่ใช้ได้จากเอกสารรุ่นที่ติดตั้ง หลีกเลี่ยงส่งพารามิเตอร์ที่ API version ไม่รองรับ

## 5. Keep-alive และการใช้หน่วยความจำ

การคงโมเดลไว้ในหน่วยความจำช่วยลดเวลาที่ต้องโหลดใหม่ แต่ใช้ RAM/VRAM ต่อเนื่อง ค่า keep-alive จึงเป็น trade-off ระหว่างการตอบครั้งถัดไปเร็วขึ้นกับการคืนหน่วยความจำให้โปรแกรมอื่น

บน GPU VRAM 4 GB โมเดลอาจต้อง offload บางส่วนไป RAM/CPU ขึ้นกับขนาด quantization, context length และ runtime จึงควรวัดจริง ไม่ควรคาดเดาจากจำนวนพารามิเตอร์อย่างเดียว

## 6. วัด latency ให้แยกส่วน

พิมพ์เวลาแต่ละช่วง:

```python
import time

start = time.perf_counter()
# เรียก retrieval
retrieval_ms = (time.perf_counter() - start) * 1000

start = time.perf_counter()
# เรียก Ollama
llm_ms = (time.perf_counter() - start) * 1000

print({
    "retrieval_ms": round(retrieval_ms, 1),
    "llm_ms": round(llm_ms, 1),
})
```

สำหรับ stream ให้แยก time-to-first-token และ total generation time ด้วย

## 7. หนึ่งรอบหรือสองรอบ

การเรียก LLM สองรอบ (ร่างแล้วให้ editor เรียบเรียง) อาจทำให้โครงสร้างอ่านง่ายขึ้น แต่เพิ่ม latency และมีโอกาสที่ editor จะเปลี่ยนความหมายหรือทำรายละเอียดหาย ควรเริ่มจาก prompt ที่ชัดและใช้การเรียกหนึ่งรอบก่อน แล้วเปรียบเทียบคุณภาพด้วยชุดทดสอบ หากสองรอบดีขึ้นจริงจึงคงไว้

## 8. ข้อผิดพลาดที่พบบ่อย

- Connection refused: Ollama ไม่ได้เปิดหรือ URL/port ผิด
- 404 model not found: ชื่อ model tag ไม่ตรงกับที่ติดตั้ง
- 400/invalid option: option หรือรูปแบบ request ไม่รองรับในเวอร์ชันนั้น
- Timeout: prompt ใหญ่หรือการสร้างคำตอบใช้เวลานาน
- Empty content: ต้องตรวจ response JSON และส่วน `message.content`
- Model unload/reload: ตรวจ keep_alive และทรัพยากรของเครื่อง

## 9. ความเป็นส่วนตัวและขอบเขต Offline

การเรียก `127.0.0.1` เป็นการเรียกบริการในเครื่อง แต่แอปทั้งระบบจะ offline จริงได้ต่อเมื่อ dependency, model, embeddings, fonts, telemetry และส่วนเสริมต่าง ๆ ไม่จำเป็นต้องดาวน์โหลดหรือติดต่ออินเทอร์เน็ตในเวลาทำงาน ทดสอบโดยปิดเครือข่ายหลังติดตั้งครบและตรวจ log/network behavior

## แหล่งอ้างอิง

- Ollama API: https://docs.ollama.com/api
- Ollama API Chat: https://docs.ollama.com/api/chat
- Ollama FAQ: https://docs.ollama.com/faq
