import time
import ollama

CHAT_MODEL = "qwen3.5:4b"
EMBED_MODEL = "bge-m3"
NUM_CTX = 8192   # ต้องตรงกับ NUM_CTX ใน app.py ไม่งั้น Ollama จะโหลดโมเดลใหม่


def test(label, function):
    start = time.perf_counter()
    try:
        result = function()
        elapsed = time.perf_counter() - start
        print(f"\n{label}: {elapsed:.2f} วินาที")
        return result
    except Exception as exc:
        print(f"\n{label} ERROR: {type(exc).__name__}: {exc}")
        return None


def chat_once(think):
    return ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": "อธิบาย Python สั้น ๆ"}],
        stream=False,
        think=think,
        keep_alive="10m",
        options={"num_predict": 200, "num_ctx": NUM_CTX},
    )


# ครั้งแรกรวมเวลาโหลดโมเดลเข้าหน่วยความจำ ครั้งถัดไปคือความเร็วจริง
test("Chat ครั้งที่ 1 (รวมโหลดโมเดล)", lambda: chat_once(False))
test("Chat ครั้งที่ 2 (ไม่คิด)", lambda: chat_once(False))
test("Chat ครั้งที่ 3 (คิดลึก)", lambda: chat_once(True))

test(
    "Embedding bge-m3",
    lambda: ollama.embed(
        model=EMBED_MODEL,
        input=["ทดสอบการสร้าง embedding ภาษาไทย"] * 8,
    ),
)

test("อ่านรายชื่อโมเดล Ollama", ollama.list)
