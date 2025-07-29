import subprocess
import sys
import os

try:
    print("🔧 Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("🚀 Starting the bot...")
    subprocess.check_call([sys.executable, "nomadly_clean/nomadly3_clean_bot.py"])

except subprocess.CalledProcessError as e:
    print(f"❌ Command failed with exit code {e.returncode}")
