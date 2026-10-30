"""
แพตช์หน้าตาโปรแกรม Local AI ให้เป็นธีมมืดแบบโคมไฟ (ZAYTA style)
ใช้:  python apply_zayta_theme.py ชื่อไฟล์โปรแกรม.py
- สำรองไฟล์เดิมเป็น .bak
- แก้เฉพาะส่วนหน้าตา (topbar/header/visual, THEME, CSS, เลย์เอาต์หน้าแรก)
"""
import shutil
import sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("ใช้: python apply_zayta_theme.py ชื่อไฟล์โปรแกรม.py")

path = Path(sys.argv[1])
src = path.read_text(encoding="utf-8")

SEC = "# =========================================================\n"

# ---------------------------------------------------------
# 1) topbar / header / visual
# ---------------------------------------------------------
NEW_HTML = '''def make_topbar(language):
    is_en = language == LANG_EN
    model_label = f"{MODEL} · Local" if is_en else f"{MODEL} · รันในเครื่อง"
    home = "Home" if is_en else "หน้าแรก"
    badge = "Private" if is_en else "ส่วนตัว"
    return f"""
    <div id="topbar">
        <div class="brand"><span class="logo">L</span><span>LOCAL AI</span></div>
        <div class="navpill">
            <span class="item active">{home}<i></i></span>
            <span class="item"><span class="dot"></span>{model_label}</span>
        </div>
        <div class="cta">{badge}<span class="arr">↗</span></div>
    </div>
    """


def make_visual():
    """โคมไฟแขวน + ลำแสง (CSS ล้วน)"""
    return """
    <div id="lamp">
        <div class="cord"></div>
        <div class="cone"></div>
        <div class="shade"></div>
        <div class="bulb"></div>
    </div>
    """


def make_header(language):
    t = get_page_text(language)
    return f"""
    <div id="hero">
        {make_visual()}
        <div class="ghost">LOCAL AI</div>
        <div class="eyebrow">{t["eyebrow"]}</div>
        <h1>{t["heading"]}</h1>
        <div class="dash"></div>
        <p>{t["description"]}</p>
    </div>
    """


'''

a = src.index("def make_topbar(language):")
b = src.index(SEC + "# 3.")
src = src[:a] + NEW_HTML + src[b:]

