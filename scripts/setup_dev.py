import subprocess
import sys
import os
from pathlib import Path

def setup_dev_environment():
    """Set up development environment"""
    print("🔧 Setting up development environment...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("\n📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Determine the pip path based on OS
    pip_path = "venv/bin/pip" if os.name != 'nt' else r"venv\Scripts\pip"
    
    # Install requirements
    print("\n📥 Installing dependencies...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("\n📝 Creating .env file template...")
        with open(".env", "w") as f:
            f.write("""# Bot Configuration
TELEGRAM_BOT_TOKEN=
WEBHOOK_SECRET=

# Notion Configuration
NOTION_TOKEN=
OFFERS_DATABASE_ID=
ADVERTISERS_DATABASE_ID=

# Development Settings
DEBUG=True
""")
        print("✨ Created .env file - please fill in your credentials")
    
    print("\n✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Fill in your credentials in .env")
    print("2. Run 'python scripts/test_webhook.py' to start local development")

if __name__ == "__main__":
    setup_dev_environment() 