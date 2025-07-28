#!/usr/bin/env python3
"""Check if FastAPI webhook server is running"""

import requests
import sys

try:
    # Check if webhook server is running
    response = requests.get("http://localhost:5000/health", timeout=5)
    if response.status_code == 200:
        print("✅ Webhook server is running on port 5000")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Webhook server returned status {response.status_code}")
except requests.ConnectionError:
    print("❌ Webhook server is NOT running on port 5000")
    print("This is why BlockBee webhooks aren't being received!")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error checking webhook server: {e}")
    sys.exit(1)