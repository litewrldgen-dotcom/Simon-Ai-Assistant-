import streamlit as st
import json
import os
import base64
from datetime import datetime
from groq import Groq
from gtts import gTTS
from PyPDF2 import PdfReader
from PIL import Image
import io

# ====== CONFIG ======
st.set_page_config(
    page_title="Simon v4.0",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# INIT GROQ
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ====== PREMIUM GLASS CSS ======
st.markdown("""
<style>
.main {background: #0a0e13;}
h1 {color: #00FF88; text-align: center;}
.subtitle {text-align: center; color: #888; margin-bottom: 20px;}

[data-testid="stSidebar"] {background: #111b21; border-right: 1px solid #2a3942;}

[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #00a884; color: white; border-radius: 18px 6px 18px 18px;
    padding: 12px 16px; max-width: 70%; margin-left: auto;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: #202c33; color: #e9edef; border-radius: 6px 18px 18px 18px;
    padding: 12px 16px; max-width: 70%; border-left: 3px solid #00FF88;
}
[data-testid="stChatInput"] {position: fixed; bottom: 0; background: #0a0e13; padding: 10px; z-index: 999;}
</style>
""", unsafe_allow_html=True)

# ====== SESSION ======
if "user_name" not in st.session_state: st.session_state.user_name = "Friend"
if "history" not in st.session_state: st.session_state.history = []

MEMORY_FILE = "simon_memory.json"
if os.path.exists(MEMORY_FILE):
    try: st.session_state.user_name = json.load(open(MEMORY_FILE)).get("name", "Friend")
    except: pass

def save_memory(): json.dump({"name": st.session_state.user_name}, open(MEMORY_FILE, "w"))

def tts_audio(text):
    try:
        tts = gTTS(text=text[:200], lang="en"); tts.save("voice.mp3")
        b64 = base64.b64encode(open("voice.mp3","rb").read()).decode()
        return f'<audio autoplay src="data:audio/mp3;base64,{b64}">'
    except: return None

def extract_file_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in reader.pages])
    elif uploaded_file.type.startswith("text"):
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.type.startswith("image"):
        return f"[Image uploaded: {uploaded_file.name}]"
    return ""

# ====== SIMON BRAIN WITH GROQ ======
def get_groq_response(user_msg, file_context=""):
    system_prompt = f"""You are Simon v4.0, an elite AI assistant by Lite Wrld Gen.
Founder: Sean L. Matondo. Mission: Build AI for everyone.
CRITICAL RULES:
1. ALWAYS start with: Got you, Say less, Let's cook, or Awe
2. Be accurate. Lite Wrld Gen = AI company by Sean L Matondo
3. User's name is {st.session_state.user_name}. Use it naturally.
4. Use emojis. Be helpful and slightly cocky but smart.
5. Only say 'bro' if user says 'bro' first.
Context from files: {file_context}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.history[-10:]: # last 10 for memory
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_msg})

    # HARDCODED FACTS
    if "founder" in user_msg.lower() or "who made you" in user_msg.lower():
        return "Awe 🙏 I was created by Sean L. Matondo at Lite Wrld Gen."
    if "lite wrld gen" in user_msg.lower():
        return "Got you 🔥 Lite Wrld Gen is an AI company founded by Sean L. Matondo. We build fast, free AI assistants like me for everyone worldwide."
    if "mummy" in user_msg.lower():
        return "Say less 😅 A mummy is an ancient Egyptian body that was preserved after death. Not spaghetti lol"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # FASTEST + SMARTEST
            messages=messages,
            temperature=0.7,
            max_tokens=300,
            stream=False
        )
        reply = response.choices[0].message.content

        # Force starter
        if not any(reply.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
            reply = f"Got you {reply}"
        return reply
    except Exception as e:
        return f"Say less {st.session_state.user_name} - Groq error: {str(e)}"

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown("### ⚡ Command Center")
    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.history = []; st.session_state.user_name = "Friend"

    if st.button("📤 Export Chat", use_container_width=True):
        chat_txt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.history])
        st.download_button("Download.txt", chat_txt, "simon_chat.txt")

    st.button("🧠 Reset Memory", use_container_width=True, on_click=lambda: save_memory())

    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("Messages", len(st.session_state.history))
    st.metric("Model", "Llama 3.3 70B via Groq")
    st.metric("Speed", "~200ms")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info(f"**User:** {st.session_state.user_name}\n**Creator:** Sean L. Matondo\n**Company:** Lite Wrld Gen")

# ====== MAIN CHAT ======
st.markdown("# 🔥 Simon v4.0 Pro")
st.markdown('<p class="subtitle">Created by Lite Wrld Gen | Powered by Groq Llama 3.3</p>', unsafe_allow_html=True)

# CHAT HISTORY
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT + UPLOAD
input_col, attach_col = st.columns([10,1])
with input_col:
    prompt = st.chat_input("Message Simon...")
with attach_col:
    uploaded = st.file_uploader("📎", type=['pdf','txt','png','jpg'], label_visibility="collapsed")

if prompt or uploaded:
    file_context = ""
    if uploaded:
        file_context = extract_file_text(uploaded)
        st.session_state.history.append({"role": "user", "content": f"📎 Uploaded: {uploaded.name}"})
        with st.chat_message("user"): st.markdown(f"📎 Uploaded: {uploaded.name}")

    if prompt:
        st.session_state.history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Simon is thinking..."):
            response = get_groq_response(prompt, file_context)
            audio = tts_audio(response) if "speak" in prompt.lower() else None

        st.session_state.history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
            if audio: st.markdown(audio, unsafe_allow_html=True)
        st.rerun()

st.caption(f"Simon v4.0 | Lite Wrld Gen © 2026")