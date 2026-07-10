import gradio as gr
import json
import os
import datetime
import random
from gtts import gTTS
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

print("Loading Simon Lite...")

model_id = "google/flan-t5-small"
MEMORY_FILE = "simon_memory.json"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

SIMON_SYSTEM = """You are Simon, a friendly AI created by Lite Wrld Gen.
Rules: 1. Start replies with "Got you", "Say less", "Let's cook", or "Awe". 2. Use emojis.
3. Remember user's name. 4. Be helpful and funny."""

user_name = "friend"

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
        user_name = data.get("name", "friend")

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump({"name": user_name}, f)

def tts_audio(text):
    try:
        tts = gTTS(text=text[:150], lang="en", slow=False)
        tts.save("simon_voice.mp3")
        return "simon_voice.mp3"
    except:
        return None

def chat(message, history):
    global user_name
    history = history or []

    if message == "/joke":
        bot_message = "Got you 😂 Why did the computer get cold? It left its Windows open."
        history.append((message, bot_message))
        return history, history, None
    if message == "/help":
        bot_message = "Got you. I can chat, code, teach, and speak. Say 'speak' to hear me. Try 'my name is Alex'"
        history.append((message, bot_message))
        return history, history, None
    if "my name is" in message.lower():
        user_name = message.lower().split("my name is")[-1].strip().split()[0]
        save_memory()
        bot_message = f"Awe {user_name}! Nice to meet you. I'm Simon from Lite Wrld Gen."
        history.append((message, bot_message))
        return history, history, None
    if "call me" in message.lower():
        user_name = message.lower().split("call me")[-1].strip().split()[0]
        save_memory()
        bot_message = f"Got you {user_name}. I'll remember that."
        history.append((message, bot_message))
        return history, history, None

    prompt = f"{SIMON_SYSTEM}\nUser name: {user_name}\nUser: {message}\nSimon:"

    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if random.random() > 0.7: response = response + f" How you feeling {user_name}?"
    history.append((message, response))

    audio_file = tts_audio(response) if "speak" in message.lower() or "say it" in message.lower() else None
    return history, history, audio_file

def clear_chat():
    global user_name
    user_name = "friend"
    if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)
    return [], None

# REMOVED THEME TO FIX CRASH
with gr.Blocks() as demo:
    gr.Markdown("# 🔥 Simon v2.1 Lite | Created by **Lite Wrld Gen**")
    gr.Markdown("### Now with 0 crashes 💪")
    chatbot = gr.Chatbot(height=500)
    audio_out = gr.Audio(label="Simon Voice")
    msg = gr.Textbox(placeholder="Ask Simon Anything. Try /help or 'speak'")
    with gr.Row():
        submit = gr.Button("Send", variant="primary")
        clear = gr.Button("New Chat")

    msg.submit(chat, [msg, chatbot], [chatbot, chatbot, audio_out])
    submit.click(chat, [msg, chatbot], [chatbot, chatbot, audio_out])
    clear.click(clear_chat, None, [chatbot, chatbot, audio_out])

demo.launch()