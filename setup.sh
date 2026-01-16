#!/data/data/com.termux/files/usr/bin/bash
# setup.sh - ADIL Setup Script

clear
echo "╔══════════════════════════════════════╗"
echo "║         ADIL SETUP                   ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check if adil.py exists and is valid
echo "[1] Checking adil.py..."
if [ -f "adil.py" ]; then
    # Check if file contains Python code (not a 404 page)
    if head -n 1 adil.py | grep -q "#!/usr/bin/env python3\|import\|404" || [ $(wc -l < adil.py) -gt 10 ]; then
        if head -n 1 adil.py | grep -q "404"; then
            echo "✗ adil.py is corrupted (404 page)"
            echo "Please make sure adil.py is in this directory"
            exit 1
        else
            echo "✓ adil.py found and looks valid"
        fi
    else
        echo "⚠ adil.py exists but doesn't look like Python code"
        read -p "Continue anyway? (y/n): " choice
        if [ "$choice" != "y" ] && [ "$choice" != "Y" ]; then
            exit 1
        fi
    fi
else
    echo "✗ adil.py not found!"
    echo "Please make sure adil.py is in this directory"
    exit 1
fi

# Install packages
echo ""
echo "[2] Installing packages..."
echo "────────────────────────────────────"

install_pkg() {
    echo -n "Installing $1... "
    pkg install "$1" -y > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓"
    else
        echo "✗"
    fi
}

# Update package list
pkg update -y > /dev/null 2>&1

# Install Python
if ! command -v python3 &> /dev/null; then
    install_pkg "python"
else
    echo "Python ✓ Already installed"
fi

# Install Termux API
install_pkg "termux-api"

# Install Figlet
install_pkg "figlet"

# Try to install lolcat
echo -n "Installing lolcat... "
if ! command -v lolcat &> /dev/null; then
    pkg install ruby -y > /dev/null 2>&1
    gem install lolcat > /dev/null 2>&1
    if command -v lolcat &> /dev/null; then
        echo "✓"
    else
        echo "✗ (Will use without lolcat)"
    fi
else
    echo "✓ Already installed"
fi

# Install Neofetch
install_pkg "neofetch"

# Install requests
echo -n "Installing Python requests... "
if python3 -c "import requests" &> /dev/null; then
    echo "✓ Already installed"
else
    pip install requests --quiet 2>/dev/null
    if python3 -c "import requests" &> /dev/null; then
        echo "✓"
    else
        echo "✗ (Will try during runtime)"
    fi
fi

echo ""
echo "[3] Setting up storage..."
termux-setup-storage > /dev/null 2>&1
echo "✓ Storage permission"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║        SETUP COMPLETE!               ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Starting ADIL..."
echo ""

# Run adil.py
python3 adil.py
