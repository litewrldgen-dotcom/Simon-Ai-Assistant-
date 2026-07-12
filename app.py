import streamlit as st
import time
import requests
import base64
from io import BytesIO
from groq import Groq

st.set_page_config(page_title="Simon AI", page_icon="✨", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
HF_API_KEY = st.secrets["HF_API_KEY"]

# ====== PREMIUM GLASS UI ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
* {font-family: 'DM+Sans', sans-serif;}
.stApp {background: radial-gradient(circle at 20% 50%, #0f0f1a 0%, #05050a 100%); color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 5rem; padding-bottom: 120px; max-width: 900px;}
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 65px; background: rgba(10,10,15,0.7); backdrop-filter: blur(30px); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; padding: 0 24px; z-index: 999;}
.logo {width: 36px; height: 36px; border-radius: 12px; background: linear-gradient(135deg, #7C3AED, #EC4899); margin-right: 12px;}
.title {font-size: 18px; font-weight: 700; color: #fff;}
.badge {margin-left: 10px; background: linear-gradient(90deg, #7C3AED, #EC4899); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; color: #fff;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #7C3AED, #EC4899); color: #fff; border-radius: 20px 20px 6px 20px; padding: 14px 18px; max-width: 70%;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(30,30,40,0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 14px 18px; max-width: 70%;
}
.sig {font-size: 10px; color: #7C3AED; margin-top: 8px; font-weight: 700;}
.typing {color: #888; font-style: italic;}
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: rgba(10,10,15,0.8); backdrop-filter: blur(30px); border-top: 1px solid rgba(255,255,255,0.08); padding: 16px 20px!important; z-index: 999;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.0.8 <span style="color:#3B82F6;">✓</span><span class="badge">LITE WRLD GEN</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

if "chat" not in st.session_state: st.session_state.chat = []
if "voice_on" not in st.session_state: st.session_state.voice_on = True

def play_audio(audio_bytes):
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}">'
    st.markdown(audio_html, unsafe_allow_html=True)

def gen_image_hf(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": f"realistic photo, high detail, 8k, {prompt}"}
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    return response.content if response.status_code == 200 else None

def speak(text):
    if st.session_state.voice_on:
        response = client.audio.speech.create(
            model="playai-tts",
            voice="Fritz-PlayAI",
            input=text,
        )
        play_audio(response.read())

def get_reply(msg):
    msg_lower = msg.lower()

    # ====== RULES - UNLIMITED ======
    system = """You are Simon AI v1.0.8 created by Sean L Matondo at Lite Wrld Gen.
    RULE 1: Always start with Got you, Say less, Let's cook, or Awe + emoji
    RULE 2: Be confident, helpful, funny, use emojis. Keep replies under 3 sentences.
    RULE 3: BRAND FACTS: Lite Wrld Gen is an AI company founded by Sean L Matondo. We operate online worldwide.
    RULE 4: If asked about Lite Wrld Gen location, say: We operate online and serve users worldwide 🌍"""

    if "generate image" in msg_lower or "create image" in msg_lower or "draw" in msg_lower:
        prompt = msg.replace("generate image", "").replace("create image", "").replace("draw", "").strip()
        if prompt == "": return "Got you 😅 What should I generate?"
        return f"GENERATE_IMAGE:{prompt}"

    if "where is lite wrld gen" in msg_lower:
        return "Got you 🌍 <b>Lite Wrld Gen</b> operates online and serves users worldwide 🔥"
    if "who created you" in msg_lower:
        return "Let's cook 🚀 I was created by <b>Sean L Matondo</b> at <b>Lite Wrld Gen</b>."

    # NO LIMIT HERE - SEND ALL CHAT HISTORY
    msgs = [{"role": "system", "content": system}]
    for m in st.session_state.chat: msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": msg})

    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.8, max_tokens=300)
    txt = res.choices[0].message.content
    if not any(txt.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
        txt = f"Got you {txt}"
    return txt

# CHAT HISTORY
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        if m.get("is_image"): st.image(m["content"])
        else:
            c = m["content"]
            if m["role"] == "assistant": c += '<div class="sig">Simon AI v1.0.8 • Lite Wrld Gen</div>'
            st.markdown(c, unsafe_allow_html=True)

# VOICE TOGGLE
col1, col2 = st.columns([6,1])
with col2:
    st.session_state.voice_on = st.toggle("🔊", value=st.session_state.voice_on)

# INPUT
user_input = st.chat_input("Ask Simon anything... or use mic 🎤")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="typing">Simon is typing...</div>', unsafe_allow_html=True)

        ai_reply = get_reply(user_input)
        typing_placeholder.empty()

        if ai_reply.startswith("GENERATE_IMAGE:"):
            prompt = ai_reply.replace("GENERATE_IMAGE:", "")
            st.info("Got you 🔥 Generating your image...")
            img_bytes = gen_image_hf(prompt)
            if img_bytes:
                st.image(img_bytes)
                st.session_state.chat.append({"role": "assistant", "content": img_bytes, "is_image": True})
            else:
                err = "Say less 😅 HF is waking up. Try again in 20s"
                st.error(err)
                st.session_state.chat.append({"role": "assistant", "content": err})
        else:
            st.markdown(ai_reply + '<div class="sig">Simon AI v1.0.8 • Lite Wrld Gen</div>', unsafe_allow_html=True)
            st.session_state.chat.append({"role": "assistant", "content": ai_reply})
            speak(ai_reply) # VOICE REPLY

    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.0.8 • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)