import streamlit as st
import json
import os
import random
import torch
from datetime import datetime

# ====== CONFIG ======
try:
    from gtts import gTTS
    import base64
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False

try:
    from transformers import pipeline
    generator = pipeline(
        "text-generation",
        model="microsoft/Phi-3-mini-4k-instruct",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    MODEL_AVAILABLE = True
except:
    MODEL_AVAILABLE = False

st.set_page_config(page_title="Simon v3.1", page_icon="🔥", layout="wide")

# ====== PREMIUM CSS ======
st.markdown("""
<style>
 .main {background-color: #0a0e13;}
  h1 {color: #00FF88; text-align: center;}
 .subtitle {text-align: center; color: #888; margin-bottom: 20px;}

  /* USER RIGHT - TEAL */
  [data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
      background: #00a884; color: white; border-radius: 16px 4px 16px 16px;
      padding: 12px 16px; max-width: 70%; margin-left: auto; font-size: 16px;
  }
  /* SIMON LEFT - DARK */
  [data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
      background: #1f2c33; color: #e9edef; border-radius: 4px 16px 16px 16px;
      padding: 12px 16px; max-width: 70%; border-left: 3px solid #00FF88; font-size: 16px;
  }
  /* SIDEBAR */
  [data-testid="stSidebar"] {background: #111b21;}
 .sidebar-btn {margin-bottom: 8px;}
</style>
""", unsafe_allow_html=True)

# ====== SESSION ======
if "user_name" not in st.session_state: st.session_state.user_name = "Friend"
if "history" not in st.session_state: st.session_state.history = []
if "uploaded_files" not in st.session_state: st.session_state.uploaded_files = []

MEMORY_FILE = "simon_memory.json"
if os.path.exists(MEMORY_FILE):
    try: st.session_state.user_name = json.load(open(MEMORY_FILE)).get("name", "Friend")
    except: pass

def save_memory(): json.dump({"name": st.session_state.user_name}, open(MEMORY_FILE, "w"))

def tts_audio(text):
    if not TTS_AVAILABLE: return None
    try:
        tts = gTTS(text=text[:200], lang="en"); tts.save("voice.mp3")
        b64 = base64.b64encode(open("voice.mp3","rb").read()).decode()
        return f'<audio autoplay src="data:audio/mp3;base64,{b64}">'
    except: return None

LITE_WRLD_INFO = "Lite Wrld Gen is an AI company founded by Sean L. Matondo. We build fast, free AI assistants like Simon for everyone worldwide."

# ====== SIMON BRAIN ======
def get_simon_response(user_msg, file_info=""):
    msg = user_msg.lower()
    context = f"User uploaded: {file_info}" if file_info else ""

    if msg in ["hi", "hello"]: return f"Got you 😎 Awe {st.session_state.user_name}! I'm Simon v3.1. What's cooking?"
    if "mummy" in msg: return "Say less 😅 A mummy is an ancient Egyptian body that was preserved."
    if "founder" in msg or "who made you" in msg: return f"Awe 🙏 I was created by Sean L. Matondo at Lite Wrld Gen."
    if "lite wrld gen" in msg: return f"Got you 🔥 {LITE_WRLD_INFO}"
    if msg == "/joke": return "Got you 😂 Why do programmers hate nature? Too many bugs."
    if msg == "/help": return f"Say less {st.session_state.user_name} 😎 Try: /joke /export /clear or upload files with the paperclip"
    if "my name is" in msg:
        name = msg.split("my name is")[-1].strip().split()[0].title()
        st.session_state.user_name = name; save_memory()
        return f"Awe {name}! Locked in. I'm Simon 🔥"

    if MODEL_AVAILABLE:
        try:
            system = f"""You are Simon v3.1, elite AI by Lite Wrld Gen. Founder: Sean L. Matondo.
Rules: 1.Start with Got you/Say less/Let's cook/Awe 2.Be accurate 3.User name: {st.session_state.user_name} 4.Use emojis"""
            prompt = f"<|system|>\n{system}\nContext: {context}\n<|end|>\n<|user|>\n{user_msg}\n<|end|>\n<|assistant|>\n"
            result = generator(prompt, max_new_tokens=150, temperature=0.7)[0]["generated_text"]
            response = result.split("<|assistant|>")[-1].split("<|end|>")[0].strip()
            if not any(response.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
                response = f"Got you {response}"
            return response
        except:
            return f"Say less {st.session_state.user_name} - Brain lag. Try again!"
    return f"Got you - I'm Simon from Lite Wrld Gen."

# ====== HEADER ======
st.markdown("# 🔥 Simon v3.1 Pro Max")
st.markdown('<p class="subtitle">Created by Lite Wrld Gen | Phi-3 Brain</p>', unsafe_allow_html=True)

# ====== LAYOUT ======
col1, col2 = st.columns([3,1])

with col1:
    # CHAT
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "file" in msg: st.caption(f"📎 {msg['file']}")

    # INPUT ROW WITH ATTACHMENT
    input_col, attach_col, send_col = st.columns([8,1,1])
    with input_col:
        prompt = st.chat_input("Message Simon...")
    with attach_col:
        uploaded = st.file_uploader("📎", type=['png','jpg','jpeg','mp3','wav','pdf','txt'], label_visibility="collapsed")
    with send_col:
        send = st.button("↑", use_container_width=True)

    if prompt or uploaded:
        file_info = ""
        if uploaded:
            file_info = f"{uploaded.name} ({uploaded.type})"
            st.session_state.uploaded_files.append(uploaded.name)
            st.session_state.history.append({"role": "user", "content": f"Uploaded {file_info}", "file": file_info})
            with st.chat_message("user"):
                st.markdown(f"📎 Uploaded: {file_info}")

        if prompt:
            st.session_state.history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            response = get_simon_response(prompt, file_info)
            audio = tts_audio(response) if "speak" in prompt.lower() else None

            st.session_state.history.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
                if audio: st.markdown(audio, unsafe_allow_html=True)

with col2:
    st.markdown("### ⚡ Command Center")

    st.markdown("#### 🛠️ Tools")
    if st.button("🗑️ New Chat", use_container_width=True, key="new"):
        st.session_state.history = []; st.session_state.user_name = "Friend"
    if st.button("📤 Export Chat", use_container_width=True, key="export"):
        chat_txt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.history])
        st.download_button("Download.txt", chat_txt, "simon_chat.txt")
    if st.button("🧠 Memory Reset", use_container_width=True, key="mem"):
        st.session_state.user_name = "Friend"; save_memory()

    st.markdown("---")
    st.markdown("#### 📊 Stats")
    st.metric("Messages", len(st.session_state.history))
    st.metric("Files Uploaded", len(st.session_state.uploaded_files))
    st.metric("Model", "Phi-3-Mini 3.8B")

    st.markdown("---")
    st.markdown("#### ℹ️ About")
    st.info(f"**User:** {st.session_state.user_name}\n\n**Creator:** Sean L. Matondo\n\n**Company:** Lite Wrld Gen")

    st.markdown("---")
    st.markdown("#### 🎯 Quick Prompts")
    if st.button("Who built you?", use_container_width=True): st.rerun()
    if st.button("Explain AI", use_container_width=True): st.rerun()
    if st.button("Write code", use_container_width=True): st.rerun()

st.caption(f"Simon v3.1 Pro Max | Lite Wrld Gen © 2026 | {datetime.now().strftime('%H:%M')}")