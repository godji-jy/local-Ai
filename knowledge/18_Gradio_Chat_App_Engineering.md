# Gradio Chat App Engineering: รูปแบบ API, State และการแก้ปัญหาเวอร์ชัน

**หมวด:** Python / Web UI / Gradio  
**คำค้น:** Gradio, ChatInterface, Blocks, history, additional_inputs, examples, queue, launch, version compatibility

## 1. ChatInterface function contract

`gr.ChatInterface` เป็น UI ระดับสูงสำหรับ chatbot โดย function หลักรับ `message` และ `history`; หากกำหนด `additional_inputs` ค่าของ component เหล่านั้นจะถูกส่งเป็น argument ต่อจาก history ตามลำดับ

ตัวอย่างเมื่อมี dropdown ภาษาเพียงหนึ่งตัว:

```python
def chat(message, history, language):
    return f"Language={language}; question={message}"

with gr.Blocks() as demo:
    language = gr.Dropdown(["Thai", "English"], value="Thai")
    gr.ChatInterface(
        fn=chat,
        additional_inputs=[language],
        examples=[
            ["AI คืออะไร", "Thai"],
            ["What is AI?", "English"],
        ],
    )
```

เมื่อมี `additional_inputs` ตัวอย่างต้องเป็น list of lists โดยลำดับค่าตรงกับ input เพิ่มเติม ตัวอย่างหนึ่งรายการจึงมี `[ข้อความ, ภาษา]` ไม่ใช่ข้อความอย่างเดียว

## 2. ประวัติแชต

เอกสาร Gradio รุ่นปัจจุบันอธิบาย history เป็น list ของ OpenAI-style dictionaries เช่น `{"role":"user","content":"..."}` และ `{"role":"assistant","content":"..."}` แต่เวอร์ชันเก่าบางรุ่นใช้รูปแบบต่างกัน ต้องตรวจเวอร์ชันจริงและ function contract ของรุ่นนั้น

ตรวจเวอร์ชัน:

```powershell
python -c "import gradio as gr; print(gr.__version__)"
```

อย่าคิดว่า `ChatInterface` มี attribute `header` หรือ `examples_handler` เสมอไป หากสร้าง `header = gr.HTML(...)` แยกไว้ ให้ใช้ตัวแปร `header` โดยตรง

## 3. อย่าผูก event ซ้ำ

`ChatInterface` จัดการการส่งข้อความให้แล้ว หากเพิ่ม `.click()` หรือ `.submit()` อีกชุดเพื่อเรียก function เดียวกัน อาจทำให้ callback ถูกเรียกด้วยจำนวน argument ไม่ตรง หรือเกิดการส่งซ้ำ

เมื่อต้องปรับ UI event ให้กำหนด component input/output ให้ตรง และตรวจทุก callback ว่าจำนวน argument ตรงกับ function signature

## 4. Theme และ CSS

เมื่อมี warning ว่า `theme` และ `css` ย้ายจาก `Blocks()` ไป `launch()` ให้ทำตาม API version ที่ติดตั้ง เช่น:

```python
with gr.Blocks(title="Local AI") as demo:
    ...

demo.launch(theme=THEME, css=CSS)
```

ใช้เอกสารของ major version ที่ติดตั้งจริง ไม่ผสมตัวอย่างจาก Gradio 4, 5 และ 6 โดยไม่ตรวจสอบ

## 5. Error checklist

- `unexpected keyword argument`: พารามิเตอร์ไม่อยู่ใน signature ของ version นั้น
- `Expected N arguments`: function inputs ที่ Gradio ผูกไว้ไม่ตรงกับ function signature
- `Examples must be a list of lists`: มี additional inputs แต่ examples ไม่ได้แนบค่าครบ
- `AttributeError`: อ้าง attribute ที่ component ไม่มี
- `TypeError` กับ Chatbot: ตรวจ constructor params ของ Gradio version

## 6. วิธีแก้ให้เป็นระบบ

1. เก็บ traceback ทั้งหมด
2. ตรวจ `gr.__version__`
3. เปิด signature ด้วย `help(gr.ChatInterface)` หรือ `inspect.signature(gr.ChatInterface)`
4. แก้เพียงจุดที่ API ไม่ตรง
5. รัน minimal app ที่มี ChatInterface อย่างเดียวก่อน
6. ค่อยเพิ่ม theme, language dropdown, examples และ Ollama ทีละส่วน

## 7. State และภาษา

ค่าภาษาควรส่งเข้า callback เป็น additional input โดยตรง อย่าอาศัย global mutable state ที่ผู้ใช้หลาย session ใช้ร่วมกัน หากต้องเก็บค่าระหว่าง event ให้เลือก state ตามรูปแบบที่ Gradio รุ่นนั้นรองรับ

## แหล่งอ้างอิง

- Gradio ChatInterface API: https://gradio.app/docs/gradio/chatinterface
- Creating a chatbot fast: https://gradio.app/guides/creating-a-chatbot-fast
- Gradio Guides: https://gradio.app/guides/
