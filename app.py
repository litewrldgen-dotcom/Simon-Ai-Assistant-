import streamlit as st
import json
import os
import random

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
        model="Qwen/Qwen2-0.5B-Instruct",
        pad_token_id=151643
    )
    MODEL_AVAILABLE = True
except:
    MODEL_AVAILABLE = False

st.set_page_config(page_title="Simon", page_icon="🔥", layout="centered")

# ====== CLEAN CSS: WHATSAPP STYLE ======
st.markdown("""
<style>
   .main {background-color: #111b21;}
    [data-testid="stChatMessage"] {padding: 8px 0;}
    [data-testid="stChatMessageContent"] {font-size: 16px;}

    /* USER RIGHT - GREEN */
    [data-testid="stChatMessage"][data-testid*="user"] {
        justify-content: flex-end;
    }
    [data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
        background: #005c4b;
        color: white;
        border-radius: 12px 0px 12px 12px;
        padding: 10px 14px;
        max-width: 75%;
        margin-left: auto;
    }

    /* SIMON LEFT - GRAY */
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        justify-content: flex-start;
    }
    [data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
        background: #202c33;
        color: #e9edef;
        border-radius: 0px 12px 12px 12px;
        padding: 10px 14px;
        max-width: 75%;
    }
    h1 {text-align: center; color: #00a884;}
</style>
""", unsafe_allow_html=True)

# ====== SESSION ======
if "user_name" not in st.session_state:
    st.session_state.user_name = "Friend"
if "history" not in st.session_state:
    st.session_state.history = []

MEMORY_FILE = "simon_memory.json"

if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as f:
            st.session_state.user_name = json.load(f).get("name", "Friend")
    except: pass

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump({"name": st.session_state.user_name}, f)

def tts_audio(text):
    if not TTS_AVAILABLE: return None
    try:
        tts = gTTS(text=text[:200], lang="en")
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay src="data:audio/mp3;base64,{b64}">'
    except: return None

# ====== SIMON BRAIN - STRICT RULES ======
def get_simon_response(user_msg):
    msg = user_msg.lower()

    # HARDCODED ANSWERS SO IT DOESN'T DUMB OUT
    if msg in ["hi", "hello", "hey"]:
        return f"Got you 😎 Hey {st.session_state.user_name}! I'm Simon from Lite Wrld Gen. What we doing today?"
    if "mummy" in msg:
        return "Say less 😅 A mummy is an ancient Egyptian person whose body was preserved after death. Not spaghetti lol"
    if "founder" in msg or "who made you" in msg:
        return f"Awe 🙏 I was created by Sean L. Matondo at Lite Wrld Gen. We're building AI for everyone."
    if "python" in msg:
        return f"Let's cook 🐍 Python is a programming language. It's what I run on. Want me to teach you some code?"
    if msg == "/joke":
        return "Got you 😂 Why did the programmer quit his job? He didn't get arrays."
    if msg == "/help":
        return f"Say less {st.session_state.user_name} 😎 I can chat, code, explain stuff. Try: 'my name is Alex' or 'explain black holes and speak'"
    if "my name is" in msg:
        name = msg.split("my name is")[-1].strip().split()[0].title()
        st.session_state.user_name = name
        save_memory()
        return f"Awe {name}! Nice to meet you. I'm Simon 🔥"

    # IF MODEL WORKS
    if MODEL_AVAILABLE:
        try:
            system = f"""You are Simon, AI by Lite Wrld Gen. Creator: Sean L. Matondo.
Rules: 1.Start with Got you/Say less/Let's cook/Awe 2.Be smart and accurate 3.Use {st.session_state.user_name}'s name 4.Use emojis 5.Only say bro if user says bro"""
            prompt = f"<|im_start|>system\n{system}\n<|im_end|>\n<|im_start|>user\n{user_msg}\n<|im_end|>\n<|im_start|>assistant\n"
            result = generator(prompt, max_new_tokens=80, temperature=0.7)[0]["generated_text"]
            response = result.split("<|im_start|>assistant")[-1].replace("<|im_end|>", "").strip()

            # Force starter
            if not any(response.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
                response = f"Got you {response}"
            return response
        except:
            return f"Say less {st.session_state.user_name} - I'm here. Ask me anything!"

    return f"Got you {st.session_state.user_name} - I'm Simon. What's up?"

# ====== UI ======
st.markdown("# 🔥 Simon")
st.markdown("*Created by Lite Wrld Gen*")

# CHAT
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT
if prompt := st.chat_input("Message Simon..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = get_simon_response(prompt)
    audio = tts_audio(response) if "speak" in prompt.lower() else None

    st.session_state.history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
        if audio:
            st.markdown(audio, unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.button("New Chat", on_click=lambda: st.session_state.update({"history": [], "user_name": "Friend"}))
    st.caption("Simon v2.9.0 | Lite Wrld Gen")