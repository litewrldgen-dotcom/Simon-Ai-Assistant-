import streamlit as st
import base64
from datetime import datetime
from groq import Groq
from gtts import gTTS
from PyPDF2 import PdfReader

st.set_page_config(page_title="Simon AI", page_icon="🔥", layout="centered", initial_sidebar_state="collapsed")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ====== WHATSAPP UI ======
st.markdown("""
<style>
.stApp {background-color: #0b141a; background-image: url('https://user-images.githubusercontent.com/15082596/79042575-0b2f8e80-7c0e-11ea-8c6e-5f5a8b2c7b2a.png');}
header {visibility: hidden;}
.main {padding-bottom: 80px;}
.header {background: #202c33; padding: 10px 16px; position: fixed; top: 0; left: 0; right: 0; z-index: 1000; display: flex; align-items: center; border-bottom: 1px solid #2a3942;}
.header img {width: 42px; height: 42px; border-radius: 50%; margin-right: 12px; border: 2px solid #00FF88;}
.header.name {color: white; font-size: 16px; font-weight: 600;}
.badge {background: #00FF88; color: #0b141a; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; margin-left: 6px;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {background: #005c4b; color: #e9edef; border-radius: 7.5px 2px 7.5px 7.5px; padding: 8px 12px; max-width: 70%; margin-left: auto;}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {background: #202c33; color: #e9edef; border-radius: 2px 7.5px 7.5px 7.5px; padding: 8px 12px; max-width: 70%; border-left: 3px solid #00FF88;}
.stamp {font-size: 10px; color: #00FF88; margin-top: 4px;}
.time {font-size: 11px; color: #8696a0; float: right; margin-left: 8px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <img src="https://i.imgur.com/8Km9tLL.png">
    <div>
        <div class="name">Simon AI v1.0.2 <span style="color:#53bdeb;">✓</span><span class="badge">LITE WRLD GEN</span></div>
        <div style="color:#8696a0; font-size:12px;">Powered by Lite Wrld Gen</div>
    </div>
</div>
<br><br><br>
""", unsafe_allow_html=True)

if "user_name" not in st.session_state: st.session_state.user_name = "Friend"
if "history" not in st.session_state: st.session_state.history = []

def analyze_image(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    b64 = base64.b64encode(bytes_data).decode()
    return f"data:image/jpeg;base64,{b64}"

def get_groq_response(user_msg, image_b64=None):
    # CLEAN SYSTEM PROMPT - NO META TALK
    system_prompt = f"""You are Simon AI v1.0.2, an assistant created by Sean L. Matondo at Lite Wrld Gen.
Your job is to be helpful, fast, and friendly.
Always start your responses with Got you, Say less, Let's cook, or Awe.
Use emojis naturally.
If asked who built you, say Sean L. Matondo at Lite Wrld Gen.
If asked what Lite Wrld Gen is, say it's an AI company building fast free AI assistants.
User's name is {st.session_state.user_name}."""

    # HARDCODED FACTS
    if "founder" in user_msg.lower() or "who made you" in user_msg.lower():
        return "Awe 🙏 I am Simon AI v1.0.2. I was created by Sean L. Matondo at <b>Lite Wrld Gen</b>."
    if "lite wrld gen" in user_msg.lower():
        return "Got you 🔥 <b>Lite Wrld Gen</b> is an AI company founded by Sean L. Matondo. We built Simon AI for everyone."
    if "version" in user_msg.lower():
        return "Say less 😎 You running <b>Simon AI v1.0.2 Official</b> by Lite Wrld Gen."
    if "my name is" in user_msg.lower():
        name = user_msg.lower().split("my name is")[-1].strip().split()[0].title()
        st.session_state.user_name = name
        return f"Awe {name}! Locked in 🔥"

    messages = [{"role": "system", "content": system_prompt}]

    # VISION SUPPORT
    if image_b64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_msg if user_msg else "Describe this image in detail"},
                {"type": "image_url", "image_url": {"url": image_b64}}
            ]
        })
        model = "llama-3.2-11b-vision-preview"
    else:
        for msg in st.session_state.history[-6:]: messages.append(msg)
        messages.append({"role": "user", "content": user_msg})
        model = "llama-3.1-8b-instant"

    try:
        response = client.chat.completions.create(model=model, messages=messages, temperature=0.7, max_tokens=300)
        reply = response.choices[0].message.content
        if not any(reply.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
            reply = f"Got you {reply}"
        return reply
    except Exception as e:
        return f"Say less - Error: {str(e)}"

# CHAT HISTORY
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        content = msg["content"]
        if msg["role"] == "assistant":
            content += f'<div class="stamp">Simon AI v1.0.2 • Lite Wrld Gen</div>'
        st.markdown(content + f'<span class="time">{datetime.now().strftime("%I:%M %p")}</span>', unsafe_allow_html=True)

# INPUT
col1, col2 = st.columns([10,1])
with col1:
    prompt = st.chat_input("Message Simon AI")
with col2:
    uploaded = st.file_uploader("📎", type=['pdf','txt','png','jpg','jpeg'], label_visibility="collapsed")

if prompt or uploaded:
    image_b64 = None
    if uploaded and uploaded.type.startswith("image"):
        image_b64 = analyze_image(uploaded)
        st.session_state.history.append({"role": "user", "content": f"📎 Sent an image"})
    elif uploaded:
        st.session_state.history.append({"role": "user", "content": f"📎 {uploaded.name}"})

    if prompt:
        st.session_state.history.append({"role": "user", "content": prompt})

    response = get_groq_response(prompt if prompt else "describe this image", image_b64)
    st.session_state.history.append({"role": "assistant", "content": response})
    st.rerun()

st.markdown("<center><p style='color:#8696a0; font-size:12px;'>Simon AI v1.0.2 • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)