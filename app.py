import streamlit as st
import time
from ai import get_ai_response
from ui import render_header, render_sidebar
from memory import load_memory, save_memory
from file_reader import read_file
from styles import load_css

st.set_page_config(page_title="Simon AI", page_icon="✨", layout="wide")
load_css()

if "chat" not in st.session_state: st.session_state.chat = []
if "memory" not in st.session_state: st.session_state.memory = load_memory()

render_header()
render_sidebar()

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

col1, col2 = st.columns([9,1])
with col1:
    user_input = st.chat_input("Ask Simon anything... ✨")
with col2:
    uploaded_file = st.file_uploader("📁", type=["pdf","txt","png","jpg","jpeg"], label_visibility="collapsed")

if user_input or uploaded_file:
    file_context, image_data = "", None
    if uploaded_file:
        file_context, image_data = read_file(uploaded_file)
        if file_context:
            user_input = f"{user_input}\n\n[FILE]: {file_context[:3000]}"

    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        for chunk in get_ai_response(st.session_state.chat, st.session_state.memory, image_data):
            full_response += chunk
            placeholder.markdown(full_response + "▌")
            time.sleep(0.01)
        placeholder.markdown(full_response)
    st.session_state.chat.append({"role": "assistant", "content": full_response})
    st.rerun()