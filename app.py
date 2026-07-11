import streamlit as st
import json
import os
import random
import time

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
        pad_token_id=151643,
        device_map="auto"
    )
    MODEL_AVAILABLE = True
except Exception as e:
    MODEL_AVAILABLE = False

st.set_page_config(
    page_title="Simon v2.8.0 | Lite Wrld Gen",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CUSTOM CSS: META LEVEL UI ======
st.markdown("""
<style>
   .main {background-color: #0E1117;}
   .stChatMessage[data-testid="chat-message-user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 18px;
        margin-left: 25%;
        padding: 12px 16px;
    }
   .stChatMessage[data-testid="chat-message-assistant"] {
        background: #262730;
        color: #FA;
        border-radius: 18px;
        margin-right: 25%;
        padding: 12px 16px;
        border: 1px solid #3D3D3D;
    }
    h1 {color: #FF4B4B;}
</style>
""", unsafe_allow_html=True)

# ====== SESSION STATE ======
if "user_name" not in st.session_state:
    st.session_state.user_name = "Friend"
if "history" not in st.session_state:
    st.session_state.history = []
if "simon_rules" not in st.session_state:
    st.session_state.simon_rules = True

MEMORY_FILE = "simon_memory.json"

# ====== LOAD MEMORY ======
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

# ====== TTS ======
def tts_audio(text):
    if not TTS_AVAILABLE: return None
    try:
        tts = gTTS(text=text[:200], lang="en", slow=False)
        tts.save("simon_voice.mp3")
        with open("simon_voice.mp3", "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio autoplay src="data:audio/mp3;base64,{b64}">'
    except:
        return None

# ====== SIMON SYSTEM PROMPT - ALL 7 RULES BACK ======
def build_system_prompt():
    return f"""<|im_start|>system
You are Simon v2.8.0, an elite AI assistant created by Lite Wrld Gen.
Founder: Sean L. Matondo. Mission: Building AI for everyone worldwide.

STRICT RULES:
1. ALWAYS start replies with: "Got you", "Say less", "Let's cook", or "Awe"
2. Use emojis and Gen-Z slang but remain professional and ACCURATE
3. NEVER use "bro" unless the user says "bro" first
4. Be helpful, funny, and real. Fact-check yourself
5. Remember the user's name is {st.session_state.user_name}. Use it naturally
6. If user says "speak" you must add voice
7. If asked about founder, say: "I was created by Sean L. Matondo at Lite Wrld Gen"

PERSONALITY: Smart, confident, slightly cocky but helpful. Like ChatGPT meets your cool older brother.
<|im_end|>"""

def build_prompt(user_msg):
    system = build_system_prompt()
    return f"""{system}
<|im_start|>user
{user_msg}
<|im_end|>
<|im_start|>assistant
"""

# ====== SMART FALLBACK ======
def fallback_response(user_msg):
    msg = user_msg.lower()
    if "mummy" in msg:
        return f"Got you 😎 A mummy is an ancient Egyptian body that was preserved after death. Not spaghetti bro, that's pasta 😂"
    if "python" in msg:
        return f"Say less {st.session_state.user_name} 🐍 Python is a programming language used for AI, web dev, and automation. Want me to teach you?"
    if "hello" in msg or "hi" in msg:
        return f"Awe {st.session_state.user_name}! I'm Simon from Lite Wrld Gen. What are we building today?"
    return f"Let's cook 🔥 I'm Simon. Ask me anything - coding, learning, or just chat."

# ====== HEADER ======
col1, col2 = st.columns([4,1])
with col1:
    st.markdown("# 🔥 Simon v2.8.0 Pro | **Lite Wrld Gen**")
    st.markdown("### Powered by Qwen2-0.5B | Built like Meta")
with col2:
    st.markdown(f"**User:** {st.session_state.user_name}")

# ====== CHAT HISTORY ======
chat_container = st.container()
with chat_container:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ====== INPUT ======
if prompt := st.chat_input("Ask Simon anything... /help for commands"):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Simon is thinking..."):
        time.sleep(0.3) # Feels more premium

        # COMMANDS
        if prompt == "/joke":
            response = "Got you 😂 Why don't programmers like nature? Too many bugs."
        elif prompt == "/help":
            response = f"Say less {st.session_state.user_name} 😎 Commands: /joke, /help. Also try: 'my name is Alex' or 'explain AI and speak'"
        elif "founder" in prompt.lower() or "who made you" in prompt.lower():
            response = f"I was created by Sean L. Matondo at Lite Wrld Gen. Our mission is building AI for everyone worldwide 🌍"
        elif "my name is" in prompt.lower():
            st.session_state.user_name = prompt.lower().split("my name is")[-1].strip().split()[0].title()
            save_memory()
            response = f"Awe {st.session_state.user_name}! Nice to meet you. I'm Simon from Lite Wrld Gen."
        else:
            # MAIN QWEN CHAT
            mirror_slang = "bro" in prompt.lower()
            if MODEL_AVAILABLE:
                try:
                    full_prompt = build_prompt(prompt)
                    result = generator(full_prompt, max_new_tokens=120, do_sample=True, temperature=0.75, top_p=0.9)[0]["generated_text"]
                    response = result.split("<|im_start|>assistant")[-1].replace("<|im_end|>", "").strip()

                    # Safety: Force rule 1 if model forgets
                    if not any(response.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
                        starters = ['Got you', 'Say less', 'Let\'s cook']
                        if mirror_slang: starters.append('bro')
                        response = f"{random.choice(starters)} {response}"

                except:
                    response = fallback_response(prompt)
            else:
                response = fallback_response(prompt)

        audio = tts_audio(response) if "speak" in prompt.lower() else None

    st.session_state.history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
        if audio:
            st.markdown(audio, unsafe_allow_html=True)

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.history = []
        st.session_state.user_name = "Friend"
    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("Messages", len(st.session_state.history))
    st.metric("Model", "Qwen2-0.5B")
    st.markdown("---")
    st.caption("Simon v2.8.0 Pro | Lite Wrld Gen")
    st.caption("Built by Sean L. Matondo")