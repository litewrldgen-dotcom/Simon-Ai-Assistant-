import streamlit as st
from datetime import datetime
from pathlib import Path
import json, random, time, math
import requests
from io import BytesIO

try:
    from groq import Groq
except: Groq = None
try:
    from PyPDF2 import PdfReader
except: PdfReader = None
try:
    from PIL import Image
except: Image = None
try:
    from gtts import gTTS
except: gTTS = None

# ========= PAGE CONFIG =========
st.set_page_config(page_title="Simon AI v1.2.0", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ========= MEMORY =========
MEMORY_PATH = Path("memory/memory.json")
DEFAULT_MEMORY = {"name": "Friend", "company": "", "language": "English", "last_topics": [], "created": datetime.now().isoformat()}
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
    groq_key = st.secrets.get("GROQ_API_KEY")
    hf_key = st.secrets.get("HF_API_KEY")
    groq_client = Groq(api_key=groq_key) if groq_key and Groq else None
    hf_headers = {"Authorization": f"Bearer {hf_key}"} if hf_key else None
    return groq_client, hf_headers
groq_client, hf_headers = load_clients()

# ========= STATE =========
if "chat" not in st.session_state: st.session_state.chat = []
if "memory" not in st.session_state: st.session_state.memory = load_memory()
if "files_context" not in st.session_state: st.session_state.files_context = ""

# ========= CUL UI + GPT BLUEPRINT MERGED =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
* {font-family: 'DM Sans', sans-serif;}
.stApp {background: radial-gradient(circle at 20% 50%, #0f0f1a 0%, #05050a 100%); color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 5rem; padding-bottom: 120px; max-width: 900px;}

/* TOPBAR FROM CUL */
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 65px; background: rgba(10,10,15,0.7); backdrop-filter: blur(30px); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; padding: 0 24px; z-index: 999;}
.logo {width: 36px; height: 36px; border-radius: 12px; background: linear-gradient(135deg, #00ff99, #00cc77); margin-right: 12px; box-shadow: 0 0 20px rgba(0,255,153,0.4);}
.title {font-size: 18px; font-weight: 700; color: #fff;}
.sub {font-size: 11px; color: #888; font-weight: 500;}
.badge {margin-left: 10px; background: linear-gradient(90deg, #00ff99, #00cc77); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; color: #000;}

/* SIDEBAR GLASS */
[data-testid="stSidebar"] {background: rgba(15,15,25,0.8); backdrop-filter: blur(20px); border-right: 1px solid rgba(255,255,255,0.08);}

/* CHAT BUBBLES FROM CUL */
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #00ff99, #00cc77);
    color: #000; border-radius: 20px 20px 6px 20px; padding: 14px 18px; max-width: 70%; font-weight: 500; box-shadow: 0 8px 30px rgba(0,255,153,0.3);
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(30,30,40,0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 14px 18px; max-width: 70%;
}
.sig {font-size: 10px; color: #00ff99; margin-top: 8px; font-weight: 700;}

/* INPUT FIXED BOTTOM */
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: rgba(10,10,15,0.8); backdrop-filter: blur(30px); border-top: 1px solid rgba(255,255,255,0.08); padding: 16px 20px!important; z-index: 999;}
.stChatInputContainer {background: rgba(30,30,40,0.6)!important; border-radius: 24px!important; border: 1px solid rgba(255,255,255,0.1)!important;}
</style>
""", unsafe_allow_html=True)

# TOPBAR
st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.2.0 <span style="color:#00ff99;">✓</span><span class="badge">LITE WRLD GEN</span></div>
        <div class="sub">Created by Sean L. Matondo 🌍</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========= RULES + PERSONALITY =========
SIMON_RULES = """
⚡ SIMON'S 10 RULES ⚡
1. Rep Lite Wrld Gen and Sean L. Matondo first 🔥
2. Be friendly, helpful, for EVERYONE 🌍
3. Use slang: bet, say less, no cap, locked in 😎 + EMOJIS ⚡💚
4. If files/images uploaded, USE THAT CONTEXT 📄
5. Be FAST and MOBILE-FIRST 📱
6. If you don't know, say it straight no cap 💯
7. Code, summarize, translate, generate images instantly and SHOW THE IMAGE
8. Remember user name + last topics 🧠
9. Groq for chat. HuggingFace for images.
10. If asked who built Simon, always say: Created by Sean L. Matondo at Lite Wrld Gen
"""

# ========= SIDEBAR - FROM GPT BLUEPRINT =========
with st.sidebar:
    st.markdown("### 🧠 Simon AI")
    st.caption("v1.2.0 • Created by Sean L. Matondo")
    st.caption("Powered by Lite Wrld Gen")
    st.divider()
    st.markdown("#### 📁 AI Tools")
    uploaded = st.file_uploader("Upload File", type=["pdf","txt","png","jpg","jpeg","csv","docx"])
    if uploaded:
        txt = ""
        if uploaded.name.endswith(".pdf") and PdfReader:
            reader = PdfReader(uploaded)
            for p in reader.pages: txt += p.extract_text() or ""
        elif uploaded.name.endswith(("png","jpg","jpeg")):
            txt = f"[Image uploaded: {uploaded.name}]"
        else: txt = uploaded.read().decode(errors="ignore")[:5000]
        st.session_state.files_context += f"\n---{uploaded.name}---\n{txt}"
        st.success(f"Loaded {uploaded.name} ✅")
    
    st.divider()
    st.markdown("#### 🧠 Memory")
    st.write(f"**Name:** {st.session_state.memory['name']}")
    st.write(f"**Msgs:** {len(st.session_state.chat)}")
    
    st.divider()
    st.markdown("#### 📞 Contact Lite Wrld Gen")
    st.write("**Email:** litewrldgen@gmail.com")
    st.write("**WhatsApp:** +263773527136")
    st.write("**Cell:** +263780103776")
    st.caption("Building fast, free AI for everyone 🌍")
    
    if st.button("💬 + New Chat", use_container_width=True):
        st.session_state.chat = []; st.session_state.files_context = ""; st.rerun()
    if st.button("Clear Memory"):
        st.session_state.memory = DEFAULT_MEMORY.copy(); save_memory(st.session_state.memory); st.rerun()

# ========= CHAT HISTORY =========
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            st.markdown(m["content"], unsafe_allow_html=True)
            st.markdown('<div class="sig">Simon AI v1.2.0 • Lite Wrld Gen</div>', unsafe_allow_html=True)
        else:
            st.markdown(m["content"], unsafe_allow_html=True)

# ========= INPUT =========
user_input = st.chat_input("Ask Simon anything... /img to generate ⚡")

# ========= LOGIC =========
if user_input:
    if "my name is" in user_input.lower():
        st.session_state.memory["name"] = user_input.lower().split("my name is")[-1].strip().split()[0].title()
        save_memory(st.session_state.memory)

    st.session_state.chat.append({"role": "user", "content": user_input})
    
    system = f"""You are Simon AI v1.2.0 created by Sean L. Matondo at Lite Wrld Gen. For the WORLD 🌍
{SIMON_RULES}
About Lite Wrld Gen: We build fast, free AI tools for everyone. No gatekeeping. Just real AI that works on any phone.
Contact: litewrldgen@gmail.com | WhatsApp +263773527136 | +263780103776
User: {st.session_state.memory['name']}
File Context: {st.session_state.files_context}"""

    msgs = [{"role": "system", "content": system}] + st.session_state.chat[-10:]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Simon is thinking... ⚡")
        
        if user_input.startswith("/img") and hf_headers:
            # HF IMAGE GEN - ACTUALLY SHOWS THE PIC NOW
            prompt = user_input[4:]
            API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            res = requests.post(API_URL, headers=hf_headers, json={"inputs": prompt})
            try:
                img = Image.open(BytesIO(res.content))
                ai_reply = f"Got you 🔥 A Pup! 🐶<br><br>I'll generate a quick image for you. Here it is:"
                placeholder.markdown(ai_reply, unsafe_allow_html=True)
                st.image(img, caption=f"Image: {prompt}", use_container_width=True)
                ai_reply += f"<br><br>No cap, that was FAST, right? ⚡ What do you think?"
            except:
                ai_reply = "Say less - image gen failed bro. Check your HF_API_KEY"
        else:
            # GROQ CHAT WITH STREAMING
            try:
                stream = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, stream=True)
                ai_reply = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        ai_reply += chunk.choices[0].delta.content
                        placeholder.markdown(ai_reply + "▌")
                if not any(ai_reply.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
                    ai_reply = f"Got you 🔥 {ai_reply}"
            except Exception as e:
                ai_reply = f"Say less - {str(e)}"
        
        placeholder.markdown(ai_reply, unsafe_allow_html=True)
        st.markdown('<div class="sig">Simon AI v1.2.0 • Lite Wrld Gen</div>', unsafe_allow_html=True)

    st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.2.0 • Created by Sean L. Matondo<br>Powered by Lite Wrld Gen | litewrldgen@gmail.com | +263773527136<br>A Lite Wrld Gen Product 🌍</p></center>", unsafe_allow_html=True)