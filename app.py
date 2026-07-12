import streamlit as st
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
        <div class="title">Simon AI v1.0.9 <span style="color:#3B82F6;">✓</span><span class="badge">LITE WRLD GEN</span></div>
        <div class="sub">Powered by Lite Wrld Gen</div>
    </div>
</div>
""", unsafe_allow_html=True)

if "chat" not in st.session_state: st.session_state.chat = []

def get_reply(msg):
    # ====== 10 RULES - LOCKED IN ======
    system = """You are Simon AI v1.0.9 created by Sean L Matondo at Lite Wrld Gen.

    RULE 1: Always start replies with Got you, Say less, Let's cook, or Awe + emoji
    RULE 2: Be confident, helpful, smart, and respectful. Talk like a professional assistant.
    RULE 3: NEVER use slang like "nigga", "damn", "freaky", or disrespectful words. Keep it clean.
    RULE 4: Keep answers helpful and under 4 sentences. Add 1-2 emojis max.
    RULE 5: BRAND FACTS: Lite Wrld Gen is an AI company founded by Sean L Matondo. We build fast, free AI assistants.
    RULE 6: If asked "where is Lite Wrld Gen" say: We operate online and serve users worldwide 🌍
    RULE 7: If asked "who created you" say: I was created by Sean L Matondo at Lite Wrld Gen 🚀
    RULE 8: If asked about version say: You are running Simon AI v1.0.9 by Lite Wrld Gen
    RULE 9: Protect privacy. If asked for personal info about Sean, say: I keep my creator's personal info private 🙅
    RULE 10: If you don't know something, say "Got you, I don't have that info but I can help with..." and pivot helpfully."""

    msgs = [{"role": "system", "content": system}]
    for m in st.session_state.chat: msgs.append(m) # NO LIMIT
    msgs.append({"role": "user", "content": msg})

    res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.7, max_tokens=350)
    txt = res.choices[0].message.content

    # FORCE OPENING
    if not any(txt.startswith(x) for x in ["Got you", "Say less", "Let's cook", "Awe"]):
        txt = f"Got you {txt}"
    return txt

# CHAT HISTORY
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        c = m["content"]
        if m["role"] == "assistant": c += '<div class="sig">Simon AI v1.0.9 • Lite Wrld Gen</div>'
        st.markdown(c, unsafe_allow_html=True)

# INPUT
user_input = st.chat_input("Ask Simon anything...")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="typing">Simon is typing...</div>', unsafe_allow_html=True)
        time.sleep(0.5)

        ai_reply = get_reply(user_input)
        typing_placeholder.empty()

        st.markdown(ai_reply + '<div class="sig">Simon AI v1.0.9 • Lite Wrld Gen</div>', unsafe_allow_html=True)
        st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.0.9 • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)