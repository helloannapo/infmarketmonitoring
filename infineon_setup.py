#!/usr/bin/env python3
"""
Infineon Competitive Intelligence Setup
Comprehensive setup script for the Infineon intelligence system
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🚀 INFINEON COMPETITIVE INTELLIGENCE SETUP")
    print("=" * 60)
    print("Setting up Infineon's Green Power competitive intelligence system")
    print("=" * 60)

def check_python_version():
    """Check Python version compatibility"""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def create_directories():
    """Create organized directory structure"""
    print("📁 Creating directory structure...")
    directories = [
        'data',
        'analysis', 
        'exports',
        'logs',
        'intelligence'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Created: {directory}/")
    
    print("✅ Directory structure created")

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    requirements = [
        'requests==2.31.0',
        'beautifulsoup4==4.12.2', 
        'pandas==2.1.4',
        'openai==0.28.1',
        'python-dotenv==1.0.0',
        'lxml==4.9.3',
        'openpyxl==3.1.2'
    ]
    
    for package in requirements:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All dependencies installed")
    return True

def create_env_template():
    """Create .env template file"""
    print("🔧 Creating environment configuration...")
    
    env_content = """# Infineon Competitive Intelligence Configuration
# Copy this file to .env and fill in your API keys

# OpenAI API Key (Required for AI analysis)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Scraping delay between requests (seconds)
SCRAPING_DELAY=2

# Optional: OpenAI model to use
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Custom title prefix for exports
SHEETS_TITLE_PREFIX=Infineon Intelligence
"""
    
    with open('config_template.txt', 'w') as f:
        f.write(env_content)
    
    print("✅ Configuration template created: config_template.txt")
    print("   📝 Copy to .env and add your OpenAI API key")

def test_imports():
    """Test that all required packages can be imported"""
    print("🧪 Testing imports...")
    
    packages = [
        'requests',
        'bs4',
        'pandas', 
        'openai',
        'dotenv',
        'openpyxl'
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError as e:
            print(f"   ❌ {package}: {e}")
            return False
    
    print("✅ All imports successful")
    return True

def create_quick_start_script():
    """Create a quick start script"""
    print("🚀 Creating quick start script...")
    
    script_content = """#!/bin/bash
# Infineon Intelligence Quick Start
echo "🚀 Starting Infineon Competitive Intelligence..."
python infineon_intelligence_scraper.py
echo "✅ Analysis complete! Check exports/ directory for results."
"""
    
    with open('run_intelligence.sh', 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod('run_intelligence.sh', 0o755)
    
    print("✅ Quick start script created: run_intelligence.sh")

def show_next_steps():
    """Show next steps for the user"""
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)
    print("1. 📝 Configure API Key:")
    print("   cp config_template.txt .env")
    print("   # Edit .env and add your OpenAI API key")
    print()
    print("2. 🧪 Test the system:")
    print("   python infineon_test.py")
    print()
    print("3. 🚀 Run intelligence analysis:")
    print("   python infineon_intelligence_scraper.py")
    print("   # or use: ./run_intelligence.sh")
    print()
    print("4. 📊 Check results:")
    print("   - Excel files: exports/")
    print("   - Analysis reports: analysis/")
    print("   - Raw data: data/")
    print("   - Logs: logs/")
    print()
    print("5. ⚙️  Configure sources:")
    print("   python intelligence_sources_config.py")
    print("=" * 60)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed during import testing")
        sys.exit(1)
    
    # Create configuration
    create_env_template()
    
    # Create quick start script
    create_quick_start_script()
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Infineon Competitive Intelligence Setup Complete!")
    print("   Ready for Green Power market analysis!")

if __name__ == "__main__":
    main()

