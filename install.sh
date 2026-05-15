#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${GREEN}     Speedtest Studio - Complete Installation Script     ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Please do not run as root${NC}"
    exit 1
fi

# ============================================================
# STEP 1: Check System Requirements
# ============================================================
echo -e "${CYAN}📋 Step 1: Checking system requirements...${NC}"

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed${NC}"
    echo "   Please install: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi
echo -e "${GREEN}✅ Python3 found: $(python3 --version)${NC}"

# Check pip3
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed${NC}"
    echo "   Please install: sudo apt-get install python3-pip"
    exit 1
fi
echo -e "${GREEN}✅ pip3 found: $(pip3 --version | cut -d' ' -f1,2)${NC}"

# Check for venv module
if ! python3 -c "import venv" &> /dev/null; then
    echo -e "${RED}❌ python3-venv is not installed${NC}"
    echo "   Please install: sudo apt-get install python3-venv"
    exit 1
fi
echo -e "${GREEN}✅ Virtual environment support available${NC}"

# ============================================================
# STEP 2: Install System Dependencies
# ============================================================
echo -e "\n${CYAN}📦 Step 2: Installing system dependencies...${NC}"

# Update package list
echo "   Updating package list..."
sudo apt-get update -qq

# Install required system packages
SYSTEM_PACKAGES=(
    "python3-pyqt5"
    "python3-pyqt5.qtwidgets"
    "python3-psutil"
    "wireless-tools"
    "net-tools"
    "python3-tk"
    "libgl1-mesa-glx"
)

for package in "${SYSTEM_PACKAGES[@]}"; do
    if dpkg -l | grep -q $package; then
        echo -e "   ${GREEN}✓${NC} $package already installed"
    else
        echo "   Installing $package..."
        sudo apt-get install -y $package
    fi
done

echo -e "${GREEN}✅ System dependencies installed${NC}"

# ============================================================
# STEP 3: Create Application Directory Structure
# ============================================================
echo -e "\n${CYAN}📁 Step 3: Creating application directory structure...${NC}"

APP_DIR="$HOME/.local/share/speedtest-studio"
VENV_DIR="$APP_DIR/venv"
CONFIG_DIR="$HOME/.config/speedtest-studio"
LOGS_DIR="$APP_DIR/logs"

# Create directories
mkdir -p "$APP_DIR"
mkdir -p "$VENV_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOGS_DIR"

echo -e "${GREEN}✅ Directory structure created${NC}"
echo "   Application: $APP_DIR"
echo "   Virtual env: $VENV_DIR"
echo "   Config:      $CONFIG_DIR"

# ============================================================
# STEP 4: Setup Python Virtual Environment
# ============================================================
echo -e "\n${CYAN}🐍 Step 4: Creating Python virtual environment...${NC}"

