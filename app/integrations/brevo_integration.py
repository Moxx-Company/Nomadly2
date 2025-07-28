"""
Brevo Email API Integration for Nomadly3
Complete implementation for transactional email notifications and delivery tracking
"""

import logging
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.config import config
from ..core.external_services import BrevoServiceInterface
from ..repositories.external_integration_repo import (
    BrevoIntegrationRepository, APIUsageLogRepository
)

logger = logging.getLogger(__name__)

class BrevoAPI(BrevoServiceInterface):
    """Complete Brevo API integration for email services"""
    
    def __init__(self):
        self.api_key = config.BREVO_API_KEY
        self.base_url = "https://api.brevo.com/v3"
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Repository dependencies
        self.brevo_repo = BrevoIntegrationRepository()
        self.api_usage_repo = APIUsageLogRepository()
        
        # Default sender information
        self.default_sender = {
            "email": "noreply@cloakhost.ru",
            "name": "Nameword Offshore Hosting"
        }
    
    async def send_transactional_email(self, to_email: str, to_name: str, 
                                      template_id: int, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send transactional email using Brevo template"""
        start_time = datetime.now()
        
        payload = {
            "to": [{"email": to_email, "name": to_name}],
            "templateId": template_id,
            "params": template_data
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/smtp/email",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/smtp/email",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 201:
                        message_id = response_data.get("messageId")
                        
                        # Store email integration record
                        integration = self.brevo_repo.create_email_record(
                            email_type="transactional",
                            recipient_email=to_email,
                            recipient_name=to_name,
                            brevo_message_id=message_id,
                            template_id=template_id,
                            template_data=template_data,
                            delivery_status="sent"
                        )
                        
                        logger.info(f"Successfully sent transactional email to {to_email} using template {template_id}")
                        
                        return {
                            "success": True,
                            "message_id": message_id,
                            "integration_id": integration.id,
                            "brevo_data": response_data
                        }
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error(f"Failed to send transactional email to {to_email}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "brevo_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception sending transactional email to {to_email}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def send_email(self, to_email: str, to_name: str, subject: str, 
                        html_content: str, sender_email: str = None, 
                        sender_name: str = None) -> Dict[str, Any]:
        """Send custom email via Brevo"""
        start_time = datetime.now()
        
        sender = {
            "email": sender_email or self.default_sender["email"],
            "name": sender_name or self.default_sender["name"]
        }
        
        payload = {
            "sender": sender,
            "to": [{"email": to_email, "name": to_name}],
            "subject": subject,
            "htmlContent": html_content
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/smtp/email",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/smtp/email",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 201:
                        message_id = response_data.get("messageId")
                        
                        # Store email integration record
                        integration = self.brevo_repo.create_email_record(
                            email_type="custom",
                            recipient_email=to_email,
                            recipient_name=to_name,
                            brevo_message_id=message_id,
                            subject=subject,
                            html_content=html_content,
                            sender_email=sender["email"],
                            sender_name=sender["name"],
                            delivery_status="sent"
                        )
                        
                        logger.info(f"Successfully sent custom email to {to_email}: {subject}")
                        
                        return {
                            "success": True,
                            "message_id": message_id,
                            "integration_id": integration.id,
                            "brevo_data": response_data
                        }
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error(f"Failed to send custom email to {to_email}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "brevo_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception sending custom email to {to_email}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """Get delivery status of sent email"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/smtp/statistics/events",
                    headers=self.headers,
                    params={"messageId": message_id}
                ) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        events = response_data.get("events", [])
                        if events:
                            latest_event = events[-1]  # Get most recent event
                            status = latest_event.get("event", "unknown")
                            
                            # Update integration record
                            integration = self.brevo_repo.get_by_message_id(message_id)
                            if integration:
                                self.brevo_repo.update_delivery_status(
                                    integration.id,
                                    delivery_status=status,
                                    event_data=latest_event
                                )
                            
                            logger.info(f"Email {message_id} status: {status}")
                            
                            return {
                                "success": True,
                                "message_id": message_id,
                                "status": status,
                                "events": events,
                                "brevo_data": response_data
                            }
                        else:
                            return {
                                "success": True,
                                "message_id": message_id,
                                "status": "no_events",
                                "events": []
                            }
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error(f"Failed to get email status for {message_id}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "brevo_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception getting email status for {message_id}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def create_template(self, template_name: str, subject: str, 
                             html_content: str) -> Dict[str, Any]:
        """Create email template in Brevo"""
        start_time = datetime.now()
        
        payload = {
            "templateName": template_name,
            "subject": subject,
            "sender": self.default_sender,
            "htmlContent": html_content,
            "isActive": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/smtp/templates",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/smtp/templates",
                        method="POST",
                        status=response.status,
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 201:
                        template_id = response_data.get("id")
                        
                        logger.info(f"Successfully created email template: {template_name} (ID: {template_id})")
                        
                        return {
                            "success": True,
                            "template_id": template_id,
                            "template_name": template_name,
                            "brevo_data": response_data
                        }
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error(f"Failed to create email template {template_name}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "brevo_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception creating email template {template_name}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        """Get list of email templates"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/smtp/templates",
                    headers=self.headers
                ) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status == 200:
                        templates = response_data.get("templates", [])
                        logger.info(f"Retrieved {len(templates)} email templates")
                        return templates
                    else:
                        logger.error(f"Failed to get email templates: {response_data}")
                        return []
                        
        except Exception as e:
            logger.error(f"Exception getting email templates: {str(e)}")
            return []
    
    async def send_domain_registration_confirmation(self, to_email: str, to_name: str, 
                                                   domain_name: str, registration_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send domain registration confirmation email"""
        subject = f"🏴‍☠️ Domain Registration Confirmed: {domain_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0a1a2a; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1a2f4a; padding: 30px; border-radius: 10px; border: 2px solid #2a5f8f;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #4a9eff; margin: 0;">🏴‍☠️ Nameword Offshore Hosting</h1>
                    <p style="color: #7fa8d3; margin: 5px 0;">Resilience | Discretion | Independence</p>
                </div>
                
                <h2 style="color: #4a9eff;">Domain Registration Successful!</h2>
                
                <div style="background-color: #0f1f3f; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #7fa8d3; margin-top: 0;">Registration Details</h3>
                    <p><strong>Domain:</strong> {domain_name}</p>
                    <p><strong>Registration Date:</strong> {registration_details.get('registration_date', 'N/A')}</p>
                    <p><strong>Expiry Date:</strong> {registration_details.get('expiry_date', 'N/A')}</p>
                    <p><strong>Nameservers:</strong> {', '.join(registration_details.get('nameservers', []))}</p>
                    <p><strong>Price Paid:</strong> ${registration_details.get('price_paid', 'N/A')} USD</p>
                </div>
                
                <div style="background-color: #2a4f1a; padding: 15px; border-radius: 5px; border-left: 5px solid #4a9f2a; margin: 20px 0;">
                    <h4 style="color: #7fa8d3; margin-top: 0;">Next Steps</h4>
                    <ul style="color: #ffffff;">
                        <li>Your domain is now active and ready to use</li>
                        <li>DNS records can be managed through our bot</li>
                        <li>Nameservers are configured for optimal performance</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #2a5f8f;">
                    <p style="color: #7fa8d3;">Need help? Contact our support team anytime.</p>
                    <p style="color: #4a9eff;">Nameword Offshore Hosting - Your Privacy, Our Priority</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, to_name, subject, html_content)
    
    async def send_payment_confirmation(self, to_email: str, to_name: str, 
                                       payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send payment confirmation email"""
        subject = f"💰 Payment Confirmed - ${payment_details.get('amount', 'N/A')} USD"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0a1a2a; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1a2f4a; padding: 30px; border-radius: 10px; border: 2px solid #2a5f8f;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #4a9eff; margin: 0;">🏴‍☠️ Nameword Offshore Hosting</h1>
                    <p style="color: #7fa8d3; margin: 5px 0;">Resilience | Discretion | Independence</p>
                </div>
                
                <h2 style="color: #4a9eff;">Payment Confirmed!</h2>
                
                <div style="background-color: #0f1f3f; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #7fa8d3; margin-top: 0;">Payment Details</h3>
                    <p><strong>Amount:</strong> ${payment_details.get('amount', 'N/A')} USD</p>
                    <p><strong>Currency:</strong> {payment_details.get('cryptocurrency', 'N/A').upper()}</p>
                    <p><strong>Transaction:</strong> {payment_details.get('transaction_hash', 'N/A')[:20]}...</p>
                    <p><strong>Order:</strong> {payment_details.get('order_id', 'N/A')}</p>
                    <p><strong>Status:</strong> <span style="color: #4a9f2a;">Completed</span></p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #2a5f8f;">
                    <p style="color: #7fa8d3;">Thank you for choosing Nameword Offshore Hosting!</p>
                    <p style="color: #4a9eff;">Your transaction has been processed securely.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, to_name, subject, html_content)
    
    async def _log_api_usage(self, endpoint: str, method: str, status: int,
                            request_data: Dict[str, Any] = None,
                            response_data: Dict[str, Any] = None,
                            response_time_ms: int = None):
        """Log API usage for monitoring"""
        try:
            self.api_usage_repo.log_api_call(
                service_name="brevo",
                api_endpoint=endpoint,
                http_method=method,
                response_status=status,
                request_data=request_data,
                response_data=response_data,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")