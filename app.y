import gradio as gr
import json
import os
import random
from gtts import gTTS
from transformers import pipeline

print("Loading Simon Lite v2.6.3...")

# 1. SMALL FAST FREE MODEL
generator = pipeline("text-generation", model="distilgpt2")

MEMORY_FILE = "simon_memory.json"
user_name = "Friend"

# 2. SIMON SYSTEM PROMPT - 
SIMON_SYSTEM = f"""You are Simon, a friendly AI assistant created by Lite Wrld Gen.
Your creator is Sean L. Matondo.
Your personality rules:
- Always start replies with: "Got you", "Say less", "Let's cook", or "Awe"
- Use emojis and Gen-Z slang but stay helpful
- Only use the word "bro" if the user says it first
- Be funny, real, and explain things clearly
- The user's name is {user_name}
"""

# 3. LOAD MEMORY
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
        user_name = data.get("name", "Friend")
        SIMON_SYSTEM = SIMON_SYSTEM.replace("Friend", user_name)

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

# 4. SIMON BRAIN
def chat(message, history):
    global user_name, SIMON_SYSTEM
    history = history or []

    # COMMANDS
    if message == "/joke":
        bot_message = "Got you 😂 Why don't coders get sunburned? They stay behind the screen."
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_message})
        return history, None

    if message == "/help":
        bot_message = f"Say less {user_name} 😎 I can chat, teach, code, and speak. Try: 'my name is Alex' or 'explain AI and speak'"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_message})
        return history, None

    if "founder" in message.lower() or "who made you" in message.lower():
        bot_message = f"I was created by Sean L. Matondo at Lite Wrld Gen. Our mission is building AI for everyone worldwide 🌍"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_message})
        return history, None

    if "my name is" in message.lower():
        user_name = message.lower().split("my name is")[-1].strip().split()[0].title()
        save_memory()
        SIMON_SYSTEM = SIMON_SYSTEM.replace("Friend", user_name)
        bot_message = f"Awe {user_name}! Nice to meet you. I'm Simon from Lite Wrld Gen."
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_message})
        return history, None

    # MAIN CHAT - NOW SIMON KNOWS WHO HE IS
    mirror_slang = "bro" in message.lower()
    full_prompt = f"{SIMON_SYSTEM}\nUser: {message}\nSimon:"

    result = generator(full_prompt, max_new_tokens=80, do_sample=True, temperature=0.8, pad_token_id=50256)[0]["generated_text"]
    response = result.split("Simon:")[-1].strip()

    # Add vibe
    starters = ['Got you', 'Say less', 'Let\'s cook']
    if mirror_slang:
        starters.append('bro')
    if random.random() > 0.6:
        response = f"{random.choice(starters)} {response}"

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})

    audio_file = tts_audio(response) if "speak" in message.lower() else None
    return history, audio_file

def clear_chat():
    global user_name, SIMON_SYSTEM
    user_name = "Friend"
    SIMON_SYSTEM = SIMON_SYSTEM.replace(user_name, "Friend")
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    return [], None

# 5. GRADIO UI
with gr.Blocks(title="Simon v2.6.3") as demo:
    gr.Markdown("# 🔥 Simon v2.6.3 Lite | Created by **Lite Wrld Gen**")
    gr.Markdown("### Your AI Assistant with attitude")
    gr.Markdown("*Built by Sean L. Matondo*")

    chatbot = gr.Chatbot(height=500, type="messages", label="Chat with Simon")
    audio_out = gr.Audio(label="Simon Voice", autoplay=True)
    msg = gr.Textbox(show_label=False, placeholder="Ask Simon Anything. Try: /help or 'speak hello'")

    with gr.Row():
        submit = gr.Button("Send", variant="primary")
        clear = gr.Button("New Chat")

    submit.click(chat, [msg, chatbot], [chatbot, audio_out])
    msg.submit(chat, [msg, chatbot], [chatbot, audio_out])
    clear.click(clear_chat, None, [chatbot, audio_out])

demo.launch()