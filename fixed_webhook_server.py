#!/usr/bin/env python3
"""
FIXED BlockBee Webhook Server for Nomadly2 Bot  
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
from database import get_db_manager
from services.confirmation_service import get_confirmation_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

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
                f"Payment pending for order {order_id}, confirmations: {confirmations}"
            )
            return jsonify({"status": "pending"})

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


def process_payment_confirmation(order_id, payment_data):
    """Process payment confirmation with proper error handling"""
    try:
        logger.info(f"🔄 Processing payment confirmation for order {order_id}")
        
        # Create new event loop for thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def process_with_timeout():
            """Process payment with timeout and proper notification handling"""
            try:
                payment_service = get_payment_service()
                confirmation_service = get_confirmation_service()
                timeout_seconds = 25  # BlockBee timeout protection

                # Get order details first
                db_manager = get_db_manager()
                order = db_manager.get_order(order_id)
                
                if not order:
                    logger.error(f"❌ Order not found: {order_id}")
                    return {"status": "error", "success": False}

                logger.info(f"✅ Order found: {order_id}, User: {order.telegram_id}, Service: {order.service_type}")

                # Process payment based on service type
                if hasattr(order, 'service_type') and order.service_type == "wallet_deposit":
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
                    # Process domain registration with timeout
                    result = await asyncio.wait_for(
                        payment_service.complete_domain_registration(order_id, payment_data),
                        timeout=timeout_seconds
                    )

                # Check success flag for domain registration confirmation
                should_send_domain_confirmation = False
                
                if result and payment_service.last_domain_registration_success:
                    logger.info(f"✅ Domain registration completed successfully for order {order_id}")
                    should_send_domain_confirmation = True
                elif order:
                    # Check if domain exists for user (manual restoration case)
                    print("in 123")
                    if hasattr(order, 'service_details') and order.service_details:
                        domain_from_order = order.service_details.get('domain_name')
                        if domain_from_order:
                            existing_domain = db_manager.get_domain_by_name(domain_from_order, order.telegram_id)
                            if existing_domain and existing_domain.status == 'active':
                                logger.info(f"✅ Domain found in database despite registration failure - sending confirmation")
                                should_send_domain_confirmation = True

                # Send domain registration confirmation if successful
                if should_send_domain_confirmation:
                    try:
                        # Get latest domain registration for this user
                        domain = db_manager.get_latest_domain_by_telegram_id(order.telegram_id)
                        if domain:
                            domain_data = {
                                "domain_name": domain.domain_name,
                                "registration_status": "Active", 
                                "expiry_date": str(domain.expiry_date) if hasattr(domain, 'expiry_date') and domain.expiry_date else "2026-07-21 23:59:59",
                                "openprovider_domain_id": getattr(domain, 'openprovider_domain_id', None),
                                "cloudflare_zone_id": getattr(domain, 'cloudflare_zone_id', None),
                                "nameservers": getattr(domain, 'nameservers', None) or ["anderson.ns.cloudflare.com", "leanna.ns.cloudflare.com"],
                                "dns_info": f"DNS configured with Cloudflare Zone ID: {getattr(domain, 'cloudflare_zone_id', 'N/A')}"
                            }
                            
                            await confirmation_service.send_domain_registration_confirmation(
                                order.telegram_id, domain_data
                            )
                            logger.info(f"✅ Domain registration confirmation sent for order {order_id}")
                        else:
                            logger.warning(f"⚠️ No domain found for confirmation of order {order_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to send domain registration confirmation: {e}")
                        import traceback
                        traceback.print_exc()
                        
                    return {"status": "completed", "success": True}

                else:
                    # Domain registration failed or was payment-only
                    logger.info(f"📧 Sending payment confirmation for order {order_id}")
                    
                    # Send payment confirmation even if registration failed
                    try:
                        # Extract order data safely
                        telegram_id = order.telegram_id
                        amount = getattr(order, 'amount_usd', 0)
                        service_type = getattr(order, 'service_type', 'domain_registration')
                        service_details = getattr(order, 'service_details', {})
                        
                        # Create order data for notification
                        order_data = {
                            "order_id": order_id,
                            "amount_usd": amount,
                            "payment_method": "cryptocurrency",
                            "service_type": service_type,
                            "domain_name": service_details.get('domain_name', 'N/A') if service_details else "N/A",
                            "contact_email": service_details.get('contact_email', 'N/A') if service_details else "N/A",
                            "txid": payment_data.get("txid", "N/A")
                        }
                        
                        # Send comprehensive payment confirmation
                        await confirmation_service.send_payment_confirmation(
                            telegram_id, order_data
                        )
                        logger.info(f"✅ Payment confirmation sent to user {telegram_id}")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to send payment confirmation: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # Final fallback notification
                        try:
                            from nomadly2_bot import get_bot_instance
                            bot_instance = get_bot_instance()
                            if bot_instance and hasattr(order, 'telegram_id'):
                                await bot_instance.send_message(
                                    chat_id=order.telegram_id,
                                    text=f"✅ Payment received for order {order_id}! Amount: ${getattr(order, 'amount_usd', 0):.2f}"
                                )
                                logger.info(f"✅ Fallback payment notification sent to user {order.telegram_id}")
                        except Exception as fallback_e:
                            logger.error(f"❌ Fallback notification failed: {fallback_e}")
                    
                    return {"status": "payment_confirmed", "success": True}
                    
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Domain registration timeout for order {order_id}")
                
                # Still send payment confirmation on timeout
                try:
                    if order:
                        await confirmation_service.send_payment_confirmation(
                            order.telegram_id, {
                                "order_id": order_id,
                                "amount_usd": getattr(order, 'amount_usd', 0),
                                "payment_method": "cryptocurrency",
                                "service_type": "domain_registration",
                                "domain_name": "Processing...",
                                "status": "Payment received - Registration in progress"
                            }
                        )
                        logger.info(f"✅ Timeout payment confirmation sent for order {order_id}")
                except Exception as e:
                    logger.error(f"❌ Timeout confirmation failed: {e}")
                
                return {"status": "timeout", "success": False}
            
            except Exception as e:
                logger.error(f"❌ Payment processing error: {e}")
                import traceback
                traceback.print_exc()
                
                # Still send payment confirmation on error
                try:
                    if order:
                        await confirmation_service.send_payment_confirmation(
                            order.telegram_id, {
                                "order_id": order_id,
                                "amount_usd": getattr(order, 'amount_usd', 0),
                                "payment_method": "cryptocurrency", 
                                "service_type": "domain_registration",
                                "domain_name": "Error occurred",
                                "status": "Payment received - Technical issue occurred"
                            }
                        )
                        logger.info(f"✅ Error payment confirmation sent for order {order_id}")
                except Exception as conf_e:
                    logger.error(f"❌ Error confirmation failed: {conf_e}")
                
                return {"status": "error", "success": False}

        # Run the processing
        result = loop.run_until_complete(process_with_timeout())
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Critical payment processing error for order {order_id}: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "critical_error", "success": False}


@app.route("/", methods=["GET"])
def health_check():
    return {"status": "ok", "service": "Nomadly2 Webhook Server"}


if __name__ == "__main__":
    logger.info("Starting BlockBee webhook server on port 8000")
    app.run(host="0.0.0.0", port=8000, debug=False)