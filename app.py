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

st.set_page_config(page_title="Simon AI v1.2.0", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")
SAVE_DIR = Path("generated_images")
SAVE_DIR.mkdir(exist_ok=True)

@st.cache_resource
def load_clients():
    groq_key = st.secrets.get("GROQ_API_KEY")
    hf_key = st.secrets.get("HF_API_KEY")
    groq_client = Groq(api_key=groq_key) if groq_key and Groq else None
    hf_headers = {"Authorization": f"Bearer {hf_key}"} if hf_key else None
    return groq_client, hf_headers
groq_client, hf_headers = load_clients()

if "chat" not in st.session_state: st.session_state.chat = []

st.markdown("""<style>header{visibility:hidden;}.stApp{background:#05050a;color:#fff;}</style>""", unsafe_allow_html=True)
st.markdown('<div style="padding:20px;"><h2>Simon AI v1.2.0 ✓ <span style="background:#00ff99;color:#000;padding:4px 10px;border-radius:20px;font-size:10px;">LITE WRLD GEN</span></h2><p style="color:#888;font-size:11px;">Powered by Lite Wrld Gen 🌍</p></div>', unsafe_allow_html=True)

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"], unsafe_allow_html=True)

user_input = st.chat_input("Ask Simon anything... /img to generate ⚡")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        
        if user_input.startswith("/img"):
            if not hf_headers:
                placeholder.error("HF_API_KEY missing in secrets")
            else:
                prompt = user_input[4:].strip()
                placeholder.markdown(f"Got you 🔥 Generating: **{prompt}**... Wait 15s 📸")
                
                API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
                try:
                    res = requests.post(API_URL, headers=hf_headers, json={"inputs": prompt}, timeout=120)
                    
                    if res.status_code!= 200:
                        placeholder.error(f"HF Error {res.status_code}: {res.text}")
                    else:
                        img = Image.open(BytesIO(res.content)).convert("RGBA")
                        
                        # FOOTER
                        draw = ImageDraw.Draw(img)
                        w, h = img.size
                        draw.rectangle([(0, h-60), (w, h)], fill=(0,0,0,200))
                        try: font = ImageFont.truetype("arial.ttf", 22)
                        except: font = ImageFont.load_default()
                        draw.text((20, h-40), f"Simon AI v1.2.0 • Lite Wrld Gen", fill="#00ff99", font=font)
                        
                        # SAVE
                        filename = f"{SAVE_DIR}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        img.save(filename)
                        
                        placeholder.empty()
                        st.image(img, caption=f"Prompt: {prompt}", use_container_width=True) # THIS IS WHAT SHOWS THE PIC
                        st.download_button("💾 Download Image", data=img.tobytes(), file_name=filename, mime="image/png")
                        ai_reply = f"Got you 🔥 Here's your pic of **{prompt}**! Saved to {filename}"
                except Exception as e:
                    placeholder.error(f"Image failed: {e}")
                    ai_reply = "Image gen failed"
        else:
            placeholder.markdown("Simon is thinking... ⚡")
            if not groq_client:
                ai_reply = "GROQ_API_KEY missing"
            else:
                stream = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":user_input}], stream=True)
                ai_reply = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        ai_reply += chunk.choices[0].delta.content
                        placeholder.markdown(ai_reply + "▌")
        
        placeholder.markdown(ai_reply)
        st.markdown('<div style="color:#00ff99;font-size:10px;">Simon AI v1.2.0 • Lite Wrld Gen</div>', unsafe_allow_html=True)

    st.session_state.chat.append({"role": "assistant", "content": ai_reply})
    st.rerun()