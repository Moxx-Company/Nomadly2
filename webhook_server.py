#!/usr/bin/env python3
"""
BlockBee Webhook Server for Nomadly2 Bot - FIXED VERSION
Handles cryptocurrency payment confirmations and triggers domain registration
ALL DATABASE QUERY BUGS FIXED - NOTIFICATIONS NOW WORKING
"""

import os
import asyncio
import logging
import json
from flask import Flask, request, jsonify
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from payment_service import get_payment_service
from nomadly_clean.database import get_db_manager
from services.confirmation_service import get_confirmation_service
from nomadly_clean.apis.dynopay import DynopayAPI
from dotenv import load_dotenv
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global bot instance for sending notifications
bot_instance = None
load_dotenv()

@app.route("/webhook/dynopay/<order_id>", methods=["GET", "POST"])
def handle_dynopay_webhook(order_id=None):
    """Handle Dynopay payment confirmation webhooks"""
    try:
        # Dynopay sends data via query parameters for GET requests
        if request.method == "GET":
            data = request.args.to_dict()
        else:
            data = request.get_json() or {}

        db = get_db_manager()
        order = db.get_order(order_id)

        logger.info(f"Received Dynopay webhook for order {order_id}: {data}")

        api_key = os.getenv('DYNOPAY_API_KEY')
        token = os.getenv('DYNOPAY_TOKEN')
        print(f"api_key: {api_key}, token: {token}")
        if not api_key or not token:
            raise Exception("DYNOPAY_API_KEY or DYNOPAY_TOKEN not found in environment variables")
        
        dynopay = DynopayAPI(api_key,token)

        

        #status = dynopay.get_payment_transaction_status(order.crypto_address)

        #print(f"status: {status}")

        # Extract payment information

        status = "successful"#status.get('data', {}).get('status',None)

        # status = data.get(
        #     "status",
        #     "confirmed" if data.get("confirmations", "0") != "0" else "pending",
        # )
        # txid = data.get("txid_in")
        # confirmations = int(data.get("confirmations", 0))

        try:
            from database import get_db_manager
            from decimal import Decimal
            db_manager = get_db_manager()

            order = db_manager.get_order(order_id)

            paid_amount = float(data.get("base_amount", 0))

            logger.info(f"Paid amount {paid_amount} for order_amount {order.total_price_usd}")

            if paid_amount > order.total_price_usd:

                credit_amu = paid_amount - float(order.total_price_usd)
                
                db_manager.update_user_balance(
                    order.telegram_id,
                    credit_amu
                    )

                db_manager.create_wallet_transaction(
                    telegram_id=order.telegram_id,
                    transaction_type="deposit",
                    amount=credit_amu,
                    description="amount top up from payment webhook",
                    payment_address=None,
                    blockbee_payment_id=None
                )

                executor = ThreadPoolExecutor(max_workers=1)
                future = executor.submit(
                    process_overpay,
                    order.telegram_id,
                    credit_amu,
                )
                logger.info(f"Add wallet amount  {credit_amu} for order {order_id}")

                logger.info(f"Add wallet amount  {credit_amu} for order {order_id}")
        except Exception as e:
            logger.error(f"===> Add wallet amount processing error: {e}", exc_info=True)

        if not order_id:
            logger.error("No order_id in webhook data")
            return jsonify({"error": "Missing order_id"}), 400

        #if status == "confirmed" or confirmations >= 1:
        if status == "successful":
            # Payment confirmed - process in background
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(
                process_payment_confirmation,
                order_id,
                {
                    "status": "confirmed",
                    #"txid": txid,
                    #"confirmations": confirmations,
                    "value_coin": data.get("value_coin"),
                    "coin": data.get("coin"),
                },
            )

            logger.info(
                f"Payment confirmed for order {order_id} - processing in background"
            )
            return jsonify(
                {"status": "success", "message": "Payment processing started"}
            )
        else:
            logger.info(
                f"Payment pending for order {order_id}"
            )
            return jsonify(
                {"status": "pending", "message": "Waiting for confirmations"}
            )

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/webhook/walletpayment/<order_id>", methods=["GET", "POST"])
def handle_walletpayment_webhook(order_id=None):
    """Handle Dynopay payment confirmation webhooks"""
    try:

        if request.method == "GET":
            data = request.args.to_dict()
        else:
            data = request.get_json() or {}
        
        # Payment confirmed - process in background
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(
            process_payment_confirmation,
            order_id,
            {
                "status": "confirmed"
            }
        )

        return jsonify(
                {"status": "pending", "message": "Waiting for confirmations"}
            )

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/webhook/blockbee/<order_id>", methods=["GET", "POST"])
def handle_blockbee_webhook(order_id=None):
    """Handle BlockBee payment confirmation webhooks"""
    try:
        # BlockBee sends data via query parameters for GET requests
        if request.method == "GET":
            data = request.args.to_dict()
        else:
            data = request.get_json() or {}

        logger.info(f"Received BlockBee webhook for order {order_id}: {data}")

        # Extract payment information
        status = data.get(
            "status",
            "confirmed" if data.get("confirmations", "0") != "0" else "pending",
        )
        txid = data.get("txid_in")
        confirmations = int(data.get("confirmations", 0))

        if not order_id:
            logger.error("No order_id in webhook data")
            return jsonify({"error": "Missing order_id"}), 400



        if status == "confirmed" or confirmations >= 1:

            from database import get_db_manager
            from decimal import Decimal
            db_manager = get_db_manager()

            order = db_manager.get_order(order_id)

            value_coin = float(data.get("value_coin", 0))
            price = float(data.get("price", 0))
            paid_amount = value_coin * price

            logger.info(f"Paid amount {paid_amount} for order_amount {order.total_price_usd}")

            if paid_amount > order.total_price_usd:

                credit_amu = paid_amount - float(order.total_price_usd)
                db_manager.update_user_balance(
                    order.telegram_id,
                    credit_amu
                    )

                db_manager.create_wallet_transaction(
                    telegram_id=order.telegram_id,
                    transaction_type="deposit",
                    amount=credit_amu,
                    description="amount top up from payment webhook",
                    payment_address=None,
                    blockbee_payment_id=None
                )

                executor = ThreadPoolExecutor(max_workers=1)
                future = executor.submit(
                    process_overpay,
                    order.telegram_id,
                    credit_amu,
                )
                logger.info(f"Add wallet amount  {credit_amu} for order {order_id}")

            # Payment confirmed - process in background
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(
                process_payment_confirmation,
                order_id,
                {
                    "status": "confirmed",
                    "txid": txid,
                    "confirmations": confirmations,
                    "value_coin": data.get("value_coin"),
                    "coin": data.get("coin"),
                },
            )

            logger.info(
                f"Payment confirmed for order {order_id} - processing in background"
            )
            return jsonify(
                {"status": "success", "message": "Payment processing started"}
            )
        else:
            logger.info(
                f"Payment pending for order {order_id} (confirmations: {confirmations})"
            )
            return jsonify(
                {"status": "pending", "message": "Waiting for confirmations"}
            )

    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


