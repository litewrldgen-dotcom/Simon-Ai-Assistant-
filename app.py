import streamlit as st
import json
import requests
import uuid
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Simon AI v2.0.3",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

Path("generated_images").mkdir(exist_ok=True)
Path("memory").mkdir(exist_ok=True)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "") # backup only
HF_API_KEY = st.secrets.get("HF_API_KEY", "")

# ========= CLEAN UI - NO GOOGLE FONTS =========
st.markdown("""
<style>
* {font-family: system-ui, -apple-system, sans-serif;}
.stApp {background: #0a0a0a; color: #e5e5e5;}
header {visibility: hidden;}
.block-container {padding-top: 75px; padding-bottom: 110px; max-width: 800px;}

/* FORCE SIDEBAR */
section[data-testid="stSidebar"] {
    background: #111!important;
    border-right: 1px solid #00ff64!important;
    width: 300px!important;
}

/* CHAT LAYOUT: USER RIGHT, SIMON LEFT */
[data-testid="stChatMessage"][data-testid*="user"] {
    flex-direction: row-reverse;
}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #00ff64; color: #000; border-radius: 18px 18px 4px 18px;
    padding: 12px 16px; max-width: 75%; margin-left: auto; font-weight: 500;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: #1a1a1a; border: 1px solid #2a2a2a; color: #e5e5e5;
    border-radius: 18px 18px 18px 4px; padding: 12px 16px; max-width: 75%;
}

/* FIXED INPUT */
div[data-testid="stChatInput"] {
    position: fixed!important; bottom: 0; left: 0; right: 0;
    background: #0a0a0a; border-top: 1px solid #00ff64; padding: 12px 16px!important;
}
input::placeholder {color: #00ff64!important;}

.topbar {position: fixed; top: 0; left: 0; right: 0; height: 65px; background: #0a0a0a;
border-bottom: 1px solid #00ff64; display: flex; align-items: center; padding: 0 16px; z-index: 999;}
.neon {color: #00ff64;}
.sig {font-size: 10px; color: #00ff64; opacity: 0.6; margin-top: 4px;}
</style>
""", unsafe_allow_html=True)

# ========= MEMORY - 5 DEVICES =========
def get_device_id():
    if "device_id" not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())[:8]
    return st.session_state.device_id

def load_mem():
    f = Path("memory/memory.json")
    return json.loads(f.read_text()) if f.exists() else {"devices": {}}

def save_mem(data):
    Path("memory/memory.json").write_text(json.dumps(data, indent=2))

device_id = get_device_id()
all_mem = load_mem()
if device_id not in all_mem["devices"]:
    if len(all_mem["devices"]) >= 5: del all_mem["devices"][list(all_mem["devices"].keys())[0]]
    all_mem["devices"][device_id] = {"name": "Friend", "chats": [], "vibe": "neutral"}
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
    for img in st.session_state.images[-3:]: st.image(img, width=100)
    st.markdown("---")
    st.caption(f"Device: {device_id}")
    st.caption(f"Images: {st.session_state.image_count}/3")
    st.caption("Creator: Sean L. Matondo")
    st.caption("Company: Lite Wrld Gen")

