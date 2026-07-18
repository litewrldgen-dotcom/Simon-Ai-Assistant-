import streamlit as st

def render_header():
    st.markdown("""
    <div class="topbar">
        <div class="logo"></div>
        <div>
            <div class="title">Simon AI v1.0.9 <span style="color:#00ff88;">✓</span> <span class="badge">LITE WRLD GEN</span></div>
            <div class="sub">Powered by Lite Wrld Gen • HF Qwen2.5-VL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar(memory, role):
    with st.sidebar:
        st.markdown("### 🧠 Simon AI")
        st.markdown("---")
        if st.button("💬 New Chat", use_container_width=True): st.session_state.chat = []
        if st.button("📂 History", use_container_width=True): st.info("History coming in v1.1")
        if st.button("📁 Files", use_container_width=True): st.info("Check uploads/ folder")
        if st.button("🧠 Memory", use_container_width=True): st.json(memory)
        if st.button("⚙ Settings", use_container_width=True): st.session_state.use_bro = not st.session_state.use_bro

        st.markdown("---")
        st.markdown(f"**Role:** {role}")
        if role == "staff":
            st.success("👑 Staff Mode")
            if st.button("📊 View All Users"): st.info("Staff tool")

        st.markdown("---")
        st.markdown(f"**Creator:** Sean L. Matondo")
        st.markdown(f"**Company:** Lite Wrld Gen")
        st.markdown(f"**Model:** Qwen2.5-VL-72B")

def render_chat_message(role, content):
    with st.chat_message(role):
        st.markdown(content)