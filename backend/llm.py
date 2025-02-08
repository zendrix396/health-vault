import requests
import os
import threading
import time

def start_server():
    os.system("node clewd.js")

def initialize_server():
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True  # Make thread daemon so it exits when main program ends
    server_thread.start()
    time.sleep(3)  # Wait for server to start

def query_claude(query, system_prompt="You are Claude, an AI assistant."):
    url = "http://127.0.0.1:8444/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    data = {
        "model": "claude-3-5-sonnet-20241022",
        "messages": messages,
        "max_tokens": 1024,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# Initialize server when module is imported
initialize_server()