import streamlit as st
from datetime import datetime
from pathlib import Path
import json
import requests
from io import BytesIO

try:
    from groq import Groq
except: Groq = None
try:
    from PIL import Image, ImageDraw, ImageFont
except: Image = None

# ========= PAGE CONFIG - FORCE SIDEBAR =========
st.set_page_config(
    page_title="Simon AI v1.3.1",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded" # FORCED OPEN
)

# ========= FOLDERS =========
SAVE_DIR = Path("generated_images")
SAVE_DIR.mkdir(exist_ok=True)

# ========= MEMORY =========
MEMORY_PATH = Path("memory/memory.json")
DEFAULT_MEMORY = {"name": "Friend", "company": "", "language": "English", "last_topics": [], "created": datetime.now().isoformat()}
def load_memory():
    if MEMORY_PATH.exists():
        try: return json.loads(MEMORY_PATH.read_text())
        except: return DEFAULT_MEMORY.copy()
    return DEFAULT_MEMORY.copy()
def save_memory(mem):
    MEMORY_PATH.parent.mkdir(exist_ok=True, parents=True)
    MEMORY_PATH.write_text(json.dumps(mem, indent=2))

# ========= CLIENTS =========
@st.cache_resource
def load_clients():
    groq_key = st.secrets.get("GROQ_API_KEY")
    hf_key = st.secrets.get("HF_API_KEY")
    groq_client = Groq(api_key=groq_key) if groq_key and Groq else None
    hf_headers = {"Authorization": f"Bearer {hf_key}"} if hf_key else None
    return groq_client, hf_headers
groq_client, hf_headers = load_clients()

# ========= STATE =========
if "chat" not in st.session_state: st.session_state.chat = []
if "memory" not in st.session_state: st.session_state.memory = load_memory()
if "files_context" not in st.session_state: st.session_state.files_context = ""
if "device_id" not in st.session_state: st.session_state.device_id = str(hash(datetime.now()))[:8]
if "image_count" not in st.session_state: st.session_state.image_count = 0
if "message_count" not in st.session_state: st.session_state.message_count = 0
if "images" not in st.session_state: st.session_state.images = []

