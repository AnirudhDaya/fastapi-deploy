#!/bin/bash

set -e

echo "==== FastAPI Deploy CLI Installer ===="
echo

# Check for Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Found Python $PYTHON_VERSION"

# Detect package manager preference
if command -v uv &> /dev/null; then
    INSTALLER="uv"
    INSTALL_CMD="uv pip install"
    echo "✅ Using uv package manager"
elif command -v pip3 &> /dev/null; then
    INSTALLER="pip"
    INSTALL_CMD="pip3 install"
    echo "✅ Using pip package manager"
else
    echo "❌ Error: Neither pip nor uv is installed."
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

echo "📦 Installing FastAPI Deploy CLI..."
cd "$PROJECT_DIR"

# Create virtual environment if requested
if [[ "$1" == "--venv" ]]; then
    echo "🔨 Creating virtual environment..."
    if [ "$INSTALLER" == "uv" ]; then
        uv venv
        source .venv/bin/activate
    else
        python3 -m venv .venv
        source .venv/bin/activate
    fi
    echo "✅ Virtual environment created and activated"
fi

# Install from local directory in development mode
$INSTALL_CMD -e .

# Check if installation was successful
if command -v fastapi-deploy &> /dev/null; then
    echo "✅ FastAPI Deploy CLI installed successfully!"
    echo "ℹ️ Run 'fastapi-deploy init' to initialize a new deployment setup."
else
    echo "❌ Error: Installation failed."
    exit 1
fi