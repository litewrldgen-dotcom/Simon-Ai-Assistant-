import json, os
MEMORY_PATH = "memory/user_memory.json"
def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r") as f: return json.load(f)
    return {}
def save_memory(data):
    with open(MEMORY_PATH, "w") as f: json.dump(data, f)
def update_memory(key, value):
    data = load_memory()
    data[key] = value
    save_memory(data)