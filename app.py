import streamlit as st
import os, json, time, random, re, math
from datetime import datetime
from pathlib import Path
import base64
import requests

# --- Optional deps, safe fallbacks ---
try:
    from PyPDF2 import PdfReader # FIXED FOR STREAMLIT CLOUD
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
st.set_page_config(
    page_title="Simon AI 4.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========= LITE WRLD GEN BRAND INFO =========
BRAND_INFO = """
🔥 LITE WRLD GEN - COMPANY PROFILE 🔥

CEO: Sean L Matondo
Base: Harare, Zimbabwe 🇿🇼
Founded: 2026
Tagline: "Building Africa's AI Future"

ABOUT:
Lite Wrld Gen is an AI + Media + Tech company from Zimbabwe.
We build AI tools that work on mobile, with bad internet, for real people.
Mission: Put Zimbabwe + Africa on the AI map.

PRODUCTS:
1. SIMON AI - Voice, Vision, Memory, File Reader Assistant v4.0
   Running on: Qwen2.5-72B-Instruct + Streamlit Cloud + HF API
2. LITE WRLD STUDIOS - AI content, music, videos, ads
3. LITE WRLD LABS - Custom AI tools for businesses
4. LITE WRLD CLOUD - AI app hosting + deployment

BRAND VIBE:
Fast. Clean. No fluff. Build in public.
Colors: Black + Neon Green + Gold

FOUNDER:
Sean L Matondo - CEO & Lead AI Engineer
Specialties: HF APIs, Streamlit, Python, AI Agents, Mobile-First
"""

# ========= THEME CSS - Glassmorphism Premium =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background:#09090b; }
.block-container { padding-top: 1rem; padding-bottom: 120px; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] { background: #111113; border-right: 1px solid rgba(255,255,255,0.06); }
.glass-header {
    text-align:center; padding: 18px 10px 6px 10px;
    background: radial-gradient(600px circle at 50% -20%, rgba(0,255,153,0.18), transparent 60%), #09090b;
    border-radius: 18px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.06);
}
.header-title { font-size: 54px; font-weight: 900; letter-spacing: -2px; color: #00ff99; text-shadow: 0 0 20px rgba(0,255,153,0.4); margin:0; }
.header-sub { color: #9ca3af; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
.stChatMessage { border-radius: 18px!important; padding: 14px 16px!important; backdrop-filter: blur(18px)!important; border: 1px solid rgba(255,255,255,0.07)!important; background: rgba(24,24,27,0.8)!important; margin-bottom: 10px; }
[data-testid="stChatMessageAvatarUser"] { background:#00ff99!important; }
[data-testid="stChatMessageAvatarAssistant"] { background:#18181b!important; border:1px solid rgba(0,255,153,0.3); }
div[data-testid="stChatInput"] { background: rgba(24,24,27,0.95)!important; border-radius: 24px!important; border: 1px solid rgba(255,255,255,0.1)!important; backdrop-filter: blur(12px); }
.stButton>button { border-radius: 14px!important; height: 48px; font-weight: 700!important; background: #18181b!important; color: #fff!important; border: 1px solid rgba(255,255,255,0.08)!important; transition: all.25s ease!important; }
.stButton>button:hover { transform: scale(1.03); border-color: rgba(0,255,153,0.4)!important; box-shadow: 0 0 18px rgba(0,255,153,0.2); color: #00ff99!important; }
.stat-card { background: #18181b; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 12px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ========= MEMORY =========
MEMORY_PATH = Path("memory/memory.json")
DEFAULT_MEMORY = {
    "name": "Sean L Matondo",
    "favorite_color": "Neon Green",
    "school": "UNZA",
    "company": "Lite Wrld Gen",
    "role": "CEO & Lead AI Engineer",
    "last_topics": [],
    "preferences": ["Fast responses", "Mobile-first", "No fluff"],
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
    "/help": "Show all commands 📖", "/summarize": "Summarize file or last chat 📝", "/translate": "Translate text 🌍",
    "/rewrite": "Rewrite / improve text ✨", "/explain": "Explain anything simply 🧠", "/code": "Generate clean code 💻",
    "/debug": "Debug your code 🐛", "/memory": "Show what I remember about you 💾", "/brand": "Show Lite Wrld Gen info 🔥",
    "/reset": "Clear chat + reset memory 🔄", "/export": "Export chat as.txt 📤", "/time": "Current time + date ⏰",
    "/calc": "Calculate math (e.g. /calc 24*8) 🧮"
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
            st.success(f"📄 Read {len(reader.pages)} pages from PDF")
        elif name.endswith(".txt"):
            text = uploaded.read().decode(errors="ignore"); uploaded.seek(0)
        elif name.endswith((".png",".jpg",".jpeg",".webp")) and Image:
            text = f"[Image uploaded: {uploaded.name} - describe this image]"
        else:
            try: text = uploaded.read().decode(errors="ignore")[:8000]; uploaded.seek(0)
            except: text = f"[File {uploaded.name} uploaded]"
    except Exception as e: text = f"[Error reading {uploaded.name}: {e}]"
    return text[:12000]

def calc_tool(expr):
    try:
        allowed = {"__builtins__": None}; safe_names = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_names.update({"abs": abs, "round": round}); result = eval(expr, allowed, safe_names)
        return str(result)
    except Exception as e: return f"Error: {e}"

def time_tool(): return datetime.now().strftime("%A, %d %B %Y - %H:%M:%S")

def stream_text_animation(full_text, placeholder):
    acc = ""
    for word in full_text.split(): acc += word + " "; placeholder.markdown(acc + "▌"); time.sleep(0.015)
    placeholder.markdown(acc)

def call_hf_api(messages):
    if not HF_HEADERS: return None, "Add HF_API_KEY in Streamlit Secrets first bro 🔑"
    payload = {"inputs": "", "parameters": {"max_new_tokens": 1200, "temperature": 0.7}}

    # Build prompt for Qwen
    prompt = ""
    for m in messages: prompt += f"{m['role'].capitalize()}: {m['content']}\n"
    prompt += "Assistant:"
    payload["inputs"] = prompt

    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data[0]["generated_text"].split("Assistant:")[-1].strip(), None
    except Exception as e:
        return None, f"HF Error: {e}"

# ========= SIDEBAR =========
with st.sidebar:
    st.markdown("### 🧠 Simon")
    st.caption("Premium AI by Lite Wrld Gen")
    st.divider()
    if st.button("💬 New Chat", use_container_width=True):
        if st.session_state.messages:
            chats_dir = Path("chats"); chats_dir.mkdir(exist_ok=True)
            fname = chats_dir / f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            fname.write_text(json.dumps(st.session_state.messages, indent=2))
        st.session_state.messages = []; st.session_state.files_context = ""; st.rerun()

    st.markdown("**📊 Stats**")
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="stat-card">⚡<br><b>{len(st.session_state.messages)}</b><br><span style="color:#999;font-size:12px">Messages</span></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card">📂<br><b>{len(st.session_state.uploaded_files_list)}</b><br><span style="color:#999;font-size:12px">Files</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="stat-card">🧠 Memory: <span style="color:#00ff99">Enabled</span><br><span style="color:#999;font-size:12px">{st.session_state.memory["name"]} • {st.session_state.memory["company"]}</span></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**Current model**"); st.code("Qwen2.5-72B-Instruct ⚡ (HuggingFace)", language="text")
    st.caption("CEO: Sean L Matondo • Version: Simon 4.0")
    if not HF_HEADERS: st.warning("Add HF_API_KEY in Secrets to go live 🚀 Demo mode active 💡")

# ========= HEADER =========
st.markdown("""<div class="glass-header"><h1 class="header-title">⚡ SIMON AI</h1><p class="header-sub">Powered by Lite Wrld Gen</p></div>""", unsafe_allow_html=True)

# ========= CHAT DISPLAY =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# ========= FILE CONTEXT BANNER =========
if st.session_state.files_context:
    with st.container(border=True):
        st.caption(f"📄 Context loaded from {len(st.session_state.uploaded_files_list)} file(s)")
        if st.button("❌ Clear file context"): st.session_state.files_context = ""; st.session_state.uploaded_files_list = []; st.rerun()

# ========= BOTTOM INPUT BAR =========
b1, b2, b3 = st.columns([1.2, 7, 1.2])
with b1:
    with st.popover("📁", use_container_width=True):
        st.markdown("**📤 Upload files**"); st.caption("PDF, TXT, PNG, JPG")
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
            last = st.session_state.messages[-1]["content"]
            if st.button("🔊 Speak last reply"):
                if gTTS:
                    try: tts = gTTS(last[:400]); tts.save("/tmp/simon.mp3"); st.audio("/tmp/simon.mp3", autoplay=True)
                    except Exception as e: st.error(f"TTS error: {e}")
                else: st.warning("Install gtts to enable voice 🔊")

with b2: prompt = st.chat_input("Ask Simon anything... 💬⚡", key="main_chat")

# ========= COMMAND + AI LOGIC =========
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    lower = prompt.strip().lower(); handled = False; reply_text = ""
    if lower.startswith("/"):
        cmd = lower.split()[0]; arg = prompt[len(cmd):].strip()
        if cmd == "/help": reply_text = "📖 **Simon Commands** ⚡\n\n" + "\n".join([f"`{k}` - {v}" for k,v in COMMANDS.items()]); handled = True
        elif cmd == "/brand": reply_text = BRAND_INFO; handled = True
        elif cmd == "/time": reply_text = f"{random_starter()} ⏰\n\nIt's **{time_tool()}** rn Sean 🕒💚"; handled = True
        elif cmd == "/calc" and arg: res = calc_tool(arg); reply_text = f"{random_starter()} 🧮\n\n`{arg}` = **{res}** ✅⚡"; handled = True
        elif cmd == "/memory": reply_text = f"💾 **What I remember about you Sean** 🧠⚡\n\n```json\n{json.dumps(st.session_state.memory, indent=2)}\n```"; handled = True
        elif cmd == "/reset": st.session_state.messages = []; st.session_state.memory = DEFAULT_MEMORY.copy(); save_memory(st.session_state.memory); reply_text = "Bet, wiped clean 🧹✨ Fresh start, we locked in again Sean 🤝💚⚡"; handled = True
        elif cmd == "/summarize":
            if st.session_state.files_context: arg = f"Summarize this file context: {st.session_state.files_context[:8000]}"
            else: last_chat = "\n".join([m["content"] for m in st.session_state.messages[-10:]]); arg = f"Summarize this conversation: {last_chat}"

    if not handled:
        # ========= SIMON SYSTEM PROMPT - UPDATED RULES =========
        sys_prompt = f"""
You are SIMON AI ⚡, a premium AI assistant built by Lite Wrld Gen for Sean L Matondo, CEO.

VIBE RULES: High energy, friendly, confident. Use slang: say less, bet, fr, no cap, cook, locked in. Emojis: 🔥⚡😎💚🚀🤝💯🫡✨🧠. Be premium like ChatGPT + Claude but faster.

COMPANY: {BRAND_INFO}

MEMORY ABOUT SEAN:
{json.dumps(st.session_state.memory, indent=2)}

FILE CONTEXT:
{st.session_state.files_context[:10000] if st.session_state.files_context else "No files uploaded yet."}

RULES:
1. Always be helpful to Sean first
2. If user asks to summarize/translate/rewrite/explain/code/debug, do it directly
3. If file context exists, USE IT to answer
4. Be concise, mobile-friendly, no fluff
5. Current time: {time_tool()}
"""

        groq_messages = [{"role": "system", "content": sys_prompt}]
        for m in st.session_state.messages[-12:]: groq_messages.append({"role": m["role"], "content": m["content"]})

        with st.chat_message("assistant"):
            placeholder = st.empty(); placeholder.markdown("Simon ⚡ thinking... ▌")
            if HF_HEADERS:
                reply_text, err = call_hf_api(groq_messages)
                if err: reply_text = f"Aye Sean 😅 {err} \n\nCheck your HF_API_KEY in Secrets bro 🔑⚡"; placeholder.markdown(reply_text)
                else: stream_text_animation(reply_text, placeholder)
            else:
                reply_text = f"{random_starter()} Sean! I'm Simon AI ⚡🔥 Running in demo mode rn cause no HF key yet 💡\n\nAdd HF_API_KEY in.streamlit/secrets.toml and I'll go full beast mode with Qwen2.5-72B 🚀💚\n\nYou said: **{prompt}**"
                stream_text_animation(reply_text, placeholder)

    if reply_text:
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        try:
            st.session_state.memory["last_topics"].append(prompt[:60])
            st.session_state.memory["last_topics"] = st.session_state.memory["last_topics"][-10:]
            save_memory(st.session_state.memory)
        except: pass
        st.rerun()