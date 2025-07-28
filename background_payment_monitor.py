#!/usr/bin/env python3
"""
Background payment monitoring service for real-time blockchain transaction detection
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import httpx

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PaymentMonitor:
    """Monitors blockchain payments in real-time"""
    
    def __init__(self):
        self.monitoring_interval = 30  # Check every 30 seconds
        self.active_payments: Dict[str, Dict] = {}  # address -> payment info
        self.bot_instance = None
        self.queue_file = 'payment_monitor_queue.json'
        
    async def start_monitoring(self):
        """Start the background payment monitoring loop"""
        logger.info("🚀 Starting real-time payment monitoring service")
        
        while True:
            try:
                # Load payments from queue file
                self._load_from_queue()
                
                logger.info(f"📊 Payment monitor cycle - Active payments: {len(self.active_payments)}")
                await self.check_pending_payments()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in payment monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def _load_from_queue(self):
        """Load payments from the shared queue file"""
        try:
            import json
            with open('payment_monitor_queue.json', 'r') as f:
                queue_data = json.load(f)
                
            # Add any new payments to our active list
            for address, info in queue_data.items():
                if address not in self.active_payments:
                    self.active_payments[address] = info
                    logger.info(f"📥 Loaded payment {address[:20]}... from queue")
                    
        except Exception as e:
            logger.debug(f"Could not load queue file: {e}")
    
    def _save_to_queue(self):
        """Save active payments to queue file"""
        try:
            import json
            with open('payment_monitor_queue.json', 'w') as f:
                json.dump(self.active_payments, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save queue file: {e}")
    
    async def check_pending_payments(self):
        """Check all pending payments for confirmations"""
        if not self.active_payments:
            logger.debug("No active payments to check")
            return
            
        logger.info(f"🔍 Checking {len(self.active_payments)} pending payments")
        
        # Import here to avoid circular imports
        from payment_service import get_payment_service
        from database import get_db_manager
        
        payment_service = get_payment_service()
        db = get_db_manager()
        
        for address, payment_info in list(self.active_payments.items()):
            try:
                # Check if payment has expired (24 hours)
                created_at = datetime.fromisoformat(payment_info['created_at'])
                if datetime.utcnow() - created_at > timedelta(hours=24):
                    logger.info(f"Payment expired for {address}")
                    del self.active_payments[address]
                    continue
                
                # Check blockchain for payment
                crypto_type = payment_info['crypto_type']
                
                # Check database for confirmed payments using direct SQL query
                try:
                    import psycopg2
                    import os
                    
                    # Direct database connection for payment verification
                    db_url = os.getenv('DATABASE_URL')
                    if db_url:
                        import psycopg2
                        conn = psycopg2.connect(db_url)
                        cursor = conn.cursor()
                        
                        # Check if order is marked as confirmed but not yet processed
                        cursor.execute(
                            "SELECT status, domain_name FROM orders WHERE crypto_address = %s AND status IN ('confirmed', 'pending') AND status != 'processed'",
                            (address,)
                        )
                        result = cursor.fetchone()
                        
                        if result:
                            logger.info(f"💰 Found confirmed payment in database for {address}!")
                            domain_name = result[1]
                            payment_info['domain'] = domain_name  # Update domain name
                            
                            # Process the payment
                            await self.process_payment_confirmation(
                                address, payment_info, {
                                    'value_received': payment_info.get('expected_amount', 9.87),
                                    'value_coin': payment_info.get('expected_amount', 9.87),
                                    'txid': 'database_confirmed',
                                    'confirmations': 6
                                }
                            )
                            
                            # Mark payment as processed in database to prevent future duplicate processing
                            cursor.execute(
                                "UPDATE orders SET status = 'processed' WHERE crypto_address = %s AND status != 'processed'",
                                (address,)
                            )
                            conn.commit()
                            
                            # CRITICAL FIX: Remove processed payment from active monitoring
                            logger.info(f"✅ Payment processed successfully - removing {address} from monitoring queue")
                            del self.active_payments[address]
                            
                            cursor.close()
                            conn.close()
                            continue
                            
                        cursor.close()
                        conn.close()
                        
                    # Also check for payment confirmations file (backup method)
                    import os
                    if os.path.exists('payment_confirmations.json'):
                        with open('payment_confirmations.json', 'r') as f:
                            confirmations = json.load(f)
                        
                        if address in confirmations:
                            payment_data = confirmations[address]
                            logger.info(f"💰 Found payment confirmation for {address}!")
                            
                            # Process the payment
                            await self.process_payment_confirmation(
                                address, payment_info, {
                                    'value_received': payment_data.get('amount_eth', 0),
                                    'value_coin': payment_data.get('amount_eth', 0),
                                    'txid': payment_data.get('txid'),
                                    'confirmations': payment_data.get('confirmations', 6)
                                }
                            )
                            
                            # Remove from confirmations file
                            del confirmations[address]
                            with open('payment_confirmations.json', 'w') as f:
                                json.dump(confirmations, f, indent=2)
                            continue
                except Exception as e:
                    logger.error(f"Error checking payment confirmations: {e}")
                
                # Use BlockBee API directly (webhook-based, won't work for polling)
                try:
                    from apis.blockbee import BlockBeeAPI
                    
                    api_key = os.getenv('BLOCKBEE_API_KEY')
                    if api_key:
                        blockbee = BlockBeeAPI(api_key)
                        # Note: BlockBee uses webhooks, not polling
                        logger.debug(f"BlockBee uses webhooks - waiting for callback for {address[:20]}...")
                    else:
                        logger.warning("BLOCKBEE_API_KEY not found")
                except Exception as e:
                    logger.error(f"Error with BlockBee API: {e}")
                        
            except Exception as e:
                logger.error(f"Error checking payment {address}: {e}")
    
    async def process_payment_confirmation(self, address: str, payment_info: Dict, payment_data: Dict):
        """Process a confirmed payment"""
        try:
            logger.info(f"💰 Payment confirmed for {address}!")
            
            # Since Payment Monitor runs as separate workflow, we need to trigger domain registration differently
            user_id = payment_info['user_id']
            domain = payment_info['domain']
            
            logger.info(f"🔄 Processing domain registration for {domain} (user {user_id})")
            
            # Check if the domain was already registered
            import psycopg2
            try:
                conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM registered_domains WHERE domain_name = %s", (domain,))
                existing_domain = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if existing_domain:
                    logger.info(f"⚠️ Domain {domain} already registered - sending notification")
                    # Send notification that payment was received and domain is already active
                    try:
                        # Get order details from database for notification
                        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT telegram_id, domain_name, tld, total_price_usd, email_provided
                            FROM orders 
                            WHERE crypto_address = %s AND status IN ('confirmed', 'processed', 'pending')
                            LIMIT 1
                        """, (address,))
                        
                        order_row = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        
                        if order_row:
                            telegram_id, domain_name, tld, total_price, email_provided = order_row
                            full_domain = f"{domain_name}.{tld}" if not domain_name.endswith(tld) else domain_name
                            
                            # Send notification using Master Notification Service
                            from services.master_notification_service import get_master_notification_service
                            
                            notification_service = get_master_notification_service()
                            payment_data = {
                                'domain_name': full_domain,
                                'amount_usd': total_price
                            }
                            
                            await notification_service.send_payment_confirmation(telegram_id, payment_data)
                            
                            # Send email if provided and not privacy email
                            if email_provided and email_provided != 'privacy@offshore.contact':
                                try:
                                    from services.email_service import EmailService
                                    email_service = EmailService()
                                    
                                    order_details = {
                                        'order_id': f'ORD-{full_domain.upper()[:5]}',
                                        'amount': total_price,
                                        'cryptocurrency': 'ETH',
                                        'domain': full_domain
                                    }
                                    
                                    email_success = email_service.send_payment_confirmation(
                                        user_email=email_provided,
                                        order_details=order_details,
                                        language='en'
                                    )
                                    
                                    if email_success:
                                        logger.info(f"📧 Payment confirmation email sent to {email_provided}")
                                    else:
                                        logger.error(f"❌ Failed to send email to {email_provided}")
                                        
                                except Exception as email_error:
                                    logger.error(f"❌ Email service error: {email_error}")
                                    
                            logger.info(f"📱 Payment confirmation sent for already-registered domain {full_domain}")
                            
                            # Remove from monitoring after notification sent
                            if address in self.active_payments:
                                del self.active_payments[address]
                                self._save_to_queue()  # Update the queue file
                                logger.info(f"🗑️ Removed payment monitoring for {address[:20]}... after successful notification")
                                
                    except Exception as notification_error:
                        logger.error(f"❌ Notification error: {notification_error}")
                    
                    return
                    
            except Exception as e:
                logger.error(f"Error checking existing domain: {e}")
            
            # Since we can't directly access bot instance, trigger domain registration via service
            try:
                # Get domain registration data using direct SQL query
                import psycopg2
                from sqlalchemy import text
                
                logger.info(f"🚀 Retrieving order details for {domain}")
                
                conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT telegram_id, domain_name, tld, nameserver_choice, 
                           email_provided, total_price_usd, status
                    FROM orders 
                    WHERE crypto_address = %s AND status IN ('paid', 'completed', 'pending')
                    LIMIT 1
                """, (address,))
                
                order_row = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if order_row:
                    telegram_id, domain_name, tld, nameserver_choice, email_provided, total_price, status = order_row
                    full_domain = f"{domain_name}.{tld}" if not domain_name.endswith(tld) else domain_name
                    logger.info(f"📋 Found order: {full_domain} for user {telegram_id}")
                    
                    # Check if domain already exists
                    import psycopg2
                    try:
                        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM domains WHERE domain_name = %s", (full_domain,))
                        existing_domain = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        
                        if existing_domain:
                            logger.info(f"⚠️ Domain {full_domain} already registered - sending notification")
                            # Send notification that payment was received and domain is already active
                            try:
                                # Send Telegram notification
                                from telegram import Bot
                                
                                bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
                                await bot.send_message(
                                    chat_id=telegram_id,
                                    text=(
                                        f"💰 **Payment Confirmed!**\n\n"
                                        f"✅ **Domain:** `{full_domain}`\n"
                                        f"💰 **Amount:** ${total_price} USD\n"
                                        f"🎉 **Status:** Active & Ready!\n\n"
                                        f"Your domain was already registered and is working perfectly.\n"
                                        f"Use /mydomains to manage your domain."
                                    ),
                                    parse_mode='Markdown'
                                )
                                
                                # Send email if provided and not privacy email
                                if email_provided and email_provided != 'privacy@offshore.contact':
                                    try:
                                        from services.email_service import EmailService
                                        email_service = EmailService()
                                        
                                        order_details = {
                                            'order_id': f'ORD-{full_domain.upper()[:5]}',
                                            'amount': total_price,
                                            'cryptocurrency': 'ETH',
                                            'domain': full_domain
                                        }
                                        
                                        email_success = email_service.send_payment_confirmation(
                                            user_email=email_provided,
                                            order_details=order_details,
                                            language='en'
                                        )
                                        
                                        if email_success:
                                            logger.info(f"📧 Payment confirmation email sent to {email_provided}")
                                        else:
                                            logger.error(f"❌ Failed to send email to {email_provided}")
                                            
                                    except Exception as email_error:
                                        logger.error(f"❌ Email service error: {email_error}")
                                
                                logger.info(f"📱 Payment confirmation sent for already-registered domain {full_domain}")
                                
                            except Exception as notification_error:
                                logger.error(f"❌ Notification error: {notification_error}")
                            
                            # Remove from monitoring
                            if address in self.active_payments:
                                del self.active_payments[address]
                            return
                            
                    except Exception as e:
                        logger.error(f"Error checking existing domain: {e}")
                    
                    # Send progress notification: Payment confirmed
                    from services.master_notification_service import get_master_notification_service
                    notification_service = get_master_notification_service()
                    await notification_service.send_progress_notification(telegram_id, full_domain, "payment_confirmed")
                    
                    # Call the actual domain registration method
                    from nomadly3_clean_bot import NomadlyCleanBot
                    
                    bot_instance = NomadlyCleanBot()
                    if bot_instance.domain_service:
                        # Send progress notification: DNS configuring
                        await notification_service.send_progress_notification(telegram_id, full_domain, "dns_configuring")
                        
                        # Send progress notification: Contacting registrar
                        await notification_service.send_progress_notification(telegram_id, full_domain, "contacting_registrar")
                        
                        # Send progress notification: Domain registering
                        await notification_service.send_progress_notification(telegram_id, full_domain, "domain_registering")
                        
                        result = await bot_instance.domain_service.register_domain_with_openprovider(
                            telegram_id=telegram_id,
                            domain_name=full_domain,
                            nameserver_choice=nameserver_choice or 'cloudflare'
                        )
                        
                        if result.get('success'):
                            logger.info(f"✅ Domain {full_domain} registered successfully!")
                            
                            # Send progress notification: Registration complete
                            await notification_service.send_progress_notification(telegram_id, full_domain, "registration_complete")
                            
                            await self._send_registration_success_notification(
                                telegram_id, full_domain, total_price, nameserver_choice or 'cloudflare', email_provided, result
                            )
                            
                            # Update order status to completed
                            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE orders 
                                SET status = 'completed', completed_at = NOW() 
                                WHERE crypto_address = %s
                            """, (address,))
                            rows_updated = cursor.rowcount
                            conn.commit()
                            cursor.close()
                            conn.close()
                            
                            logger.info(f"✅ Updated {rows_updated} order(s) to completed status")
                            
                            # Remove from monitoring after successful registration
                            if address in self.active_payments:
                                del self.active_payments[address]
                                self._save_to_queue()
                                logger.info(f"🗑️ Removed {address[:20]}... from monitoring queue")
                        else:
                            logger.error(f"❌ Domain registration failed: {result.get('error')}")
                    else:
                        logger.error("❌ Domain service not available")
                else:
                    logger.error(f"❌ No confirmed order found for payment address {address}")
                    # Check if we have any order with this address regardless of status
                    try:
                        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT telegram_id, domain_name, tld, nameserver_choice, 
                                   email_provided, total_price_usd, status
                            FROM orders 
                            WHERE crypto_address = %s AND status != 'completed'
                            LIMIT 1
                        """, (address,))
                        
                        any_order = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        
                        if any_order:
                            telegram_id, domain_name, tld, nameserver_choice, email_provided, total_price, status = any_order
                            full_domain = f"{domain_name}.{tld}" if not domain_name.endswith(tld) else domain_name
                            logger.info(f"🔍 Found order with status '{status}' for {full_domain} - proceeding with registration")
                            
                            # Check if domain already exists first
                            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM domains WHERE domain_name = %s", (full_domain,))
                            existing_domain = cursor.fetchone()
                            cursor.close()
                            conn.close()
                            
                            if existing_domain:
                                logger.info(f"⚠️ Domain {full_domain} already registered - updating order status to completed")
                                
                                # Update order status to completed since domain is already registered
                                conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                                cursor = conn.cursor()
                                cursor.execute("""
                                    UPDATE orders 
                                    SET status = 'completed', completed_at = NOW() 
                                    WHERE crypto_address = %s
                                """, (address,))
                                rows_updated = cursor.rowcount
                                conn.commit()
                                cursor.close()
                                conn.close()
                                
                                logger.info(f"✅ Updated {rows_updated} order(s) to completed status for existing domain")
                                
                                # Remove from monitoring
                                if address in self.active_payments:
                                    del self.active_payments[address]
                                    self._save_to_queue()
                                    logger.info(f"🗑️ Removed {address[:20]}... from monitoring queue")
                                    
                            elif not existing_domain:
                                # Send progress notifications and register domain
                                from services.master_notification_service import get_master_notification_service
                                notification_service = get_master_notification_service()
                                
                                # Send payment confirmed notification
                                await notification_service.send_progress_notification(telegram_id, full_domain, "payment_confirmed")
                                
                                # Create bot instance and register domain
                                from nomadly3_clean_bot import NomadlyCleanBot
                                bot_instance = NomadlyCleanBot()
                                
                                if bot_instance.domain_service:
                                    # Send finalizing notification
                                    await notification_service.send_progress_notification(telegram_id, full_domain, "domain_registering")
                                    
                                    result = await bot_instance.domain_service.register_domain_with_openprovider(
                                        telegram_id=telegram_id,
                                        domain_name=full_domain,
                                        nameserver_choice=nameserver_choice or 'cloudflare'
                                    )
                                    
                                    if result.get('success'):
                                        logger.info(f"✅ Domain {full_domain} registered successfully!")
                                        
                                        # Send registration complete notification
                                        await notification_service.send_progress_notification(telegram_id, full_domain, "registration_complete")
                                        
                                        # Send final success notification with buttons
                                        domain_data = {
                                            'domain_name': full_domain,
                                            'openprovider_domain_id': result.get('domain_id', 'N/A'),
                                            'expires_at': '2026-07-25',
                                            'nameserver_mode': nameserver_choice or 'cloudflare'
                                        }
                                        
                                        await notification_service.send_domain_registration_success(telegram_id, domain_data)
                                        
                                        # Update order status to completed
                                        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                                        cursor = conn.cursor()
                                        cursor.execute("""
                                            UPDATE orders 
                                            SET status = 'completed', completed_at = NOW() 
                                            WHERE crypto_address = %s
                                        """, (address,))
                                        rows_updated = cursor.rowcount
                                        conn.commit()
                                        cursor.close()
                                        conn.close()
                                        
                                        logger.info(f"✅ Updated {rows_updated} order(s) to completed status")
                                        
                                    else:
                                        logger.error(f"❌ Domain registration failed: {result.get('error')}")
                                else:
                                    logger.error("❌ Domain service not available")
                            else:
                                logger.info(f"⚠️ Domain {full_domain} already registered")
                                
                    except Exception as debug_error:
                        logger.error(f"❌ Error processing any-status order: {debug_error}")
                    
            except Exception as e:
                logger.error(f"Error during domain registration: {e}")
            
            # Legacy bot instance code (won't work but kept for reference)
            if self.bot_instance:
                user_id = payment_info['user_id']
                domain = payment_info['domain']
                
                logger.info(f"🔄 Processing domain registration for {domain} (user {user_id})")
                logger.info(f"🔍 Bot instance available: {hasattr(self.bot_instance, 'application')}")
                logger.info(f"🔍 Domain service available: {hasattr(self.bot_instance, 'domain_service')}")
                logger.info(f"🔍 Bot instance type: {type(self.bot_instance)}")
                
                # Check if the domain was already registered
                import psycopg2
                try:
                    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM registered_domains WHERE domain_name = %s", (domain,))
                    existing_domain = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    if existing_domain:
                        logger.info(f"⚠️ Domain {domain} already registered - skipping registration")
                        # Send notification that domain was already registered
                        try:
                            await self.bot_instance.application.bot.send_message(
                                chat_id=user_id,
                                text=(
                                    f"✅ **Payment Confirmed!**\n\n"
                                    f"Your domain **{domain}** was already registered and is active.\n"
                                    f"Thank you for your payment!"
                                ),
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"❌ Failed to send already-registered notification: {e}")
                        # Remove from monitoring
                        if address in self.active_payments:
                            del self.active_payments[address]
                        return
                        
                except Exception as e:
                    logger.error(f"Error checking existing domain: {e}")
                
                # Send payment confirmation notification to user
                try:
                    await self.bot_instance.application.bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"💰 **Payment Confirmed!**\n\n"
                            f"Your payment for **{domain}** has been confirmed.\n"
                            f"Domain registration is starting automatically...\n\n"
                            f"You'll receive another notification when complete!"
                        ),
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to send payment confirmation notification: {e}")
                
                # Trigger domain registration through bot's domain service
                try:
                    # Load user session to get registration details
                    import json
                    with open('user_sessions.json', 'r') as f:
                        sessions = json.load(f)
                    
                    user_session = sessions.get(str(user_id), {})
                    logger.info(f"🔍 User session loaded: {user_session.keys() if user_session else 'No session'}")
                    
                    # Get domain service from bot instance
                    if hasattr(self.bot_instance, 'domain_service'):
                        domain_service = self.bot_instance.domain_service
                        logger.info(f"✅ Domain service found in bot instance")
                        
                        # Extract nameserver choice and email from session
                        nameserver_choice = user_session.get('nameserver_choice', 'cloudflare')
                        technical_email = user_session.get('technical_email', 'cloakhost@tutamail.com')
                        
                        logger.info(f"🔧 Registration details: domain={domain}, nameserver={nameserver_choice}, email={technical_email}")
                        
                        # Process domain registration - THIS IS THE CRITICAL CALL
                        logger.info(f"🚀 CALLING DOMAIN REGISTRATION SERVICE NOW...")
                        result = await domain_service.process_domain_registration(
                            telegram_id=user_id,
                            domain_name=domain,
                            payment_method="crypto",
                            nameserver_choice=nameserver_choice,
                            crypto_currency=payment_info.get('crypto_type', 'eth')
                        )
                        
                        logger.info(f"🎯 Domain registration result: {result}")
                        
                        # Remove from monitoring only after successful registration
                        if result.get('success'):
                            logger.info(f"✅ Registration successful - removing from monitoring")
                            if address in self.active_payments:
                                del self.active_payments[address]
                        else:
                            logger.error(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
                            # Keep monitoring for potential retry
                            logger.info(f"⏳ Keeping payment in monitoring for potential retry")
                        
                        if result.get('success'):
                            # Send confirmation service email
                            try:
                                from services.confirmation_service import ConfirmationService
                                confirmation_service = ConfirmationService()
                                
                                # Create domain data structure for confirmation
                                domain_data = {
                                    "domain_name": domain,
                                    "registration_status": "Active",
                                    "expiry_date": "2026-07-24 23:59:59",
                                    "openprovider_domain_id": result.get('openprovider_domain_id'),
                                    "cloudflare_zone_id": result.get('cloudflare_zone_id'),
                                    "nameservers": result.get('nameservers', ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"]),
                                    "dns_info": f"DNS configured with {nameserver_choice.title()}"
                                }
                                
                                await confirmation_service.send_domain_registration_confirmation(
                                    telegram_id=user_id,
                                    domain_data=domain_data
                                )
                            except Exception as e:
                                logger.error(f"Error sending confirmation email: {e}")
                            
                            await self.bot_instance.application.bot.send_message(
                                chat_id=user_id,
                                text=(
                                    f"🎉 **Domain Registered Successfully!**\n\n"
                                    f"**Domain:** {domain}\n"
                                    f"**Status:** Active\n"
                                    f"**Nameservers:** {nameserver_choice}\n\n"
                                    f"Your domain is now live! 🚀\n"
                                    f"Check your email for confirmation details."
                                ),
                                parse_mode='Markdown'
                            )
                            
                            # Update session to mark as complete
                            user_session['payment_confirmed'] = True
                            user_session['registration_complete'] = True
                            sessions[str(user_id)] = user_session
                            
                            with open('user_sessions.json', 'w') as f:
                                json.dump(sessions, f, indent=2)
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            await self.bot_instance.application.bot.send_message(
                                chat_id=user_id,
                                text=(
                                    f"❌ **Domain Registration Failed**\n\n"
                                    f"Domain: {domain}\n"
                                    f"Error: {error_msg}\n\n"
                                    f"Please contact support for assistance."
                                ),
                                parse_mode='Markdown'
                            )
                    else:
                        logger.error("Domain service not available in bot instance")
                        await self.bot_instance.application.bot.send_message(
                            chat_id=user_id,
                            text=(
                                f"⚠️ **System Error**\n\n"
                                f"Domain registration service temporarily unavailable.\n"
                                f"Your payment has been confirmed.\n"
                                f"Please contact support to complete registration."
                            ),
                            parse_mode='Markdown'
                        )
                except Exception as e:
                    logger.error(f"Error during domain registration: {e}")
                    await self.bot_instance.application.bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"⚠️ **Registration Error**\n\n"
                            f"Your payment was confirmed but registration encountered an error.\n"
                            f"Error: {str(e)}\n\n"
                            f"Please contact support for assistance."
                        ),
                        parse_mode='Markdown'
                    )
                    
        except Exception as e:
            logger.error(f"Error processing payment confirmation: {e}")
    
    def add_payment_monitoring(self, address: str, payment_info: Dict):
        """Add a payment address to monitoring"""
        logger.info(f"📍 Adding payment monitoring for {address}")
        self.active_payments[address] = payment_info

    def set_bot_instance(self, bot_instance):
        """Set the bot instance for notifications"""
        self.bot_instance = bot_instance
        logger.info("✅ Bot instance connected to payment monitor")

def add_payment_address(address: str, user_id: int, order_id: str, crypto_type: str, amount: float):
    """Global function to add payment address to queue"""
    try:
        import json
        from datetime import datetime
        
        # Load existing queue
        try:
            with open('payment_monitor_queue.json', 'r') as f:
                queue = json.load(f)
        except FileNotFoundError:
            queue = {}
        
        # Add new payment
        queue[address] = {
            "user_id": user_id,
            "domain": f"order_{order_id}",  # Will be updated when we get domain name
            "crypto_type": crypto_type,
            "expected_amount": amount,
            "order_number": order_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save queue
        with open('payment_monitor_queue.json', 'w') as f:
            json.dump(queue, f, indent=2)
            
        logger.info(f"✅ Added payment {address} to monitor queue")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add payment to queue: {e}")
        return False

def remove_payment_monitoring(address: str):
        """Remove a payment from monitoring"""
        try:
            with open('payment_monitor_queue.json', 'r') as f:
                queue = json.load(f)
            if address in queue:
                del queue[address]
                with open('payment_monitor_queue.json', 'w') as f:
                    json.dump(queue, f, indent=2)
                logger.info(f"🗑️ Removed payment monitoring for {address}")
        except Exception as e:
            logger.error(f"Error removing payment monitoring: {e}")

# Global payment monitor instance
payment_monitor = PaymentMonitor()

async def start_payment_monitor(bot_instance=None):
    """Start the payment monitoring service"""
    payment_monitor.bot_instance = bot_instance
    await payment_monitor.start_monitoring()

if __name__ == "__main__":
    # Run standalone for testing
    asyncio.run(start_payment_monitor())