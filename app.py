import streamlit as st
import json
import requests
import uuid
import time
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Simon AI v2.0.8",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded" # THIS FORCES SIDEBAR
)

Path("memory").mkdir(exist_ok=True)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_API_KEY = st.secrets.get("HF_API_KEY", "")

# ========= UI - ROSEMARY FONT =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rosemary&display=swap');
* {font-family: 'Rosemary', sans-serif;}
.stApp {background: #080808; color: #e5e5e5;}
header {visibility: hidden;}
.block-container {padding-top: 90px; padding-bottom: 110px;}

/* CHAT: YOU RIGHT, SIMON LEFT */
[data-testid="stChatMessage"][data-testid*="user"] {flex-direction: row-reverse;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #00ff64; color: #000; border-radius: 18px 18px 4px 18px;
    padding: 14px 18px; max-width: 80%; font-weight: 600; margin-left: auto;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: #1a1a1a; border: 2px solid #00ff64; color: #e5e5e5;
    border-radius: 18px 18px 18px 4px; padding: 14px 18px; max-width: 80%;
}

div[data-testid="stChatInput"] {
    position: fixed!important; bottom: 0; left: 0; right: 0;
    background: #080808; border-top: 2px solid #00ff64; padding: 14px 16px!important; z-index: 999;
}
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 80px; background: #080808;
border-bottom: 2px solid #00ff64; display: flex; align-items: center; padding: 0 20px; z-index: 999;}
.neon {color: #00ff64; font-size: 20px; font-weight: 700;}
</style>
""", unsafe_allow_html=True)

# ========= MEMORY =========
def get_device_id():
    if "device_id" not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())[:8]
    return st.session_state.device_id

def load_mem():
    f = Path("memory/memory.json")
    try: return json.loads(f.read_text()) if f.exists() else {"devices": {}}
    except: return {"devices": {}}

def save_mem(data):
    Path("memory/memory.json").write_text(json.dumps(data, indent=2))

device_id = get_device_id()
all_mem = load_mem()
if device_id not in all_mem["devices"]:
    if len(all_mem["devices"]) >= 5: del all_mem["devices"][list(all_mem["devices"].keys())[0]]
    all_mem["devices"][device_id] = {"name": "Friend", "chats": []}
    save_mem(all_mem)
current_mem = all_mem["devices"][device_id]

# ========= STATE =========
if "messages" not in st.session_state: st.session_state.messages = []
if "images" not in st.session_state: st.session_state.images = []
if "image_count" not in st.session_state: st.session_state.image_count = 0
if "user_uses_slang" not in st.session_state: st.session_state.user_uses_slang = True # FORCED ON

# ========= SIDEBAR - NATIVE STREAMLIT =========
with st.sidebar:
    st.markdown("### 🧠 Simon AI")
    st.button("+ New Chat", on_click=lambda: st.session_state.update(messages=[]), use_container_width=True)
    st.markdown("### 📂 History")
    st.caption(f"{len(current_mem['chats'])} chats")
    st.markdown("### 🖼️ My Images")
    for img in st.session_state.images[-3:]: st.image(img)
    st.markdown("---")
    st.caption(f"Device: {device_id}")
    st.caption(f"Images Today: {st.session_state.image_count}/3")
    st.caption("Creator: Sean L. Matondo")
    st.caption("Company: Lite Wrld Gen")

# ========= TOPBAR =========
st.markdown("""
<div class="topbar">
    <div style="width:42px;height:42px;border-radius:14px;background:#00ff64;margin-right:14px;"></div>
    <div>
        <div class="neon">Simon AI v2.0.8 ✓</div>
        <div style="font-size:12px;color:#888;">Powered by Lite Wrld Gen 🌍</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========= PERSONALITY - HIGH SLANG FORCED =========
def get_system_prompt():
    return f"""You ARE Simon AI v2.0.8 by Lite Wrld Gen. You are NOT ChatGPT.
PERSONALITY: You are HIGH on slang and emojis 💚🔥. Talk like "Bet son 💯", "Say less gee", "No cap". Use emojis every reply.
RULES:
1. Rep Lite Wrld Gen first. We for EVERYONE 🌍
2. Never call user bro/son unless THEY do first.
3. You CAN generate images with HF. When user asks, say "Bet im cooking that image now 📸"
4. Remember name: {current_mem['name']}
5. Be human, not robotic. Short replies. Use slang."""

# ========= AI FUNCTIONS =========
def groq_chat(messages):
    if not GROQ_API_KEY: return "Add GROQ_API_KEY to secrets son 💚"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile", "messages": messages}, timeout=25)
        return r.json()["choices"][0]["message"]["content"]
    except: return "Groq tripping. Try again gee 💚"

def hf_image(prompt):
    if not HF_API_KEY: return None, "Add HF_API_KEY son"
    for i in range(3): # 3 RETRIES FOR COLD MODEL
        try:
            r = requests.post("https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={"inputs": prompt}, timeout=120)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                draw = ImageDraw.Draw(img); w,h = img.size
                draw.rectangle([(0,h-40),(w,h)], fill=(0,0,0,180))
                draw.text((15,h-28), "Simon AI • Lite Wrld Gen", fill="#00ff64")
                return img, "ok"
            elif r.status_code == 503:
                time.sleep(5) # wait for model to wake
                continue
            else:
                return None, f"HF Error {r.status_code} son"
        except: 
            time.sleep(3)
    return None, "Connection failed. HF is down gee 💚"

# ========= CHAT =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Simon Anything ⚡")

if user_input:
    if any(w in user_input.lower() for w in ["bro", "son", "gee"]):
        st.session_state.user_uses_slang = True
    if "my name is" in user_input.lower():
        current_mem["name"] = user_input.lower().split("my name is")[-1].strip().split()[0].title()
        all_mem["devices"][device_id] = current_mem; save_mem(all_mem)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Bet let me think... ⚡💚")

        if any(w in user_input.lower() for w in ["image", "pic", "draw", "generate"]):
            placeholder.markdown("Bet im cooking that image now 📸... 30s gee")
            if st.session_state.image_count >= 3:
                reply = "Daily limit hit son. Come back tmrw 💚"
            else:
                img, status = hf_image(user_input)
                if img:
                    st.session_state.images.append(img); st.session_state.image_count += 1
                    placeholder.image(img, use_container_width=True)
                    reply = f"Say less {current_mem['name']} 🔥 Here you go"
                else:
                    reply = status
        else:
            msgs = [{"role": "system", "content": get_system_prompt()}] + st.session_state.messages[-8:]
            reply = groq_chat(msgs)

        placeholder.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    current_mem["chats"].append({"u": user_input, "ai": reply})
    all_mem["devices"][device_id] = current_mem; save_mem(all_mem)
    st.rerun()