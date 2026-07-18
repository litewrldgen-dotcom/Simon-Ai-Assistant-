import streamlit as st

def render_header():
    st.markdown("""
    <div class="topbar">
        <div class="logo"></div>
        <div>
            <div class="title">Simon AI v1.0.9 <span style="color:#00ff88;">✓</span> <span class="badge">LITE WRLD GEN</span></div>
            <div class="sub">Powered by Lite Wrld Gen</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar(memory):
    with st.sidebar:
        st.markdown("### 🧠 Simon AI")
        st.markdown("---")
        st.button("💬 New Chat", use_container_width=True)
        st.button("📂 History", use_container_width=True)
        st.button("📁 Files", use_container_width=True)
        st.button("🧠 Memory", use_container_width=True)
        st.button("⚙ Settings", use_container_width=True)
        st.markdown("---")
        st.markdown(f"**Creator:** Sean L. Matondo")
        st.markdown(f"**Company:** Lite Wrld Gen")
        st.markdown(f"**Model:** Llama 3.3 70B")
        st.markdown(f"**Memory:** {'Enabled' if memory else 'Off'}")

def render_chat_message(role, content):
    with st.chat_message(role):
        st.markdown(content)