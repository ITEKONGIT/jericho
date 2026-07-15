#!/usr/bin/env python3
import argparse
import requests
import sys
import json

# The internal IP of your Windows Inference Server
OLLAMA_HOST = "http://192.168.1.50:11434/api/generate"
DEFAULT_MODEL = "deepseek-coder" 

def stream_response(prompt, model, system_prompt=None):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    if system_prompt:
        payload["system"] = system_prompt

    try:
        with requests.post(OLLAMA_HOST, json=payload, stream=True, timeout=30) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line).get("response", "")
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
        print() 
        
    except requests.exceptions.RequestException as e:
        print(f"\n[-] API Connection Failed. Is the Windows node online? Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jericho Local AI Inference Bridge")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="Ollama model to execute")
    parser.add_argument("-s", "--system", help="System prompt to dictate AI behavior")
    parser.add_argument("prompt", nargs="?", help="Direct prompt text (optional if piping data)")

    args = parser.parse_args()

    piped_data = ""
    if not sys.stdin.isatty():
        piped_data = sys.stdin.read()

    final_prompt = ""
    if args.system:
        final_prompt += f"System Directive: {args.system}\n\n"
    if args.prompt:
        final_prompt += f"{args.prompt}\n"
    if piped_data:
        final_prompt += f"\nData Context:\n{piped_data}"

    if not final_prompt.strip():
        print("[-] Error: No prompt or piped data provided.")
        parser.print_help()
        sys.exit(1)

    stream_response(final_prompt, args.model, args.system)
