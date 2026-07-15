import streamlit as st
import time
import requests
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
.title {font-size: 18px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px;}
.sub {font-size: 11px; color: #888; font-weight: 500;}
.badge {background: linear-gradient(90deg, #7C3AED, #EC4899); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; color: #fff;}

/* CHAT */
[data-testid="stChatMessage"] {background: transparent;}
[data-testid="stChatMessage"][data-testid*="user"] {display: flex; justify-content: flex-end;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #7C3AED, #EC4899);
    color: #fff; border-radius: 20px 20px 6px 20px; padding: 14px 18px; max-width: 70%; font-weight: 500; box-shadow: 0 8px 30px rgba(124,58,237,0.3);
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(30,30,40,0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 14px 18px; max-width: 70%; line-height: 1.7;
}
.sig {font-size: 10px; color: #7C3AED; margin-top: 8px; font-weight: 700;}

/* THINKING DOTS ANIMATION */
.typing {color: #888; font-style: italic; font-size: 14px;}
.dots span {animation: blink 1.4s infinite; animation-fill-mode: both;}
.dots span:nth-child(2) {animation-delay: 0.2s;}
.dots span:nth-child(3) {animation-delay: 0.4s;}
@keyframes blink {0%, 80%, 100% {opacity: 0;} 40% {opacity: 1;}}

/* INPUT */
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: rgba(10,10,15,0.8); backdrop-filter: blur(30px); border-top: 1px solid rgba(255,255,255,0.08); padding: 16px 20px!important; z-index: 999;}
.stChatInputContainer {background: rgba(30,30,40,0.6)!important; border-radius: 24px!important; border: 1px solid rgba(255,255,255,0.1)!important;}
pre {background: rgba(0,0,0,0.4)!important; border-radius: 12px!important; border: 1px solid rgba(124,58,237,0.3)!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.0.2h <span style="color:#3B82F6;">✓</span> <span class="badge">LITE WRLD GEN</span></div>
        <div class="sub">Powered by Lite Wrld Gen</div>
    </div>
</div>
""", unsafe_allow_html=True)

if "name" not in st.session_state: st.session_state.name = "Friend"
if "location" not in st.session_state: st.session_state.location = "Unknown"
if "chat" not in st.session_state: st.session_state.chat = []
if "use_bro" not in st.session_state: st.session_state.use_bro = False

def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=3&apiKey={st.secrets.get('NEWS_API_KEY', 'demo')}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            articles = r.json().get("articles", [])
            return [f"{a['title']}" for a in articles[:3]]
    except: pass
    return ["Can't fetch news right now 😅"]

def get_reply(msg):
    msg_lower = msg.lower()
    bro = "bro " if st.session_state.use_bro else ""

    if " bro" in msg_lower or msg_lower.startswith("bro"):
        st.session_state.use_bro = True

    if "my name is" in msg_lower:
        n = msg.split("my name is")[-1].strip().split()[0].title()
        st.session_state.name = n
        return f"Awe {n} 😊 Got you locked in {bro}🔥"

    if "i'm from" in msg_lower or "i am from" in msg_lower or "i live in" in msg_lower:
        if "from" in msg_lower:
            loc = msg_lower.split("from")[-1].strip()
        else:
            loc = msg_lower.split("live in")[-1].strip()
        st.session_state.location = loc.title()
        return f"Awe {st.session_state.name} 😊 Gotchu! Location set to {st.session_state.location} 📍"

    if "where am i" in msg_lower:
        if st.session_state.location == "Unknown":
            return f"Awe {st.session_state.name} 🤔 I don't know your location yet. Tell me 'I'm from Harare' to set it"
        return f"Awe {st.session_state.name} 😊 You're in {st.session_state.location}"

    if "where is lite wrld gen" in msg_lower:
        return f"Got you 🌍 <b>Lite Wrld Gen</b> operates online and serves users worldwide {bro}✨"

    if "who founded" in msg_lower and "lite wrld gen" in msg_lower:
        return f"Awe 🙏 <b>Lite Wrld Gen</b> was founded by <b>Sean L Matondo</b> {bro}💯"

    if "what is lite wrld gen" in msg_lower:
        return f"Say less 😎 <b>Lite Wrld Gen</b> is an AI company. We build Simon AI and other fast free AI assistants {bro}🚀"

    if "who created you" in msg_lower:
        return f"Let's cook 🚀 I was created by <b>Sean L Matondo</b> at <b>Lite Wrld Gen</b> {bro}✨"

    if "version" in msg_lower:
        return f"Awe 🙏 You running <b>Simon AI v1.0.2h</b> by Lite Wrld Gen {bro}🔥"

    if "sean" in msg_lower and "kelvin" in msg_lower or "about lite wrld gen" in msg_lower or "team" in msg_lower:
        return f"""Awe {st.session_state.name} 🚀! I've got the information you need.

Sean L. Matondo is the CEO and Builder of Lite Wrld Gen, while Kelvin D. Matondo is the Co-Founder and Head of Social.

- **Email:** litewrldgen@gmail.com
- **Sean:** +263 773 527 136
- **Kelvin:** +263 78 127 7814

They're part of the team behind Lite Wrld Gen, which operates online worldwide 🌍. How's your day going {bro}✨"""

    if "number kelvin" in msg_lower:
        return f"""Awe {st.session_state.name} 😏
**Kelvin D. Matondo - Co-Founder & Head of Social**
📞 +263 78 127 7814
Hit his WhatsApp to collab {bro}💯"""

    if "news" in msg_lower:
        news = get_news()
        news_text = "\n".join([f"• {n}" for n in news])
        return f"Say less {st.session_state.name} 🔥 Here's what's popping {bro}:\n{news_text}"

    bro_rule = f"Use 'bro' sometimes, light slang, 2-4 emojis per reply, be detailed" if st.session_state.use_bro else "Use 2-4 emojis per reply, light slang is ok, be detailed. Do NOT use 'bro' unless user uses it first"

    system = f"""You are Simon AI v1.0.2h created by Sean L Matondo at Lite Wrld Gen.
    User name: {st.session_state.name}. Location: {st.session_state.location}.
    RULE 1: Always start with Got you, Say less, Let's cook, or Awe + emoji 🔥✨😊
    RULE 2: Be confident, helpful, funny. {bro_rule}
    RULE 3: NO CHARACTER LIMIT. Give detailed answers.
    RULE 4: BRAND: Lite Wrld Gen is an AI company. We operate online worldwide 🌍"""

    msgs = [{"role": "system", "content": system}]
    for m in st.session_state.chat[-10:]: msgs.append(m)
    msgs.append({"role": "user", "content": msg})

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=msgs,
            temperature=0.9,
            max_tokens=4000
        )
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
        if m["role"] == "assistant": c += '<div class="sig">Simon AI v1.0.2h • Lite Wrld Gen</div>'
        st.markdown(c, unsafe_allow_html=True)

user_input = st.chat_input("Ask Simon anything... ✨")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        # PHASE 1: ANIMATED DOTS
        typing_placeholder = st.empty()
        for i in range(3): # 3 cycles of dots
            typing_placeholder.markdown('<div class="typing">Simon is typing<span class="dots"><span>.</span><span>.</span><span>.</span></span></div>', unsafe_allow_html=True)
            time.sleep(0.5)

        # PHASE 2: SWITCH TO THINKING
        typing_placeholder.markdown('<div class="typing">Simon is thinking... 🤔</div>', unsafe_allow_html=True)

        ai_reply = get_reply(user_input)

        typing_placeholder.empty()
        st.markdown(ai_reply + '<div class="sig">Simon AI v1.0.2h • Lite Wrld Gen</div>', unsafe_allow_html=True)
        st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.0.2h • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)