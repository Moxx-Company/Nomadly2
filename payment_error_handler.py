
def handle_payment_creation_error(query, crypto, error_details, order_id=None):
    """Handle payment creation errors with user-friendly messages"""
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    error_str = str(error_details).lower()
    
    if "address not set on admin panel" in error_str:
        message = f"""❌ **{crypto.upper()} Temporarily Unavailable**

{crypto.upper()} payments require additional configuration.

**Available alternatives:**
• Bitcoin (BTC) ✅
• Ethereum (ETH) ✅  
• Litecoin (LTC) ✅
• Dogecoin (DOGE) ✅
• Bitcoin Cash (BCH) ✅

Please select a different cryptocurrency."""
        
        keyboard = [
            [InlineKeyboardButton("🔷 Bitcoin (BTC)", callback_data=f"create_crypto_btc_{order_id}" if order_id else "crypto_btc")],
            [InlineKeyboardButton("🔷 Ethereum (ETH)", callback_data=f"create_crypto_eth_{order_id}" if order_id else "crypto_eth")],
            [InlineKeyboardButton("🔷 Litecoin (LTC)", callback_data=f"create_crypto_ltc_{order_id}" if order_id else "crypto_ltc")],
            [InlineKeyboardButton("🔷 Dogecoin (DOGE)", callback_data=f"create_crypto_doge_{order_id}" if order_id else "crypto_doge")],
            [InlineKeyboardButton("💰 Use Wallet Balance", callback_data="wallet")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        
    elif "resource not found" in error_str:
        message = f"""❌ **{crypto.upper()} Not Supported**

{crypto.upper()} is not available through our payment system.

**Supported cryptocurrencies:**
• Bitcoin (BTC) ✅
• Ethereum (ETH) ✅
• Litecoin (LTC) ✅  
• Dogecoin (DOGE) ✅

Please select a different payment method."""
        
        keyboard = [
            [InlineKeyboardButton("🔷 Bitcoin (BTC)", callback_data=f"create_crypto_btc_{order_id}" if order_id else "crypto_btc")],
            [InlineKeyboardButton("🔷 Ethereum (ETH)", callback_data=f"create_crypto_eth_{order_id}" if order_id else "crypto_eth")],
            [InlineKeyboardButton("💰 Use Wallet Balance", callback_data="wallet")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        
    else:
        message = f"""❌ **{crypto.upper()} Payment Creation Failed**

An error occurred while creating your {crypto.upper()} payment address.

**Error:** {str(error_details)[:100]}...

Please try again or use a different payment method."""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Try Again", callback_data=f"create_crypto_{crypto.lower()}_{order_id}" if order_id else f"crypto_{crypto.lower()}")],
            [InlineKeyboardButton("💰 Use Wallet Balance", callback_data="wallet")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
    
    return message, InlineKeyboardMarkup(keyboard)
