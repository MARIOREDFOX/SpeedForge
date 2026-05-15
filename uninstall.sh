#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║         Speedtest Studio - Complete Uninstallation       ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Confirm uninstallation
echo -e "${YELLOW}⚠️  Warning: This will completely remove Speedtest Studio${NC}"
echo -e "   This includes:"
echo -e "   • Application files"
echo -e "   • Python virtual environment"
echo -e "   • Configuration files"
echo -e "   • Logs and data"
echo -e "   • Desktop integration"
echo ""
read -p "Are you sure you want to continue? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Uninstallation cancelled.${NC}"
    exit 0
fi

echo ""

# ============================================================
# STEP 1: Remove Application Directory and Virtual Environment
# ============================================================
echo -e "${CYAN}🗑️  Step 1: Removing application and virtual environment...${NC}"

APP_DIR="$HOME/.local/share/speedtest-studio"
VENV_DIR="$APP_DIR/venv"

if [ -d "$APP_DIR" ]; then
    # Deactivate venv if active
    if [ ! -z "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null
    fi
    
    rm -rf "$APP_DIR"
    echo -e "${GREEN}✅ Removed: $APP_DIR${NC}"
else
    echo -e "${YELLOW}⚠️  Application directory not found${NC}"
fi

# ============================================================
# STEP 2: Remove Configuration Files
# ============================================================
echo -e "\n${CYAN}🗑️  Step 2: Removing configuration files...${NC}"

CONFIG_DIR="$HOME/.config/speedtest-studio"
if [ -d "$CONFIG_DIR" ]; then
    rm -rf "$CONFIG_DIR"
    echo -e "${GREEN}✅ Removed: $CONFIG_DIR${NC}"
else
    echo -e "${YELLOW}⚠️  Config directory not found${NC}"
fi

# ============================================================
# STEP 3: Remove Desktop Integration
# ============================================================
echo -e "\n${CYAN}🗑️  Step 3: Removing desktop integration...${NC}"

# Desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/speedtest-studio.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo -e "${GREEN}✅ Removed desktop entry${NC}"
else
    echo -e "${YELLOW}⚠️  Desktop entry not found${NC}"
fi

# Symbolic link in ~/.local/bin
LOCAL_BIN_LINK="$HOME/.local/bin/speedtest-studio"
if [ -L "$LOCAL_BIN_LINK" ]; then
    rm "$LOCAL_BIN_LINK"
    echo -e "${GREEN}✅ Removed symbolic link from ~/.local/bin${NC}"
fi

# Remove from PATH in bashrc (optional)
if grep -q "speedtest-studio" "$HOME/.bashrc" 2>/dev/null; then
    sed -i '/speedtest-studio/d' "$HOME/.bashrc"
    echo -e "${GREEN}✅ Cleaned up PATH entries in .bashrc${NC}"
fi

# ============================================================
# STEP 4: Remove Old History Files (Optional)
# ============================================================
echo -e "\n${CYAN}🗑️  Step 4: Cleaning up old data files...${NC}"

HISTORY_FILE="$HOME/.speedometer_history.json"
if [ -f "$HISTORY_FILE" ]; then
    read -p "Remove old speed test history? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$HISTORY_FILE"
        echo -e "${GREEN}✅ Removed history file${NC}"
    fi
fi

# ============================================================
# STEP 5: Python Packages Cleanup (Optional)
# ============================================================
echo -e "\n${CYAN}🐍 Step 5: Python packages cleanup...${NC}"
echo -e "${YELLOW}Note: Python packages were installed in a virtual environment${NC}"
echo -e "      which has been removed with the application directory."
echo ""
read -p "Remove globally installed Python packages (speedtest-cli, psutil, GPUtil)? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing Python packages...${NC}"
    pip3 uninstall -y speedtest-cli psutil GPUtil 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Removed Python packages${NC}"
    else
        echo -e "${YELLOW}⚠️  Packages not found or already removed${NC}"
    fi
fi

# ============================================================
# STEP 6: System Dependencies (Optional)
# ============================================================
echo -e "\n${CYAN}📦 Step 6: System dependencies...${NC}"
echo -e "${YELLOW}System packages (python3-pyqt5, python3-psutil, wireless-tools)${NC}"
echo -e "were installed as system dependencies."
echo ""
read -p "Remove system packages? (y/n) - This may affect other applications: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing system packages...${NC}"
    sudo apt-get remove -y python3-pyqt5 python3-psutil wireless-tools 2>/dev/null
    sudo apt-get autoremove -y
    echo -e "${GREEN}✅ Removed system packages${NC}"
fi

# ============================================================
# UNINSTALLATION SUMMARY
# ============================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Uninstallation Complete Successfully!        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📋 Removed items:${NC}"
echo -e "   ${GREEN}✓${NC} Application and virtual environment"
echo -e "   ${GREEN}✓${NC} Configuration files"
echo -e "   ${GREEN}✓${NC} Desktop integration"
echo -e "   ${GREEN}✓${NC} Symbolic links"
echo ""
echo -e "${YELLOW}💡 To complete cleanup, you may want to:${NC}"
echo -e "   • Close any running instances of Speedtest Studio"
echo -e "   • Restart your terminal session"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"