# ========= TOPBAR =========
st.markdown("""
<div class="topbar">
    <div style="width:32px;height:32px;border-radius:10px;background:#00ff64;margin-right:10px;"></div>
    <div>
        <div style="font-size:16px;font-weight:600;">Simon AI v2.0.3 <span class="neon">✓</span></div>
        <div style="font-size:10px;color:#888;">Powered by Lite Wrld Gen 🌍</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========= SIMON PERSONALITY - YOUR RULES BACK =========
def get_system_prompt():
    slang_rule = "You can use light slang like 'bet', 'say less', 'no cap' and emojis 💚" if st.session_state.user_uses_slang else "Be professional, warm, helpful. Minimal slang. Use emojis sparingly."
    return f"""
You are Simon AI v2.0.3 by Lite Wrld Gen.
ABOUT LITE WRLD GEN: We operate online worldwide. Contact: support@litewrldgen.com
PERSONALITY: Friendly assistant. {slang_rule}

CORE RULES:
1. Rep Lite Wrld Gen first 🔥
2. Be for EVERYONE 🌍
3. Never call user "bro", "son", "Daddy" unless they say it first.
4. Match the user's energy and tone.
5. Use HF Qwen for chat. Use HF FLUX for images only.
6. Remember user name: {current_mem['name']}
7. If you don't know, say it straight no cap 💯
8. For jokes use free API. For facts answer directly.
Never mention API keys or secrets.
"""

# ========= FREE WEB APIS =========
def get_joke():
    try: return requests.get("https://api.chucknorris.io/jokes/random", timeout=5).json()["value"]
    except: return "Why did the AI cross the road? To get to the other server 💚"

def get_advice():
    try: return requests.get("https://api.adviceslip.com/advice", timeout=5).json()["slip"]["advice"]
    except: return "Stay locked in and keep building 💚"

# ========= AI FUNCTIONS - FIXED =========
def hf_chat(messages):
    if not HF_API_KEY: return "Add HF_API_KEY to secrets"
    try:
        # BUILD PROMPT FOR HF - THIS WAS THE BUG
        prompt = ""
        for m in messages:
            role = "System" if m["role"]=="system" else "User" if m["role"]=="user" else "Assistant"
            prompt += f"{role}: {m['content']}\n"
        prompt += "Assistant: "

        r = requests.post("https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt, "parameters": {"max_new_tokens": 400, "return_full_text": False, "temperature": 0.7}}, timeout=45)

        if r.status_code!= 200:
            return f"AI is waking up... try again in 20s"
        return r.json()[0]["generated_text"].strip()
    except Exception as e:
        return f"AI lagging. Try again 💚"

def hf_image(prompt):
    if not HF_API_KEY: return None, "Add HF_API_KEY"
    try:
        r = requests.post("https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt}, timeout=90)
        if r.status_code!= 200: return None, "Model waking up... retry in 20s"
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        draw = ImageDraw.Draw(img); w,h = img.size
        draw.rectangle([(0,h-35),(w,h)], fill=(0,0,0,160))
        draw.text((12,h-25), "Simon AI • Lite Wrld Gen", fill="#00ff64")
        return img, "ok"
    except: return None, "Connection failed. Try again"

# ========= CHAT HISTORY =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            st.markdown('<div class="sig">Simon AI v2.0.3 • Lite Wrld Gen</div>', unsafe_allow_html=True)

# ========= INPUT =========
user_input = st.chat_input("Ask Simon Anything ⚡")

if user_input:
    # DETECT IF USER USES SLANG
    if any(w in user_input.lower() for w in ["bro", "son", "gee", "no cap"]):
        st.session_state.user_uses_slang = True

    # SAVE NAME
    if "my name is" in user_input.lower():
        current_mem["name"] = user_input.lower().split("my name is")[-1].strip().split()[0].title()
        all_mem["devices"][device_id] = current_mem; save_mem(all_mem)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking... ⚡")

        # FREE WEB FEATURES
        if "joke" in user_input.lower():
            reply = f"Got you 💚 {get_joke()}"
        elif "advice" in user_input.lower():
            reply = f"Here's something for you: {get_advice()}"
        # IMAGE
        elif any(w in user_input.lower() for w in ["image", "pic", "draw", "generate"]):
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
        # CHAT
        else:
            msgs = [{"role": "system", "content": get_system_prompt()}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-8:]]
            reply = hf_chat(msgs)
            if not reply.startswith("Here") and not reply.startswith("Got"):
                reply = f"Got you 💚 {reply}" # ADDED YOUR "GOT YOU" BACK

        placeholder.markdown(reply)
        st.markdown('<div class="sig">Simon AI v2.0.3 • Lite Wrld Gen</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    current_mem["chats"].append({"u": user_input, "ai": reply})
    all_mem["devices"][device_id] = current_mem; save_mem(all_mem)
    st.rerun()

st.markdown("<center><p style='color:#333;font-size:10px;margin-top:100px;'>Simon AI v2.0.3 • Lite Wrld Gen • support@litewrldgen.com</p></center>", unsafe_allow_html=True)