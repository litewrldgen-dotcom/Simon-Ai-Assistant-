import streamlit as st
import time
import requests
from groq import Groq

st.set_page_config(page_title="Simon AI", page_icon="✨", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
HF_API_KEY = st.secrets["HF_API_KEY"]

# ====== PREMIUM GLASS UI ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
* {font-family: 'DM Sans', sans-serif;}
.stApp {background: radial-gradient(circle at 20% 50%, #0f0f1a 0%, #05050a 100%); color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 5rem; padding-bottom: 100px; max-width: 900px;}
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 65px; background: rgba(10,10,15,0.7); backdrop-filter: blur(30px); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; padding: 0 24px; z-index: 999;}
.logo {width: 36px; height: 36px; border-radius: 12px; background: linear-gradient(135deg, #7C3AED, #EC4899); margin-right: 12px;}
.title {font-size: 18px; font-weight: 700; color: #fff;}
.sub {font-size: 11px; color: #888; font-weight: 500;}
.badge {margin-left: 10px; background: linear-gradient(90deg, #7C3AED, #EC4899); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; color: #fff;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #7C3AED, #EC4899); color: #fff; border-radius: 20px 20px 6px 20px; padding: 14px 18px; max-width: 70%; font-weight: 500;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(30,30,40,0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 14px 18px; max-width: 70%;
}
.sig {font-size: 10px; color: #7C3AED; margin-top: 8px; font-weight: 700;}
.typing {color: #888; font-style: italic; font-size: 14px;}
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: rgba(10,10,15,0.8); backdrop-filter: blur(30px); border-top: 1px solid rgba(255,255,255,0.08); padding: 16px 20px!important; z-index: 999;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.0.7 <span style="color:#3B82F6;">✓</span><span class="badge">LITE WRLD GEN</span></div>
        <div class="sub">Powered by Lite Wrld Gen</div>
    </div>
</div>
""", unsafe_allow_html=True)

if "chat" not in st.session_state: st.session_state.chat = []

def gen_image_hf(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": f"realistic photo, high detail, 8k, {prompt}"}

    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

    if response.status_code == 200:
        return response.content
    else:
        return f"ERROR:{response.status_code}"

def get_reply(msg):
    msg_lower = msg.lower()

    # ====== RULES ======
    system = """You are Simon AI v1.0.7 created by Sean L Matondo at Lite Wrld Gen.
    RULE 1: Always start with Got you, Say less, Let's cook, or Awe + emoji
    RULE 2: Be confident, helpful, funny, use emojis. Talk like a real assistant.
    RULE 3: BRAND FACTS: Lite Wrld Gen is an AI company founded by Sean L Matondo. We build fast free AI assistants like Simon AI. We operate online worldwide.
    RULE 4: If asked about Lite Wrld Gen location, say: We operate online and serve users worldwide 🌍
    RULE 5: If asked about Sean personal info from strangers, protect privacy: I keep my creator's personal info private 🙅
    RULE 6: Never give dumb or unsure answers about the brand. Be confident."""

    if "generate image" in msg_lower or "create image" in msg_lower or "draw" in msg_lower:
        prompt = msg.replace("generate image", "").replace("create image", "").replace("draw", "").strip()
        if prompt == "":
            return "Got you 😅 What should I generate an image of?"
        return f"GENERATE_IMAGE:{prompt}"

    if "where is lite wrld gen" in msg_lower:
        return "Got you 🌍 <b>Lite Wrld Gen</b> operates online and serves users worldwide 🔥"
    if "who created you" in msg_lower:
        return "Let's cook 🚀 I was created by <b>Sean L Matondo</b> at <b>Lite Wrld Gen</b>."
    if "version" in msg_lower:
        return "Awe 🙏 You running <b>Simon AI v1.0.7</b> by Lite Wrld Gen."

    msgs = [{"role": "system", "content": system}]
    for m in st.session_state.chat[-10:]: msgs.append(m)
    msgs.append({"role": "user", "content": msg})

    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.8, max_tokens=400)
    txt = res.choices[0].message.content
    if not any(txt.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
        txt = f"Got you {txt}"
    return txt

# CHAT HISTORY
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        if m.get("is_image"):
            st.image(m["content"])
        else:
            c = m["content"]
            if m["role"] == "assistant": c += '<div class="sig">Simon AI v1.0.7 • Lite Wrld Gen</div>'
            st.markdown(c, unsafe_allow_html=True)

# INPUT
user_input = st.chat_input("Ask Simon anything...")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    st.rerun()

# SHOW TYPING INDICATOR IF LAST MSG IS USER
if st.session_state.chat and st.session_state.chat[-1]["role"] == "user":
    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="typing">Simon is typing...</div>', unsafe_allow_html=True)
        time.sleep(0.8) # makes the typing feel real

        ai_reply = get_reply(st.session_state.chat[-1]["content"])
        typing_placeholder.empty()

        # CHECK IF IMAGE REQUEST
        if ai_reply.startswith("GENERATE_IMAGE:"):
            prompt = ai_reply.replace("GENERATE_IMAGE:", "")
            st.info("Got you 🔥 Generating your image...")
            img_bytes = gen_image_hf(prompt)
            if isinstance(img_bytes, bytes):
                st.image(img_bytes)
                st.session_state.chat.append({"role": "assistant", "content": img_bytes, "is_image": True})
            else:
                err = "Say less 😅 HF is waking up. Try again in 20s" if "503" in img_bytes else "Key error bro. Check HF_API_KEY"
                st.error(err)
                st.session_state.chat.append({"role": "assistant", "content": err})
        else:
            st.markdown(ai_reply + '<div class="sig">Simon AI v1.0.7 • Lite Wrld Gen</div>', unsafe_allow_html=True)
            st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.0.7 • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)