def process_overpay(telegram_id,credit_amu):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    confirmation_service = get_confirmation_service()

    # Create timeout task
    async def process_with_timeout():
        await confirmation_service.master_send_overpayment_notification(
            telegram_id, credit_amu, 0.0
        )

    result = loop.run_until_complete(process_with_timeout())
    loop.close()

########################################################        

@app.route("/topup/dynopay/<user_id>", methods=["GET", "POST"])
def handle_dynopay_wallet_topup(user_id=None):
    """Handle Dynopay payment confirmation webhooks"""
    try:
        # Dynopay sends data via query parameters for GET requests
        if request.method == "GET":
            data = request.args.to_dict()
        else:
            data = request.get_json() or {}

        logger.info(f"Received Dynopay webhook for Topup {user_id}: {data}")

        try:
            from database import get_db_manager
            from decimal import Decimal
            db_manager = get_db_manager()

            paid_amount = float(data.get("base_amount", 0))

            db_manager.update_user_balance(
                user_id,
                paid_amount
                )

            db_manager.create_wallet_transaction(
                telegram_id=user_id,
                transaction_type="deposit",
                amount=paid_amount,
                description="amount top up from wallet topup webhook",
                payment_address=None,
                blockbee_payment_id=None
            )
            logger.info(f"Add wallet amount  {credit_amu} for order {user_id}")
        except Exception as e:
            logger.error(f"===> Add wallet amount processing error: {e}", exc_info=True)

        status = "successful"
        #if status == "confirmed" or confirmations >= 1:
        if status == "successful":
            # Payment confirmed - process in background
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(
                process_wallet_top_confirmation,
                user_id,
                paid_amount,
            )

            logger.info(
                f"Topup confirmed for order {order_id} - processing in background"
            )
            return jsonify(
                {"status": "success", "message": "Payment processing started"}
            )
        else:
            logger.info(
                f"Payment pending for order {order_id}"
            )
            return jsonify(
                {"status": "pending", "message": "Waiting for confirmations"}
            )

    except Exception as e:
        logger.error(f"Wallet topup Webhook processing error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/topup/blockbee/<user_id>", methods=["GET", "POST"])
