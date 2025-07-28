
def get_cryptocurrency_error_message(crypto, error_type):
    """Get user-friendly error message for cryptocurrency issues"""
    
    crypto_names = {
        "btc": "Bitcoin",
        "eth": "Ethereum", 
        "ltc": "Litecoin",
        "usdt": "Tether",
        "doge": "Dogecoin",
        "trx": "TRON",
        "bnb": "Binance Coin",
        "bch": "Bitcoin Cash",
        "dash": "Dash",
        "xmr": "Monero",
        "matic": "Polygon"
    }
    
    crypto_name = crypto_names.get(crypto, crypto.upper())
    
    if error_type == "Address not set on admin panel and not sent":
        return f"""❌ {crypto_name} Temporarily Unavailable
        
{crypto_name} payments require additional configuration on our payment provider.

**Available alternatives:**
• Bitcoin Cash (BCH) - ✅ Working
• Ethereum (ETH) - Check status  
• Bitcoin (BTC) - Check status

Would you like to try a different cryptocurrency or use balance payment?"""
    
    elif error_type == "Unknown error" or error_type == "{}":
        return f"""❌ {crypto_name} Service Unavailable

Our payment provider is experiencing issues with {crypto_name}.

**Please try:**
1. Different cryptocurrency
2. Balance payment 
3. Contact support if issue persists

We apologize for the inconvenience."""
    
    else:
        return f"""❌ {crypto_name} Payment Issue
        
Technical error: {error_type}

Please try a different payment method or contact support."""
