import streamlit as st
from datetime import datetime
from groq import Groq
from gtts import gTTS
from PyPDF2 import PdfReader
from io import BytesIO

st.set_page_config(page_title="Simon AI", page_icon="✨", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ====== OUT OF THIS WORLD GLASS UI ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
* {font-family: 'DM Sans', sans-serif;}
.stApp {background: radial-gradient(circle at 20% 50%, #0f0f1a 0%, #05050a 100%); color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 5rem; padding-bottom: 8rem; max-width: 900px;}

/* HEADER GLASS */
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 65px; background: rgba(10,10,15,0.6); backdrop-filter: blur(30px); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; padding: 0 24px; z-index: 999;}
.logo {width: 36px; height: 36px; border-radius: 12px; background: linear-gradient(135deg, #7C3AED, #EC4899); margin-right: 12px;}
.title {font-size: 18px; font-weight: 700; color: #fff;}
.sub {font-size: 11px; color: #888; font-weight: 500;}
.badge {margin-left: 10px; background: linear-gradient(90deg, #7C3AED, #EC4899); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; color: #fff;}

/* CHAT */
[data-testid="stChatMessage"] {background: transparent;}
[data-testid="stChatMessage"][data-testid*="user"] {display: flex; justify-content: flex-end;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #7C3AED, #EC4899);
    color: #fff; border-radius: 20px 20px 6px 20px; padding: 14px 18px; max-width: 70%; font-weight: 500; box-shadow: 0 8px 30px rgba(124,58,237,0.3);
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(30,30,40,0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 14px 18px; max-width: 70%;
}
.sig {font-size: 10px; color: #7C3AED; margin-top: 8px; font-weight: 700;}

/* INPUT BAR WITH UPLOAD INSIDE */
.stChatInput {position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 800px;}
.stChatInputContainer {background: rgba(20,20,30,0.7); backdrop-filter: blur(30px); border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); padding: 10px 16px; display: flex; align-items: center;}
.stFileUploader {padding: 0!important;}
.stFileUploader > div {height: 40px!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.0.0 <span style="color:#3B82F6;">✓</span><span class="badge">LITE WRLD GEN</span></div>
        <div class="sub">Powered by Lite Wrld Gen</div>
    </div>
</div>
""", unsafe_allow_html=True)

if "name" not in st.session_state: st.session_state.name = "Friend"
if "chat" not in st.session_state: st.session_state.chat = []

def get_reply(msg):
    system = f"""You are Simon AI v1.0.0 by Lite Wrld Gen. Creator: Sean L Matondo.
Rule 1: Start every answer with Got you, Say less, Let's cook, or Awe
Rule 2: Be friendly, fast, use emojis
Rule 3: If asked about Lite Wrld Gen, say it's an AI company by Sean L Matondo
User name is {st.session_state.name}"""

    if "founder" in msg.lower(): return "Awe 🙏 Simon AI v1.0.0 was created by <b>Sean L Matondo</b> at <b>Lite Wrld Gen</b>."
    if "version" in msg.lower(): return "Say less 😎 Running <b>Simon AI v1.0.0</b> by Lite Wrld Gen."
    if "lite wrld gen" in msg.lower(): return "Got you 🔥 Lite Wrld Gen builds fast AI assistants for everyone."
    if "my name is" in msg.lower():
        n = msg.lower().split("my name is")[-1].strip().split()[0].title()
        st.session_state.name = n
        return f"Let's cook {n}! Locked in 🔥"

    msgs = [{"role": "system", "content": system}]
    for m in st.session_state.chat[-10:]: msgs.append(m)
    msgs.append({"role": "user", "content": msg})

    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.8, max_tokens=400)
        txt = res.choices[0].message.content
        if not txt.startswith(("Got you", "Say less", "Let's cook", "Awe")): txt = f"Got you {txt}"
        return txt
    except Exception as e: return f"Say less - {str(e)}"

# CHAT HISTORY
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        c = m["content"]
        if m["role"] == "assistant": c += '<div class="sig">Simon AI v1.0.0 • Lite Wrld Gen</div>'
        st.markdown(c, unsafe_allow_html=True)

# INPUT + UPLOAD TOGETHER
col1, col2 = st.columns([9,1])
with col1:
    user_input = st.chat_input("Ask Simon anything...")
with col2:
    file = st.file_uploader(" ", type=['pdf','txt'], label_visibility="collapsed")

if user_input or file:
    if file:
        st.session_state.chat.append({"role": "user", "content": f"📎 {file.name}"})
        if file.type == "application/pdf":
            pdf = PdfReader(file)
            user_input = "Summarize this PDF: " + " ".join([p.extract_text() for p in pdf.pages[:3]])
        else:
            user_input = "Summarize this file: " + file.getvalue().decode("utf-8")[:2000]

    if user_input:
        st.session_state.chat.append({"role": "user", "content": user_input})

    ai_reply = get_reply(user_input if user_input else "summarize")
    st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.0.0 • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)