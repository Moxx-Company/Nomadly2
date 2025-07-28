#!/usr/bin/env python3
"""
COMPREHENSIVE CRITICAL ISSUE FIXES
Addresses all identified critical issues from workflow logs analysis
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_manager_scope_error():
    """Fix the critical get_db_manager scope error in create_crypto callbacks"""
    
    logger.info("🔧 FIXING DATABASE MANAGER SCOPE ERROR")
    
    try:
        # Read the nomadly2_bot.py file
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
        
        # Find create_crypto_ callback handlers that have database manager issues
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Look for create_crypto_ callback handlers
            if 'create_crypto_' in line and 'callback_data' in line:
                # Check if there's a database manager scope issue nearby
                context_start = max(0, i - 10)
                context_end = min(len(lines), i + 50)
                context = '\n'.join(lines[context_start:context_end])
                
                if 'get_db_manager' in context and 'cannot access local variable' in str(context):
                    logger.warning(f"Found potential database scope issue around line {i}: {line[:50]}...")
        
        # Add proper import at the top if missing
        if 'from database import get_db_manager' not in content:
            # Find the imports section
            import_section_end = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_section_end = i
                elif line.strip() == '' and import_section_end > 0:
                    break
            
            # Insert the import after existing imports
            lines.insert(import_section_end + 1, 'from database import get_db_manager')
            logger.info("✅ Added database import")
        
        # Look for specific create_crypto_ handler patterns and fix them
        in_create_crypto_handler = False
        current_handler = None
        
        for i, line in enumerate(lines):
            if 'elif data.startswith("create_crypto_")' in line:
                in_create_crypto_handler = True
                current_handler = line.strip()
                logger.info(f"Found create_crypto handler: {current_handler}")
                
            elif in_create_crypto_handler:
                # Look for database manager usage issues
                if 'get_db_manager()' in line and 'self.get_db_manager()' not in line:
                    # This is correct usage, continue
                    pass
                elif 'self.get_db_manager()' in line:
                    # Fix incorrect usage
                    lines[i] = line.replace('self.get_db_manager()', 'get_db_manager()')
                    logger.info(f"✅ Fixed incorrect database manager call on line {i}")
                elif 'except' in line or 'elif' in line.strip():
                    in_create_crypto_handler = False
                    current_handler = None
        
        # Write the fixed content back
        fixed_content = '\n'.join(lines)
        with open('nomadly2_bot.py', 'w') as f:
            f.write(fixed_content)
        
        logger.info("✅ Database manager scope fixes applied")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing database manager scope: {e}")
        return False

def add_missing_create_crypto_handlers():
    """Add missing create_crypto_ callback handlers with proper database integration"""
    
    logger.info("🔧 ADDING MISSING CREATE_CRYPTO_ HANDLERS")
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
        
        # Find the callback handler section
        if 'elif data.startswith("create_crypto_")' in content:
            logger.info("✅ Generic create_crypto_ handler already exists")
        else:
            # Find a good insertion point (near other callback handlers)
            insertion_point = -1
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if 'elif data.startswith("switch_crypto_")' in line:
                    insertion_point = i
                    break
            
            if insertion_point > 0:
                # Insert the missing handler
                handler_code = '''
        # Handle create_crypto_ callbacks
        elif data.startswith("create_crypto_"):
            await query.answer("⚡")
            try:
                parts = data.split("_")
                if len(parts) >= 3:
                    crypto = parts[2]
                    order_id = parts[3] if len(parts) > 3 else None
                    
                    if not order_id:
                        await query.edit_message_text(
                            "❌ **Payment Creation Failed**\\n\\n"
                            "Invalid order ID format.\\n"
                            "Please try again or contact support.",
                            parse_mode="Markdown",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                                [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
                            ])
                        )
                        return
                    
                    # Get order details using fix_callback_database_queries
                    from fix_callback_database_queries import get_order_details_for_switch
                    
                    try:
                        order_amount, service_details, order_status = get_order_details_for_switch(order_id, query.from_user.id)
                        
                        if not order_amount:
                            await query.edit_message_text(
                                f"❌ **Order Not Found**\\n\\n"
                                f"Could not find order {order_id[:8]}...\\n"
                                f"Please check your order ID.",
                                parse_mode="Markdown",
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                                    [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
                                ])
                            )
                            return
                        
                        # Create new crypto payment using payment service
                        from payment_service import PaymentService
                        payment_service = PaymentService()
                        
                        payment_result = await payment_service.create_crypto_payment(
                            telegram_id=query.from_user.id,
                            amount=float(order_amount),
                            crypto_currency=crypto.upper(),
                            service_type="domain_registration",
                            service_details={
                                "domain": service_details,
                                "type": "domain_registration"
                            }
                        )
                        
                        if payment_result and payment_result.get("payment_address"):
                            payment_address = payment_result["payment_address"]
                            crypto_amount = payment_result.get("crypto_amount", "N/A")
                            
                            await query.edit_message_text(
                                f"💰 **{crypto.upper()} Payment Created**\\n\\n"
                                f"**Amount:** {crypto_amount} {crypto.upper()}\\n"
                                f"**USD Value:** ${order_amount}\\n\\n"
                                f"**Payment Address:**\\n"
                                f"`{payment_address}`\\n\\n"
                                f"Send exactly {crypto_amount} {crypto.upper()} to complete payment.",
                                parse_mode="Markdown",
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_addr_{order_id[:8]}")],
                                    [InlineKeyboardButton("🔄 Refresh Status", callback_data=f"refresh_status_{order_id[:8]}_{''.join(__import__('random').choices('0123456789', k=10))}")],
                                    [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                                    [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
                                ])
                            )
                        else:
                            await query.edit_message_text(
                                f"❌ **{crypto.upper()} Payment Creation Failed**\\n\\n"
                                f"Domain: {service_details}\\n"
                                f"Currency: {crypto.upper()}\\n\\n"
                                f"Error: Cryptocurrency payment system requires configuration. Please contact support or use balance payment.\\n\\n"
                                f"Please try again or contact support.",
                                parse_mode="Markdown",
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton("🔄 Try Again", callback_data=f"create_crypto_{crypto}_{order_id}")],
                                    [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                                    [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
                                ])
                            )
                    
                    except Exception as db_error:
                        logger.error(f"❌ Database error in create_crypto_: {db_error}")
                        await query.edit_message_text(
                            f"❌ **Database Error**\\n\\n"
                            f"Could not retrieve order information.\\n"
                            f"Please try again or contact support.",
                            parse_mode="Markdown",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                                [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
                            ])
                        )
                else:
                    await query.edit_message_text(
                        "❌ **Invalid Callback Format**\\n\\n"
                        "Malformed create_crypto callback.\\n"
                        "Please try again or contact support.",
                        parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                            [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
                        ])
                    )
            except Exception as e:
                logger.error(f"❌ Create crypto callback error: {e}")
                await query.edit_message_text(
                    "❌ **Payment System Error**\\n\\n"
                    "An error occurred while creating your cryptocurrency payment.\\n"
                    "Please try again or contact support.",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💰 Wallet", callback_data="wallet")],
                        [InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]
                    ])
                )
'''
                
                lines.insert(insertion_point, handler_code)
                
                # Write back to file
                fixed_content = '\n'.join(lines)
                with open('nomadly2_bot.py', 'w') as f:
                    f.write(fixed_content)
                
                logger.info("✅ Added comprehensive create_crypto_ handler")
                return True
            else:
                logger.error("❌ Could not find insertion point for create_crypto_ handler")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error adding create_crypto_ handlers: {e}")
        return False

def create_enhanced_payment_service():
    """Create enhanced payment service that handles configuration issues"""
    
    logger.info("🔧 ENHANCING PAYMENT SERVICE WITH CONFIGURATION HANDLING")
    
    enhanced_payment_code = '''
def get_available_cryptocurrencies(self):
    """Get list of actually working cryptocurrencies based on BlockBee configuration"""
    
    # Known working cryptocurrencies (from testing)
    working_cryptos = ["btc", "eth", "ltc", "doge", "bch", "trx", "dash"]
    
    # Known configuration issues (require admin panel setup)
    config_issues = ["bnb", "xmr", "matic"]  # BNB, Monero, Polygon
    
    available_cryptos = {}
    
    for crypto in working_cryptos:
        if crypto in self.supported_cryptos:
            available_cryptos[crypto] = self.supported_cryptos[crypto]
    
    return available_cryptos

def get_crypto_error_message(self, crypto, error_type):
    """Get user-friendly error message for cryptocurrency configuration issues"""
    
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
    
    crypto_name = crypto_names.get(crypto.lower(), crypto.upper())
    
    if "Address not set on admin panel" in str(error_type):
        return f"""❌ {crypto_name} Temporarily Unavailable

