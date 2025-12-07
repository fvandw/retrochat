# This file is part of the RetroChat distribution (https://github.com/fvandw/retrochat).
# Copyright (c) 2025 fvandw.
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import serial
import requests
import unidecode
import time
import sys
import argparse

# --- CONFIGURATION ---
SYSTEM_PROMPT = {
    "role": "system", 
    "content": "You are a helpful assistant. Do not use Markdown (bold, italic, code blocks)."
}

def parse_arguments():
    parser = argparse.ArgumentParser(description="RetroChat serial Ollama proxy")
    
    parser.add_argument("port", nargs='?', default='/tmp/proxy_pty', 
                        help="Serial port (ex: /dev/ttyUSB0, COM3, or /tmp/proxy_pty)")
    
    parser.add_argument("--baud", type=int, default=9600, help="Baudrate")
    parser.add_argument("--model", type=str, default="gemma3:12b", help="Ollama model to query")
    parser.add_argument("--server", type=str, default="localhost", help="Ollama server address")
    parser.add_argument("--server_port", type=int, default=11434, help="Ollama server port")
    
    return parser.parse_args()

def clean_text(text):
    """
    ASCII clean up
    """
    if not text: return ""
    ascii_text = unidecode.unidecode(text)
    # markdown
    clean = ascii_text.replace('**', '').replace('##', '').replace('`', '')
    # CR+NL
    return clean.replace('\n', '\r\n')

def ask_ollama(url, model, history):
    """
    Prompts Ollama, sending back the conversation history
    """
    print(f" [Ollama] Sending context with {len(history)} messages...")
    try:
        response = requests.post(url, json={
            "model": model,
            "messages": history,
            "stream": False 
        })
        
        if response.status_code == 200:
            return response.json()['message']['content']
        else:
            return f"Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"Connection error: {e}"

def main():
    args = parse_arguments()
    SERIAL_PORT = args.port
    MODEL_NAME = args.model
    BAUDRATE = args.baud
    OLLAMA_BASE_URL = f"http://{args.server}:{args.server_port}/api/chat"
    print(f"--- Serial AI Proxy ---")
    print(f"Port: {SERIAL_PORT} \nBaudrate: {BAUDRATE}\nModel: {MODEL_NAME}")
    
    try:
        partner = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1, rtscts=False)
        print("Ready. Waiting for Partner...")
    except Exception as e:
        print(f"Cannot open port: {e}")
        sys.exit(1)

    conversation_history = [SYSTEM_PROMPT]
    buffer = ""
    
    while True:
        try:
            if partner.in_waiting > 0:
                char = partner.read().decode('ascii', errors='ignore')
                
                if char == '\r' or char == '\n':
                    prompt = buffer.strip()
                    
                    if prompt:
                        print(f" [User] {prompt}")
                        
                        # --- /NEW => restart conversation ---
                        if prompt.lower() == "/new":
                            conversation_history = [SYSTEM_PROMPT]
                            print(" [System] Conversation reset.")
                            partner.write(b'\r\n[Conversation Reset]\r\n\r\n> ')
                            buffer = ""
                            continue
                        
                        # 1. Add the prompt to the context
                        conversation_history.append({"role": "user", "content": prompt})
                        
                        # 2. Query Ollama with context
                        ai_reply = ask_ollama(OLLAMA_BASE_URL, MODEL_NAME, conversation_history)
                        print(f" [Model] {ai_reply[:50]}...")
                        
                        # 3. Add response to context
                        conversation_history.append({"role": "assistant", "content": ai_reply})
                        
                        # 4. clean up and send response
                        partner_msg = clean_text(ai_reply)
                        
                        partner.write(b'\r\n') 
                        for letter in partner_msg:
                            partner.write(letter.encode('ascii', errors='ignore'))
                            time.sleep(0.005) 
                            
                        partner.write(b'\r\n\r\n> ')
                        
                    buffer = "" # Reset buffer
                else:
                    buffer += char
            
            time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()