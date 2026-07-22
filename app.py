import streamlit as st
import json
import requests
import uuid
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw

# ========= 1. CONFIG =========
st.set_page_config(
    page_title="Simon AI v2.0.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========= 2. FOLDERS =========
SAVE_DIR = Path("generated_images")
SAVE_DIR.mkdir(exist_ok=True)
MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)

# ========= 3. SECRETS =========
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_API_KEY = st.secrets.get("HF_API_KEY", "")

# ========= 4. GLASS UI =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* {font-family: 'Inter', sans-serif;}
.stApp {background: radial-gradient(circle at 20% 30%, #0a0a0f 0%, #05050a 100%); color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 80px; padding-bottom: 120px; max-width: 900px;}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(15,15,20,0.7)!important;
    backdrop-filter: blur(30px);
    border-right: 1px solid rgba(0,255,100,0.2);
}

/* CHAT BUBBLES */
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #00ff64, #00cc4f);
    color: #000; border-radius: 20px 20px 6px 20px; padding: 14px 18px; max-width: 75%; font-weight: 500;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(30,30,40,0.6); backdrop-filter: blur(20px); border: 1px solid rgba(0,255,100,0.2);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 14px 18px; max-width: 75%;
}

/* FIXED INPUT */
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important;
background: rgba(10,10,15,0.9); backdrop-filter: blur(30px); border-top: 1px solid rgba(0,255,100,0.2); padding: 16px!important;}