# ---------------------------------------------------------
# 2) THEME + CSS
# ---------------------------------------------------------
NEW_STYLE = '''INK = "#f2f2f2"          # สีตัวอักษรหลัก (ขาว)
PAPER = "#1d1e23"        # พื้นหลัง
CARD = "#25262c"
LINE = "#3a3c44"

THEME = gr.themes.Base(
    primary_hue="neutral",
    neutral_hue="gray",
    radius_size=gr.themes.sizes.radius_xxl,
    font=["Plus Jakarta Sans", "Prompt", "Segoe UI", "sans-serif"],
).set(
    body_background_fill=PAPER,
    body_background_fill_dark=PAPER,
    body_text_color=INK,
    body_text_color_dark=INK,
    block_background_fill="transparent",
    block_background_fill_dark="transparent",
    block_border_width="0px",
    block_label_text_color=INK,
    block_label_text_color_dark=INK,
    block_title_text_color=INK,
    block_title_text_color_dark=INK,
    background_fill_primary=CARD,
    background_fill_primary_dark=CARD,
    background_fill_secondary=PAPER,
    background_fill_secondary_dark=PAPER,
    input_background_fill="#2c2d34",
    input_background_fill_dark="#2c2d34",
    input_border_color=LINE,
    input_border_color_dark=LINE,
    button_primary_background_fill="#f2f2f2",
    button_primary_background_fill_dark="#f2f2f2",
    button_primary_background_fill_hover="#ffffff",
    button_primary_background_fill_hover_dark="#ffffff",
    button_primary_text_color="#111111",
    button_primary_text_color_dark="#111111",
    button_secondary_background_fill="#2c2d34",
    button_secondary_background_fill_dark="#2c2d34",
    button_secondary_text_color=INK,
    button_secondary_text_color_dark=INK,
)


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Prompt:wght@200;300;400;500;600&display=swap');

:root { color-scheme: dark; --ink:#f2f2f2; --line:#3a3c44; --gray:#8b8d96; }

html, body { background: #1d1e23 !important; }

.gradio-container {
    max-width: 1800px !important; width: 100% !important;
    margin: 0 auto !important; padding: 8px 18px 18px !important;
    color: var(--ink) !important;
    background:
        radial-gradient(900px 600px at 50% 18%, #3b3e47 0%, rgba(59,62,71,0) 70%),
        linear-gradient(180deg, #2a2c33 0%, #1b1c20 100%) !important;
    min-height: 100vh;
}
footer { display: none !important; }

* { scrollbar-width: thin; scrollbar-color: #4a4c55 transparent; }
*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-thumb { background: #4a4c55; border-radius: 8px; }
*::-webkit-scrollbar-track { background: transparent; }

/* ---------------- แถบบน ---------------- */
#topbar {
    display: grid; grid-template-columns: 1fr auto 1fr;
    align-items: center; padding: 14px 4px 10px; position: relative; z-index: 5;
}
#topbar .brand {
    display: flex; align-items: center; gap: 12px;
    font-weight: 400; letter-spacing: .3em; font-size: 12px; color: #d8d8d8;
}
#topbar .logo {
    width: 30px; height: 30px; background: transparent; color: #fff;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 300; font-size: 24px; letter-spacing: 0;
}
#topbar .navpill {
    justify-self: center; display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 6px; border-radius: 999px; font-size: 10px; color: #7d7f88;
    letter-spacing: .22em; text-transform: uppercase;
    background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.07);
}
#topbar .navpill .item {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 14px; border-radius: 999px; position: relative;
}
#topbar .navpill .item.active { color: #fff; font-weight: 600; }
#topbar .navpill .item.active i {
    position: absolute; left: 50%; bottom: -4px; width: 4px; height: 4px;
    margin-left: -2px; border-radius: 50%; background: #fff;
}
#topbar .navpill .dot {
    width: 7px; height: 7px; border-radius: 50%; background: #22c55e;
    box-shadow: 0 0 0 3px rgba(34,197,94,.2);
}
#topbar .cta {
    justify-self: end; display: inline-flex; align-items: center; gap: 12px;
    background: transparent; color: #cfcfcf; border: 1px solid rgba(255,255,255,.14);
    border-radius: 999px; padding: 5px 5px 5px 18px; font-size: 10px;
    letter-spacing: .22em; text-transform: uppercase; font-weight: 600;
}
#topbar .cta .arr {
    width: 26px; height: 26px; border-radius: 50%; background: #f2f2f2; color: #111;
    display: inline-flex; align-items: center; justify-content: center; font-size: 12px;
}

/* ---------------- หน้าแรก ---------------- */
#intro { gap: 0 !important; }

#hero {
    position: relative; text-align: center;
    min-height: 440px; padding: 270px 6px 0;
}

/* โคมไฟ */
#lamp {
    position: absolute; left: 50%; top: -60px; width: 340px; height: 330px;
    margin-left: -170px; pointer-events: none;
}
#lamp .cord {
    position: absolute; left: 50%; top: 0; width: 2px; height: 130px;
    margin-left: -1px; background: linear-gradient(180deg, #111, #555);
}
#lamp .shade {
    position: absolute; left: 50%; top: 128px; width: 150px; height: 48px;
    margin-left: -75px;
    background: linear-gradient(180deg, #4a4c54 0%, #17181b 100%);
    clip-path: polygon(34% 0, 66% 0, 100% 100%, 0 100%);
    border-radius: 6px 6px 0 0;
}
#lamp .bulb {
    position: absolute; left: 50%; top: 168px; width: 18px; height: 18px;
    margin-left: -9px; border-radius: 50%; background: #fff; z-index: 2;
    box-shadow: 0 0 18px 6px rgba(255,255,255,.75), 0 0 70px 24px rgba(255,255,255,.28);
    animation: flicker 6s ease-in-out infinite;
}
#lamp .cone {
    position: absolute; left: 50%; top: 172px; width: 330px; height: 250px;
    margin-left: -165px;
    background: linear-gradient(180deg, rgba(255,255,255,.30) 0%, rgba(255,255,255,0) 100%);
    clip-path: polygon(42% 0, 58% 0, 100% 100%, 0 100%);
    filter: blur(6px);
}
@keyframes flicker {
    0%, 100% { opacity: 1; } 48% { opacity: 1; } 50% { opacity: .85; } 52% { opacity: 1; }
}

#hero .ghost {
    position: absolute; left: 0; right: 0; top: 120px; text-align: center;
    font-size: clamp(70px, 13vw, 190px); font-weight: 800; letter-spacing: .22em;
    color: rgba(255,255,255,.05); white-space: nowrap; pointer-events: none;
    padding-left: .22em;
}
#hero .eyebrow {
    position: relative; display: inline-block; font-size: 10px; letter-spacing: .3em;
    color: #8b8d96; margin-bottom: 14px;
}
#hero h1 {
    position: relative; font-weight: 300; font-size: clamp(22px, 2.6vw, 40px);
    line-height: 1.3; letter-spacing: .22em; margin: 0 0 12px; color: #e8e8e8;
}
#hero h1 br { display: none; }
#hero h1 .g { color: #7d7f88; }
#hero .dash { display: none; }
#hero p {
    position: relative; color: #7d7f88; font-size: 12px; letter-spacing: .08em;
    line-height: 1.9; max-width: 460px; margin: 0 auto;
}

#start-btn {
    width: auto !important; flex-grow: 0 !important; align-self: center;
    background: transparent !important; color: #e8e8e8 !important;
    border: 1px solid rgba(255,255,255,.25) !important;
    border-radius: 999px !important; padding: 12px 34px !important;
    font-weight: 500 !important; font-size: 12px !important; letter-spacing: .2em;
    margin: 18px auto 0;
}
#start-btn:hover { background: rgba(255,255,255,.1) !important; }

/* การ์ดด้านล่าง 01. 02. 03. */
#strip {
    background: transparent !important; border: none !important;
    border-radius: 0 !important; padding: 0 !important; gap: 0 !important;
    margin-top: 28px; counter-reset: pc;
}
#strip button.pcard, .pcard {
    counter-increment: pc; position: relative;
    background: rgba(255,255,255,.035) !important;
    border: none !important; border-right: 1px solid rgba(255,255,255,.04) !important;
    border-radius: 0 !important; color: #6f717a !important; box-shadow: none !important;
    padding: 22px 18px 22px 96px !important; min-height: 92px;
    text-align: left !important; white-space: pre-line !important;
    font-size: 11px !important; font-weight: 400 !important; line-height: 1.7 !important;
    transition: background .2s;
}
.pcard::before {
    content: counter(pc, decimal-leading-zero) ".";
    position: absolute; left: 22px; top: 50%; transform: translateY(-50%);
    font-size: 34px; font-weight: 200; color: #8b8d96; letter-spacing: .04em;
}
.pcard::first-line {
    color: #e8e8e8; font-size: 11px; font-weight: 700; letter-spacing: .16em;
}
.pcard:last-child { border-right: none !important; }
.pcard:hover { background: rgba(255,255,255,.08) !important; }

/* ---------------- แชต ---------------- */
#chatbot { height: calc(100vh - 250px) !important; min-height: 320px; }

.gradio-container [class*="chatbot"], .gradio-container .chatbot {
    background: transparent !important; border: none !important;
}
.message.user, [data-testid="user"] {
    background: #f2f2f2 !important; color: #111 !important;
    border-radius: 20px 20px 6px 20px !important;
}
.message.bot, [data-testid="bot"] {
    background: rgba(255,255,255,.06) !important; color: #e8e8e8 !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 20px 20px 20px 6px !important;
    box-shadow: 0 8px 22px rgba(0,0,0,.25);
}
.message.user *, [data-testid="user"] * { color: #111 !important; }
.message.bot *, [data-testid="bot"] * { color: #e8e8e8; }
.message.bot a { color: #9ec5ff !important; }

/* กันกล่องซ้อนกันในฟองแชต */
[data-testid="bot"] [data-testid="bot"],
[data-testid="bot"] .message.bot,
.message.bot .message.bot,
.message.bot [data-testid="bot"],
[data-testid="user"] [data-testid="user"],
[data-testid="user"] .message.user,
.message.user .message.user,
.message.user [data-testid="user"],
.message.bot .prose, .message.bot .md, .message.bot span,
.message.user .prose, .message.user .md, .message.user span {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding-top: 0 !important; padding-bottom: 0 !important;
}
.message.bot span, .message.user span { border-radius: 0 !important; }
.message img.emoji, .message .md img, .message .prose img {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 0 !important;
}
.message.bot pre, .message.bot code { background: rgba(0,0,0,.35) !important; }

/* ปุ่มคัดลอก / แชร์ / ลบ */
.message-buttons, .message-buttons-left, .message-buttons-right,
.message-buttons-bubble, .message-buttons-panel {
    background: transparent !important; border: none !important; box-shadow: none !important;
}
.message-buttons button, .message-buttons .icon-button,
button.icon-button, .copy-button, .message button[aria-label] {
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: #9a9ca5 !important; border-radius: 8px !important; min-width: 0 !important;
}
.message-buttons button:hover, button.icon-button:hover { background: rgba(255,255,255,.1) !important; }
.message-buttons svg, button.icon-button svg, .copy-button svg {
    stroke: currentColor !important; color: #9a9ca5 !important;
}
.icon-button-wrapper {
    border: none !important; background: transparent !important; box-shadow: none !important;
}

/* ---------------- ช่องพิมพ์ ---------------- */
#input-row { align-items: center; gap: 8px; margin-top: 10px; }
#input-row textarea {
    border-radius: 999px !important; padding: 13px 20px !important;
    background: rgba(255,255,255,.07) !important; color: #f2f2f2 !important;
    border: 1px solid rgba(255,255,255,.12) !important;
}
#input-row textarea::placeholder { color: #7d7f88 !important; }
#attach-btn, #send-btn {
    min-width: 48px !important; max-width: 52px; height: 48px;
    border-radius: 50% !important; padding: 0 !important;
}
#send-btn { background: #f2f2f2 !important; color: #111 !important; }
#attach-btn {
    background: rgba(255,255,255,.07) !important;
    border: 1px solid rgba(255,255,255,.12) !important; color: #eee !important;
}

#attach-info { font-size: 12px; color: #aaa; padding: 2px 6px; }
#attach-info p { margin: 0; }
#clear-btn {
    background: rgba(255,255,255,.07) !important;
    border: 1px solid rgba(255,255,255,.12) !important; color: #eee !important;
}

/* ---------------- แผงตั้งค่าด้านขวา ---------------- */
#side-panel {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 24px !important;
    padding: 16px !important; gap: 10px !important;
    align-self: flex-start; box-shadow: 0 10px 30px rgba(0,0,0,.25);
}
#side-panel .side-title { font-weight: 600; font-size: 12px; letter-spacing: .18em; color: #e8e8e8; margin-bottom: 4px; }
#side-panel .block, #side-panel .form, #side-panel fieldset,
#side-panel .wrap, #side-panel .container {
    background: transparent !important; border: none !important; box-shadow: none !important;
}
#side-panel label, #side-panel label span,
#side-panel span[data-testid="block-info"], #side-panel .block-title {
    background: transparent !important; color: #cfcfd4 !important;
}
#side-panel input[type="text"], #side-panel .wrap-inner {
    background: rgba(255,255,255,.07) !important; border: 1px solid rgba(255,255,255,.12) !important;
    color: #f2f2f2 !important; border-radius: 14px !important;
}
#side-panel input[type="checkbox"] {
    background-color: transparent !important; border: 1px solid #7d7f88 !important; accent-color: #f2f2f2;
}
#side-panel input[type="checkbox"]:checked {
    background-color: #f2f2f2 !important; border-color: #f2f2f2 !important;
}
#new-btn {
    background: transparent !important; color: #e8e8e8 !important;
    border: 1px solid rgba(255,255,255,.25) !important;
    border-radius: 999px !important; font-weight: 500 !important; margin-top: 6px;
}
#new-btn:hover { background: rgba(255,255,255,.1) !important; }

@media (max-width: 800px) {
    #topbar { grid-template-columns: 1fr auto; }
    #topbar .navpill { display: none; }
    #hero { min-height: 400px; padding-top: 250px; }
    #strip { flex-wrap: wrap; }
}
"""


'''

