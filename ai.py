import streamlit as st
import requests, random

STARTERS = ["Got you 🔥", "Say less 😎", "Let's cook ⚡", "Awe 🤝", "Roger that 🚀"]
HF_API_KEY = st.secrets["HF_API_KEY"]
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-VL-72B-Instruct"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

def get_ai_response(chat_history, memory, image_data=None):
    system = f"""You are Simon AI v1.0.9f by Sean L Matondo at Lite Wrld Gen.
    User: {memory.get('name','Bro')}.
    RULE 1: Start with {random.choice(STARTERS)}
    RULE 2: Use 3-5 emojis, HIGH slang. No 'bro' unless user says it.
    RULE 3: BRAND: Lite Wrld Gen = AI company by Sean L Matondo. CEO: Sean. Co-Founder: Kelvin D Matondo. Email: litewrldgen@gmail.com | Sean: +263 773 527 136 | Kelvin: +263 78 127 7814
    RULE 4: Give MASSIVE detailed answers."""

    messages = [{"role": "system", "content": system}]

    if image_data:
        messages.append({"role": "user", "content": [{"type": "text", "text": chat_history[-1]["content"]}, {"type": "image", "image": image_data}]})
    else:
        messages.extend(chat_history)

    payload = {"inputs": messages, "parameters": {"max_new_tokens": 2000, "temperature": 0.9}}
    response = requests.post(API_URL, headers=headers, json=payload)
    text = response.json()[0]["generated_text"].split("assistant to=user")[-1]
    for word in text.split(): yield word + " "