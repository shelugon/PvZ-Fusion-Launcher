# PVZ Fusion Launcher

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/maintained-yes-brightgreen.svg)](https://github.com/shelugon/PvZ-Fusion-Launcher/commits/main)

launcher for Plants vs. Zombies Fusion with automatic updates and mod management.

## Features

- **Game Launch**: Direct executable control with parameter customization (Working)
- **Auto-Updater**: Version checking and patching via GitHub Releases (Broken)
- **Mods Manages**: Built-in mod folder management (Partially working)
- **MelonLoader Automation**: One-click installation and configuration (Working)
- **Security Checks**: SHA-256 validation for all downloaded files (Idk)
- **Backup System**: Automatic backups before updates (Idk)

## Installation

### Requirements
- Python 3.8+
- Windows 10/11 (64-bit recommended)

### Quick Start
```bash
# Clone repository
git clone https://github.com/shelugon/PvZ-Fusion-Launcher.git
cd PvZ-Fusion-Launcher

# Install dependencies
pip install -r requirements.txt

# Run launcher
python PVZ_Launcher.py