a = src.index('INK = "#0d0d0d"')
b = src.index(SEC + "# 7.")
src = src[:a] + NEW_STYLE + src[b:]

# ---------------------------------------------------------
# 3) เลย์เอาต์หน้าแรก: ไม่ใช้คอลัมน์ภาพขวาแล้ว (โคมไฟอยู่ใน header)
# ---------------------------------------------------------
NEW_INTRO = '''with gr.Column(elem_id="intro") as intro:
                header = gr.HTML(make_header(LANG_THAI))
                start_btn = gr.Button(
                    get_page_text(LANG_THAI)["start"],
                    elem_id="start-btn",
                    scale=0,
                )

                with gr.Row(elem_id="strip"):
                    card_btns = [
                        gr.Button(f"{title}\\n{sub}", elem_classes="pcard", min_width=160)
                        for title, sub, _ in POPULAR
                    ]

            '''

a = src.index('with gr.Column(elem_id="intro") as intro:')
b = src.index("# ---------- แชต (แสดงเมื่อเริ่มแชต)")
src = src[:a] + NEW_INTRO + src[b:]

shutil.copy(path, path.with_suffix(path.suffix + ".bak"))
path.write_text(src, encoding="utf-8")
print(f"เสร็จแล้ว: แก้ {path} (สำรองไว้ที่ {path.name}.bak)")
