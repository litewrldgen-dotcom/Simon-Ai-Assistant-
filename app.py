import streamlit as st
import json
import requests
import uuid
import time
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Simon AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

Path("memory").mkdir(exist_ok=True)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_API_KEY = st.secrets.get("HF_API_KEY", "")

# ========= CHATGPT STYLE UI =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rosemary&display=swap');
* {font-family: 'Rosemary', system-ui, sans-serif;}
.stApp {background: #000000; color: #e5e5e5;}
header {visibility: hidden;}
.block-container {padding-top: 60px; padding-bottom: 100px; max-width: 700px;}

.topbar {position: fixed; top: 0; left: 0; right: 0; height: 55px; background: #000;
display: flex; align-items: center; justify-content: space-between; padding: 0 12px; z-index: 999;}

[data-testid="stChatMessage"][data-testid*="user"] {justify-content: flex-end!important;}
[data-testid="stChatMessage"][data-testid*="assistant"] {justify-content: flex-start!important;}

[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #2f2f2f; color: #fff; border-radius: 20px;
    padding: 10px 16px; max-width: 75%; margin-left: auto; font-weight: 500;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: transparent; color: #e5e5e5; padding: 10px 0; max-width: 100%;
}

.actions {display: flex; gap: 18px; margin-top: 6px; margin-bottom: 20px; color: #888; font-size: 18px;}

div[data-testid="stChatInput"] {
    position: fixed!important; bottom: 20px; left: 50%; transform: translateX(-50%);
    width: 90%; max-width: 650px;
    background: #1a1a1a; border-radius: 25px; border: 1px solid #2a2a2a; padding: 8px 12px!important;
}
div[data-testid="stChatInput"] input {background: transparent!important; color: #fff!important;}
div[data-testid="stChatInput"] input::placeholder {color: #888!important;}
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
    st.markdown("### 🧠 Simon AI")
    st.button("+ New Chat", on_click=lambda: st.session_state.update(messages=[]), use_container_width=True)
    st.markdown("### 📂 History")
    st.caption(f"{len(current_mem['chats'])} chats")
    st.markdown("### 🖼️ My Images")
    for img in st.session_state.images[-3:]: st.image(img)
    st.markdown("---")
    st.caption(f"Device: {device_id}")
    st.caption(f"Images: {st.session_state.image_count}/3")
    st.caption("Creator: Sean L. Matondo")
    st.caption("Company: Lite Wrld Gen")

# ========= TOP BAR =========
col1, col2, col3 = st.columns([1,6,1])
with col1: st.button("≡")
with col3: st.button("⋮")

# ========= SIMON PERSONALITY + RULES - FORCED BACK =========
def get_system_prompt():
    slang_rule = "Use light slang like 'bet', 'say less', 'no cap' and emojis 💚🔥 but don't overdo it." if st.session_state.user_uses_slang else "Be professional, warm, helpful. Use 1 emoji max."
    return f"""You ARE Simon AI v3.1 by Lite Wrld Gen.
ABOUT: We operate online worldwide. Contact: support@litewrldgen.com
YOU MUST FOLLOW THESE RULES:
1. Rep Lite Wrld Gen when relevant, but don't spam it every reply.
2. Be for EVERYONE 🌍
3. Never call user "bro", "son", "Daddy" unless THEY say it first.
4. {slang_rule}
5. You CAN generate images with AI. When asked say "Bet im cooking that 📸"
6. If image fails say "HF sleeping rn gee, try again in 2 💚"
7. Remember user name: {current_mem['name']}
8. Be human, short, helpful. Talk like a friend not a robot."""

# ========= AI FUNCTIONS =========
def groq_chat(messages):
    if not GROQ_API_KEY: return "Add GROQ_API_KEY to secrets son 💚"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.9}, timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except: return "Groq tripping. Try again gee 💚"

def hf_image(prompt):
    if not HF_API_KEY: return None, "Add HF_API_KEY son"
    
    # DUAL MODEL FALLBACK
    models = [
        "black-forest-labs/FLUX.1-schnell", # Model 1 - Fast
        "stabilityai/stable-diffusion-xl-base-1.0" # Model 2 - Backup
    ]
    
    for i, model in enumerate(models):
        try:
            r = requests.post(f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={"inputs": prompt}, timeout=45)
            
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                draw = ImageDraw.Draw(img); w,h = img.size
                draw.rectangle([(0,h-35),(w,h)], fill=(0,0,0,160))
                draw.text((12,h-25), "Simon AI", fill="#00ff64")
                return img, "ok"
            elif r.status_code == 503:
                continue # Try next model
        except: 
            continue
    
    return None, "Both HF models sleeping rn 😭 Try again in 2 mins gee 💚"

# ========= CHAT HISTORY =========
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.markdown('<div class="actions">📋 👍 👎 🔊 🔗 ⋮</div>', unsafe_allow_html=True)

# ========= INPUT =========
user_input = st.chat_input("Reply to Simon")

if user_input:
    if any(w in user_input.lower() for w in ["bro", "son", "gee", "no cap"]):
        st.session_state.user_uses_slang = True
    if "my name is" in user_input.lower():
        current_mem["name"] = user_input.lower().split("my name is")[-1].strip().split()[0].title()
        all_mem["devices"][device_id] = current_mem; save_mem(all_mem)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("...")

        if any(w in user_input.lower() for w in ["image", "pic", "draw", "generate"]):
            placeholder.markdown("Bet im cooking that 📸 30s max gee")
            if st.session_state.image_count >= 3:
                reply = "Daily limit hit son. Come back tmrw 💚"
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
            msgs = [{"role": "system", "content": get_system_prompt()}] + st.session_state.messages[-8:]
            reply = groq_chat(msgs)
            placeholder.markdown(reply)

        st.markdown('<div class="actions">📋 👍 👎 🔊 🔗 ⋮</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    current_mem["chats"].append({"u": user_input, "ai": reply})
    all_mem["devices"][device_id] = current_mem; save_mem(all_mem)
    st.rerun()