import subprocess

try:
    print("🔧 Installing dependencies...")
    subprocess.check_call(["python", "install", "-r", "requirements.txt"])

    print("🚀 Starting the bot...")
    subprocess.check_call(["python", "nomadly_clean/nomadly3_clean_bot.py"])

except subprocess.CalledProcessError as e:
    print(f"❌ Command failed with exit code {e.returncode}")
