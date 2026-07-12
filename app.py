import streamlit as st
import base64
from datetime import datetime
from groq import Groq
from gtts import gTTS
from PyPDF2 import PdfReader
from io import BytesIO

st.set_page_config(page_title="Simon AI", page_icon="🔥", layout="centered")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ====== PREMIUM DARK GLASS UI ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="st"] {font-family: 'Inter', sans-serif;}
.stApp {background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); color: #e0e0e0;}
header {visibility: hidden;}
.main {padding-top: 80px; padding-bottom: 120px;}

/* HEADER */
.header {background: rgba(20,20,20,0.8); backdrop-filter: blur(20px); padding: 12px 20px; position: fixed; top: 0; left: 0; right: 0; z-index: 1000; display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1);}
.header img {width: 40px; height: 40px; border-radius: 50%; margin-right: 12px; border: 2px solid #00FF88;}
.header.name {color: white; font-size: 17px; font-weight: 700;}
.badge {background: linear-gradient(90deg, #00FF88, #00CC66); color: #000; font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 6px; margin-left: 8px;}

/* CHAT BUBBLES */
[data-testid="stChatMessage"] {background: transparent; border: none;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #00FF88, #00CC66);
    color: #000;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    max-width: 75%;
    margin-left: auto;
    font-weight: 500;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(40,40,40,0.6);
    backdrop-filter: blur(10px);
    color: #e0e0e0;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    max-width: 75%;
    border: 1px solid rgba(255,255,255,0.1);
}
.stamp {font-size: 10px; color: #00FF88; margin-top: 6px; font-weight: 600;}
.time {font-size: 11px; color: #777; float: right; margin-left: 8px;}

/* INPUT BAR */
.stChatInput {position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 700px; z-index: 999;}
.stChatInputContainer {background: rgba(30,30,30,0.8); backdrop-filter: blur(20px); border-radius: 24px; border: 1px solid rgba(255,255,255,0.1); padding: 8px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <img src="https://i.imgur.com/8Km9tLL.png">
    <div>
        <div class="header.name">Simon AI v1.1.1 <span style="color:#00AAFF;">✓</span><span class="badge">LITE WRLD GEN</span></div>
        <div style="color:#888; font-size:12px;">Powered by Lite Wrld Gen</div>
    </div>
</div>
""", unsafe_allow_html=True)

if "user_name" not in st.session_state: st.session_state.user_name = "Friend"
if "history" not in st.session_state: st.session_state.history = []

def analyze_image(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    b64 = base64.b64encode(bytes_data).decode()
    return f"data:image/jpeg;base64,{b64}"

def get_groq_response(user_msg, image_b64=None):
    # ====== SIMON RULES ARE BACK ======
    system_prompt = f"""You are Simon AI v1.1.1, created by Sean L. Matondo at Lite Wrld Gen.
CRITICAL: Always start your response with Got you, Say less, Let's cook, or Awe
Be friendly, fast, and use emojis.
If asked who built you: Sean L. Matondo at Lite Wrld Gen
If asked what Lite Wrld Gen is: An AI company building fast free AI assistants
User's name is {st.session_state.user_name}."""

    # HARDCODED FACTS
    if "founder" in user_msg.lower() or "who made you" in user_msg.lower():
        return "Awe 🙏 I am Simon AI v1.1.1. I was created by Sean L. Matondo at <b>Lite Wrld Gen</b>."
    if "lite wrld gen" in user_msg.lower():
        return "Got you 🔥 <b>Lite Wrld Gen</b> is an AI company founded by Sean L. Matondo. We build Simon AI."
    if "version" in user_msg.lower():
        return "Say less 😎 You running <b>Simon AI v1.1.1 Premium</b> by Lite Wrld Gen."
    if "my name is" in user_msg.lower():
        name = user_msg.lower().split("my name is")[-1].strip().split()[0].title()
        st.session_state.user_name = name
        return f"Let's cook {name}! Locked in 🔥"

    messages = [{"role": "system", "content": system_prompt}]

    if image_b64:
        messages.append({"role": "user", "content": [{"type": "text", "text": user_msg}, {"type": "image_url", "image_url": {"url": image_b64}}]})
        model = "llama-3.2-11b-vision-preview"
    else:
        for msg in st.session_state.history[-8:]: messages.append(msg)
        messages.append({"role": "user", "content": user_msg})
        model = "llama-3.1-8b-instant"

    try:
        response = client.chat.completions.create(model=model, messages=messages, temperature=0.8, max_tokens=400)
        reply = response.choices[0].message.content
        # FORCE THE OPENING
        if not any(reply.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
            reply = f"Got you {reply}"
        return reply
    except Exception as e:
        return f"Say less - Error: {str(e)}"

# CHAT HISTORY
chat_container = st.container()
with chat_container:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            content = msg["content"]
            if msg["role"] == "assistant":
                content += f'<div class="stamp">Simon AI v1.1.1 • Lite Wrld Gen</div>'
            st.markdown(content + f'<span class="time">{datetime.now().strftime("%I:%M %p")}</span>', unsafe_allow_html=True)

# INPUT + UPLOAD SIDE BY SIDE
input_col, upload_col = st.columns([8,1])
with input_col:
    prompt = st.chat_input("Message Simon AI...")
with upload_col:
    uploaded = st.file_uploader("📎", type=['pdf','txt','png','jpg','jpeg'], label_visibility="collapsed")

if prompt or uploaded:
    image_b64 = None
    if uploaded:
        if uploaded.type.startswith("image"):
            image_b64 = analyze_image(uploaded)
            st.session_state.history.append({"role": "user", "content": f"📎 Image uploaded"})
        else:
            st.session_state.history.append({"role": "user", "content": f"📎 {uploaded.name}"})

    if prompt:
        st.session_state.history.append({"role": "user", "content": prompt})

    response = get_groq_response(prompt if prompt else "describe this image", image_b64)
    st.session_state.history.append({"role": "assistant", "content": response})
    st.rerun()

st.markdown("<center><p style='color:#555; font-size:12px; margin-top:100px;'>Simon AI v1.1.1 • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)