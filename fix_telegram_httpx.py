#!/usr/bin/env python3
"""
Telegram HTTPx Compatibility Fix
Patches HTTPXRequest to remove proxy parameter that causes compatibility issues
"""

import sys
import httpx
from telegram.request._httpxrequest import HTTPXRequest

# Store original _build_client method
_original_build_client = HTTPXRequest._build_client

def patched_build_client(self):
    """Patched version that removes proxy parameter from client_kwargs"""
    # Get original client kwargs
    client_kwargs = self._client_kwargs.copy()
    
    # Remove proxy parameter if it exists (this is what causes the error)
    if 'proxy' in client_kwargs:
        print(f"Removing proxy parameter: {client_kwargs['proxy']}")
        del client_kwargs['proxy']
    
    # Return AsyncClient without proxy parameter
    return httpx.AsyncClient(**client_kwargs)

# Apply the patch
HTTPXRequest._build_client = patched_build_client

print("✅ HTTPXRequest patched successfully - proxy parameter removed")

# Now test if we can create a telegram application
if __name__ == "__main__":
    try:
        from telegram.ext import Application
        
        # Test bot creation
        BOT_TOKEN = "8058274028:AAFSNDsJ5upG_gLEkWOl9M5apgTypkNDecQ"
        app = Application.builder().token(BOT_TOKEN).build()
        print("✅ Telegram Application created successfully with patch!")
        
        # Import our bot implementation
        from nomadly3_complete_bot import Nomadly3CompleteBot
        
        # Create and run bot
        bot = Nomadly3CompleteBot()
        bot.run()
        
    except Exception as e:
        print(f"❌ Patch test failed: {e}")
        import traceback
        traceback.print_exc()