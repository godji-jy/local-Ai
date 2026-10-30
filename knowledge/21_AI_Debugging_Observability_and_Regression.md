# AI System Debugging, Observability และ Regression Testing

**หมวด:** AI Engineering / Software Quality  
**คำค้น:** observability, latency, tracing, regression, evaluation set, hallucination, retrieval metrics, monitoring

## 1. แยกปัญหาเป็น component

ระบบ Local AI ที่ใช้ RAG มีส่วนประกอบหลัก:

1. UI รับคำถามและภาษา
2. Conversation manager สร้าง history
3. Query preprocessing
4. Embedding model
5. Vector database retrieval
6. Context assembly
7. LLM inference
8. Output validation/formatting
9. UI render

หากคำตอบผิด ให้ตรวจทีละชั้น อย่ารีบเปลี่ยนโมเดลก่อนรู้ว่าปัญหาอยู่ตรง retrieval หรือ generation

## 2. Metrics ที่ควรวัด

- Request count และ error rate
- Retrieval latency
- Embedding latency
- LLM time-to-first-token
- LLM total generation time
- Prompt token count และ output token count ถ้ามีข้อมูลจาก runtime
- Number of retrieved chunks
- Empty retrieval rate
- User feedback / corrected answer count

หลีกเลี่ยง log เนื้อหาส่วนตัวหรือคำถามทั้งหมดโดยไม่มีเหตุผล

## 3. Trace ต่อหนึ่งคำถาม

ให้สร้าง request ID แล้วแนบกับ log ทุกขั้น เช่น:

```text
request_id=R102 stage=query_parse status=ok elapsed_ms=2
request_id=R102 stage=retrieve status=ok count=5 elapsed_ms=65
request_id=R102 stage=ollama status=ok elapsed_ms=9200
request_id=R102 stage=render status=ok elapsed_ms=8
```

จะเห็นทันทีว่าช้าจาก retrieval หรือ LLM และพบว่าระบบมีการเรียกโมเดลซ้ำกี่ครั้ง

## 4. Regression test set

เก็บคำถามจริงที่เคยมีปัญหาไว้เป็นชุดทดสอบ โดยแต่ละตัวอย่างมี:

- question
- expected language
- expected source/document
- key facts ที่ต้องมี
- incorrect claims ที่ห้ามมี
- acceptable answer traits

หลังแก้ prompt, embedding model, chunk size, top-k หรือ LLM ให้รันชุดเดิมและเปรียบเทียบ

## 5. คะแนนคุณภาพคำตอบ

ให้ผู้ประเมินให้คะแนน 0–2 หรือ 1–5 ในมิติ:

- Correctness: เนื้อหาถูกต้อง
- Relevance: ตอบคำถามตรง
- Completeness: ครบประเด็นสำคัญ
- Groundedness: มีหลักฐานจาก context
- Citation correctness: อ้างแหล่งจริงและตรงข้อความ
- Language/style: ภาษาเหมาะสม อ่านง่าย

คะแนนจาก LLM evaluator ใช้ช่วยคัดกรองได้ แต่ไม่ควรใช้แทนการตรวจโดยมนุษย์ทั้งหมด โดยเฉพาะงานที่มีผลต่อความปลอดภัย

## 6. แยก retrieval failure กับ generation failure

- Retrieved context ไม่เกี่ยวข้อง: ปัญหา retrieval, chunk, embedding, query หรือ metadata
- Context ถูกแต่คำตอบผิด: ปัญหา generation prompt, model capability หรือ context overload
- คำตอบดีแต่ไม่มีแหล่ง: ปัญหา metadata/citation assembly
- ข้อความขาด: ปัญหา output token cap, timeout หรือ rendering
- คำตอบภาษาไม่ตรง: ตรวจ language setting, history และตัวอย่าง input

## 7. การทดลองแบบควบคุม

เปลี่ยนตัวแปรทีละอย่าง เช่น chunk size 400 เทียบ 600 โดยใช้คำถามชุดเดียวกัน, embedding model เดียวกัน และ metric เดียวกัน บันทึก config ทุกครั้ง ห้ามสรุปจากคำถามตัวอย่างเพียงข้อเดียว

## 8. Human feedback loop

ให้ผู้ใช้ระบุว่าคำตอบผิดตรงไหนและแหล่งใดควรใช้ ตรวจ feedback ก่อนนำไปแก้ knowledge base เพราะ feedback ก็อาจผิดได้ บันทึกสถานะ accepted/rejected และเหตุผลก่อนแก้เอกสาร

## แหล่งอ้างอิง

- scikit-learn model evaluation: https://scikit-learn.org/stable/modules/model_evaluation.html
- Chroma docs: https://docs.trychroma.com/
- Python logging: https://docs.python.org/3/library/logging.html
