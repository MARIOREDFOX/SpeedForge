#!/bin/bash

# Quick setup wrapper script

echo "Speedtest Studio - Automated Setup"
echo "=================================="
echo ""

# Check if script exists
if [ ! -f "speedometer_gui.py" ]; then
    echo "❌ Error: speedometer_gui.py not found in current directory!"
    echo "Please rename your Python script to 'speedometer_gui.py'"
    exit 1
fi

# Make scripts executable
chmod +x install.sh uninstall.sh

# Run installation
./install.sh

# Check installation result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup completed successfully!"
    echo ""
    read -p "Launch Speedtest Studio now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Ensure PATH includes ~/.local/bin
        export PATH="$HOME/.local/bin:$PATH"
        speedtest-studio
    fi
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