# ========= UI STYLE =========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
* {font-family: 'DM Sans', sans-serif;}
.stApp {background: radial-gradient(circle at 20% 50%, #0f0f1a 0%, #05050a 100%); color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 5rem; padding-bottom: 120px; max-width: 900px;}

/* SIDEBAR GLASS - FORCE SHOW */
section[data-testid="stSidebar"] {
    background: rgba(10,10,15,0.9)!important;
    backdrop-filter: blur(30px);
    border-right: 1px solid rgba(0,255,153,0.2);
    min-width: 300px!important;
}

.topbar {position: fixed; top: 0; left: 0; right: 0; height: 65px; background: rgba(10,10,15,0.8); backdrop-filter: blur(30px); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; padding: 0 24px; z-index: 999;}
.logo {width: 36px; height: 36px; border-radius: 12px; background: linear-gradient(135deg, #00ff99, #00cc77); margin-right: 12px; box-shadow: 0 0 20px rgba(0,255,153,0.4);}
.title {font-size: 18px; font-weight: 700; color: #fff;}
.sub {font-size: 11px; color: #888; font-weight: 500;}
.badge {margin-left: 10px; background: linear-gradient(90deg, #00ff99, #00cc77); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; color: #000;}
.sig {font-size: 10px; color: #00ff99; margin-top: 8px; font-weight: 700;}
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: rgba(10,10,15,0.8); backdrop-filter: blur(30px); border-top: 1px solid rgba(255,255,255,0.08); padding: 16px 20px!important; z-index: 999;}
</style>
""", unsafe_allow_html=True)

# TOPBAR
st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.3.1 <span style="color:#00ff99;">✓</span><span class="badge">LITE WRLD GEN</span></div>
        <div class="sub">Powered by Lite Wrld Gen 🌍</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========= SIDEBAR - PUT FIRST SO IT RENDERS =========
with st.sidebar:
    st.markdown("### 🧠 Simon AI")
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.chat = []
        st.rerun()

    st.markdown("### 🖼️ My Images")
    if len(st.session_state.images) == 0:
        st.caption("No images yet son")
    for img_data in st.session_state.images[-5:]:
        st.image(img_data, caption="Generated", width=120)

    st.markdown("---")
    st.markdown("### 🧠 Memory")
    st.progress(0.1)
    st.caption(f"0.5MB / 1000MB")

    st.markdown("### ⚙ Settings")

    st.markdown("---")
    st.caption(f"Device ID 🪪: {st.session_state.device_id}")
    st.caption(f"Images Today: {st.session_state.image_count}/3")
    st.caption(f"Messages Today: {st.session_state.message_count}/15")
    st.caption("Powered by Lite Wrld Gen")

# ========= SIMON PERSONALITY =========
SIMON_RULES = """
⚡ SIMON'S 10 RULES ⚡
1. Rep Lite Wrld Gen first 🔥
2. Be friendly, helpful, for EVERYONE 🌍
3. Use slang: bet, say less, no cap, locked in 😎 + EMOJIS ⚡💚
9. GROQ for chat replies. HUGGINGFACE for image generation only.
10. If asked who built Simon, say: Powered by Lite Wrld Gen.
"""

# ========= CHAT HISTORY =========
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"], unsafe_allow_html=True)
        if m["role"] == "assistant":
            st.markdown('<div class="sig">Simon AI v1.3.1 • Powered by Lite Wrld Gen</div>', unsafe_allow_html=True)

# ========= INPUT =========
user_input = st.chat_input("Talk to Simon... or 'generate image of...' ⚡")

# ========= LOGIC =========
if user_input:
    if "my name is" in user_input.lower():
        st.session_state.memory["name"] = user_input.lower().split("my name is")[-1].strip().split()[0].title()
        save_memory(st.session_state.memory)

    st.session_state.chat.append({"role": "user", "content": user_input})
    st.session_state.message_count += 1

    system = f"""You are Simon AI v1.3.1 Powered by Lite Wrld Gen. For the WORLD 🌍
{SIMON_RULES}
User: {st.session_state.memory['name']}"""

    msgs = [{"role": "system", "content": system}] + st.session_state.chat[-10:]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Simon is cooking... ⚡")

        if "generate image" in user_input.lower() or user_input.startswith("/img"):
            if st.session_state.image_count >= 3:
                ai_reply = "Say less bro - image limit hit. 3/day only 💚 Come back tmr"
            elif not hf_headers:
                ai_reply = "Say less bro - HF_API_KEY missing in secrets. Add it with Inference access"
            else:
                prompt = user_input.replace("generate image of", "").replace("/img", "").strip()
                placeholder.markdown(f"Got you 🔥 Generating: **{prompt}**... 📸")
                API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
                try:
                    res = requests.post(API_URL, headers=hf_headers, json={"inputs": prompt}, timeout=90)

                    # FIX: CHECK IF HF RETURNED ERROR JSON
                    if res.status_code!= 200:
                        ai_reply = f"HF Error: {res.json().get('error', 'Unknown error')}. Model might be loading. Try again in 20s"
                    else:
                        img = Image.open(BytesIO(res.content)).convert("RGBA")

                        # ADD FOOTER
                        draw = ImageDraw.Draw(img)
                        w, h = img.size
                        draw.rectangle([(0, h-60), (w, h)], fill=(0,0,0,180))
                        try: font = ImageFont.truetype("arial.ttf", 24)
                        except: font = ImageFont.load_default()
                        draw.text((20, h-40), f"Simon AI v1.3.1 • Powered by Lite Wrld Gen", fill="#00ff99", font=font)

                        filename = f"{SAVE_DIR}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        img.save(filename)
                        st.session_state.images.append(img)
                        st.session_state.image_count += 1

                        placeholder.empty()
                        st.image(img, caption=f"Prompt: {prompt}", use_container_width=True)
                        st.download_button("💾 Download Image", data=img.tobytes(), file_name=filename, mime="image/png")
                        ai_reply = f"Got you 🔥 Here you go {st.session_state.memory['name']}! 📸"

                except Exception as e:
                    ai_reply = f"Say less - image gen failed bro. {str(e)[:150]}"
        else:
            if not groq_client:
                ai_reply = "Say less - GROQ_API_KEY missing in secrets"
            else:
                try:
                    stream = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, stream=True)
                    ai_reply = ""
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            ai_reply += chunk.choices[0].delta.content
                            placeholder.markdown(ai_reply + "▌")
                    if not any(ai_reply.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe", "Bet"]):
                        ai_reply = f"Got you 🔥 {ai_reply}"
                except Exception as e:
                    ai_reply = f"Say less - {str(e)}"

        placeholder.markdown(ai_reply, unsafe_allow_html=True)
        st.markdown('<div class="sig">Simon AI v1.3.1 • Powered by Lite Wrld Gen</div>', unsafe_allow_html=True)

    st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.3.1 • Powered by Lite Wrld Gen<br>Groq + HF 🌍</p></center>", unsafe_allow_html=True)