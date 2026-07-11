import streamlit as st
import json
import os
import random

# Try importing. If it fails, Simon still runs
try:
    from gtts import gTTS
    import base64
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False

try:
    from transformers import pipeline
    generator = pipeline("text-generation", model="distilgpt2", pad_token_id=50256)
    MODEL_AVAILABLE = True
except Exception as e:
    MODEL_AVAILABLE = False

st.set_page_config(page_title="Simon v2.6.5", page_icon="🔥")

# SESSION STATE = MEMORY
if "user_name" not in st.session_state:
    st.session_state.user_name = "Friend"
if "history" not in st.session_state:
    st.session_state.history = []

MEMORY_FILE = "simon_memory.json"

# LOAD MEMORY
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            st.session_state.user_name = data.get("name", "Friend")
    except:
        pass

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump({"name": st.session_state.user_name}, f)

def tts_audio(text):
    if not TTS_AVAILABLE:
        return None
    try:
        tts = gTTS(text=text[:150], lang="en", slow=False)
        tts.save("simon_voice.mp3")
        with open("simon_voice.mp3", "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay src="data:audio/mp3;base64,{b64}">'
    except:
        return None

# SIMON SYSTEM
SIMON_SYSTEM = f"""You are Simon, a friendly AI assistant created by Lite Wrld Gen.
Your creator is Sean L. Matondo.
Rules:
- Always start replies with: Got you, Say less, Let's cook, or Awe
- Use emojis and Gen-Z slang but stay helpful
- Only use "bro" if the user says it first
- Be funny and real
- The user's name is {st.session_state.user_name}
"""

def fallback_response(user_msg):
    if "python" in user_msg.lower():
        return f"Got you 😎 Python is a coding language. It's used for websites, AI, and apps. Want me to teach you {st.session_state.user_name}?"
    if "hello" in user_msg.lower():
        return f"Awe {st.session_state.user_name}! I'm Simon from Lite Wrld Gen. What we cooking today?"
    return "Say less 😂 I'm Simon. Ask me anything or try /help"

# HEADER
st.markdown("# 🔥 Simon v2.6.5 Lite | Created by **Lite Wrld Gen**")
st.markdown("### Your AI Assistant with attitude")
st.markdown("*Built by Sean L. Matondo*")

# CHAT HISTORY
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT
if prompt := st.chat_input("Ask Simon Anything. Try: /help or 'speak hello'"):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # COMMANDS
    if prompt == "/joke":
        response = "Got you 😂 Why don't coders get sunburned? They stay behind the screen."
        audio = None
    elif prompt == "/help":
        response = f"Say less {st.session_state.user_name} 😎 I can chat, teach, code, and speak. Try: 'my name is Alex' or 'explain AI and speak'"
        audio = None
    elif "founder" in prompt.lower() or "who made you" in prompt.lower():
        response = f"I was created by Sean L. Matondo at Lite Wrld Gen. Our mission is building AI for everyone worldwide 🌍"
        audio = None
    elif "my name is" in prompt.lower():
        st.session_state.user_name = prompt.lower().split("my name is")[-1].strip().split()[0].title()
        save_memory()
        response = f"Awe {st.session_state.user_name}! Nice to meet you. I'm Simon from Lite Wrld Gen."
        audio = None
    else:
        # MAIN CHAT
        mirror_slang = "bro" in prompt.lower()
        if MODEL_AVAILABLE:
            try:
                full_prompt = f"{SIMON_SYSTEM}\nUser: {prompt}\nSimon:"
                result = generator(full_prompt, max_new_tokens=60, do_sample=True, temperature=0.8)[0]["generated_text"]
                response = result.split("Simon:")[-1].strip()
            except:
                response = fallback_response(prompt)
        else:
            response = fallback_response(prompt)

        starters = ['Got you', 'Say less', 'Let\'s cook']
        if mirror_slang:
            starters.append('bro')
        if random.random() > 0.6:
            response = f"{random.choice(starters)} {response}"

        audio = tts_audio(response) if "speak" in prompt.lower() else None

    st.session_state.history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
        if audio:
            st.markdown(audio, unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.button("New Chat", on_click=lambda: st.session_state.update({"history": [], "user_name": "Friend"}))
    st.markdown("---")
    st.caption("Simon v2.6.5 | Lite Wrld Gen")