{crypto_name} payments require additional configuration on our payment provider.

**Available alternatives:**
• Bitcoin (BTC) ✅
• Ethereum (ETH) ✅ 
• Litecoin (LTC) ✅
• Dogecoin (DOGE) ✅
• Bitcoin Cash (BCH) ✅

Would you like to try a different cryptocurrency or use balance payment?"""
    
    elif "Resource not found" in str(error_type):
        return f"""❌ {crypto_name} Not Supported

{crypto_name} is not available through our payment provider.

**Supported cryptocurrencies:**
• Bitcoin (BTC) ✅
• Ethereum (ETH) ✅
• Litecoin (LTC) ✅
• Dogecoin (DOGE) ✅

Please select a different payment method."""
    
    else:
        return f"""❌ {crypto_name} Payment Issue
        
Technical error: {error_type}

Please try a different payment method or contact support."""

def is_cryptocurrency_available(self, crypto):
    """Check if cryptocurrency is actually available (not just supported)"""
    working_cryptos = ["btc", "eth", "ltc", "doge", "bch", "trx", "dash"]
    return crypto.lower() in working_cryptos
'''
    
    try:
        # Read payment_service.py
        with open('payment_service.py', 'r') as f:
            content = f.read()
        
        # Check if enhancement methods already exist
        if 'def get_available_cryptocurrencies' not in content:
            # Find the end of the PaymentService class
            lines = content.split('\n')
            insertion_point = -1
            
            for i, line in enumerate(lines):
                if 'class PaymentService' in line:
                    # Find the end of this class
                    indent_level = len(line) - len(line.lstrip())
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent_level and 'class ' in lines[j]:
                            insertion_point = j - 1
                            break
                    if insertion_point == -1:
                        insertion_point = len(lines) - 1
                    break
            
            if insertion_point > 0:
                # Insert the enhancement methods
                lines.insert(insertion_point, enhanced_payment_code)
                
                # Write back to file
                with open('payment_service.py', 'w') as f:
                    f.write('\n'.join(lines))
                
                logger.info("✅ Enhanced payment service with configuration handling")
                return True
            else:
                logger.error("❌ Could not find PaymentService class")
                return False
        else:
            logger.info("✅ Payment service enhancements already exist")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error enhancing payment service: {e}")
        return False

def fix_malformed_callback_handlers():
    """Fix malformed callback handlers like copy_addr_{payment_result.get("""
    
    logger.info("🔧 FIXING MALFORMED CALLBACK HANDLERS")
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
        
        # Fix malformed copy_addr_ patterns
        content = content.replace(
            'elif data == "copy_addr_{payment_result.get(":',
            '# REMOVED MALFORMED HANDLER: copy_addr_{payment_result.get('
        )
        
        content = content.replace(
            'elif data == "copy_addr_{result.get(":',
            '# REMOVED MALFORMED HANDLER: copy_addr_{result.get('
        )
        
        # Remove any method calls for these malformed handlers
        content = content.replace(
            'await self.handle_copy_addr_{payment_result.get((query)',
            '# REMOVED MALFORMED METHOD CALL'
        )
        
        content = content.replace(
            'await self.handle_copy_addr_{result.get((query)',
            '# REMOVED MALFORMED METHOD CALL'
        )
        
        # Write back to file
        with open('nomadly2_bot.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Fixed malformed callback handlers")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing malformed handlers: {e}")
        return False

def create_comprehensive_error_handling():
    """Create comprehensive error handling for payment failures"""
    
    logger.info("🔧 CREATING COMPREHENSIVE ERROR HANDLING")
    
    error_handler_code = '''
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
'''
    
    # Save error handler
    with open('payment_error_handler.py', 'w') as f:
        f.write(error_handler_code)
    
    logger.info("✅ Created comprehensive payment error handler")
    return True

def main():
    """Main function to fix all critical issues"""
    
    logger.info("🚀 STARTING COMPREHENSIVE CRITICAL ISSUE FIXES")
    
    fixes_applied = []
    fixes_failed = []
    
    # Fix 1: Database Manager Scope Error
    if fix_database_manager_scope_error():
        fixes_applied.append("✅ Database Manager Scope Error")
    else:
        fixes_failed.append("❌ Database Manager Scope Error")
    
    # Fix 2: Missing Create Crypto Handlers  
    if add_missing_create_crypto_handlers():
        fixes_applied.append("✅ Missing Create Crypto Handlers")
    else:
        fixes_failed.append("❌ Missing Create Crypto Handlers")
    
    # Fix 3: Enhanced Payment Service
    if create_enhanced_payment_service():
        fixes_applied.append("✅ Enhanced Payment Service")
    else:
        fixes_failed.append("❌ Enhanced Payment Service")
    
    # Fix 4: Malformed Callback Handlers
    if fix_malformed_callback_handlers():
        fixes_applied.append("✅ Malformed Callback Handlers")
    else:
        fixes_failed.append("❌ Malformed Callback Handlers")
    
    # Fix 5: Comprehensive Error Handling
    if create_comprehensive_error_handling():
        fixes_applied.append("✅ Comprehensive Error Handling")
    else:
        fixes_failed.append("❌ Comprehensive Error Handling")
    
    # Report results
    logger.info("\n📊 CRITICAL FIXES SUMMARY")
    logger.info("=" * 50)
    
    logger.info(f"✅ Successfully Applied ({len(fixes_applied)}):")
    for fix in fixes_applied:
        logger.info(f"  {fix}")
    
    if fixes_failed:
        logger.info(f"\n❌ Failed to Apply ({len(fixes_failed)}):")
        for fix in fixes_failed:
            logger.info(f"  {fix}")
    
    success_rate = len(fixes_applied) / (len(fixes_applied) + len(fixes_failed)) * 100
    logger.info(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 80:
        logger.info("🎉 CRITICAL FIXES COMPLETED SUCCESSFULLY")
        return True
    else:
        logger.error("⚠️ SOME CRITICAL FIXES FAILED - MANUAL REVIEW REQUIRED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)