# Create virtual environment
python3 -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to create virtual environment${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Virtual environment created${NC}"

# Activate and install packages
echo "   Installing Python packages in virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip -q

# Install required Python packages
PACKAGES=(
    "speedtest-cli"
    "psutil"
    "PyQt5"
    "PyQt5-sip"
    "GPUtil"
)

for package in "${PACKAGES[@]}"; do
    echo "   Installing $package..."
    pip install "$package" -q
done

# Verify installations
echo "   Verifying installations..."
python -c "import speedtest; import psutil; from PyQt5.QtWidgets import QApplication; import GPUtil" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All Python packages installed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Some packages may have issues, but continuing...${NC}"
fi

deactivate

# ============================================================
# STEP 5: Copy Application Files
# ============================================================
echo -e "\n${CYAN}📄 Step 5: Copying application files...${NC}"

# Check if source file exists
if [ ! -f "speedometer_gui.py" ]; then
    echo -e "${RED}❌ speedometer_gui.py not found in current directory${NC}"
    echo "   Please ensure your Python script is named 'speedometer_gui.py'"
    exit 1
fi

# Copy main application
cp speedometer_gui.py "$APP_DIR/"
chmod +x "$APP_DIR/speedometer_gui.py"
echo -e "${GREEN}✅ Application copied${NC}"

# Create launcher script
cat > "$APP_DIR/speedtest-studio" << 'EOF'
#!/bin/bash
# Speedtest Studio Launcher

APP_DIR="$HOME/.local/share/speedtest-studio"
VENV_DIR="$APP_DIR/venv"
LOG_FILE="$APP_DIR/logs/speedtest.log"

# Activate virtual environment and run
source "$VENV_DIR/bin/activate"
python "$APP_DIR/speedometer_gui.py" "$@" 2>&1 | tee -a "$LOG_FILE"
deactivate
EOF

chmod +x "$APP_DIR/speedtest-studio"
echo -e "${GREEN}✅ Launcher script created${NC}"

# Create version file
cat > "$APP_DIR/version.txt" << EOF
Speedtest Studio
Version: 1.0.0
Installation Date: $(date)
Python Environment: Virtual Environment
EOF

# ============================================================
# STEP 6: Create Desktop Integration
# ============================================================
echo -e "\n${CYAN}🖥️  Step 6: Creating desktop integration...${NC}"

# Desktop entry
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/speedtest-studio.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Speedtest Studio
Comment=Advanced Internet Speed Test with Hardware Monitoring
Exec=$APP_DIR/speedtest-studio
Icon=utilities-system-monitor
Terminal=false
Categories=Network;System;Monitor;
Keywords=speed;test;internet;network;benchmark;
StartupNotify=true
X-GNOME-UsesNotifications=true
EOF

echo -e "${GREEN}✅ Desktop entry created${NC}"

# Create symbolic link in ~/.local/bin
mkdir -p "$HOME/.local/bin"
ln -sf "$APP_DIR/speedtest-studio" "$HOME/.local/bin/speedtest-studio"
echo -e "${GREEN}✅ Symbolic link created in ~/.local/bin${NC}"

# Add ~/.local/bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bash_profile" 2>/dev/null
    echo -e "${YELLOW}⚠️  Added ~/.local/bin to PATH (restart terminal or run 'source ~/.bashrc')${NC}"
fi

# ============================================================
# STEP 7: Create Configuration File
# ============================================================
echo -e "\n${CYAN}⚙️  Step 7: Creating default configuration...${NC}"

cat > "$CONFIG_DIR/settings.json" << EOF
{
    "version": "1.0.0",
    "theme": "dark",
    "auto_start": false,
    "history_limit": 10,
    "hardware_monitoring": true,
    "update_interval_ms": 30,
    "gauge_max_speeds": [10, 50, 100, 500, 1000]
}
EOF

echo -e "${GREEN}✅ Configuration created${NC}"

# ============================================================
# STEP 8: Post-Installation Setup
# ============================================================
echo -e "\n${CYAN}🔧 Step 8: Post-installation setup...${NC}"

# Check for GPU support
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ NVIDIA GPU detected - Full GPU monitoring available${NC}"
else
    echo -e "${YELLOW}⚠️  No NVIDIA GPU detected - Basic GPU info only${NC}"
fi

# Check network interfaces
if command -v iwgetid &> /dev/null; then
    echo -e "${GREEN}✅ Wireless tools available${NC}"
else
    echo -e "${YELLOW}⚠️  iwgetid not found - WiFi detection limited${NC}"
fi

# Create uninstall script
cat > "$APP_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# Uninstall script is located in the original installation directory
# Please run uninstall.sh from where you originally installed
echo "Please run the original uninstall.sh script"
EOF

chmod +x "$APP_DIR/uninstall.sh"

# ============================================================
# INSTALLATION SUMMARY
# ============================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Installation Complete Successfully!         ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📊 Installation Details:${NC}"
echo -e "   ${GREEN}•${NC} Application:    ${YELLOW}Speedtest Studio${NC}"
echo -e "   ${GREEN}•${NC} Location:       ${YELLOW}$APP_DIR${NC}"
echo -e "   ${GREEN}•${NC} Virtual Env:    ${YELLOW}$VENV_DIR${NC}"
echo -e "   ${GREEN}•${NC} Config:         ${YELLOW}$CONFIG_DIR${NC}"
echo -e "   ${GREEN}•${NC} Logs:           ${YELLOW}$LOGS_DIR${NC}"
echo ""
echo -e "${CYAN}🚀 How to Run:${NC}"
echo -e "   ${GREEN}1.${NC} From terminal:  ${YELLOW}speedtest-studio${NC}"
echo -e "   ${GREEN}2.${NC} From menu:       ${YELLOW}Applications → Speedtest Studio${NC}"
echo -e "   ${GREEN}3.${NC} Direct:         ${YELLOW}$APP_DIR/speedtest-studio${NC}"
echo ""
echo -e "${CYAN}📦 Installed Packages (in venv):${NC}"
echo -e "   • speedtest-cli  (Speed testing)"
echo -e "   • psutil         (Hardware monitoring)"
echo -e "   • PyQt5          (GUI framework)"
echo -e "   • GPUtil         (GPU monitoring)"
echo ""
echo -e "${YELLOW}💡 Note: If 'speedtest-studio' command not found, run:${NC}"
echo -e "   ${BLUE}source ~/.bashrc${NC} ${YELLOW}or${NC} ${BLUE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"