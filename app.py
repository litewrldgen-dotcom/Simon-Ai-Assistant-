import streamlit as st
import time
import requests
from groq import Groq
from datetime import datetime

st.set_page_config(page_title="Simon AI", page_icon="✨", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ====== OLD CUL GLASS UI WITH ICONS ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
* {font-family: 'DM Sans', sans-serif;}
.stApp {background: radial-gradient(circle at 20% 50%, #0f0f1a 0%, #05050a 100%); color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 5rem; padding-bottom: 100px; max-width: 900px;}

/* TOPBAR LIKE IN IMAGE */
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 70px; background: rgba(10,10,15,0.7); backdrop-filter: blur(30px); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; padding: 0 20px; z-index: 999;}
.logo {width: 45px; height: 45px; border-radius: 15px; background: linear-gradient(135deg, #A855F7, #EC4899); margin-right: 12px;}
.title {font-size: 20px; font-weight: 700; color: #fff;}
.badge {margin-left: 10px; background: linear-gradient(90deg, #EC4899, #F43F5E); padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; color: #fff;}

/* CHAT BUBBLES WITH ICONS LIKE IMAGE */
[data-testid="stChatMessage"] {display: flex; align-items: flex-start; gap: 12px;}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {width: 35px; height: 35px; border-radius: 10px; flex-shrink: 0;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageAvatar"] {background: #EF4444; display: flex; align-items: center; justify-content: center; font-size: 20px;}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageAvatar"] {background: #F97316; display: flex; align-items: center; justify-content: center; font-size: 20px;}

[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #1F1F2A; color: #fff; border-radius: 15px; padding: 14px 18px; max-width: 80%;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: transparent; color: #e5e5e5; border-radius: 0; padding: 0; max-width: 80%; line-height: 1.7;
}
.sig {font-size: 11px; color: #A855F7; margin-top: 12px; font-weight: 700;}
.typing {color: #888; font-style: italic;}
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: rgba(10,10,15,0.9); backdrop-filter: blur(30px); border-top: 1px solid rgba(255,255,255,0.08); padding: 16px 20px!important; z-index: 999; border-radius: 15px; margin: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.0.1g <span style="color:#3B82F6;">✓</span><span class="badge">LITE WRLD GEN</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

if "chat" not in st.session_state: st.session_state.chat = []
if "user_name" not in st.session_state: st.session_state.user_name = "friend"
if "user_location" not in st.session_state: st.session_state.user_location = "Unknown"
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
    if "my name is" in msg.lower():
        st.session_state.user_name = msg.lower().split("my name is")[-1].strip().split()[0].title()

    if " bro" in msg.lower() or msg.lower().startswith("bro"):
        st.session_state.use_bro = True

    if "i'm from" in msg.lower() or "i am from" in msg.lower() or "i live in" in msg.lower():
        if "from" in msg.lower():
            loc = msg.lower().split("from")[-1].strip()
        else:
            loc = msg.lower().split("live in")[-1].strip()
        st.session_state.user_location = loc.title()
        return f"Awe {st.session_state.user_name} 😊 Gotchu! Location set to {st.session_state.user_location} 📍"

    if "where am i" in msg.lower():
        if st.session_state.user_location == "Unknown":
            return f"Awe {st.session_state.user_name} 🤔 I don't know your location yet. Tell me 'I'm from Harare' to set it"
        return f"Awe {st.session_state.user_name} 😊 You're in {st.session_state.user_location}"

    # DETAILED TEAM INFO LIKE IN YOUR IMAGE
    if "sean" in msg.lower() and "kelvin" in msg.lower() or "team" in msg.lower():
        bro = "bro " if st.session_state.use_bro else ""
        return f"""Awe {st.session_state.user_name} 🚀! I've got the information you need.

Sean L. Matondo is the CEO and Builder of Lite Wrld Gen, while Kelvin D. Matondo is the Co-Founder and Head of Social. If you need to get in touch with them, you can reach out through the following contact details:

• **Email:** litewrldgen@gmail.com
• **Sean:** +263 773 527 136
• **Kelvin:** +263 78 127 7814

They're part of the team behind Lite Wrld Gen, which operates online worldwide 🌍. By the way, how's your day going {bro}✨"""

    if "number kelvin" in msg.lower():
        return f"""Awe {st.session_state.user_name} 😊
**Kelvin D. Matondo - Co-Founder & Head of Social**
📞 +263 78 127 7814
Hit his WhatsApp to collab or get posted 💯"""

    if "news" in msg.lower():
        news = get_news()
        news_text = "\n".join([f"• {n}" for n in news])
        return f"Awe {st.session_state.user_name} 📰 Here's what's happening right now:\n{news_text}\n\nLet me know if you want more details on any of these ✨"

    bro_rule = "Use light slang and 2-4 emojis, be detailed and descriptive" if st.session_state.use_bro else "Be detailed, descriptive, friendly, and use 2-4 emojis. Explain things fully."

    # NO CHAR LIMIT - REMOVED MAX_TOKENS CAP
    system = f"""You are Simon AI v1.0.1g by Lite Wrld Gen. The user's name is {st.session_state.user_name}. Location: {st.session_state.user_location}.

    RULE 1: Greet with "Awe {{name}}" and use 2-4 emojis. Be descriptive and detailed in answers.
    RULE 2: Talk style: {bro_rule}. Write full paragraphs, use bullet points when listing info.
    RULE 3: NO CHARACTER LIMIT. Give complete answers with details and examples.
    RULE 4: FOR CODING: Always help with full code and explanations.
    RULE 5: BRAND: Lite Wrld Gen operates online worldwide 🌍
    RULE 6: TEAM: Sean L. Matondo = CEO, Builder. Kelvin D. Matondo = Co-Founder & Head of Social.
    RULE 7: CONTACT: Email: litewrldgen@gmail.com | Sean: +263 773 527 136 | Kelvin: +263 78 127 7814"""

    msgs = [{"role": "system", "content": system}]
    for m in st.session_state.chat: msgs.append(m)
    msgs.append({"role": "user", "content": msg})

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=msgs,
            temperature=0.9,
            max_tokens=4000 # UNLOCKED - NO MORE CHAR LIMIT
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Yo 😅 Simon hit a snag. Error: {str(e)[:100]}"

# CUSTOM CHAT DISPLAY WITH ICONS
for m in st.session_state.chat:
    with st.chat_message(m["role"], avatar="😊" if m["role"]=="user" else "🤖"):
        st.markdown(m["content"])
        if m["role"]=="assistant":
            st.markdown('<div class="sig">Simon AI v1.0.1g • Lite Wrld Gen</div>', unsafe_allow_html=True)

user_input = st.chat_input("Ask Simon anything... ✨")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("assistant", avatar="🤖"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="typing">Simon is typing... 🤔</div>', unsafe_allow_html=True)
        time.sleep(0.5)
        ai_reply = get_reply(user_input)
        typing_placeholder.empty()
        st.markdown(ai_reply)
        st.markdown('<div class="sig">Simon AI v1.0.1g • Lite Wrld Gen</div>', unsafe_allow_html=True)
        st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()