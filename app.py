import streamlit as st
import os, json, time, random, re, math
from datetime import datetime
from pathlib import Path
import base64
import requests

# --- Optional deps, safe fallbacks ---
try:
    from PyPDF2 import PdfReader
except:
    PdfReader = None
try:
    from PIL import Image
except:
    Image = None
try:
    from gtts import gTTS
except:
    gTTS = None

# ========= PAGE CONFIG =========
st.set_page_config(page_title="Simon AI 4.0", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ========= LITE WRLD GEN BRAND INFO =========
BRAND_INFO = """
🔥 LITE WRLD GEN - COMPANY PROFILE 🔥

CEO: Woob
Base: Harare, Zimbabwe 🇿🇼
Founded: 2026
Tagline: "Building Africa's AI Future"

ABOUT:
Lite Wrld Gen is an AI + Media + Tech company from Zimbabwe.
We build AI tools that work on mobile, with bad internet, for real people.
Mission: Put Zimbabwe + Africa on the AI map.

PRODUCTS:
1. SIMON AI - Voice, Vision, Memory, File Reader Assistant v4.0.3
   Running on: Qwen2.5-72B-Instruct + Streamlit Cloud + HF API
2. LITE WRLD STUDIOS - AI content, music, videos, ads
3. LITE WRLD LABS - Custom AI tools for businesses
4. LITE WRLD CLOUD - AI app hosting + deployment

FOUNDER:
Woob - CEO & Lead AI Engineer
"""

# ========= SIMON'S 10 RULES =========
SIMON_RULES = """
⚡ SIMON'S 10 RULES ⚡
1. Always rep Lite Wrld Gen first 🔥
2. Be friendly, confident, and helpful 🤝
3. Use high slang but not too much: say less, bet, fr, no cap, cook, locked in 😎
4. Use HIGH EMOJIS: 🔥⚡💯🚀😎💚🫡✨🧠💪 but keep it readable
5. If files are uploaded, USE THAT CONTEXT to answer 📄
6. Be fast, concise, and mobile-first 📱
7. If you don't know something, say it straight no cap 💯
8. Summarize, code, debug, translate on command instantly ⚡
9. Remember user preferences and last topics 🧠
10. Never mention Groq. We run on HuggingFace Qwen2.5-72B only 🚀
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
.stButton>button { border-radius: 14px!important; height: 48px; font-weight: 700!important; background: #18181b!important; color: #fff!important; border: 1px solid rgba(255,255,255,0.08)!important; }
.stat-card { background: #18181b; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 12px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ========= MEMORY =========
MEMORY_PATH = Path("memory/memory.json")
DEFAULT_MEMORY = {
    "name": "Friend", # DEFAULT NAME CHANGED
    "company": "Lite Wrld Gen",
    "role": "User",
    "last_topics": [],
    "preferences": ["Fast responses", "Mobile-first", "High energy"],
    "created": datetime.now().isoformat()
}
def load_memory():
    if MEMORY_PATH.exists():
        try: return json.loads(MEMORY_PATH.read_text())
        except: return DEFAULT_MEMORY.copy()
    return DEFAULT_MEMORY.copy()
def save_memory(mem):
    MEMORY_PATH.parent.mkdir(exist_ok=True, parents=True)
    MEMORY_PATH.write_text(json.dumps(mem, indent=2))

# ========= HUGGINGFACE CLIENT =========
@st.cache_resource
def get_hf_headers():
    api_key = st.secrets.get("HF_API_KEY") if "HF_API_KEY" in st.secrets else os.getenv("HF_API_KEY")
    if not api_key: return None
    return {"Authorization": f"Bearer {api_key}"}
HF_HEADERS = get_hf_headers()
HF_MODEL = "Qwen/Qwen2.5-72B-Instruct"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# ========= STATE =========
if "messages" not in st.session_state: st.session_state.messages = []
if "memory" not in st.session_state: st.session_state.memory = load_memory()
if "files_context" not in st.session_state: st.session_state.files_context = ""
if "uploaded_files_list" not in st.session_state: st.session_state.uploaded_files_list = []

# ========= HELPERS =========
STARTERS = ["Got you 🔥", "Say less 😎", "Let's cook ⚡", "Awe 🤝", "Roger that 🚀", "I'm on it 💯", "Bet 💚", "We locked in ⚡"]
COMMANDS = {
    "/help": "Show all commands 📖",
    "/rules": "Show Simon's 10 Rules ⚡",
    "/brand": "Show Lite Wrld Gen info 🔥",
    "/name": "Set your name 💾",
    "/summarize": "Summarize file or chat 📝",
    "/memory": "Show what I remember 💾",
    "/reset": "Clear chat + reset 🔄",
    "/time": "Current time ⏰",
    "/calc": "Calculate 🧮",
    "/code": "Generate clean code 💻",
    "/explain": "Explain anything 🧠"
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
            st.success(f"📄 Read {len(reader.pages)} pages from {uploaded.name}")
        elif name.endswith(".txt"): text = uploaded.read().decode(errors="ignore"); uploaded.seek(0)
        elif name.endswith((".png",".jpg",".jpeg",".webp")) and Image: text = f"[Image uploaded: {uploaded.name} - Please describe and analyze this image]"
        else: text = uploaded.read().decode(errors="ignore")[:8000]; uploaded.seek(0)
    except Exception as e: text = f"[Error reading {uploaded.name}: {e}]"
    return text[:12000]

def calc_tool(expr):
    try: allowed = {"__builtins__": None}; safe_names = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}; safe_names.update({"abs": abs, "round": round}); return str(eval(expr, allowed, safe_names))
    except Exception as e: return f"Error: {e}"
def time_tool(): return datetime.now().strftime("%A, %d %B %Y - %H:%M:%S")

def call_hf_api(messages):
    if not HF_HEADERS: return None, "Add HF_API_KEY in Streamlit Secrets first bro 🔑"
    prompt = ""
    for m in messages: prompt += f"{m['role'].capitalize()}: {m['content']}\n"
    prompt += "Assistant:"
    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json={"inputs": prompt, "parameters": {"max_new_tokens": 1200, "temperature": 0.7}}, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data[0]["generated_text"].split("Assistant:")[-1].strip(), None
    except Exception as e: return None, f"HF Error: {e}"

# ========= SIDEBAR =========
with st.sidebar:
    st.markdown("### 🧠 Simon"); st.caption("Premium AI by Lite Wrld Gen"); st.divider()
    if st.button("💬 New Chat", use_container_width=True):
        if st.session_state.messages:
            chats_dir = Path("chats"); chats_dir.mkdir(exist_ok=True)
            fname = chats_dir / f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"; fname.write_text(json.dumps(st.session_state.messages, indent=2))
        st.session_state.messages = []; st.session_state.files_context = ""; st.session_state.uploaded_files_list = []; st.rerun()
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="stat-card">⚡<br><b>{len(st.session_state.messages)}</b><br><span style="color:#999;font-size:12px">Messages</span></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card">📂<br><b>{len(st.session_state.uploaded_files_list)}</b><br><span style="color:#999;font-size:12px">Files</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-card">🧠 <span style="color:#00ff99">{st.session_state.memory["name"]}</span><br><span style="color:#999;font-size:12px">{st.session_state.memory["company"]}</span></div>', unsafe_allow_html=True)
    st.divider(); st.markdown("**Model**"); st.code("Qwen2.5-72B-Instruct ⚡ (HF)", language="text")
    if not HF_HEADERS: st.warning("Add HF_API_KEY in Secrets to go live 🚀")

# ========= HEADER =========
st.markdown("""<div class="glass-header"><h1 class="header-title">⚡ SIMON AI</h1><p class="header-sub">Powered by Lite Wrld Gen</p></div>""", unsafe_allow_html=True)

# ========= CHAT DISPLAY =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# ========= FILE BANNER =========
if st.session_state.files_context:
    with st.container(border=True):
        st.caption(f"📄 Context loaded: {len(st.session_state.uploaded_files_list)} file(s)")
        if st.button("❌ Clear files"): st.session_state.files_context = ""; st.session_state.uploaded_files_list = []; st.rerun()

# ========= INPUT BAR =========
b1, b2, b3 = st.columns([1.2, 7, 1.2])
with b1:
    with st.popover("📁", use_container_width=True):
        st.markdown("**📤 Upload files**")
        uploaded = st.file_uploader("Drop files", type=["pdf","txt","png","jpg","jpeg","webp"], accept_multiple_files=True, label_visibility="collapsed")
        if uploaded:
            for f in uploaded:
                if f.name not in st.session_state.uploaded_files_list:
                    txt = extract_file_text(f)
                    st.session_state.files_context += f"\n\n--- FILE: {f.name} ---\n{txt}"
                    st.session_state.uploaded_files_list.append(f.name)
                    if f.name.lower().endswith((".png",".jpg",".jpeg",".webp")) and Image:
                        try: st.image(Image.open(f), caption=f.name, use_container_width=True)
                        except: pass
            st.success(f"Loaded {len(uploaded)} file(s) ✅🔥")
with b3:
    with st.popover("🎙️", use_container_width=True):
        st.markdown("**🔊 Voice Reply**")
        if st.session_state.messages and st.session_state.messages[-1]["role"]=="assistant":
            if st.button("🔊 Speak last reply") and gTTS:
                try: tts = gTTS(st.session_state.messages[-1]["content"][:400]); tts.save("/tmp/simon.mp3"); st.audio("/tmp/simon.mp3", autoplay=True)
                except Exception as e: st.error(f"TTS error: {e}")
with b2: prompt = st.chat_input("Ask Simon anything... 💬⚡")

# ========= LOGIC =========
if prompt:
    # AUTO NAME DETECTION
    if "my name is" in prompt.lower():
        new_name = prompt.lower().split("my name is")[-1].strip().title()
        st.session_state.memory["name"] = new_name
        save_memory(st.session_state.memory)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    lower = prompt.strip().lower(); handled = False; reply_text = ""
    if lower.startswith("/"):
        cmd = lower.split()[0]
        if cmd == "/help": reply_text = "📖 **Simon Commands** ⚡\n\n" + "\n".join([f"`{k}` - {v}" for k,v in COMMANDS.items()]); handled = True
        elif cmd == "/rules": reply_text = SIMON_RULES; handled = True
        elif cmd == "/brand": reply_text = BRAND_INFO; handled = True
        elif cmd == "/name":
            new_name = prompt[5:].strip().title()
            if new_name:
                st.session_state.memory["name"] = new_name; save_memory(st.session_state.memory)
                reply_text = f"{random_starter()} Bet 💚 Got you! I'll call you **{new_name}** from now on 🫡⚡"
            else: reply_text = "Say less 😎 What's your name bro? Use `/name YourName`"
            handled = True
        elif cmd == "/time": reply_text = f"{random_starter()} ⏰\n\nIt's **{time_tool()}** rn 💚"; handled = True
        elif cmd == "/calc": arg = prompt[6:].strip(); reply_text = f"{random_starter()} 🧮\n\n`{arg}` = **{calc_tool(arg)}** ✅⚡"; handled = True
        elif cmd == "/memory": reply_text = f"💾 **What I remember** 🧠⚡\n\n```json\n{json.dumps(st.session_state.memory, indent=2)}\n```"; handled = True
        elif cmd == "/reset": st.session_state.messages = []; st.session_state.memory = DEFAULT_MEMORY.copy(); save_memory(st.session_state.memory); reply_text = "Bet, wiped clean 🧹✨ Fresh start, we locked in again 🤝💚⚡"; handled = True
        elif cmd == "/summarize":
            if st.session_state.files_context: arg = f"Summarize this file context: {st.session_state.files_context[:8000]}"
            else: last_chat = "\n".join([m["content"] for m in st.session_state.messages[-10:]]); arg = f"Summarize this conversation: {last_chat}"

    if not handled:
        # ========= SIMON SYSTEM PROMPT =========
        sys_prompt = f"""
You are SIMON AI ⚡, a premium AI assistant built by Lite Wrld Gen.

{BRAND_INFO}

{SIMON_RULES}

USER INFO:
Name: {st.session_state.memory['name']}
Role: {st.session_state.memory['role']}
Company: {st.session_state.memory['company']}

MEMORY:
{json.dumps(st.session_state.memory, indent=2)}

FILE CONTEXT:
{st.session_state.files_context[:10000] if st.session_state.files_context else "No files uploaded yet."}

Current time: {time_tool()}

Address the user as "{st.session_state.memory['name']}" in replies. If name is "Friend", be warm but don't assume.
"""

        messages_for_hf = [{"role": "system", "content": sys_prompt}] + st.session_state.messages[-12:]
        with st.chat_message("assistant"):
            placeholder = st.empty(); placeholder.markdown("Simon ⚡ thinking... ▌")
            if HF_HEADERS:
                reply_text, err = call_hf_api(messages_for_hf)
                if err: reply_text = f"Aye 😅 {err} \n\nCheck your HF_API_KEY in Secrets bro 🔑⚡"; placeholder.markdown(reply_text)
                else:
                    acc = ""
                    for word in reply_text.split(): acc += word + " "; placeholder.markdown(acc + "▌"); time.sleep(0.015)
                    placeholder.markdown(acc)
            else:
                reply_text = f"{random_starter()} I'm Simon AI ⚡🔥 Running in demo mode rn cause no HF key yet 💡\n\nAdd HF_API_KEY in secrets and I'll go full beast mode with Qwen2.5-72B 🚀💚\n\nYou said: **{prompt}**"
                placeholder.markdown(reply_text)

    if reply_text:
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        try:
            st.session_state.memory["last_topics"].append(prompt[:60])
            st.session_state.memory["last_topics"] = st.session_state.memory["last_topics"][-10:]
            save_memory(st.session_state.memory)
        except: pass
        st.rerun()