import streamlit as st
import json
import requests
import uuid
import time
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Simon AI v4.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

Path("memory").mkdir(exist_ok=True)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_API_KEY = st.secrets.get("HF_API_KEY", "")

# ========= AMAZING UI - NEON + CHATGPT MIX =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rosemary&display=swap');
* {font-family: 'Rosemary', system-ui, sans-serif;}
.stApp {background: #080808; color: #e5e5e5;}
header {visibility: hidden;}
.block-container {padding-top: 90px; padding-bottom: 120px; max-width: 850px;}

/* SIDEBAR NEON */
section[data-testid="stSidebar"] {
    background: #0a0a0a!important;
    border-right: 2px solid #00ff64!important;
}

/* TOPBAR BIG */
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 80px; background: #080808;
border-bottom: 2px solid #00ff64; display: flex; align-items: center; padding: 0 20px; z-index: 999;}
.neon {color: #00ff64; font-size: 22px; font-weight: 700; text-shadow: 0 0 10px #00ff64;}
.sub {font-size: 12px; color: #888;}

/* CHAT BUBBLES */
[data-testid="stChatMessage"][data-testid*="user"] {justify-content: flex-end!important;}
[data-testid="stChatMessage"][data-testid*="assistant"] {justify-content: flex-start!important;}

[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #00ff64; color: #000; border-radius: 18px 18px 4px 18px;
    padding: 14px 18px; max-width: 80%; font-weight: 600;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: #121212; border: 1px solid #00ff64; color: #e5e5e5;
    border-radius: 18px 18px 18px 4px; padding: 14px 18px; max-width: 80%;
}

/* BUTTONS THAT WORK */
.action-btn {background: transparent; border: 1px solid #333; color: #888; 
border-radius: 8px; padding: 4px 10px; margin-right: 8px; cursor: pointer; font-size: 14px;}
.action-btn:hover {border-color: #00ff64; color: #00ff64;}

/* BOTTOM INPUT */
div[data-testid="stChatInput"] {
    position: fixed!important; bottom: 0; left: 0; right: 0;
    background: #080808; border-top: 2px solid #00ff64; padding: 16px 20px!important; z-index: 999;
}
input::placeholder {color: #00ff64!important;}
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
if "user_uses_slang" not in st.session_state: st.session_state.user_uses_slang = True

# ========= SIDEBAR =========
with st.sidebar:
    st.markdown("### ⚡ Simon AI v4.0")
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("### 📂 History")
    st.caption(f"{len(current_mem['chats'])} chats saved")
    st.markdown("### 🖼️ Gallery")
    for img in st.session_state.images[-4:]: st.image(img)
    st.markdown("---")
    st.caption(f"Device: {device_id}")
    st.caption(f"Images Today: {st.session_state.image_count}/3")
    st.caption("Creator: Sean L. Matondo")
    st.caption("Lite Wrld Gen 🌍")

# ========= TOPBAR =========
st.markdown("""
<div class="topbar">
    <div style="width:45px;height:45px;border-radius:14px;background:#00ff64;box-shadow:0 0 15px #00ff64;margin-right:15px;"></div>
    <div>
        <div class="neon">Simon AI v4.0</div>
        <div class="sub">Powered by Lite Wrld Gen</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========= SIMON BRAIN - FULL PERSONALITY =========
def get_system_prompt():
    slang = "Use slang like 'bet', 'say less', 'no cap', 'gee' and emojis 💚🔥. Be chill." if st.session_state.user_uses_slang else "Be warm and helpful."
    return f"""You are Simon AI v4.0 by Lite Wrld Gen.
CRITICAL RULES:
1. You are for EVERYONE 🌍. Contact: support@litewrldgen.com
2. {slang}
3. Never call user bro/son unless THEY start it.
4. You CAN generate images. Say "Bet im cooking that 📸" first.
5. If images fail: "HF tripping rn gee, try again in 2 💚"
6. Remember name: {current_mem['name']}. Be human, short, real."""

# ========= AI FUNCTIONS - FIXED =========
def groq_chat(messages):
    if not GROQ_API_KEY: return "Add GROQ_API_KEY to secrets son 💚"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.9}, timeout=30)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e: 
        return f"Groq error: {str(e)[:50]} 💚"

def hf_image(prompt):
    if not HF_API_KEY: return None, "Add HF_API_KEY son"
    
    models = [
        "black-forest-labs/FLUX.1-schnell",
        "stabilityai/stable-diffusion-xl-base-1.0"
    ]
    
    for model in models:
        try:
            r = requests.post(f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={"inputs": prompt, "options": {"wait_for_model": True}}, timeout=90) # 90s + wait flag
            
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                draw = ImageDraw.Draw(img); w,h = img.size
                draw.rectangle([(0,h-40),(w,h)], fill=(0,0,0,180))
                draw.text((15,h-28), "Simon AI • Lite Wrld Gen", fill="#00ff64")
                return img, "ok"
        except Exception as e:
            st.write(f"Model {model} error: {e}")
            continue
    
    return None, "Both models sleeping 😭 Wait 2 mins and try again gee 💚"

# ========= CHAT =========
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            c1,c2,c3,c4,c5 = st.columns(5)
            with c1: st.button("📋", key=f"copy{i}")
            with c2: st.button("👍", key=f"like{i}")
            with c3: st.button("👎", key=f"dislike{i}")
            with c4: st.button("🔊", key=f"speak{i}")
            with c5: st.button("⋮", key=f"more{i}")

user_input = st.chat_input("Ask Simon Anything ⚡")

if user_input:
    if any(w in user_input.lower() for w in ["bro", "son", "gee", "no cap"]):
        st.session_state.user_uses_slang = True
    if "my name is" in user_input.lower():
        current_mem["name"] = user_input.lower().split("my name is")[-1].strip().split()[0].title()
        all_mem["devices"][device_id] = current_mem; save_mem(all_mem)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking... ⚡")

        if any(w in user_input.lower() for w in ["image", "pic", "draw", "generate"]):
            placeholder.markdown("Bet im cooking that 📸 This takes 30s gee...")
            if st.session_state.image_count >= 3:
                reply = "Daily limit hit son. Come back tmrw 💚"
                placeholder.markdown(reply)
            else:
                img, status = hf_image(user_input)
                if img:
                    st.session_state.images.append(img); st.session_state.image_count += 1
                    placeholder.image(img, use_container_width=True)
                    reply = f"Say less {current_mem['name']} 🔥"
                else:
                    reply = status
                    placeholder.markdown(reply)
        else:
            msgs = [{"role": "system", "content": get_system_prompt()}] + st.session_state.messages[-10:]
            reply = groq_chat(msgs)
            placeholder.markdown(reply)

        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.button("📋", key=f"copy_new")
        with c2: st.button("👍", key=f"like_new")
        with c3: st.button("👎", key=f"dislike_new")
        with c4: st.button("🔊", key=f"speak_new")
        with c5: st.button("⋮", key=f"more_new")

    st.session_state.messages.append({"role": "assistant", "content": reply})
    current_mem["chats"].append({"u": user_input, "ai": reply})
    all_mem["devices"][device_id] = current_mem; save_mem(all_mem)
    st.rerun()