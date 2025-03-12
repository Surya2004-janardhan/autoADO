import requests
import sys
import os
import json

# Qwen API Endpoint
QWEN_API_URL = "http://127.0.0.1:11434/api/generate"

# Change this to match your available model in `ollama list`
MODEL_NAME = "qwen2.5-coder:1.5b"

def send_code_to_qwen(file_path, task):
    """Reads the file, sends code to Qwen API, and prints response."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    if not code.strip():
        print("❌ Error: The file is empty.")
        return

    # Construct prompt for Qwen
    prompt_map = {
        "analyze": "Analyze the following code and provide insights frame breif points:",
        "debug": "Find and explain any errors in the following code frame breif points only and in the end give overall corrected code in one go :",
        "optimize": "Optimize the following code for efficiency and readability and tell what points u\you optimized , in the end give overall optimized code in one go:"
    }

    if task not in prompt_map:
        print(f"❌ Error: Unsupported task '{task}'. Use 'analyze', 'debug', or 'optimize'.")
        return

    full_prompt = f"{prompt_map[task]}\n\n```python\n{code}\n```"

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,  # Set to True if you want streaming responses
        "temperature": 0.2,
        "max_tokens": 1024
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(QWEN_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        qwen_response = response.json().get("response", "No response received.")

        print("\n📢 Qwen AI Response:\n")
        print(qwen_response)
        print("\n──────────────────────────────────\n")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error communicating with Qwen: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python qwen_client.py <file_path> <task>")
    else:
        send_code_to_qwen(sys.argv[1], sys.argv[2])
