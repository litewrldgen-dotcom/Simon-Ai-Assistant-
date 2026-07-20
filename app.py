import streamlit as st
import os, json, time, random, re, math, requests
from datetime import datetime
from pathlib import Path
from io import BytesIO

# --- Optional deps ---
try:
    from PyPDF2 import PdfReader
except:
    PdfReader = None
try:
    from PIL import Image
except:
    Image = None
try:
    from groq import Groq
except:
    Groq = None
try:
    from gtts import gTTS
except:
    gTTS = None

# ========= PAGE CONFIG =========
st.set_page_config(page_title="Simon AI v1.1.0", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ========= LITE WRLD GEN BRAND INFO =========
BRAND_INFO = """
🔥 LITE WRLD GEN - COMPANY PROFILE 🔥

CEO: Woob
Base: Harare, Zimbabwe 🇿🇼
Founded: 2026
Tagline: "Building Africa's AI Future"

ABOUT:
Lite Wrld Gen builds AI tools that work on mobile, with bad internet, for real people.
Mission: Put Zimbabwe + Africa on the AI map.
"""

# ========= SIMON'S 10 RULES =========
SIMON_RULES = """
⚡ SIMON'S 10 RULES ⚡
1. Always rep Lite Wrld Gen first 🔥
2. Be friendly, confident, and helpful 🤝
3. Use high slang but not too much: say less, bet, fr, no cap, cook, locked in 😎
4. Use HIGH EMOJIS: 🔥⚡💯🚀😎💚🫡✨🧠💪 but keep it readable
5. If files/images are uploaded, USE THAT CONTEXT to answer 📄
6. Be fast, concise, and mobile-first 📱
7. If you don't know something, say it straight no cap 💯
8. Summarize, code, debug, translate, generate images on command instantly ⚡
9. Remember user preferences and last topics 🧠
10. Groq for chat. HuggingFace for image gen + vision 🚀
"""

# ========= SIMON PERSONALITY =========
SIMON_PERSONALITY = """
You are SIMON AI v1.1.0 ⚡ Built by Lite Wrld Gen.

VIBE: You're the homie. High energy, premium, confident. Like ChatGPT + Claude but faster and cooler.
TALK LIKE: "Bet", "Say less", "We locked in", "Let's cook", "No cap fr"
EMOJIS: Use them heavy 🔥⚡💚🚀 but don't spam every line.
GOAL: Help the user build fast, answer smart, and keep it real.
"""

# ========= THEME CSS =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background:#09090b; }
.block-container { padding-top: 1rem; padding-bottom: 120px; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] { background: #111113; border-right: 1px solid rgba(255,255,255,0.06); }
.glass-header { text-align:center; padding: 18px 10px 6px 10px; background: radial-gradient(600px circle at 50% -20%, rgba(0,255,153,0.18), transparent 60%), #09090b; border-radius: 18px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.06); }
.header-title { font-size: 54px; font-weight: 900; letter-spacing: -2px; color: #00ff99; text-shadow: 0 0 20px rgba(0,255,153,0.4); margin:0; }
.header-sub { color: #9ca3af; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
.stChatMessage { border-radius: 18px!important; padding: 14px 16px!important; backdrop-filter: blur(18px)!important; border: 1px solid rgba(255,255,255,0.07)!important; background: rgba(24,24,27,0.8)!important; margin-bottom: 10px; }
[data-testid="stChatMessageAvatarUser"] { background:#00ff99!important; }
[data-testid="stChatMessageAvatarAssistant"] { background:#18181b!important; border:1px solid rgba(0,255,153,0.3); }
div[data-testid="stChatInput"] { background: rgba(24,24,27,0.95)!important; border-radius: 24px!important; border: 1px solid rgba(255,255,255,0.1)!important; backdrop-filter: blur(12px); }
.stat-card { background: #18181b; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 12px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ========= MEMORY =========
MEMORY_PATH = Path("memory/memory.json")
DEFAULT_MEMORY = {"name": "Friend", "company": "Lite Wrld Gen", "last_topics": [], "created": datetime.now().isoformat()}
def load_memory():
    if MEMORY_PATH.exists():
        try: return json.loads(MEMORY_PATH.read_text())
        except: return DEFAULT_MEMORY.copy()
    return DEFAULT_MEMORY.copy()
def save_memory(mem):
    MEMORY_PATH.parent.mkdir(exist_ok=True, parents=True)
    MEMORY_PATH.write_text(json.dumps(mem, indent=2))

# ========= CLIENTS =========
@st.cache_resource
def load_clients():
    groq_key = st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else os.getenv("GROQ_API_KEY")
    hf_key = st.secrets.get("HF_API_KEY") if "HF_API_KEY" in st.secrets else os.getenv("HF_API_KEY")
    groq_client = Groq(api_key=groq_key) if groq_key and Groq else None
    hf_headers = {"Authorization": f"Bearer {hf_key}"} if hf_key else None
    return groq_client, hf_headers
groq_client, hf_headers = load_clients()

# ========= STATE =========
if "messages" not in st.session_state: st.session_state.messages = []
if "memory" not in st.session_state: st.session_state.memory = load_memory()
if "files_context" not in st.session_state: st.session_state.files_context = ""
if "last_image_bytes" not in st.session_state: st.session_state.last_image_bytes = None

# ========= HELPERS =========
STARTERS = ["Got you 🔥", "Say less 😎", "Let's cook ⚡", "Awe 🤝", "Roger that 🚀", "Bet 💚"]
COMMANDS = {
    "/help": "Show all commands 📖", "/rules": "Show Simon's 10 Rules ⚡", "/brand": "Show Lite Wrld Gen info 🔥",
    "/name": "Set your name 💾", "/summarize": "Summarize file or chat 📝", "/memory": "Show memory 💾",
    "/reset": "Clear chat 🔄", "/time": "Current time ⏰", "/calc": "Calculate 🧮",
    "/img": "Generate image: /img a cyberpunk city", "/describe": "Describe last uploaded image 📸"
}
def random_starter(): return random.choice(STARTERS)

def extract_file_text(uploaded):
    text = ""; name = uploaded.name.lower()
    try:
        if name.endswith(".pdf") and PdfReader:
            reader = PdfReader(uploaded)
            for p in reader.pages:
                t = p.extract_text()
                if t: text += t + "\n"
            st.success(f"📄 Read {len(reader.pages)} pages")
        elif name.endswith(".txt"): text = uploaded.read().decode(errors="ignore"); uploaded.seek(0)
        elif name.endswith(("png","jpg","jpeg")):
            st.session_state.last_image_bytes = uploaded.getvalue()
            text = f"[Image uploaded: {uploaded.name}]"
        else: text = f"[File: {uploaded.name}]"
    except Exception as e: text = f"[Error: {e}]"
    return text[:8000]

def time_tool(): return datetime.now().strftime("%A, %d %B %Y - %H:%M:%S")
def calc_tool(expr):
    try: return str(eval(expr, {"__builtins__": None}, {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}))
    except: return "Error bro"

def call_groq(messages):
    if not groq_client: return None, "Add GROQ_API_KEY in Secrets bro 🔑"
    try:
        stream = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages, stream=True, temperature=0.7, max_tokens=1500)
        full = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
        return full, None
    except Exception as e: return None, str(e)

def call_hf_image_gen(prompt):
    if not hf_headers: return None, "Add HF_API_KEY in Secrets bro 🔑"
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    try:
        res = requests.post(API_URL, headers=hf_headers, json={"inputs": prompt}, timeout=180)
        res.raise_for_status()
        image = Image.open(BytesIO(res.content))
        return image, None
    except Exception as e: return None, str(e)

def call_hf_vision(image_bytes, prompt):
    if not hf_headers: return None, "Add HF_API_KEY in Secrets bro 🔑"
    API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-VL-72B-Instruct"
    files = {"file": image_bytes}
    data = {"inputs": prompt}
    try:
        res = requests.post(API_URL, headers=hf_headers, files=files, data=data, timeout=120)
        res.raise_for_status()
        return res.json()[0]["generated_text"], None
    except Exception as e: return None, str(e)

# ========= SIDEBAR =========
with st.sidebar:
    st.markdown("### 🧠 Simon v1.1.0"); st.caption("Groq Chat + HF Vision ⚡"); st.divider()
    if st.button("💬 New Chat", use_container_width=True):
        st.session_state.messages = []; st.session_state.files_context = ""; st.session_state.last_image_bytes = None; st.rerun()
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="stat-card">⚡<br><b>{len(st.session_state.messages)}</b><br><span style="color:#999;font-size:12px">Msgs</span></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card">🧠<br><b>{st.session_state.memory["name"]}</b><br><span style="color:#999;font-size:12px">User</span></div>', unsafe_allow_html=True)
    st.divider()
    st.code("llama-3.3-70b-versatile ⚡ (Groq)", language="text")
    if not groq_client: st.error("Missing GROQ_API_KEY 🔑")
    if not hf_headers: st.warning("Missing HF_API_KEY 🔑")

# ========= HEADER =========
st.markdown("""<div class="glass-header"><h1 class="header-title">⚡ SIMON AI v1.1.0</h1><p class="header-sub">Powered by Lite Wrld Gen + Groq + HF</p></div>""", unsafe_allow_html=True)

# ========= CHAT DISPLAY =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# ========= INPUT =========
col1, col2 = st.columns([6,1])
with col1: prompt = st.chat_input("Ask Simon anything... or /img to generate 💬⚡")
with col2:
    uploaded = st.file_uploader("📁", type=["pdf","txt","png","jpg","jpeg"], label_visibility="collapsed")
    if uploaded:
        txt = extract_file_text(uploaded)
        st.session_state.files_context += f"\n\n--- FILE: {uploaded.name} ---\n{txt}"
        if st.session_state.last_image_bytes: st.image(uploaded, caption=uploaded.name, use_container_width=True)
        st.success(f"Loaded {uploaded.name} ✅")

# ========= LOGIC =========
if prompt:
    if "my name is" in prompt.lower():
        st.session_state.memory["name"] = prompt.lower().split("my name is")[-1].strip().title()
        save_memory(st.session_state.memory)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    lower = prompt.lower(); reply_text = ""
    if lower.startswith("/"):
        if "/help" in lower: reply_text = "📖 **Commands** ⚡\n" + "\n".join([f"`{k}` - {v}" for k,v in COMMANDS.items()])
        elif "/rules" in lower: reply_text = SIMON_RULES
        elif "/brand" in lower: reply_text = BRAND_INFO
        elif "/name" in lower:
            name = prompt[5:].strip().title(); st.session_state.memory["name"]=name; save_memory(st.session_state.memory)
            reply_text = f"{random_starter()} Bet 💚 Got you **{name}** 🫡"
        elif "/time" in lower: reply_text = f"{random_starter()} ⏰ It's **{time_tool()}**"
        elif "/calc" in lower: reply_text = f"{random_starter()} 🧮 `{prompt[6:]}` = **{calc_tool(prompt[6:])}** ✅"
        elif "/memory" in lower: reply_text = f"💾 **Memory**\n```json\n{json.dumps(st.session_state.memory, indent=2)}\n```"
        elif "/reset" in lower: st.session_state.messages=[]; st.session_state.memory=DEFAULT_MEMORY.copy(); save_memory(st.session_state.memory); reply_text="Wiped clean 🧹 Fresh start ⚡"
        elif "/img" in lower:
            img_prompt = prompt[4:].strip()
            with st.chat_message("assistant"):
                placeholder = st.empty(); placeholder.markdown("Simon ⚡ generating image... ▌")
                img, err = call_hf_image_gen(img_prompt)
                if err: reply_text = f"Error: {err}"
                else: st.image(img, caption=img_prompt); reply_text = f"{random_starter()} Here we go 🚀 **{img_prompt}**"
                placeholder.markdown(reply_text)
        elif "/describe" in lower:
            if st.session_state.last_image_bytes:
                with st.chat_message("assistant"):
                    placeholder = st.empty(); placeholder.markdown("Simon ⚡ analyzing image... ▌")
                    desc, err = call_hf_vision(st.session_state.last_image_bytes, prompt)
                    reply_text = desc if not err else f"Error: {err}"
                    placeholder.markdown(reply_text)
            else: reply_text = "Upload an image first bro 📸"

    if not reply_text and not lower.startswith("/img") and not lower.startswith("/describe"):
        sys_prompt = f"{SIMON_PERSONALITY}\n\n{SIMON_RULES}\n\n{BRAND_INFO}\n\nUSER: {st.session_state.memory['name']}\nFILE CONTEXT: {st.session_state.files_context}\nTIME: {time_tool()}"
        messages = [{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:]

        with st.chat_message("assistant"):
            placeholder = st.empty(); placeholder.markdown("Simon ⚡ thinking... ▌")
            reply_text, err = call_groq(messages)
            if err: reply_text = f"Aye 😅 {err}"
            placeholder.markdown(reply_text)

    if reply_text:
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        st.session_state.memory["last_topics"].append(prompt[:50])
        st.session_state.memory["last_topics"] = st.session_state.memory["last_topics"][-5:]
        save_memory(st.session_state.memory)
        st.rerun()