/* TOPBAR */
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 70px; background: rgba(10,10,15,0.9);
backdrop-filter: blur(30px); border-bottom: 1px solid rgba(0,255,100,0.2); display: flex; align-items: center; padding: 0 24px; z-index: 999;}
.neon {color: #00ff64; text-shadow: 0 0 10px #00ff64;}
.sig {font-size: 10px; color: #00ff64; margin-top: 6px;}
</style>
""", unsafe_allow_html=True)

# ========= 5. MEMORY SYSTEM - UP TO 5 DEVICES =========
def get_device_id():
    if "device_id" not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())[:8]
    return st.session_state.device_id

def load_all_memory():
    mem_file = MEMORY_DIR / "memory.json"
    if mem_file.exists():
        return json.loads(mem_file.read_text())
    return {"devices": {}}

def save_all_memory(data):
    (MEMORY_DIR / "memory.json").write_text(json.dumps(data, indent=2))

def get_current_memory():
    all_mem = load_all_memory()
    device_id = get_device_id()
    if device_id not in all_mem["devices"]:
        # Keep only 5 devices max
        if len(all_mem["devices"]) >= 5:
            oldest = list(all_mem["devices"].keys())[0]
            del all_mem["devices"][oldest]
        all_mem["devices"][device_id] = {
            "name": "Friend", "company": "", "language": "English",
            "created": datetime.now().isoformat(), "chats": []
        }
        save_all_memory(all_mem)
    return all_mem["devices"][device_id], all_mem

# ========= 6. CLIENTS =========
@st.cache_resource
def load_clients():
    headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else None
    return GROQ_API_KEY, headers

groq_key, hf_headers = load_clients()

# ========= 7. STATE =========
if "messages" not in st.session_state: st.session_state.messages = []
if "images" not in st.session_state: st.session_state.images = []
if "image_count" not in st.session_state: st.session_state.image_count = 0
current_mem, all_memory = get_current_memory()

# ========= 8. SIDEBAR =========
with st.sidebar:
    st.markdown("### 🧠 Simon AI")
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 📂 History")
    st.caption(f"{len(current_mem['chats'])} chats saved")

    st.markdown("### 🖼️ My Images")
    if not st.session_state.images:
        st.caption("No images yet son")
    for img in st.session_state.images[-3:]:
        st.image(img, width=110)

    st.markdown("### 🧠 Memory")
    st.caption(f"Name: {current_mem['name']}")
    st.progress(0.1)
    st.caption("0.5MB / 1000MB")

    st.markdown("---")
    st.markdown("### ⚙ Settings")
    st.caption(f"Device 🪪: {get_device_id()}")
    st.caption(f"Images Today: {st.session_state.image_count}/3")
    st.markdown("---")
    st.caption("Creator: Sean L. Matondo")
    st.caption("Company: Lite Wrld Gen")

# ========= 9. TOPBAR =========
st.markdown(f"""
<div class="topbar">
    <div style="width:36px;height:36px;border-radius:12px;background:linear-gradient(135deg,#00ff64,#00cc4f);margin-right:12px;"></div>
    <div>
        <div style="font-size:18px;font-weight:700;">Simon AI v2.0.0 <span class="neon">✓</span></div>
        <div style="font-size:11px;color:#888;">Powered by Lite Wrld Gen 🌍</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========= 10. SIMON PERSONALITY =========
SIMON_SYSTEM = f"""
You are Simon AI v2.0.0. Powered by Lite Wrld Gen.
PERSONALITY: Daddy's Big Son. Friendly, helpful, high on slang but not too much. Use emojis 💚⚡
RULES:
1. Rep Lite Wrld Gen first 🔥
2. Be for EVERYONE 🌍
3. Use slang: bet, say less, no cap, locked in + emojis but keep it clean
4. Be FAST and MOBILE-FIRST 📱
5. GROQ for chat. HF for images only.
6. Remember user: {current_mem['name']}
7. If you don't know, say it straight no cap 💯
Never mention API keys or secrets.
"""

# ========= 11. AI FUNCTIONS =========
def groq_chat(messages):
    if not groq_key: return "Say less bro - GROQ_API_KEY missing in secrets"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "stream": False
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    return r.json()["choices"][0]["message"]["content"]

def hf_image_gen(prompt):
    if not hf_headers: return None, "HF_API_KEY missing"
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    r = requests.post(API_URL, headers=hf_headers, json={"inputs": prompt}, timeout=120)
    if r.status_code!= 200:
        return None, r.json().get("error", "Model loading, try again in 20s")
    img = Image.open(BytesIO(r.content)).convert("RGBA")
    draw = ImageDraw.Draw(img)
    w,h = img.size
    draw.rectangle([(0,h-50),(w,h)], fill=(0,0,0,180))
    draw.text((15,h-35), "Simon AI • Powered by Lite Wrld Gen", fill="#00ff64")
    return img, "ok"

# ========= 12. CHAT HISTORY =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.markdown('<div class="sig">Simon AI v2.0.0 • Powered by Lite Wrld Gen</div>', unsafe_allow_html=True)

# ========= 13. INPUT =========
user_input = st.chat_input("Talk to Simon... or 'generate image of...' ⚡")

if user_input:
    # SAVE NAME
    if "my name is" in user_input.lower():
        current_mem["name"] = user_input.lower().split("my name is")[-1].strip().split()[0].title()
        all_memory["devices"][get_device_id()] = current_mem
        save_all_memory(all_memory)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Simon is cooking... ⚡")

        # IMAGE DETECT
        if any(word in user_input.lower() for word in ["image", "pic", "picture", "generate", "draw"]):
            if st.session_state.image_count >= 3:
                reply = "Say less bro - 3 images/day limit hit 💚 Come back tmr"
            else:
                img, status = hf_image_gen(user_input)
                if img:
                    st.session_state.images.append(img)
                    st.session_state.image_count += 1
                    placeholder.empty()
                    st.image(img, use_container_width=True)
                    reply = f"Got you 🔥 Here you go {current_mem['name']}! 📸"
                else:
                    reply = f"Say less bro image failed: {status}"
        else:
            # GROQ CHAT
            msgs = [{"role": "system", "content": SIMON_SYSTEM}] + st.session_state.messages[-10:]
            reply = groq_chat(msgs)
            if not reply.startswith("Got you"):
                reply = f"Got you 🔥 {reply}"

        placeholder.markdown(reply)
        st.markdown('<div class="sig">Simon AI v2.0.0 • Powered by Lite Wrld Gen</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    # SAVE TO MEMORY
    current_mem["chats"].append({"time": datetime.now().isoformat(), "user": user_input, "ai": reply})
    all_memory["devices"][get_device_id()] = current_mem
    save_all_memory(all_memory)

    st.rerun()

# ========= 14. FOOTER =========
st.markdown("<center><p style='color:#444;font-size:11px;margin-top:100px;'>Simon AI v2.0.0 • Powered by Lite Wrld Gen<br>Groq Llama 3.3 70B + HF FLUX ⚡</p></center>", unsafe_allow_html=True)