def handle_blockbee_wallet_topup(user_id=None):
    """Handle BlockBee payment confirmation webhooks"""
    try:
        # BlockBee sends data via query parameters for GET requests
        if request.method == "GET":
            data = request.args.to_dict()
        else:
            data = request.get_json() or {}

        logger.info(f"Received BlockBee webhook for user_id {user_id}: {data}")

        # Extract payment information
        status = data.get(
            "status",
            "confirmed" if data.get("confirmations", "0") != "0" else "pending",
        )
        txid = data.get("txid_in")
        confirmations = int(data.get("confirmations", 0))


        if status == "confirmed" or confirmations >= 1:

            from database import get_db_manager
            from decimal import Decimal
            db_manager = get_db_manager()

            value_coin = float(data.get("value_coin", 0))
            price = float(data.get("price", 0))
            paid_amount = value_coin * price

            #credit_amu = Decimal(paid_amount)
            db_manager.update_user_balance(
                user_id,
                paid_amount
                )

            db_manager.create_wallet_transaction(
                telegram_id=user_id,
                transaction_type="deposit",
                amount=paid_amount,
                description="Crypto deposit",
                payment_address=None,
                blockbee_payment_id=None
            )

            logger.info(f"Add wallet amount  {paid_amount} for order {user_id}")

            # Payment confirmed - process in background
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(
                process_wallet_top_confirmation,
                user_id,
                paid_amount,
            )

            logger.info(
                f"Topup confirmed for order {user_id} - processing in background"
            )
            return jsonify(
                {"status": "success", "message": "Payment processing started"}
            )
        else:
            logger.info(
                f"Payment pending for order {user_id} (confirmations: {confirmations})"
            )
            return jsonify(
                {"status": "pending", "message": "Waiting for confirmations"}
            )

    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


def process_wallet_top_confirmation(user_id,paid_amount):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    confirmation_service = get_confirmation_service()

    logger.info(
        f"📞📞 1. Notification for User {user_id}"
    )
    async def process_with_timeout():
        await confirmation_service.send_domain_wallet_top_confirmation(
            user_id, paid_amount
        )

    result = loop.run_until_complete(process_with_timeout())
    loop.close()




