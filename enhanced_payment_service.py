#!/usr/bin/env python3
"""
Enhanced Payment Service with Async API Integration
Modernized version of payment_service.py with async API clients and monitoring
"""

import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Import enhanced monitoring
from enhanced_monitoring import logger, monitor_performance, business_metrics

# Import async API clients
from async_api_clients import (
    AsyncOpenProviderAPI, 
    AsyncCloudflareAPI, 
    create_domain_with_dns
)

class EnhancedPaymentService:
    """Enhanced payment service with async APIs and comprehensive monitoring"""
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.last_domain_registration_success = False
        
        # API credentials from environment
        self.openprovider_credentials = {
            "username": os.getenv("OPENPROVIDER_USERNAME"),
            "password": os.getenv("OPENPROVIDER_PASSWORD")
        }
        
        self.cloudflare_credentials = {
            "email": os.getenv("CLOUDFLARE_EMAIL"),
            "api_key": os.getenv("CLOUDFLARE_GLOBAL_API_KEY"),
            "api_token": os.getenv("CLOUDFLARE_API_TOKEN")
        }
    
    @monitor_performance("enhanced_domain_registration")
    async def complete_domain_registration_enhanced(
        self, 
        order_id: str, 
        webhook_data: Dict[str, Any]
    ) -> bool:
        """
        Enhanced domain registration with async APIs and comprehensive monitoring
        """
        start_time = datetime.utcnow()
        
        try:
            logger.info(
                "enhanced_domain_registration_started",
                order_id=order_id,
                webhook_data_keys=list(webhook_data.keys())
            )
            
            # Track business metric
            business_metrics.track_domain_registration_started(
                domain="processing",
                payment_method=webhook_data.get('coin', 'unknown')
            )
            
            # Get order from database
            session = self.db_manager.get_session()
            try:
                order = session.query(self.db_manager.Order).filter_by(
                    order_id=order_id
                ).first()
                
                if not order:
                    logger.error(
                        "enhanced_order_not_found",
                        order_id=order_id
                    )
                    return False
                
                # Parse service data
                service_data = order.service_data or {}
                domain_name = service_data.get("domain_name")
                nameserver_choice = service_data.get("nameserver_choice", "cloudflare")
                
                if not domain_name:
                    logger.error(
                        "enhanced_domain_name_missing",
                        order_id=order_id,
                        service_data=service_data
                    )
                    return False
                
                logger.info(
                    "enhanced_domain_processing",
                    order_id=order_id,
                    domain=domain_name,
                    nameserver_choice=nameserver_choice
                )
                
                # Send status notification
                await self._notify_user_status_enhanced(
                    order.telegram_id,
                    f"🌐 Processing domain registration for {domain_name}..."
                )
                
                # Generate contact data
                contact_data = await self._generate_contact_data_async(order.telegram_id)
                
                # Use async API integration for domain creation
                result = await create_domain_with_dns(
                    domain_name=domain_name,
                    contact_data=contact_data,
                    nameserver_choice=nameserver_choice,
                    openprovider_credentials=self.openprovider_credentials,
                    cloudflare_credentials=self.cloudflare_credentials
                )
                
                if result["success"]:
                    # Store domain registration in database
                    domain_record_id = await self._store_domain_registration_enhanced(
                        order=order,
                        domain_name=domain_name,
                        domain_id=result["domain_id"],
                        cloudflare_zone_id=result["zone_id"],
                        nameservers=result["nameservers"]
                    )
                    
                    if domain_record_id:
                        # Calculate duration for metrics
                        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                        
                        # Track successful completion
                        business_metrics.track_domain_registration_completed(
                            domain_name, 
                            duration_ms
                        )
                        
                        # Send success notification
                        await self._notify_user_status_enhanced(
                            order.telegram_id,
                            f"🎉 Domain {domain_name} registered successfully!"
                        )
                        
                        # Set success flag for webhook
                        self.last_domain_registration_success = True
                        
                        logger.info(
                            "enhanced_domain_registration_completed",
                            order_id=order_id,
                            domain=domain_name,
                            domain_id=result["domain_id"],
                            cloudflare_zone_id=result["zone_id"],
                            duration_ms=duration_ms
                        )
                        
                        return True
                    else:
                        logger.error(
                            "enhanced_database_storage_failed",
                            order_id=order_id,
                            domain=domain_name
                        )
                        
                        business_metrics.track_domain_registration_failed(
                            domain_name,
                            "database_storage_failed"
                        )
                        
                        await self._notify_user_status_enhanced(
                            order.telegram_id,
                            f"⚠️ Domain {domain_name} registered but database storage failed - please contact support"
                        )
                        
                        return False
                else:
                    # Registration failed
                    error_msg = ", ".join(result.get("errors", ["Unknown error"]))
                    
                    logger.error(
                        "enhanced_domain_registration_failed",
                        order_id=order_id,
                        domain=domain_name,
                        errors=result.get("errors", [])
                    )
                    
                    business_metrics.track_domain_registration_failed(
                        domain_name,
                        "api_registration_failed"
                    )
                    
                    await self._notify_user_status_enhanced(
                        order.telegram_id,
                        f"❌ Domain {domain_name} registration failed - please contact support"
                    )
                    
                    return False
                    
            finally:
                session.close()
                
        except Exception as e:
            logger.error(
                "enhanced_domain_registration_error",
                order_id=order_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            business_metrics.track_domain_registration_failed(
                "unknown",
                f"exception_{type(e).__name__}"
            )
            
            return False
    
    async def _notify_user_status_enhanced(self, telegram_id: int, message: str):
        """Enhanced user notification with monitoring"""
        try:
            from telegram import Bot
            
            bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(
                "enhanced_user_notification_sent",
                telegram_id=telegram_id,
                message_length=len(message)
            )
            
        except Exception as e:
            logger.error(
                "enhanced_user_notification_failed",
                telegram_id=telegram_id,
                error=str(e)
            )
    
    async def _generate_contact_data_async(self, telegram_id: int) -> Dict[str, Any]:
        """Generate contact data asynchronously with monitoring"""
        try:
            # This would use the existing random contact generation
            # but wrapped in async monitoring
            
            # For now, return a basic structure
            contact_data = {
                "name": {
                    "first_name": "Domain",
                    "last_name": "Owner"
                },
                "address": {
                    "street": "123 Privacy Lane",
                    "city": "Anonymous City", 
                    "state": "CA",
                    "zipcode": "90210",
                    "country": "US"
                },
                "phone": {
                    "country_code": "+1",
                    "area_code": "555",
                    "subscriber_number": "0123456"
                },
                "email": f"privacy{telegram_id}@nomadly.domains"
            }
            
            logger.info(
                "contact_data_generated",
                telegram_id=telegram_id
            )
            
            return contact_data
            
        except Exception as e:
            logger.error(
                "contact_data_generation_failed",
                telegram_id=telegram_id,
                error=str(e)
            )
            raise
    
    async def _store_domain_registration_enhanced(
        self,
        order,
        domain_name: str,
        domain_id: str,
        cloudflare_zone_id: Optional[str],
        nameservers: list
    ) -> Optional[int]:
        """Enhanced domain storage with monitoring"""
        try:
            session = self.db_manager.get_session()
            
            try:
                # Create domain record
                domain_record = self.db_manager.RegisteredDomain(
                    telegram_id=order.telegram_id,
                    domain_name=domain_name,
                    openprovider_domain_id=domain_id,
                    cloudflare_zone_id=cloudflare_zone_id,
                    nameservers=nameservers,
                    registration_date=datetime.utcnow(),
                    expiry_date=datetime.utcnow().replace(year=datetime.utcnow().year + 1),
                    status="active",
                    payment_method=order.payment_method
                )
                
                session.add(domain_record)
                session.commit()
                
                domain_record_id = domain_record.id
                
                logger.info(
                    "enhanced_domain_stored",
                    domain_record_id=domain_record_id,
                    domain=domain_name,
                    openprovider_id=domain_id,
                    cloudflare_zone_id=cloudflare_zone_id
                )
                
                return domain_record_id
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(
                "enhanced_domain_storage_error",
                domain=domain_name,
                error=str(e)
            )
            return None

# Wrapper function to maintain compatibility with existing code
async def enhanced_complete_domain_registration(order_id: str, webhook_data: Dict[str, Any]):
    """Wrapper function for enhanced domain registration"""
    from database import get_db_manager
    
    db_manager = get_db_manager()
    enhanced_service = EnhancedPaymentService(db_manager)
    
    return await enhanced_service.complete_domain_registration_enhanced(
        order_id, 
        webhook_data
    )

if __name__ == "__main__":
    # Test the enhanced payment service
    async def test_enhanced_service():
        logger.info("testing_enhanced_payment_service")
        
        # This would test the enhanced service
        # with mock data if needed
        
        logger.info("enhanced_payment_service_test_completed")
    
    asyncio.run(test_enhanced_service())