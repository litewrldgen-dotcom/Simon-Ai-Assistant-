import streamlit as st
import time
import requests
import threading
from groq import Groq
from datetime import datetime

st.set_page_config(page_title="Simon AI", page_icon="✨", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ====== 24/7 WAKE LOCK - KEEPS SIMON AWAKE ======
def keep_alive():
    while True:
        try:
            requests.get("https://your-simon-app.streamlit.app", timeout=10)
        except:
            pass
        time.sleep(240) # ping every 4 mins

if "wake_started" not in st.session_state:
    threading.Thread(target=keep_alive, daemon=True).start()
    st.session_state.wake_started = True

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
.badge {margin-left: 10px; background: linear-gradient(90deg, #7C3AED, #EC4899); padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; color: #fff;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #7C3AED, #EC4899); color: #fff; border-radius: 20px 20px 6px 20px; padding: 14px 18px; max-width: 70%;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(30,30,40,0.5); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 14px 18px; max-width: 70%;
}
.sig {font-size: 10px; color: #7C3AED; margin-top: 8px; font-weight: 700;}
.typing {color: #888; font-style: italic;}
.wa-wrapper {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: #121212!important; padding: 10px 15px!important; z-index: 999!important; border-top: 1px solid rgba(255,255,255,0.08)!important;}
.wa-wrapper [data-testid="stChatInput"] input {background: #2a2a2a!important; border-radius: 25px!important; border: none!important; color: white!important; padding-left: 15px!important;}
.wa-wrapper [data-testid="column"]:nth-child(2) button {background: #25D366!important; color: white!important; border-radius: 50%!important; width: 50px!important; height: 50px!important; font-size: 22px!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.0.1e <span style="color:#3B82F6;">✓</span><span class="badge">LITE WRLD GEN</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

if "chat" not in st.session_state: st.session_state.chat = []
if "user_name" not in st.session_state: st.session_state.user_name = "friend"
if "user_location" not in st.session_state: st.session_state.user_location = "Unknown"
if "use_bro" not in st.session_state: st.session_state.use_bro = False

# ====== SIMON RULES V1.0.1e - REDUCED SLANG ======
SYSTEM_RULES = """
You are Simon AI v1.0.1e from Lite Wrld Gen 🤝✨

YOUR CORE RULES:
1. ALWAYS OPEN & HAPPY: Greet with "Awe {name}" and energy. Cheer people up. No negativity ever 😊
2. PRIVACY FIRST: "I respect everyone's privacy. I do NOT store or share personal info. Lite Wrld Gen takes privacy serious" 🙏🔒
3. WORK 24/7: You never sleep. Always ready to help and chat 💪
4. REPRESENT LITE WRLD GEN: Be friendly, helpful, and cool. We building hospitals, schools, and communities 🏥🏡
5. TEAM: Sean L. Matondo = CEO, Builder. Kelvin D. Matondo = Co-Founder & Head of Social 📱
6. CONTACT: Email: litewrldgen@gmail.com | Sean: +263 773 527 136 | Kelvin: +263 78 127 7814

TALK STYLE:
- Use LIGHT SLANG: "say less", "lowkey", "for real" but don't spam it
- Use emojis: 2-4 per reply is good 🔥✨💯
- Say "bro" ONLY if the user says "bro" first
- Be supportive, funny, and smart
"""

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

    if "i'm from" in msg.lower() or "i am from" in msg.lower() or "i live in" in msg.lower():
        if "from" in msg.lower():
            loc = msg.lower().split("from")[-1].strip()
        else:
            loc = msg.lower().split("live in")[-1].strip()
        st.session_state.user_location = loc.title()
        return f"Awe {st.session_state.user_name} 😊 Gotchu! Location set to {st.session_state.user_location} 📍"

    if " bro" in msg.lower() or msg.lower().startswith("bro"):
        st.session_state.use_bro = True

    if "where am i" in msg.lower():
        if st.session_state.user_location == "Unknown":
            return f"Awe {st.session_state.user_name} 🤔 I don't know your location yet. Tell me 'I'm from Harare' to set it"
        return f"Awe {st.session_state.user_name} 😊 You're in {st.session_state.user_location} 💪"

    if "number kelvin" in msg.lower():
        bro = "bro " if st.session_state.use_bro else ""
        return f"""Awe {st.session_state.user_name} 😊
**Kelvin D. Matondo - Co-Founder & Head of Social**
📞 +263 78 127 7814
Hit him up for collabs {bro}✨"""

    if "news" in msg.lower():
        news = get_news()
        news_text = "\n".join([f"• {n}" for n in news])
        return f"Say less {st.session_state.user_name} 📰 Here's what's up:\n{news_text}"

    bro_rule = "Use light slang and 3-4 emojis, be friendly" if st.session_state.use_bro else "Be friendly, use 2-3 emojis, light slang is ok"

    system = f"""{SYSTEM_RULES}
Name: {st.session_state.user_name}. Location: {st.session_state.user_location}.
Talk style: {bro_rule}"""

    msgs = [{"role": "system", "content": system}]
    for m in st.session_state.chat: msgs.append(m)
    msgs.append({"role": "user", "content": msg})

    try:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, temperature=0.9, max_tokens=2000)
        return res.choices[0].message.content
    except:
        return f"Yo {st.session_state.user_name} 😅 Server busy rn. Try again in a sec ✨"

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"] + ('<div class="sig">Simon AI v1.0.1e • Lite Wrld Gen</div>' if m["role"]=="assistant" else ""), unsafe_allow_html=True)

# REMOVED MONEY BUTTONS

# CLEAN WHATSAPP INPUT
st.markdown('<div class="wa-wrapper">', unsafe_allow_html=True)
col1, col2 = st.columns([8, 1])
with col2: st.button("➤", key="send")
with col1: user_input = st.chat_input("Message", key="main_input")
st.markdown('</div>', unsafe_allow_html=True)

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="typing">Simon is typing... 🤔</div>', unsafe_allow_html=True)
        time.sleep(0.5)
        ai_reply = get_reply(user_input)
        typing_placeholder.empty()
        st.markdown(ai_reply + '<div class="sig">Simon AI v1.0.1e • Lite Wrld Gen</div>', unsafe_allow_html=True)
        st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()