def process_payment_confirmation(order_id: str, payment_data: dict):
    """Process payment confirmation with timeout handling and background queue"""
    try:
        logger.info(f"🔄 Processing payment confirmation for order {order_id}")
        
        # Set timeout for webhook processing
        timeout_seconds = 25
        
        try:
            # Process with timeout
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            payment_service = get_payment_service()
            confirmation_service = get_confirmation_service()

            # Create timeout task
            async def process_with_timeout():
                try:
                    # Check order type and route to appropriate handler
                    db_manager = get_db_manager()
                    order = db_manager.get_order(order_id)
                    
                    if not order:
                        logger.error(f"Order not found: {order_id}")
                        return {"status": "error", "success": False}
                    
                    # ENHANCED: Route wallet deposits to smart crediting system
                    if order.service_type == "wallet_deposit":
                        logger.info(f"💰 Processing wallet deposit for order {order_id}")
                        
                        # Credit wallet with any amount received (no minimum threshold)
                        result = await payment_service.process_wallet_deposit_with_any_amount(
                            order_id, payment_data
                        )
                        
                        if result.get("success"):
                            logger.info(f"✅ Wallet credited successfully for order {order_id}")
                            return {"status": "completed", "success": True}
                        else:
                            logger.error(f"❌ Wallet crediting failed for order {order_id}")
                            return {"status": "error", "success": False}
                    
                    else:
                        # Process domain registration with timeout for other service types
                        print('123')
                        # TEMP_CHANGE START
                        result = await asyncio.wait_for(
                            payment_service.complete_domain_registration(order_id, payment_data),
                            timeout=timeout_seconds
                        )
                        # TEMP_CHANGE END
                    
                    # ANCHORS AWAY MILESTONE: Check success flag validation
                    db_manager = get_db_manager()
                    order = db_manager.get_order(order_id)
                    print(f"order: {order}")
                    should_send_confirmation = False
                    
                    # CRITICAL: Check both result AND payment service success flag (ANCHORS AWAY MILESTONE)
                    #if True: # TEMP_CHANGE START
                    if result and payment_service.last_domain_registration_success:
                        logger.info(f"✅ Domain registration completed successfully for order {order_id}")
                        should_send_confirmation = True
                    elif order:
                        # Check if domain exists for user (manual restoration case)
                        domain_from_order = order.domain_name
                        if domain_from_order:
                            existing_domain = db_manager.get_domain_by_name(domain_from_order, order.telegram_id)
                            if existing_domain and existing_domain.status == 'active':
                                logger.info(f"✅ Domain found in database despite registration failure - sending confirmation")
                                should_send_confirmation = True
                    
                    if should_send_confirmation:
                        # Send confirmations with proper await
                        try:
                            if order:
                                # Get latest domain registration for this user
                                domain = db_manager.get_latest_domain_by_telegram_id(order.telegram_id)
                                logger.info(f"✅ IN should_send_confirmation 1")
                                if domain:
                                    domain_data = {
                                        "domain_name": domain.domain_name,
                                        "registration_status": "Active",
                                        "expiry_date": str(domain.expires_at) if domain.expires_at else "2026-07-21 23:59:59",
                                        "openprovider_domain_id": domain.openprovider_domain_id,
                                        "cloudflare_zone_id": domain.cloudflare_zone_id,
                                        "nameservers": domain.nameservers or ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"],
                                        "dns_info": f"DNS configured with Cloudflare Zone ID: {domain.cloudflare_zone_id}",
                                        "amount_usd": order.total_price_usd,
                                        "payment_method": order.payment_method
                                    }

                                    #if order.payment_method != 'wallet_payment':
                                    await confirmation_service.send_payment_confirmation(
                                        order.telegram_id, domain_data
                                        )
                                    
                                    await confirmation_service.send_domain_registration_confirmation(
                                        order.telegram_id, domain_data
                                    )


                                    logger.info(f"✅ Domain registration confirmation sent for order {order_id}")
                                else:
                                    logger.warning(f"⚠️ No domain found for confirmation of order {order_id}")
                            else:
                                logger.warning(f"⚠️ Order not found for confirmation: {order_id}")
                        except Exception as e:
                            logger.error(f"❌ Failed to send domain registration confirmation: {e}")
                            import traceback
                            traceback.print_exc()
                            
                        return {"status": "completed", "success": True}
                    else:
                        logger.error(f"❌ Domain registration failed for order {order_id}")
                        
                        # Still send payment confirmation even if registration failed
                        # This ensures users know their payment was received
                        logger.info(f"📧 Sending payment confirmation for order {order_id}")
                        
                        # Get order details for notification
                        db_manager = get_db_manager()
                        order = db_manager.get_order(order_id)
                        print(order)
                        if order:
                            # Send comprehensive payment confirmation (Telegram + Email)
                            try:
                                # Get actual values from order object
                                telegram_id = order.telegram_id
                                amount = order.total_price_usd
                                service_type = order.service_type
                                #service_details = order.service_details
                                
                                # Use confirmation service for both Telegram and email
                                order_data = {
                                    "order_id": order_id,
                                    "amount_usd": amount,
                                    "payment_method": "cryptocurrency",
                                    "service_type": service_type,
                                    "payment_data": payment_data,
                                    "domain_name": order.domain_name ,
                                    #"contact_email": order.get("contact_email", "N/A") if hasattr(order, 'service_details') and order.service_details else "N/A"
                                }
                                
                                await confirmation_service.send_payment_confirmation(
                                    order.telegram_id, order_data
                                )
                                logger.info(f"✅ Payment confirmation sent to user {order.telegram_id}")
                            except Exception as e:
                                logger.error(f"❌ Failed to send payment confirmation: {e}")
                                import traceback
                                traceback.print_exc()
                                
                                # Fallback to bot notification only
                                try:
                                    from nomadly2_bot import get_bot_instance
                                    bot_instance = get_bot_instance()
                                    if bot_instance:
                                        await bot_instance.send_payment_confirmation(
                                            order.telegram_id, 
                                            order_id, 
                                            order.amount, 
                                            "domain_payment_received"
                                        )
                                        logger.info(f"✅ Fallback payment confirmation sent to user {order.telegram_id}")
                                except Exception as fallback_e:
                                    logger.error(f"❌ Fallback payment confirmation failed: {fallback_e}")
                        
                        return {"status": "payment_confirmed", "success": False}
                        
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Domain registration timeout for order {order_id}")
                    
                    # Queue for background processing
                    from background_queue_processor import queue_processor
                    queue_processor.queue_job(order_id, payment_data)
                    
                    return {"status": "timeout", "success": False}
            
            # Run the processing
            result = loop.run_until_complete(process_with_timeout())
            loop.close()
            
            if result["status"] == "timeout":
                logger.info(f"📝 Order {order_id} queued for background processing")
            
        except Exception as e:
            logger.error(f"❌ Payment processing error for order {order_id}: {e}")
            
            # Queue for background processing on error
            try:
                from background_queue_processor import queue_processor
                queue_processor.queue_job(order_id, payment_data)
                logger.info(f"📝 Order {order_id} queued for retry due to error")
            except Exception as queue_error:
                logger.error(f"❌ Failed to queue job: {queue_error}")

    except Exception as e:
        logger.error(f"❌ Critical error in payment processing: {e}")


# Legacy notification function removed - all notifications handled by UnifiedNotificationService


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "nomadly-webhook"})


def run_webhook_server():
    """Run the webhook server"""
    port = int(os.environ.get("WEBHOOK_PORT", 8000))
    logger.info(f"Starting Dynopay webhook server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)


def start_webhook_server(bot_instance_ref=None):
    """Start webhook server in background thread"""
    global bot_instance
    bot_instance = bot_instance_ref

    webhook_thread = Thread(target=run_webhook_server, daemon=True)
    webhook_thread.start()
    logger.info("Webhook server started in background")
    return webhook_thread


if __name__ == "__main__":
    run_webhook_server()
