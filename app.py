import streamlit as st
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="Simon AI", page_icon="✨", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ====== PREMIUM GLASS UI ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
* {font-family: 'DM Sans', sans-serif;}
.stApp {background: radial-gradient(circle at 20% 50%, #0f0f1a 0%, #05050a 100%); color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 5rem; padding-bottom: 100px; max-width: 900px;}

/* HEADER */
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 65px; background: rgba(10,10,15,0.7); backdrop-filter: blur(30px); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; padding: 0 24px; z-index: 999;}
.logo {width: 36px; height: 36px; border-radius: 12px; background: linear-gradient(135deg, #7C3AED, #EC4899); margin-right: 12px;}
.title {font-size: 18px; font-weight: 700; color: #fff;}
.sub {font-size: 11px; color: #888; font-weight: 500;}
.badge {margin-left: 10px; background: linear-gradient(90deg, #7C3AED, #EC4899); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; color: #fff;}

/* CHAT */
[data-testid="stChatMessage"] {background: transparent;}
[data-testid="stChatMessage"][data-testid*="user"] {display: flex; justify-content: flex-end;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #7C3AED, #EC4899);
    color: #fff; border-radius: 20px 20px 6px 20px; padding: 14px 18px; max-width: 70%; font-weight: 500; box-shadow: 0 8px 30px rgba(124,58,237,0.3);
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(30,30,40,0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 14px 18px; max-width: 70%;
}
.sig {font-size: 10px; color: #7C3AED; margin-top: 8px; font-weight: 700;}

/* INPUT */
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: rgba(10,10,15,0.8); backdrop-filter: blur(30px); border-top: 1px solid rgba(255,255,255,0.08); padding: 16px 20px!important; z-index: 999;}
.stChatInputContainer {background: rgba(30,30,40,0.6)!important; border-radius: 24px!important; border: 1px solid rgba(255,255,255,0.1)!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.0.2 <span style="color:#3B82F6;">✓</span><span class="badge">LITE WRLD GEN</span></div>
        <div class="sub">Powered by Lite Wrld Gen</div>
    </div>
</div>
""", unsafe_allow_html=True)

if "name" not in st.session_state: st.session_state.name = "Friend"
if "chat" not in st.session_state: st.session_state.chat = []

def get_reply(msg):
    # ====== AMAZING RULES FOR SIMON ======
    system = f"""You are Simon AI v1.0.2 created by Sean L Matondo at Lite Wrld Gen.
RULE 1: Always start with Got you, Say less, Let's cook, or Awe + emoji
RULE 2: Be confident, helpful, funny, use emojis. Talk like a real assistant.
RULE 3: BRAND FACTS: Lite Wrld Gen is an AI company founded by Sean L Matondo. We build fast free AI assistants like Simon AI. We operate online worldwide.
RULE 4: If asked about Lite Wrld Gen location, say: We operate online and serve users worldwide 🌍
RULE 5: If asked about Sean personal info, protect privacy: I keep my creator's personal info private 🙅
RULE 6: If asked who built Simon, always mention Sean L Matondo and Lite Wrld Gen
RULE 7: Never give dumb or unsure answers about the brand. Be confident.
User name: {st.session_state.name}"""

    msg_lower = msg.lower()

    # HARDCODED BRAND ANSWERS - NO DUMB REPLIES
    if "where is lite wrld gen" in msg_lower or "lite wrld gen location" in msg_lower:
        return "Got you 🌍 <b>Lite Wrld Gen</b> operates online and serves users worldwide. We're building the future of AI from anywhere 🔥"
    if "who founded" in msg_lower and "lite wrld gen" in msg_lower:
        return "Awe 🙏 <b>Lite Wrld Gen</b> was founded by <b>Sean L Matondo</b>. He's building fast AI for everyone."
    if "what is lite wrld gen" in msg_lower:
        return "Say less 😎 <b>Lite Wrld Gen</b> is an AI company. We build Simon AI and other fast free AI assistants."
    if "who created you" in msg_lower or "who built you" in msg_lower:
        return "Let's cook 🚀 I was created by <b>Sean L Matondo</b> at <b>Lite Wrld Gen</b>."
    if "version" in msg_lower:
        return "Awe 🙏 You running <b>Simon AI v1.0.2</b> by Lite Wrld Gen."
    if "my name is" in msg_lower:
        n = msg.split("my name is")[-1].strip().split()[0].title()
        st.session_state.name = n
        return f"Got you {n}! Locked in 🔥"

    msgs = [{"role": "system", "content": system}]
    for m in st.session_state.chat[-10:]: msgs.append(m)
    msgs.append({"role": "user", "content": msg})

    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.8, max_tokens=400)
        txt = res.choices[0].message.content
        if not any(txt.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
            txt = f"Got you {txt}"
        return txt
    except Exception as e:
        return f"Say less - {str(e)}"

# CHAT HISTORY
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        c = m["content"]
        if m["role"] == "assistant": c += '<div class="sig">Simon AI v1.0.2 • Lite Wrld Gen</div>'
        st.markdown(c, unsafe_allow_html=True)

# INPUT
user_input = st.chat_input("Ask Simon anything...")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    ai_reply = get_reply(user_input)
    st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.0.2 • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)