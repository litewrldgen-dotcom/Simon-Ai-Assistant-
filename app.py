import streamlit as st
import json
import requests
import uuid
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw

st.set_page_config(page_title="Simon AI v4.4", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
Path("memory").mkdir(exist_ok=True)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_API_KEY = st.secrets.get("HF_API_KEY", "")
EMAIL_USER = st.secrets.get("EMAIL_USER", "")
EMAIL_PASS = st.secrets.get("EMAIL_PASS", "")

# ========= UI =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rosemary&display=swap');
* {font-family: 'Rosemary', system-ui, sans-serif; font-size: 14px!important;}
.stApp {background: #080808; color: #e5e5e5;}
header {visibility: hidden;}
.block-container {padding-top: 90px; padding-bottom: 120px; max-width: 850px;}
section[data-testid="stSidebar"] {background: #0a0a0a!important; border-right: 2px solid #00ff64!important;}
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 70px; background: #080808;
border-bottom: 2px solid #00ff64; display: flex; align-items: center; padding: 0 20px; z-index: 999;}
.neon {color: #00ff64; font-size: 18px!important; font-weight: 700; text-shadow: 0 0 8px #00ff64;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #00ff64; color: #000; border-radius: 16px 16px 4px 16px; padding: 10px 14px; max-width: 75%; font-weight: 600;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: #121212; border: 1px solid #00ff64; color: #e5e5e5;
    border-radius: 16px 16px 16px 4px; padding: 10px 14px; max-width: 75%;
}
.stButton>button {background: #1a1a1a!important; border: 1px solid #333!important; color: #888!important;
border-radius: 6px!important; padding: 4px 8px!important; font-size: 12px!important; height: 28px!important;}
.stButton>button:hover {border-color: #00ff64!important; color: #00ff64!important;}
</style>
""", unsafe_allow_html=True)

# ========= EMAIL FUNCTION =========
def send_feedback(to_email, subject, body):
    if not EMAIL_USER or not EMAIL_PASS: return False
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        return True
    except: return False

# ========= MEMORY =========
def get_device_id():
    if "device_id" not in st.session_state: st.session_state.device_id = str(uuid.uuid4())[:8]
    return st.session_state.device_id

def load_mem():
    f = Path("memory/memory.json")
    try: return json.loads(f.read_text()) if f.exists() else {"devices": {}}
    except: return {"devices": {}}

def save_mem(data): Path("memory/memory.json").write_text(json.dumps(data, indent=2))

device_id = get_device_id()
all_mem = load_mem()
if device_id not in all_mem["devices"]:
    if len(all_mem["devices"]) >= 5: del all_mem["devices"][list(all_mem["devices"].keys())[0]]
    all_mem["devices"][device_id] = {"name": "Friend", "email": "", "chats": []}
    save_mem(all_mem)
current_mem = all_mem["devices"][device_id]

# ========= STATE =========
if "messages" not in st.session_state: st.session_state.messages = []
if "images" not in st.session_state: st.session_state.images = []
if "image_count" not in st.session_state: st.session_state.image_count = 0
if "user_uses_slang" not in st.session_state: st.session_state.user_uses_slang = True
if "pending_feedback" not in st.session_state: st.session_state.pending_feedback = None # stores which msg user clicked

# ========= SIDEBAR =========
with st.sidebar:
    st.markdown("### ⚡ Simon AI v4.4")
    if st.button("+ New Chat", use_container_width=True): st.session_state.messages = []; st.rerun()
    st.markdown("### 📂 History")
    st.caption(f"{len(current_mem['chats'])} chats")
    st.markdown("### 🖼️ Gallery")
    for img in st.session_state.images[-4:]: st.image(img)
    st.markdown("---")
    st.text_input("Your Email", value=current_mem["email"], key="user_email_input",
                  on_change=lambda: save_mem(all_mem.update({"devices": {**all_mem["devices"], device_id: {**current_mem, "email": st.session_state.user_email_input}}})))
    st.caption("Used for feedback reports")

# ========= TOPBAR =========
st.markdown("""
<div class="topbar">
    <div style="width:40px;height:40px;border-radius:12px;background:#00ff64;box-shadow:0 0 12px #00ff64;margin-right:12px;"></div>
    <div><div class="neon">Simon AI v4.4</div><div style="font-size:11px;color:#888;">Powered by Lite Wrld Gen</div></div>
</div>
""", unsafe_allow_html=True)

# ========= SIMON BRAIN =========
def get_system_prompt():
    slang = "Use slang like 'bet', 'say less', 'no cap', 'gee' and emojis 💚🔥. Be chill and short." if st.session_state.user_uses_slang else "Be warm and helpful. Use 1 emoji max."
    return f"""You ARE Simon AI v4.4 by Lite Wrld Gen.
ABOUT: We operate online worldwide. Contact: support@litewrldgen.com
RULES: 1. Rep Lite Wrld Gen when relevant. 2. Be for EVERYONE 🌍 3. Never call user "bro", "son" unless THEY start it.
4. {slang} 5. Say "Bet im cooking that 📸" for images. 6. If image fails: "HF tripping rn gee"
7. Name: {current_mem['name']} 8. Be human, short, helpful."""

# ========= AI FUNCTIONS =========
def groq_chat(messages):
    if not GROQ_API_KEY: return "Add GROQ_API_KEY son 💚"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.9}, timeout=30)
        return r.json()["choices"][0]["message"]["content"]
    except: return "Groq tripping. Try again gee 💚"

def hf_image(prompt):
    if not HF_API_KEY: return None, "Add HF_API_KEY son"
    models = ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0"]
    for model in models:
        try:
            r = requests.post(f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={"inputs": prompt, "options": {"wait_for_model": True}}, timeout=90)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                draw = ImageDraw.Draw(img); w,h = img.size
                draw.rectangle([(0,h-35),(w,h)], fill=(0,0,0,180))
                draw.text((12,h-25), "Simon AI • Lite Wrld Gen", fill="#00ff64")
                return img, "ok"
        except: continue
    return None, "Both models sleeping 😭 Wait 2 mins gee 💚"

# ========= FEEDBACK POPUP =========
if st.session_state.pending_feedback:
    i, feedback_type = st.session_state.pending_feedback
    with st.container():
        st.warning(f"Drop your email so Lite Wrld Gen can follow up 💚")
        user_email = st.text_input("Email", key="feedback_email")
        c1, c2 = st.columns(2)
        if c1.button("Send Feedback"):
            user_q = st.session_state.messages[i-1]['content']
            ai_a = st.session_state.messages[i]['content']
            body = f"Feedback: {feedback_type}\nFrom: {user_email}\nDevice: {device_id}\n\nUser: {user_q}\nSimon: {ai_a}"
            if send_feedback("litewrldgen@gmail.com", f"Simon AI {feedback_type} - {device_id}", body):
                st.success("Sent to Lite Wrld Gen 💚")
                current_mem["email"] = user_email
                all_mem["devices"][device_id] = current_mem; save_mem(all_mem)
            else: st.error("Email not set up yet son")
            st.session_state.pending_feedback = None
            st.rerun()
        if c2.button("Cancel"):
            st.session_state.pending_feedback = None
            st.rerun()

# ========= CHAT =========
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            cols = st.columns(5)
            if cols[1].button("👍", key=f"like{i}"):
                st.session_state.pending_feedback = (i, "LIKE")
                st.rerun()
            if cols[2].button("👎", key=f"dislike{i}"):
                st.session_state.pending_feedback = (i, "DISLIKE")
                st.rerun()
            cols[0].button("📋", key=f"copy{i}")
            cols[3].button("🔊", key=f"speak{i}")
            cols[4].button("⋮", key=f"more{i}")

user_input = st.chat_input("Ask Simon Anything ⚡")

if user_input:
    if any(w in user_input.lower() for w in ["bro", "son", "gee", "no cap"]): st.session_state.user_uses_slang = True
    if "my name is" in user_input.lower():
        current_mem["name"] = user_input.lower().split("my name is")[-1].strip().split()[0].title()
        all_mem["devices"][device_id] = current_mem; save_mem(all_mem)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking... ⚡")

        if any(w in user_input.lower() for w in ["image", "pic", "draw", "generate"]):
            placeholder.markdown("Bet im cooking that 📸 30s max gee...")
            if st.session_state.image_count >= 3: reply = "Daily limit hit son. Come back tmrw 💚"
            else:
                img, status = hf_image(user_input)
                if img:
                    st.session_state.images.append(img); st.session_state.image_count += 1
                    placeholder.image(img, use_container_width=True)
                    reply = f"Say less {current_mem['name']} 🔥"
                else: reply = status; placeholder.markdown(reply)
        else:
            msgs = [{"role": "system", "content": get_system_prompt()}] + st.session_state.messages[-10:]
            reply = groq_chat(msgs); placeholder.markdown(reply)

        cols = st.columns(5)
        cols[0].button("📋", key="copy_new")
        cols[1].button("👍", key="like_new")
        cols[2].button("👎", key="dislike_new")
        cols[3].button("🔊", key="speak_new")
        cols[4].button("⋮", key="more_new")

    st.session_state.messages.append({"role": "assistant", "content": reply})
    current_mem["chats"].append({"u": user_input, "ai": reply})
    all_mem["devices"][device_id] = current_mem; save_mem(all_mem)
    st.rerun()