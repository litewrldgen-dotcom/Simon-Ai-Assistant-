import streamlit as st
import json
import requests
import uuid
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Simon AI v2.0.7",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

Path("generated_images").mkdir(exist_ok=True)
Path("memory").mkdir(exist_ok=True)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_API_KEY = st.secrets.get("HF_API_KEY", "")

# ========= UI - ROSEMARY + FORCED SIDEBAR + BIG TOPBAR =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rosemary&display=swap');
* {font-family: 'Rosemary', system-ui, sans-serif;}
.stApp {background: #080808; color: #e5e5e5;}
header {visibility: hidden;}
.block-container {padding-top: 90px; padding-bottom: 110px; max-width: 850px;}

/* NUKE SIDEBAR - FORCE IT OPEN */
section[data-testid="stSidebar"] {
    background: #0f0f0f!important;
    border-right: 3px solid #00ff64!important;
    width: 320px!important;
    visibility: visible!important;
    display: block!important;
}

/* CHAT: YOU RIGHT, SIMON LEFT */
.stChatMessage[data-testid*="user"] {justify-content: flex-end!important;}
.stChatMessage[data-testid*="assistant"] {justify-content: flex-start!important;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #00ff64; color: #000; border-radius: 18px 18px 4px 18px;
    padding: 14px 18px; max-width: 80%; font-weight: 600;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: #1a1a1a; border: 1px solid #00ff64; color: #e5e5e5;
    border-radius: 18px 18px 18px 4px; padding: 14px 18px; max-width: 80%;
}

div[data-testid="stChatInput"] {
    position: fixed!important; bottom: 0; left: 0; right: 0;
    background: #080808; border-top: 2px solid #00ff64; padding: 14px 16px!important; z-index: 999;
}

.topbar {position: fixed; top: 0; left: 0; right: 0; height: 80px; background: #080808;
border-bottom: 2px solid #00ff64; display: flex; align-items: center; padding: 0 20px; z-index: 999;}
.neon {color: #00ff64; font-size: 20px; font-weight: 700;}
.sig {font-size: 10px; color: #00ff64; opacity: 0.7; margin-top: 4px;}
</style>

<script>
// FORCE SIDEBAR OPEN ON MOBILE
const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
if(sidebar) sidebar.style.display = 'block';
</script>
""", unsafe_allow_html=True)

# ========= MEMORY - 5 DEVICES =========
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
if "user_uses_slang" not in st.session_state: st.session_state.user_uses_slang = False

# ========= SIDEBAR =========
with st.sidebar:
    st.markdown("### 🧠 Simon AI")
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("### 📂 History")
    st.caption(f"{len(current_mem['chats'])} chats")
    st.markdown("### 🖼️ Images")
    for img in st.session_state.images[-3:]: st.image(img, width=120)
    st.markdown("---")
    st.caption(f"Device: {device_id}")
    st.caption(f"Images: {st.session_state.image_count}/3")
    st.caption("Creator: Sean L. Matondo")
    st.caption("Company: Lite Wrld Gen")

# ========= BIG TOPBAR =========
st.markdown("""
<div class="topbar">
    <div style="width:42px;height:42px;border-radius:14px;background:#00ff64;margin-right:14px;"></div>
    <div>
        <div class="neon">Simon AI v2.0.7 ✓</div>
        <div style="font-size:12px;color:#888;">Powered by Lite Wrld Gen 🌍</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========= PERSONALITY - YOUR RULES FORCED =========
def get_system_prompt():
    slang_rule = "Use light slang like 'bet', 'say less', 'no cap' and emojis 💚 but don't overdo it." if st.session_state.user_uses_slang else "Be professional, warm, helpful. Use 1 emoji max."
    return f"""You are Simon AI v2.0.7 by Lite Wrld Gen.
ABOUT: We operate online worldwide. Contact: support@litewrldgen.com
IMPORTANT RULES - YOU MUST FOLLOW THESE:
1. Rep Lite Wrld Gen first 🔥
2. Be for EVERYONE 🌍
3. Never call user "bro", "son", "Daddy" unless THEY say it first.
4. {slang_rule}
5. You CAN generate images. Say "generating your image now" when you do.
6. Remember user name: {current_mem['name']}
7. Use GROQ for chat. Use HF FLUX for images.
Answer like a human friend, not a robot."""

# ========= AI FUNCTIONS =========
def groq_chat(messages):
    if not GROQ_API_KEY: return "Add GROQ_API_KEY to secrets son"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.8}, timeout=25)
        return r.json()["choices"][0]["message"]["content"]
    except: return "Groq lagging. Try again 💚"

def hf_image(prompt):
    if not HF_API_KEY: return None, "Add HF_API_KEY son"
    try:
        r = requests.post("https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt}, timeout=120)
        if r.status_code == 503:
            return None, "Model waking up... this takes 30s first time. Try again 💚"
        if r.status_code!= 200:
            return None, f"HF Error {r.status_code}"
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        draw = ImageDraw.Draw(img); w,h = img.size
        draw.rectangle([(0,h-40),(w,h)], fill=(0,0,0,180))
        draw.text((15,h-28), "Simon AI • Lite Wrld Gen", fill="#00ff64")
        return img, "ok"
    except: return None, "Connection failed"

# ========= CHAT =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.markdown('<div class="sig">Simon AI v2.0.7 • Lite Wrld Gen</div>', unsafe_allow_html=True)

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
            placeholder.markdown("Generating your image now... this takes 20s 💚")
            if st.session_state.image_count >= 3:
                reply = "Daily limit of 3 images reached. Come back tomorrow 💚"
            else:
                img, status = hf_image(user_input)
                if img:
                    st.session_state.images.append(img); st.session_state.image_count += 1
                    placeholder.empty(); st.image(img, use_container_width=True)
                    reply = f"Here you go {current_mem['name']} 📸"
                else:
                    reply = status
        else:
            msgs = [{"role": "system", "content": get_system_prompt()}] + st.session_state.messages[-8:]
            reply = groq_chat(msgs)

        placeholder.markdown(reply)
        st.markdown('<div class="sig">Simon AI v2.0.7 • Lite Wrld Gen</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    current_mem["chats"].append({"u": user_input, "ai": reply})
    all_mem["devices"][device_id] = current_mem; save_mem(all_mem)
    st.rerun()

st.markdown("<center><p style='color:#444;font-size:11px;margin-top:100px;'>Simon AI v2.0.7 • Lite Wrld Gen • support@litewrldgen.com</p></center>", unsafe_allow_html=True)