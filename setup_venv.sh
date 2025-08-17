#!/bin/bash

# Infineon Intelligence System - Virtual Environment Setup Script
# This script creates and configures a Python virtual environment for the project

set -e  # Exit on any error

echo "🚀 Setting up Infineon Intelligence System Virtual Environment"
echo "================================================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment 'venv' already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf venv
    else
        echo "✅ Using existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created successfully"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    # Suppress SSL warnings during installation
    pip install -r requirements.txt --quiet
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f "config_template.txt" ]; then
        echo "📝 Creating .env file from template..."
        cp config_template.txt .env
        echo "✅ .env file created from config_template.txt"
        echo "⚠️  Please edit .env file and add your OpenAI API key"
    else
        echo "⚠️  No config_template.txt found, creating basic .env file..."
        echo "# Infineon Intelligence System Configuration" > .env
        echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
        echo "✅ Basic .env file created"
        echo "⚠️  Please edit .env file and add your OpenAI API key"
    fi
else
    echo "✅ .env file already exists"
fi

# Create missing directories if they don't exist
echo "📁 Creating project directories..."
mkdir -p data analysis exports logs intelligence
echo "✅ Project directories created/verified"

# Test the setup
echo "🧪 Testing the setup..."
python3 -c "
import sys
import warnings

# Suppress SSL warnings
warnings.filterwarnings('ignore', category=Warning, module='urllib3')

print(f'✅ Python path: {sys.executable}')
try:
    import requests
    import bs4
    import pandas
    import openai
    import dotenv
    import openpyxl
    print('✅ All required packages imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    print('💡 Try running: pip install -r requirements.txt')
    sys.exit(1)
"

echo ""
echo "🎉 Virtual environment setup completed successfully!"
echo "================================================================"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run tests: python3 infineon_test.py"
echo "4. Start intelligence gathering: python3 infineon_intelligence_scraper.py"
echo ""
echo "💡 To activate the virtual environment in the future:"
echo "   source venv/bin/activate"
echo ""
echo "💡 To deactivate the virtual environment:"
echo "   deactivate"
echo ""
echo "⚠️  Note: If you see SSL warnings, they are harmless and won't affect functionality."
echo "   The system uses LibreSSL which is compatible with all required operations."
echo ""
