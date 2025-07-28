#!/usr/bin/env python3
"""
Webhook processor for BlockBee payments
Handles the actual domain registration after payment confirmation
"""

import asyncio
import logging
from typing import Dict, Any
from fresh_database import get_db_manager
from services.master_notification_service import MasterNotificationService
from domain_service import DomainService
from apis.production_cloudflare import CloudflareAPI
from apis.production_registry import RegistryAPI

logger = logging.getLogger(__name__)

class WebhookProcessor:
    def __init__(self):
        self.db = get_db_manager()
        self.notification_service = MasterNotificationService()
        self.domain_service = DomainService()
        self.cloudflare = CloudflareAPI()
        self.registry = RegistryAPI()
        
    async def process_payment(self, order_id: str, webhook_data: Dict[str, Any]) -> bool:
        """Process confirmed payment from BlockBee webhook"""
        try:
            logger.info(f"🔄 Processing payment for order {order_id}")
            
            # Get order from database
            order = self.db.get_order(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return False
                
            if order.status == 'completed':
                logger.info(f"Order {order_id} already completed")
                return True
                
            # Extract payment info
            amount_paid = float(webhook_data.get('value_coin', 0))
            txid = webhook_data.get('txid_in', webhook_data.get('txid', ''))
            confirmations = int(webhook_data.get('confirmations', 0))
            
            logger.info(f"💰 Payment details: {amount_paid} {order.crypto_currency}, {confirmations} confirmations")
            
            # Update order status
            self.db.update_order_status(order_id, 'completed', txid)
            logger.info(f"✅ Order {order_id} marked as completed")
            
            # Send payment confirmation to user
            await self.notification_service.send_payment_confirmation(
                telegram_id=order.telegram_id,
                payment_data={
                    'domain_name': order.domain_name,
                    'amount_usd': order.total_price_usd,
                    'txid': txid
                }
            )
            
            # Register the domain
            logger.info(f"🌐 Starting domain registration for {order.domain_name}")
            
            try:
                # Create Cloudflare zone first
                zone_result = self.cloudflare.create_zone(order.domain_name)
                if not zone_result['success']:
                    logger.error(f"Failed to create Cloudflare zone: {zone_result['error']}")
                    return False
                    
                cloudflare_zone_id = zone_result['zone_id']
                logger.info(f"✅ Cloudflare zone created: {cloudflare_zone_id}")
                
                # Get nameservers
                ns_result = self.cloudflare.get_nameservers(order.domain_name)
                if not ns_result['success']:
                    logger.error(f"Failed to get nameservers: {ns_result['error']}")
                    return False
                    
                nameservers = ns_result['nameservers']
                logger.info(f"✅ Got nameservers: {nameservers}")
                
                # Register domain with registry
                reg_result = self.registry.register_domain(
                    domain=order.domain_name,
                    period=1,
                    email=order.email or 'cloakhost@tutamail.com',
                    nameservers=nameservers
                )
                
                if not reg_result['success']:
                    logger.error(f"Domain registration failed: {reg_result['error']}")
                    return False
                    
                logger.info(f"✅ Domain registered successfully!")
                
                # Save to registered domains
                self.db.add_registered_domain(
                    telegram_id=order.telegram_id,
                    domain_name=order.domain_name,
                    registry_id=reg_result.get('domain_id'),
                    cloudflare_zone_id=cloudflare_zone_id,
                    nameservers=nameservers,
                    email=order.email or 'cloakhost@tutamail.com'
                )
                
                # Send success notification
                await self.notification_service.send_domain_registration_success(
                    telegram_id=order.telegram_id,
                    domain_data={
                        'domain_name': order.domain_name,
                        'nameservers': nameservers
                    }
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Domain registration error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            return False