import gradio as gr
import json
import os
import random
from gtts import gTTS
from transformers import T5ForConditionalGeneration, T5Tokenizer

print("Loading Simon Lite v2.6...")

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

MEMORY_FILE = "simon_memory.json"
user_name = "friend"

# SIMON SYSTEM RULES ARE BACK 🔥
SIMON_SYSTEM = """You are Simon, an AI created by Lite Wrld Gen.
Rules:
1. Always start replies with: "Got you", "Say less", "Let's cook", or "Awe"
2. Use emojis and Gen-Z slang
3. Be helpful, funny, and real
4. If user says "my name is ___" remember it
5. If user says "speak" add voice"""

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
        bot_message = "Got you 😂 Why don't coders get sunburned? They stay behind the screen."
        history.append((message, bot_message))
        return history, history, None
    if message == "/help":
        bot_message = f"Say less {user_name}. I chat, code, teach, and speak. Try 'my name is Alex' or 'speak hello'"
        history.append((message, bot_message))
        return history, history, None
    if "my name is" in message.lower():
        user_name = message.lower().split("my name is")[-1].strip().split()[0]
        save_memory()
        bot_message = f"Awe {user_name}! Nice to meet you. I'm Simon from Lite Wrld Gen."
        history.append((message, bot_message))
        return history, history, None

    # RULES ARE BACK IN THE PROMPT
    prompt = f"{SIMON_SYSTEM}\nUser name: {user_name}\nUser: {message}\nSimon:"
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=120, do_sample=True, temperature=0.8)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Add random Simon vibe
    if random.random() > 0.6:
        response = f"{random.choice(['Got you', 'Say less', 'Let's cook'])} {response}"

    history.append((message, response))
    audio_file = tts_audio(response) if "speak" in message.lower() else None
    return history, history, audio_file

def clear_chat():
    global user_name
    user_name = "friend"
    if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)
    return [], None

# NO THEME HERE = NO CRASH
with gr.Blocks() as demo:
    gr.Markdown("# 🔥 Simon v2.6 Lite | Created by **Lite Wrld Gen**")
    gr.Markdown("### Your AI with attitude")
    chatbot = gr.Chatbot(height=500)
    audio_out = gr.Audio(label="Simon Voice")
    msg = gr.Textbox(placeholder="Ask Simon Anything. Try: /help or 'speak'")
    with gr.Row():
        submit = gr.Button("Send", variant="primary")
        clear = gr.Button("New Chat")

    submit.click(chat, [msg, chatbot], [chatbot, chatbot, audio_out])
    msg.submit(chat, [msg, chatbot], [chatbot, chatbot, audio_out])
    clear.click(clear_chat, None, [chatbot, chatbot, audio_out])

demo.launch()