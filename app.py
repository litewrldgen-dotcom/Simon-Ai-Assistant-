import streamlit as st
import os, json, time, random, math
from datetime import datetime
from pathlib import Path
import requests
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

# ========= PAGE CONFIG =========
st.set_page_config(page_title="Simon AI v1.2.0", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ========= LITE WRLD GEN BRAND INFO =========
BRAND_INFO = """
🔥 LITE WRLD GEN 🔥

Building AI tools for EVERYONE 🌍
Mission: "AI that works on any phone, with any internet"

Simon AI v1.2.0 - Fast, Free, For The World
"""

# ========= SIMON'S 10 RULES =========
SIMON_RULES = """
⚡ SIMON'S 10 RULES ⚡
1. Rep Lite Wrld Gen first 🔥
2. Be friendly, helpful, for EVERYONE 🌍
3. Use slang but keep it clean: bet, say less, no cap, locked in 😎
4. Use EMOJIS: 🔥⚡💯🚀😎💚 but keep it readable
5. If files/images uploaded, USE THAT CONTEXT 📄
6. Be FAST and MOBILE-FIRST 📱
7. If you don't know, say it straight no cap 💯
8. Code, summarize, translate, generate images instantly ⚡
9. Remember user name + last topics 🧠
10. Groq for chat. HuggingFace for images. Speed only 🚀
"""

# ========= SIMON PERSONALITY =========
SIMON_PERSONALITY = """
You are SIMON AI v1.2.0 ⚡ Built by Lite Wrld Gen for the WORLD.

VIBE: The homie. High energy, smart, confident.
TALK LIKE: "Bet", "Say less", "We locked in", "Let's cook", "No cap fr"
EMOJIS: Use them 🔥⚡💚 but don't spam.
GOAL: Help anyone, anywhere. Keep it fast.
Address the user by their name if known, else call them "Friend".
"""

# ========= THEME CSS =========
st.markdown("""
<style>
.main { background:#09090b; }
.glass-header { text-align:center; padding: 18px; background: radial-gradient(600px circle at 50% -20%, rgba(0,255,153,0.18), transparent 60%), #09090b; border-radius: 18px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.06); }
.header-title { font-size: 48px; font-weight: 900; color: #00ff99; margin:0; }
.header-sub { color: #9ca3af; font-size: 13px; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

# ========= MEMORY =========
MEMORY_PATH = Path("memory/memory.json")
DEFAULT_MEMORY = {"name": "Friend", "last_topics": []} # DEFAULT = FRIEND
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
    groq_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    hf_key = st.secrets.get("HF_API_KEY") or os.getenv("HF_API_KEY")
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
STARTERS = ["Got you 🔥", "Say less 😎", "Let's cook ⚡", "We locked in 🚀"]
COMMANDS = {"/help":"Commands 📖","/rules":"10 Rules ⚡","/brand":"About 🔥","/name":"Set name 💾","/img":"Generate image","/describe":"Describe image","/reset":"Clear chat"}

def extract_file_text(uploaded):
    text = ""; name = uploaded.name.lower()
    try:
        if name.endswith(".pdf") and PdfReader:
            reader = PdfReader(uploaded)
            for p in reader.pages:
                t = p.extract_text()
                if t: text += t + "\n"
        elif name.endswith(("png","jpg","jpeg")):
            st.session_state.last_image_bytes = uploaded.getvalue()
            text = f"[Image: {uploaded.name}]"
        else: text = uploaded.read().decode(errors="ignore")[:4000]; uploaded.seek(0)
    except Exception as e: text = f"[Error: {e}]"
    return text[:6000]

def call_groq(messages):
    if not groq_client: return None, "Add GROQ_API_KEY in Secrets 🔑"
    try:
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages, temperature=0.7, max_tokens=1200)
        return res.choices[0].message.content, None
    except Exception as e: return None, str(e)

def call_hf_image_gen(prompt):
    if not hf_headers: return None, "Add HF_API_KEY in Secrets 🔑"
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    try:
        res = requests.post(API_URL, headers=hf_headers, json={"inputs": prompt}, timeout=180)
        image = Image.open(BytesIO(res.content))
        return image, None
    except Exception as e: return None, str(e)

# ========= SIDEBAR =========
with st.sidebar:
    st.markdown("### 🧠 Simon v1.2.0")
    st.caption("For the World 🌍")
    if st.button("💬 New Chat"):
        st.session_state.messages = []; st.session_state.files_context = ""; st.rerun()
    st.write(f"**User:** {st.session_state.memory['name']}")
    st.code("llama-3.3-70b-versatile ⚡", language="text")
    if not groq_client: st.error("Missing GROQ_API_KEY")

# ========= HEADER =========
st.markdown('<div class="glass-header"><h1 class="header-title">⚡ SIMON AI</h1><p class="header-sub">AI FOR EVERYONE</p></div>', unsafe_allow_html=True)

# ========= CHAT =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

uploaded = st.file_uploader("📁 Upload PDF or Image", type=["pdf","png","jpg","jpeg"])
if uploaded:
    txt = extract_file_text(uploaded)
    st.session_state.files_context += f"\n---{uploaded.name}---\n{txt}"
    st.success(f"Loaded {uploaded.name} ✅")

prompt = st.chat_input("Ask Simon anything...")

# ========= LOGIC =========
if prompt:
    if "my name is" in prompt.lower():
        st.session_state.memory["name"] = prompt.lower().split("my name is")[-1].strip().title()
        save_memory(st.session_state.memory)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    reply_text = ""
    if prompt.startswith("/"):
        if "/help" in prompt: reply_text = "📖 " + str(COMMANDS)
        elif "/rules" in prompt: reply_text = SIMON_RULES
        elif "/brand" in prompt: reply_text = BRAND_INFO
        elif "/name" in prompt:
            name = prompt[5:].strip().title(); st.session_state.memory["name"]=name; save_memory(st.session_state.memory)
            reply_text = f"{random.choice(STARTERS)} Bet 💚 Got you **{name}** 🫡"
        elif "/img" in prompt:
            with st.chat_message("assistant"):
                img, err = call_hf_image_gen(prompt[4:])
                reply_text = "Error" if err else "Here you go 🚀"
                if img: st.image(img)
        elif "/describe" in prompt and st.session_state.last_image_bytes:
            reply_text = "Vision coming soon bro, HF endpoint needs upgrade 😅"
        elif "/reset" in prompt:
            st.session_state.messages=[]; st.session_state.memory=DEFAULT_MEMORY.copy(); save_memory(st.session_state.memory); reply_text="Wiped clean 🧹"
    
    if not reply_text:
        sys = f"{SIMON_PERSONALITY}\n{RULES}\n{BRAND_INFO}\nUSER: {st.session_state.memory['name']}\nCONTEXT: {st.session_state.files_context}"
        msgs = [{"role":"system","content":sys}] + st.session_state.messages[-8:]
        reply_text, err = call_groq(msgs)
        if err: reply_text = f"Aye 😅 {err}"

    with st.chat_message("assistant"): st.markdown(reply_text)
    st.session_state.messages.append({"role": "assistant", "content": reply_text})
    st.rerun()