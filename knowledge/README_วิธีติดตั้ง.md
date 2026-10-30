# Local AI — Deep Knowledge Add-on Pack

ชุดนี้มีเอกสาร Markdown ภาษาไทยเชิงลึก 16 ไฟล์ สำหรับต่อยอดฐานความรู้ Local AI เดิม โดยเน้น Programming, Data Quality, ML evaluation, Math, LLM prompting, RAG/ChromaDB, Ollama, Gradio, ESP32, MQTT, debugging, SQL, defensive cybersecurity, Computer Vision และการตรวจสอบโครงงาน AI/Automation

## ไฟล์ในชุดนี้

- `11_Advanced_Python_Engineering.md`
- `12_Data_Engineering_and_Data_Quality.md`
- `13_ML_Evaluation_and_Data_Leakage.md`
- `14_Math_Foundations_for_ML.md`
- `15_LLM_Prompt_Engineering_and_Structured_Output.md`
- `16_RAG_Chroma_Retrieval_Engineering.md`
- `17_Ollama_Local_Model_Operations.md`
- `18_Gradio_Chat_App_Engineering.md`
- `19_ESP32_Sensors_Calibration_and_Signal_Processing.md`
- `20_MQTT_Reliable_IoT_Architecture.md`
- `21_AI_Debugging_Observability_and_Regression.md`
- `22_SQL_Data_Modeling_and_Query_Performance.md`
- `23_Defensive_Cybersecurity_for_Student_Apps.md`
- `24_Computer_Vision_and_Model_Evaluation.md`
- `25_Engineering_AI_Project_Validation.md`
- `26_LocalAI_Accuracy_and_Knowledge_Governance.md`

## วิธีนำไปใช้

1. ปิด Local AI ก่อนแก้ฐานความรู้
2. สำรองโฟลเดอร์ `knowledge/` และ `chroma_db/` ทั้งสองโฟลเดอร์ โดยคัดลอกเป็น backup แยกไว้ ห้ามลบฐานข้อมูลเดิม
3. แตกไฟล์ `.md` ทั้งหมดจากโฟลเดอร์ `knowledge_addon/` ใน ZIP ไปไว้ใน `C:\Users\g\Desktop\LocalAI\knowledge\`
4. ตรวจชื่อไฟล์ว่าซ้ำกับไฟล์เดิมหรือไม่ หากซ้ำให้เปรียบเทียบก่อนเขียนทับ
5. ใช้ขั้นตอน ingest ที่โปรเจกต์เดิมใช้อยู่ เพื่อเพิ่มเอกสารเข้า ChromaDB
6. ตรวจจำนวนเอกสาร/จำนวน chunk และทดสอบ query ตัวอย่างจากแต่ละหัวข้อ

**สำคัญ:** อย่ารันคำสั่ง rebuild หรือสคริปต์ที่ลบ `chroma_db/` จนกว่าจะตรวจโค้ด `add_knowledge.py` และยืนยันว่าเป็นโหมดเพิ่ม/อัปเดตโดยไม่ลบข้อมูลเดิม

## ข้อจำกัดที่ควรรู้

- ไฟล์ใน `knowledge/` ยังไม่ถูกใช้โดย Chat UI จนกว่า `chat()` จะ query ChromaDB และแนบผลค้นกลับเข้า prompt
- การเพิ่มเอกสารผ่าน RAG เพิ่มข้อมูลอ้างอิงที่ค้นได้ แต่ไม่ได้ฝึกหรือเปลี่ยน weights ของ `qwen3:4b`
- ความแม่นยำต้องวัดด้วยชุดคำถามทดสอบ โดยตรวจทั้งผล retrieval และคำตอบสุดท้าย
- เอกสาร API/ซอฟต์แวร์อาจเปลี่ยนตามเวอร์ชัน ให้ตรวจเอกสารทางการและเวอร์ชันที่ติดตั้งก่อนใช้พารามิเตอร์

## แนะนำลำดับพัฒนาต่อ

1. เชื่อม `chat()` เข้ากับ ChromaDB ก่อน
2. แสดงแหล่งที่มาของ chunk ที่ถูกค้นมาในคำตอบ
3. ทำชุดทดสอบ 30–50 คำถาม พร้อมคำตอบ/แหล่งอ้างอิงที่คาดหวัง
4. วัด Retrieval Recall@k และความถูกต้องของคำตอบ
5. ปรับ chunk size, overlap, embedding model และ top-k ทีละค่า

## แหล่งทางการหลัก

- Chroma: https://docs.trychroma.com/
- Ollama API: https://docs.ollama.com/api
- Gradio ChatInterface: https://gradio.app/docs/gradio/chatinterface
- Python documentation: https://docs.python.org/3/
- scikit-learn: https://scikit-learn.org/stable/
- PyTorch: https://docs.pytorch.org/
- Espressif ESP-IDF: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/
- OASIS MQTT 5.0: https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html
- OWASP Top 10:2025: https://top10.owasp.org/2025/
