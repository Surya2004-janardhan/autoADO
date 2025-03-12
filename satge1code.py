import requests
import sys
import os
import json
import time
from pathlib import Path

# Qwen API Endpoint
QWEN_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"

def find_recent_python_file(directory):
    """Find the most recently modified Python file in the given directory."""
    python_files = list(Path(directory).rglob("*.py"))  # Get all Python files
    if not python_files:
        print("❌ No Python files found in the current directory.")
        return None

    recent_file = max(python_files, key=lambda f: f.stat().st_mtime)
    return str(recent_file)

def send_code_to_qwen(file_path, task):
    """Reads the file, sends code to Qwen API, and replaces the old code with the response."""
    if not file_path or not os.path.exists(file_path):
        print(f"❌ Error: No valid Python file found.")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    if not code.strip():
        print("❌ Error: The file is empty.")
        return

    # Define prompts for different tasks
    prompt_map = {
        "analyze": "Analyze the following code and provide insights (brief points only):",
        "debug": "Find and explain any errors in the following code (brief points only), then provide the corrected code:",
        "optimize": "Optimize the following code for efficiency and readability, and provide the improved version:"
    }

    if task not in prompt_map:
        print(f"❌ Error: Unsupported task '{task}'. Use 'analyze', 'debug', or 'optimize'.")
        return

    full_prompt = f"{prompt_map[task]}\n\n```python\n{code}\n```"

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,  
        "temperature": 0.2,
        "max_tokens": 1024
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(QWEN_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        qwen_response = response.json().get("response", "")

        if not qwen_response:
            print("❌ No response received from Qwen.")
            return

        print("\n✅ Updating your code with Qwen's response...\n")

        # Overwrite the original file with the new response
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(qwen_response)

        print(f"✅ Code successfully updated in {file_path}!")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error communicating with Qwen: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <task>")
    else:
        recent_file = find_recent_python_file(os.getcwd())
        if recent_file:
            send_code_to_qwen(recent_file, sys.argv[1])
