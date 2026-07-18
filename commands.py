import streamlit as st
def handle_command(cmd, memory, role):
    if cmd == "/memory": return f"🧠 I remember: {memory}"
    if cmd == "/brand": return "🔥 Lite Wrld Gen by Sean L Matondo + Kelvin D Matondo. We build free AI for the world 🌍"
    if cmd == "/staff" and role == "staff": return "👑 Staff panel unlocked bro"
    return "Command not found 😅"