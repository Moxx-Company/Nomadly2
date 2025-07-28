#!/usr/bin/env python3
"""
Unified Notification Service
Single source of truth for all payment and domain registration notifications
"""

import json
import logging
from typing import Dict, Any, Optional
from database import get_db_manager
from services.confirmation_service import get_confirmation_service

logger = logging.getLogger(__name__)

class UnifiedNotificationService:
    """Single notification service handling all payment and domain events"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.confirmation_service = get_confirmation_service()
        
    async def process_payment_notification(self, order_id: str, payment_data: dict, payment_service) -> bool:
        """Process payment confirmation with comprehensive validation"""
        try:
            logger.info(f"🔔 Processing unified payment notification for order {order_id}")
            
            # Get order details
            order = self.db.get_order(order_id)
            if not order:
                logger.error(f"Order not found: {order_id}")
                return False
                
            # 1. Send payment confirmation (always sent)
            await self._send_payment_confirmation(order, payment_data)
            
            # 2. Handle domain registration validation (if applicable)
            if order.service_type == "domain_registration":
                return await self._handle_domain_registration_notification(order, payment_service)
                
            logger.info(f"✅ Non-domain service notification completed for order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Unified notification processing failed for order {order_id}: {e}")
            return False
    
    async def _send_payment_confirmation(self, order, payment_data: dict):
        """Send payment confirmation notification"""
        order_data = {
            "order_id": order.order_id,
            "amount_usd": order.amount,
            "payment_method": "Cryptocurrency",
            "transaction_id": payment_data.get("txid", "N/A"),
            "service_description": order.service_type.replace("_", " ").title(),
        }
        
        await self.confirmation_service.send_payment_confirmation(
            order.telegram_id, order_data
        )
        logger.info(f"✅ Payment confirmation sent to user {order.telegram_id}")
    
    async def _handle_domain_registration_notification(self, order, payment_service) -> bool:
        """Handle domain registration success/failure notifications with strict validation"""
        try:
            # STRICT VALIDATION: Check if domain registration actually succeeded
            registration_successful = False
            domain = None
            
            # Check 1: Payment service must explicitly report success
            if hasattr(payment_service, 'last_domain_registration_success'):
                registration_successful = getattr(payment_service, 'last_domain_registration_success', False)
                logger.info(f"Payment service reports registration success: {registration_successful}")
            
            # Check 2: If payment service reports success, verify domain exists in database
            if registration_successful:
                domain = self.db.get_domain_by_telegram_id(order.telegram_id)
                
                if domain and hasattr(domain, 'openprovider_domain_id') and domain.openprovider_domain_id:
                    # Check 3: Verify real OpenProvider domain ID (8+ digits)
                    if (str(domain.openprovider_domain_id).isdigit() and 
                        len(str(domain.openprovider_domain_id)) >= 8):
                        logger.info(f"✅ Domain verification passed: {domain.openprovider_domain_id}")
                    else:
                        logger.warning(f"❌ Invalid domain ID: {domain.openprovider_domain_id}")
                        registration_successful = False
                else:
                    logger.warning("❌ No valid domain found despite payment service success report")
                    registration_successful = False
            
            # Send appropriate notification based on validation results
            if registration_successful and domain:
                await self._send_domain_success_notification(order, domain)
                return True
            else:
                await self._send_domain_processing_notification(order)
                return False
                
        except Exception as e:
            logger.error(f"❌ Domain registration notification error: {e}")
            await self._send_domain_processing_notification(order)
            return False
    
    async def _send_domain_success_notification(self, order, domain):
        """Send domain registration success notification"""
        logger.info(f"✅ DOMAIN REGISTRATION CONFIRMED - sending success notification")
        logger.info(f"   Domain: {domain.domain_name}")
        logger.info(f"   OpenProvider ID: {domain.openprovider_domain_id}")
        logger.info(f"   Cloudflare Zone: {domain.cloudflare_zone_id}")
        
        # Use Master Notification Service
        from services.master_notification_service import get_master_notification_service
        
        notification_service = get_master_notification_service()
        domain_data = {
            "domain_name": domain.domain_name,
            "registration_status": "Active",
            "openprovider_domain_id": domain.openprovider_domain_id,
            "cloudflare_zone_id": domain.cloudflare_zone_id,
        }
        
        await notification_service.send_domain_registration_success(order.telegram_id, domain_data)
        logger.info(f"✅ Domain registration success notification sent to user {order.telegram_id}")
    
    async def _send_domain_processing_notification(self, order):
        """Send honest domain processing notification"""
        logger.info(f"⏳ Domain registration incomplete for order {order.order_id} - sending processing notification")
        
        # Use Master Notification Service
        from services.master_notification_service import get_master_notification_service
        
        notification_service = get_master_notification_service()
        await notification_service.send_progress_notification(
            order.telegram_id, 
            order.service_details.get('domain_name', 'domain'), 
            "payment_received"
        )
        logger.info(f"✅ Processing status notification sent to user {order.telegram_id}")
    
    def _parse_nameservers(self, nameservers_data) -> list:
        """Parse nameservers from various formats"""
        if isinstance(nameservers_data, list):
            return nameservers_data
        elif isinstance(nameservers_data, str):
            try:
                return json.loads(nameservers_data)
            except:
                from payment_service import get_real_cloudflare_nameservers
                return [get_real_cloudflare_nameservers()]
        else:
            from payment_service import get_real_cloudflare_nameservers
            return [get_real_cloudflare_nameservers()]

# Global service instance
_unified_notification_service = None

def get_unified_notification_service() -> UnifiedNotificationService:
    """Get the global unified notification service instance"""
    global _unified_notification_service
    if _unified_notification_service is None:
        _unified_notification_service = UnifiedNotificationService()
    return _unified_notification_service