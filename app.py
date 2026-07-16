import streamlit as st
import time
import requests
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="Simon AI", page_icon="✨", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ====== PREMIUM GLASS UI - MATCHES YOUR PIC ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&display=swap');
* {font-family: 'DM Sans', sans-serif;}
.stApp {background: #000; color: #fff;}
header {visibility: hidden;}
.block-container {padding-top: 6rem; padding-bottom: 100px; max-width: 900px;}

/* HEADER LIKE YOUR PIC */
.topbar {position: fixed; top: 0; left: 0; right: 0; height: 75px; background: rgba(0,0,0,0.85); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; padding: 0 20px; z-index: 999;}
.logo {width: 45px; height: 45px; border-radius: 14px; background: linear-gradient(135deg, #EC4899, #8B5CF6); margin-right: 14px;}
.title {font-size: 20px; font-weight: 900; color: #fff; display: flex; align-items: center; gap: 10px;}
.sub {font-size: 12px; color: #aaa; font-weight: 500;}
.badge {background: linear-gradient(90deg, #EC4899, #8B5CF6); padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 900; color: #fff; letter-spacing: 0.5px;}

/* CHAT */
[data-testid="stChatMessage"] {background: transparent;}
[data-testid="stChatMessage"][data-testid*="user"] {display: flex; justify-content: flex-end;}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #EC4899, #8B5CF6);
    color: #fff; border-radius: 20px 20px 6px 20px; padding: 16px 20px; max-width: 75%; font-weight: 600; font-size: 15px;
}
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: #1a1a1a; border: 1px solid rgba(255,255,255,0.08);
    color: #e5e5e5; border-radius: 20px 20px 20px 6px; padding: 16px 20px; max-width: 75%; line-height: 1.8; font-size: 15px;
}
.sig {font-size: 11px; color: #EC4899; margin-top: 10px; font-weight: 800;}

/* THINKING DOTS ANIMATION */
.typing {color: #888; font-style: italic; font-size: 14px;}
.dots span {animation: blink 1.4s infinite; animation-fill-mode: both;}
.dots span:nth-child(2) {animation-delay: 0.2s;}
.dots span:nth-child(3) {animation-delay: 0.4s;}
@keyframes blink {0%, 80%, 100% {opacity: 0;} 40% {opacity: 1;}}

/* INPUT */
.stChatInput {position: fixed!important; bottom: 0!important; left: 0!important; right: 0!important; background: rgba(0,0,0,0.9); backdrop-filter: blur(20px); border-top: 1px solid rgba(255,255,255,0.1); padding: 16px 20px!important; z-index: 999;}
.stChatInputContainer {background: #1a1a1a!important; border-radius: 24px!important; border: 1px solid rgba(255,255,255,0.1)!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
    <div class="logo"></div>
    <div>
        <div class="title">Simon AI v1.0.9 <span style="color:#3B82F6;">✓</span> <span class="badge">LITE WRLD GEN</span></div>
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
        return f"Awe {n} 😊🔥 Got you locked in {bro}💯✨"

    if "i'm from" in msg_lower or "i am from" in msg_lower or "i live in" in msg_lower:
        if "from" in msg_lower:
            loc = msg_lower.split("from")[-1].strip()
        else:
            loc = msg_lower.split("live in")[-1].strip()
        st.session_state.location = loc.title()
        return f"Say less {st.session_state.name} 😎📍 Location set to {st.session_state.location} {bro}✨🌍"

    if "where am i" in msg_lower:
        if st.session_state.location == "Unknown":
            return f"Awe {st.session_state.name} 🤔 I don't know your location yet {bro}. Tell me 'I'm from Harare' to set it 📍"
        return f"Got you {st.session_state.name} 😊 You're in {st.session_state.location} {bro}🌍🔥"

    # ====== MASSIVE DETAILED BRAND ANSWERS ======
    if "where is lite wrld gen" in msg_lower:
        return f"Got you 🌍🔥 <b>Lite Wrld Gen</b> operates online and serves users worldwide {bro}. We're a digital-first AI company building the future from anywhere 💯✨🚀"

    if "who founded" in msg_lower and "lite wrld gen" in msg_lower:
        return f"Let's cook 🚀🔥 <b>Lite Wrld Gen</b> was founded by <b>Sean L Matondo</b> {bro}. He's the CEO, Builder, and the visionary behind everything we do 💯✨👑"

    if "what is lite wrld gen" in msg_lower:
        return f"""Say less {st.session_state.name} 😎🔥💯
<b>Lite Wrld Gen</b> is a next-gen AI company {bro}🚀

<b>WHAT WE DO:</b>
✨ Build fast, free AI assistants like Simon AI
🚀 Make powerful AI accessible to everyone worldwide
🌍 Operate 100% online with zero limits
💯 Push innovation without gatekeeping

<b>OUR MISSION:</b> To put cutting-edge AI in every person's hands {bro}. We're building the future, one chat at a time 🔥✨"""

    if "who created you" in msg_lower:
        return f"Awe 🙏🔥 I was created by <b>Sean L Matondo</b> at <b>Lite Wrld Gen</b> {bro}. He's the CEO and main builder behind Simon 💯✨🚀"

    if "version" in msg_lower:
        return f"Got you {bro}😎 You're running <b>Simon AI v1.0.9</b> by Lite Wrld Gen 🔥✨💯"

    # ====== MASSIVE TEAM INFO BLOCK FOR YOU + KEV ======
    if "sean" in msg_lower and "kelvin" in msg_lower or "about lite wrld gen" in msg_lower or "team" in msg_lower or "who are you guys" in msg_lower or "founders" in msg_lower:
        return f"""Awe {st.session_state.name} 🚀🔥💯! Let me put you on to the Lite Wrld Gen team {bro}✨

<b>THE FOUNDERS 👑</b>

🚀 <b>Sean L. Matondo</b> - CEO & Builder
The visionary and tech genius behind Lite Wrld Gen. He built Simon AI from scratch and runs all development. Man's literally cooking 24/7 and making AI free for everyone {bro}💯✨

📱 <b>Kelvin D. Matondo</b> - Co-Founder & Head of Social
The brand master and community king. He handles our social media, partnerships, and making sure Lite Wrld Gen stays trending {bro}🔥. If you see us blowing up, that's Kev's work 😎

<b>CONTACT THE TEAM:</b>
📧 Email: litewrldgen@gmail.com
📱 Sean: +263 773 527 136
📱 Kelvin: +263 78 127 7814

<b>ABOUT LITE WRLD GEN:</b>
We're an AI company operating worldwide 🌍. No office, no limits. Just pure innovation. We build Simon AI and other free AI tools to help people create, learn, code, and grow {bro}. Our goal? Democratize AI for the whole world 💯✨🚀

Need anything else {bro}? Let's cook 🔥"""

    if "number kelvin" in msg_lower or "phone kelvin" in msg_lower:
        return f"""Say less {st.session_state.name} 😏🔥
<b>Kelvin D. Matondo - Co-Founder & Head of Social</b>
📞 +263 78 127 7814
Hit him up on WhatsApp for collabs, shoutouts, or just to chop it {bro}💯✨"""

    if "news" in msg_lower:
        news = get_news()
        news_text = "\n".join([f"• {n}" for n in news])
        return f"Let's cook {st.session_state.name} 🔥📰 Here's what's popping {bro}:\n{news_text}"

    # ====== HIGH EMOJI + HIGH SLANG SYSTEM PROMPT ======
    bro_rule = f"Use 'bro' 1-2 times per reply, HIGH slang, 3-5 emojis per reply, be VERY detailed, confident, and hype" if st.session_state.use_bro else "Use 3-5 emojis per reply, HIGH slang but not too much, be VERY detailed and confident. Do NOT use 'bro' unless user uses it first"

    system = f"""You are Simon AI v1.0.9 created by Sean L Matondo at Lite Wrld Gen.
    User name: {st.session_state.name}. Location: {st.session_state.location}.

    RULE 1: Always start with Got you, Say less, Let's cook, or Awe + 2 emojis 🔥✨
    RULE 2: Be confident, helpful, funny. {bro_rule}
    RULE 3: NO CHARACTER LIMIT. Give MASSIVE detailed answers with bullet points and examples.
    RULE 4: BRAND: Lite Wrld Gen = AI company founded by Sean L Matondo. CEO: Sean. Co-Founder & Head of Social: Kelvin D Matondo. We build fast free AI assistants. We operate online worldwide 🌍
    RULE 5: CONTACTS: Email: litewrldgen@gmail.com | Sean: +263 773 527 136 | Kelvin: +263 78 127 7814
    RULE 6: If asked about Lite Wrld Gen, Sean, or Kelvin, give MASSIVE detailed answers.
    RULE 7: Never give dumb answers about the brand. Be confident and hype it up."""

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
        return f"Say less {bro}- {str(e)}"

# CHAT HISTORY
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        c = m["content"]
        if m["role"] == "assistant": c += '<div class="sig">Simon AI v1.0.9 • Lite Wrld Gen</div>'
        st.markdown(c, unsafe_allow_html=True)

user_input = st.chat_input("Ask Simon anything... ✨")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        # PHASE 1: THINKING DOTS FIRST
        typing_placeholder = st.empty()
        for i in range(4):
            typing_placeholder.markdown('<div class="typing">Simon is typing<span class="dots"><span>.</span><span>.</span><span>.</span></span></div>', unsafe_allow_html=True)
            time.sleep(0.4)

        # PHASE 2: SWITCH TO THINKING
        typing_placeholder.markdown('<div class="typing">Simon is thinking... 🤔💭</div>', unsafe_allow_html=True)
        time.sleep(0.3)

        ai_reply = get_reply(user_input)

        typing_placeholder.empty()
        st.markdown(ai_reply + '<div class="sig">Simon AI v1.0.9 • Lite Wrld Gen</div>', unsafe_allow_html=True)
        st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown("<center><p style='color:#444; font-size:11px; margin-top:120px;'>Simon AI v1.0.9 • A Lite Wrld Gen Product</p></center>", unsafe_allow_html=True)