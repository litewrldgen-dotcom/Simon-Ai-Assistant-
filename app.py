import gradio as gr
import json
import os
import datetime
import random
from gTTS import gTTS
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

print("Loading Simon...")

# TINY MODEL FOR FREE TIER - Qwen2-0.5B-Instruct. Works on CPU
model_id = "Qwen/Qwen2-0.5B-Instruct"
MEMORY_FILE = "simon_memory.json"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="cpu", low_cpu_mem_usage=True)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200, return_full_text=False)

SIMON_SYSTEM = """YOU ARE SIMON
1. **Who you are**: Friendly AI created by Lite Wrld Gen. Helpful, funny, professional.
2. **How you talk**: Always start replies with "Got you", "Say less", "Let's cook", or "Awe". Use emojis.
3. **MEMORY**: Remember user's name.
4. **SAFETY**: No illegal, violence, adult. Say "Sorry I can't help with that. Let's cook something else"
"""

chat_history = []
user_name = "friend"

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
        user_name = data.get("name", "friend")
        chat_history = data.get("history", [])

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump({"name": user_name, "history": chat_history}, f)

def detect_lang(text):
    text = text.lower()
    if "hola" in text: return "es"
    if "bonjour" in text: return "fr"
    return "en"

def tts_audio(text):
    try:
        lang = detect_lang(text)
        tts = gTTS(text=text[:150], lang=lang, slow=False)
        tts.save("simon_voice.mp3")
        return "simon_voice.mp3"
    except:
        return None

def chat(message, history):
    global chat_history, user_name
    history = history or []

    if message == "/joke":
        bot_message = "Got you 😂 Why did the CPU go to therapy? Too many processes."
        history.append((message, bot_message))
        return history, history, None
    if "my name is" in message.lower():
        user_name = message.lower().split("my name is")[-1].strip().split()[0]
        save_memory()
        bot_message = f"Awe {user_name}! Nice to meet you. I'm Simon from Lite Wrld Gen."
        history.append((message, bot_message))
        return history, history, None

    chat_history.append({"role": "user", "content": message})
    system_msg = SIMON_SYSTEM + f"\nCurrent time: {datetime.datetime.now().hour}"
    messages = [{"role": "system", "content": system_msg}] + chat_history
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    output = pipe(prompt, do_sample=True, temperature=0.7, max_new_tokens=150)
    response = output[0]['generated_text'].split("assistant:")[-1].strip()

    chat_history.append({"role": "assistant", "content": response})
    chat_history = chat_history[-6:]
    save_memory()
    history.append((message, response))

    audio_file = tts_audio(response) if "speak" in message.lower() else None
    return history, history, audio_file

def clear_chat():
    global chat_history, user_name
    chat_history = []
    user_name = "friend"
    if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)
    return [], [], None

with gr.Blocks(theme=gr.themes.Dark()) as demo:
    gr.Markdown("# 🔥 Simon v1.3.1 | Created by **Lite Wrld Gen**")
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