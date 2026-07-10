import gradio as gr
import json
import os
import random
from gtts import gTTS
from transformers import T5ForConditionalGeneration, T5Tokenizer

print("Loading Simon Lite v2.3...")

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

MEMORY_FILE = "simon_memory.json"
user_name = "friend" # default name

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
        bot_message = "Got you 😂 Why don't programmers like nature? Too many bugs."
        history.append((message, bot_message))
        return history, history, None
    if message == "/help":
        bot_message = "Got you. I'm Simon from Lite Wrld Gen. I can chat, code, teach, and speak. Say 'speak' to hear me."
        history.append((message, bot_message))
        return history, history, None
    if "my name is" in message.lower():
        user_name = message.lower().split("my name is")[-1].strip().split()[0]
        save_memory()
        bot_message = f"Awe {user_name}! Nice to meet you. I'll remember that."
        history.append((message, bot_message))
        return history, history, None

    # NEUTRAL PROMPT - doesn't assume who it's talking to
    prompt = f"You are Simon from Lite Wrld Gen. Be helpful, funny. Start with 'Got you' or 'Say less'. Question: {message}"
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=100)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    history.append((message, response))
    audio_file = tts_audio(response) if "speak" in message.lower() else None
    return history, history, audio_file

def clear_chat():
    global user_name
    user_name = "friend"
    if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)
    return [], None

with gr.Blocks() as demo:
    gr.Markdown("# 🔥 Simon v2.3 Lite | Created by **Lite Wrld Gen**")
    gr.Markdown("### Your AI Assistant")
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