# RetroChat
A minimalist LLM prompting system for retro computers. Because KB and MHz are plenty enough for prompting purposes!

RetroChat is a proof-of-concept project that connects your retro computer to a modern LLM served by Ollama.

## Architecture
Because computers designed in the 80s lack the processing power to handle TLS encryption or complex JSON parsing, RetroChat relies on a "Man-in-the-Middle" proxy architecture:
- the retro computer runs a minimal terminal client.
- a modern PC runs a Python proxy that manages the serial connection and the chat context history, cleans the output and prompts the AI.
- a LLM is served through Ollama, on the proxy itself, or on a remote server.

## Prerequisites
### Scenerio A: Hardware + emulated hardware
 - a modern PC running the proxy and a retro computer emulator (eg Hatari for the Atari ST) 

### Scenario B: 100% hardware
 - a modern PC running the proxy
 - a compatible retro computer (Atari ST only for the moment)
 - a Null-modem cable connecting the proxy to the retro computer
 
### Software
 - a Ollama server accessible from the proxy, or running on the machine hosting the proxy
 - Python 3.x support on the machine running the proxy

## Installation (proxy-side)
1. Clone the repository: 
```
git clone https://github.com/fvandw/retrochat
cd retrochat
```

2. Install dependencies
```
pip install pyserial requests unidecode
```

3. pull an AI Model to run through Ollama (eg tinyllama)
```
ollama pull tinyllama
```

## Usage
### Scenario A: Hardware + emulated hardware

This method uses ``socat`` to create a virtual null-modem cable between the retro computer and the proxy.
1. **setup the virtual connection**
```bash
./cable.sh
# Creates /tmp/client_pty and /tmp/proxy_pty 
```

2. **start the proxy**
```bash
python3 proxy.py --model tinyllama
```

3. **Configure the emulator**
 - **Atari ST (Hatari)**
   - open Hatari settings (F12) 
   - go to ``Devices``
   - check ``Enable RS232 emulation``
   - set RS232 Read/Write file to: ``/tmp/client/pty``

4. **Run the Atari Client**
 - Load ``TERMINAL.LST`` in GFA Basic and run it.
  
### Scenario B: 100% Hardware
1. Connect the Cable: Plug the Null-Modem cable between the Atari and your PC (USB-Serial adapter).

2. Find your Serial Port:

- Linux: ``/dev/ttyUSB0`` or ``/dev/ttyACM0``
- Windows: ``COM3``, ``COM4``, etc.

Note: On Linux, ensure the current user is in the ``dialout`` group.

3. Start the proxy:
```
python3 proxy.py /dev/ttyUSB0 --model tinyllama
```

### License
GNU General Public License 3.0