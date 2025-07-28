"""
Email Service for Nomadly3 - Business Logic Layer
Pure Python layer handling email alert business logic
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..repositories.user_repo import UserRepository
from ..repositories.domain_repo import DomainRepository
from ..repositories.external_integration_repo import (
    BrevoIntegrationRepository, TelegramIntegrationRepository
)
from ..core.config import config

logger = logging.getLogger(__name__)

class EmailAlertType(Enum):
    """Email alert type enumeration"""
    DOMAIN_EXPIRY_WARNING = "domain_expiry_warning"
    DOMAIN_EXPIRY_URGENT = "domain_expiry_urgent"
    DOMAIN_EXPIRED = "domain_expired"
    PAYMENT_RECEIVED = "payment_received"
    DOMAIN_REGISTERED = "domain_registered"
    WALLET_CREDITED = "wallet_credited"

@dataclass
class EmailRequest:
    """Email sending request"""
    recipient_email: str
    recipient_name: Optional[str]
    template_type: EmailAlertType
    template_data: Dict[str, Any]
    telegram_id: int
    priority: str = "normal"  # normal, high, urgent

@dataclass
class EmailSendResult:
    """Result of email sending operation"""
    success: bool
    email_id: Optional[str] = None
    error: Optional[str] = None
    delivery_status: str = "pending"

class EmailService:
    """Service for email-related business logic"""
    
    def __init__(self, user_repo: UserRepository, domain_repo: DomainRepository,
                 brevo_repo: BrevoIntegrationRepository = None,
                 telegram_repo: TelegramIntegrationRepository = None):
        self.user_repo = user_repo
        self.domain_repo = domain_repo
        self.brevo_repo = brevo_repo or BrevoIntegrationRepository()
        self.telegram_repo = telegram_repo or TelegramIntegrationRepository()
        
        # Email business logic constants
        self.FROM_EMAIL = "noreply@nomadly.offshore"
        self.FROM_NAME = "Nomadly Offshore Domains"
        self.MAX_RETRY_ATTEMPTS = 3
        self.EMAIL_RATE_LIMIT_PER_USER = 10  # Per day
        
    # Domain Expiry Email Alerts
    
    def send_domain_expiry_alerts(self) -> Dict[str, Any]:
        """
        Send domain expiry alerts to users
        Business logic for determining and sending expiry notifications
        """
        try:
            sent_count = 0
            failed_count = 0
            
            # Get domains expiring in warning periods
            warning_periods = [30, 15, 7, 3, 1]  # Days
            
            for days_ahead in warning_periods:
                expiring_domains = self.domain_repo.get_expiring_domains(days_ahead)
                
                for domain in expiring_domains:
                    # Check if user has email
                    user = self.user_repo.get_by_telegram_id(int(domain.telegram_id))
                    if not user or not getattr(user, 'email', None):
                        continue
                    
                    # Determine alert type
                    alert_type = self._determine_expiry_alert_type(days_ahead)
                    
                    # Prepare email data
                    email_data = {
                        "domain_name": str(domain.domain_name),
                        "expires_at": domain.expires_at,
                        "days_until_expiry": days_ahead,
                        "renewal_url": f"https://nomadly.offshore/renew/{domain.id}",
                        "user_name": getattr(user, 'first_name', 'Valued Customer')
                    }
                    
                    # Send email
                    email_request = EmailRequest(
                        recipient_email=str(user.email),
                        recipient_name=getattr(user, 'first_name', None),
                        template_type=alert_type,
                        template_data=email_data,
                        telegram_id=int(domain.telegram_id),
                        priority="high" if days_ahead <= 3 else "normal"
                    )
                    
                    result = self.send_email(email_request)
                    if result.success:
                        sent_count += 1
                    else:
                        failed_count += 1
                        logger.error(f"Failed to send expiry alert for {domain.domain_name}: {result.error}")
            
            return {
                "success": True,
                "alerts_sent": sent_count,
                "alerts_failed": failed_count,
                "message": f"Domain expiry alerts processed: {sent_count} sent, {failed_count} failed"
            }
            
        except Exception as e:
            logger.error(f"Error sending domain expiry alerts: {e}")
            return {"success": False, "error": f"Alert processing failed: {str(e)}"}
    
    def _determine_expiry_alert_type(self, days_until_expiry: int) -> EmailAlertType:
        """Determine email alert type based on days until expiry"""
        if days_until_expiry <= 0:
            return EmailAlertType.DOMAIN_EXPIRED
        elif days_until_expiry <= 3:
            return EmailAlertType.DOMAIN_EXPIRY_URGENT
        else:
            return EmailAlertType.DOMAIN_EXPIRY_WARNING
    
    # Payment Confirmation Emails
    
    def send_payment_confirmation(self, telegram_id: int, payment_data: Dict[str, Any]) -> EmailSendResult:
        """
        Send payment confirmation email
        """
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user or not getattr(user, 'email', None):
                return EmailSendResult(
                    success=False,
                    error="User not found or no email address"
                )
            
            # Prepare email data
            email_data = {
                "payment_amount": payment_data.get("amount", "0.00"),
                "cryptocurrency": payment_data.get("cryptocurrency", "Unknown"),
                "service_description": payment_data.get("service", "Domain Registration"),
                "transaction_id": payment_data.get("transaction_id", "N/A"),
                "user_name": getattr(user, 'first_name', 'Valued Customer'),
                "payment_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            email_request = EmailRequest(
                recipient_email=str(user.email),
                recipient_name=getattr(user, 'first_name', None),
                template_type=EmailAlertType.PAYMENT_RECEIVED,
                template_data=email_data,
                telegram_id=telegram_id
            )
            
            return self.send_email(email_request)
            
        except Exception as e:
            logger.error(f"Error sending payment confirmation: {e}")
            return EmailSendResult(
                success=False,
                error=f"Payment confirmation failed: {str(e)}"
            )
    
    # Domain Registration Confirmation
    
    def send_domain_registration_confirmation(self, telegram_id: int, domain_data: Dict[str, Any]) -> EmailSendResult:
        """
        Send domain registration confirmation email
        """
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user or not getattr(user, 'email', None):
                return EmailSendResult(
                    success=False,
                    error="User not found or no email address"
                )
            
            # Prepare email data
            email_data = {
                "domain_name": domain_data.get("domain_name", "Unknown"),
                "expires_at": domain_data.get("expires_at", datetime.utcnow()),
                "nameserver_mode": domain_data.get("nameserver_mode", "cloudflare"),
                "registration_price": domain_data.get("price", "0.00"),
                "user_name": getattr(user, 'first_name', 'Valued Customer'),
                "management_url": f"https://nomadly.offshore/domains/{domain_data.get('domain_id')}",
                "registration_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            email_request = EmailRequest(
                recipient_email=str(user.email),
                recipient_name=getattr(user, 'first_name', None),
                template_type=EmailAlertType.DOMAIN_REGISTERED,
                template_data=email_data,
                telegram_id=telegram_id,
                priority="high"
            )
            
            return self.send_email(email_request)
            
        except Exception as e:
            logger.error(f"Error sending domain registration confirmation: {e}")
            return EmailSendResult(
                success=False,
                error=f"Registration confirmation failed: {str(e)}"
            )
    
    # Wallet Credit Notifications
    
    def send_wallet_credit_notification(self, telegram_id: int, credit_data: Dict[str, Any]) -> EmailSendResult:
        """
        Send wallet credit notification email
        """
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user or not getattr(user, 'email', None):
                return EmailSendResult(
                    success=False,
                    error="User not found or no email address"
                )
            
            # Prepare email data
            email_data = {
                "credited_amount": credit_data.get("amount", "0.00"),
                "previous_balance": credit_data.get("previous_balance", "0.00"),
                "new_balance": credit_data.get("new_balance", "0.00"),
                "credit_reason": credit_data.get("reason", "Overpayment refund"),
                "user_name": getattr(user, 'first_name', 'Valued Customer'),
                "credit_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            email_request = EmailRequest(
                recipient_email=str(user.email),
                recipient_name=getattr(user, 'first_name', None),
                template_type=EmailAlertType.WALLET_CREDITED,
                template_data=email_data,
                telegram_id=telegram_id
            )
            
            return self.send_email(email_request)
            
        except Exception as e:
            logger.error(f"Error sending wallet credit notification: {e}")
            return EmailSendResult(
                success=False,
                error=f"Wallet credit notification failed: {str(e)}"
            )
    
    # Core Email Sending Logic
    
    def send_email(self, request: EmailRequest) -> EmailSendResult:
        """
        Send email with business logic validation
        """
        try:
            # Validate rate limiting
            if not self._check_rate_limit(request.telegram_id):
                return EmailSendResult(
                    success=False,
                    error="Email rate limit exceeded for user"
                )
            
            # Validate email format
            if not self._is_valid_email(request.recipient_email):
                return EmailSendResult(
                    success=False,
                    error="Invalid email address format"
                )
            
            # Generate email content
            email_content = self._generate_email_content(request.template_type, request.template_data)
            if not email_content:
                return EmailSendResult(
                    success=False,
                    error="Failed to generate email content"
                )
            
            # This would integrate with actual email service (Brevo, SendGrid, etc.)
            # For business logic structure, implementing the interface
            email_id = self._send_via_email_provider(
                to_email=request.recipient_email,
                to_name=request.recipient_name,
                subject=email_content["subject"],
                html_content=email_content["html"],
                priority=request.priority
            )
            
            if email_id:
                # Record email sending for rate limiting
                self._record_email_sent(request.telegram_id)
                
                return EmailSendResult(
                    success=True,
                    email_id=email_id,
                    delivery_status="sent"
                )
            else:
                return EmailSendResult(
                    success=False,
                    error="Email provider failed to send"
                )
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return EmailSendResult(
                success=False,
                error=f"Email sending failed: {str(e)}"
            )
    
    def _generate_email_content(self, template_type: EmailAlertType, data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Generate email content based on template type"""
        templates = {
            EmailAlertType.DOMAIN_EXPIRY_WARNING: {
                "subject": f"⚠️ Domain {data.get('domain_name')} expires in {data.get('days_until_expiry')} days",
                "html": self._generate_expiry_warning_html(data)
            },
            EmailAlertType.DOMAIN_EXPIRY_URGENT: {
                "subject": f"🚨 URGENT: Domain {data.get('domain_name')} expires in {data.get('days_until_expiry')} days",
                "html": self._generate_expiry_urgent_html(data)
            },
            EmailAlertType.DOMAIN_EXPIRED: {
                "subject": f"❌ Domain {data.get('domain_name')} has expired",
                "html": self._generate_domain_expired_html(data)
            },
            EmailAlertType.PAYMENT_RECEIVED: {
                "subject": f"✅ Payment received - ${data.get('payment_amount')} {data.get('cryptocurrency')}",
                "html": self._generate_payment_confirmation_html(data)
            },
            EmailAlertType.DOMAIN_REGISTERED: {
                "subject": f"🏴‍☠️ Domain registered successfully - {data.get('domain_name')}",
                "html": self._generate_registration_confirmation_html(data)
            },
            EmailAlertType.WALLET_CREDITED: {
                "subject": f"💰 Wallet credited - ${data.get('credited_amount')}",
                "html": self._generate_wallet_credit_html(data)
            }
        }
        
        return templates.get(template_type)
    
    def _generate_expiry_warning_html(self, data: Dict[str, Any]) -> str:
        """Generate domain expiry warning email HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #001f3f; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #003d7a; padding: 30px; border-radius: 10px;">
                <h1 style="color: #00d4aa; margin-bottom: 20px;">🏴‍☠️ Nomadly Offshore Domains</h1>
                <h2 style="color: #ffffff;">Domain Expiry Notice</h2>
                <p>Dear {data.get('user_name', 'Valued Customer')},</p>
                <p>Your domain <strong>{data.get('domain_name')}</strong> will expire in <strong>{data.get('days_until_expiry')} days</strong> on {data.get('expires_at', '').strftime('%Y-%m-%d') if data.get('expires_at') else 'N/A'}.</p>
                <p>To ensure uninterrupted service, please renew your domain before the expiration date.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{data.get('renewal_url', '#')}" style="background-color: #00d4aa; color: #001f3f; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Renew Domain</a>
                </div>
                <p style="font-size: 12px; color: #cccccc; margin-top: 30px;">
                    Resilience | Discretion | Independence<br>
                    This is an automated message from Nomadly Offshore Domains.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _generate_expiry_urgent_html(self, data: Dict[str, Any]) -> str:
        """Generate urgent domain expiry email HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #4a0e0e; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #8b0000; padding: 30px; border-radius: 10px; border: 2px solid #ff6b6b;">
                <h1 style="color: #ff6b6b; margin-bottom: 20px;">🏴‍☠️ Nomadly Offshore Domains</h1>
                <h2 style="color: #ffffff;">🚨 URGENT: Domain Expiring Soon</h2>
                <p>Dear {data.get('user_name', 'Valued Customer')},</p>
                <p><strong>URGENT ACTION REQUIRED:</strong> Your domain <strong>{data.get('domain_name')}</strong> will expire in <strong>{data.get('days_until_expiry')} days</strong>.</p>
                <p style="color: #ff6b6b; font-weight: bold;">Failure to renew will result in domain suspension and potential loss.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{data.get('renewal_url', '#')}" style="background-color: #ff6b6b; color: #ffffff; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; animation: blink 1s infinite;">RENEW NOW</a>
                </div>
                <p style="font-size: 12px; color: #cccccc; margin-top: 30px;">
                    Resilience | Discretion | Independence<br>
                    This is an automated urgent message from Nomadly Offshore Domains.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _generate_domain_expired_html(self, data: Dict[str, Any]) -> str:
        """Generate domain expired email HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #2c2c2c; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #404040; padding: 30px; border-radius: 10px;">
                <h1 style="color: #ff9999; margin-bottom: 20px;">🏴‍☠️ Nomadly Offshore Domains</h1>
                <h2 style="color: #ffffff;">❌ Domain Expired</h2>
                <p>Dear {data.get('user_name', 'Valued Customer')},</p>
                <p>Your domain <strong>{data.get('domain_name')}</strong> has expired and may be suspended.</p>
                <p>Contact support immediately to recover your domain before it becomes available for re-registration.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://t.me/nomadly_support" style="background-color: #ff9999; color: #2c2c2c; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Contact Support</a>
                </div>
                <p style="font-size: 12px; color: #cccccc; margin-top: 30px;">
                    Resilience | Discretion | Independence<br>
                    This is an automated message from Nomadly Offshore Domains.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _generate_payment_confirmation_html(self, data: Dict[str, Any]) -> str:
        """Generate payment confirmation email HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0f3460; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #16537e; padding: 30px; border-radius: 10px;">
                <h1 style="color: #00d4aa; margin-bottom: 20px;">🏴‍☠️ Nomadly Offshore Domains</h1>
                <h2 style="color: #ffffff;">✅ Payment Confirmed</h2>
                <p>Dear {data.get('user_name', 'Valued Customer')},</p>
                <p>We have successfully received your payment of <strong>${data.get('payment_amount')} {data.get('cryptocurrency')}</strong> for {data.get('service_description')}.</p>
                <div style="background-color: #0f3460; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Transaction Details:</strong></p>
                    <p>Amount: ${data.get('payment_amount')} {data.get('cryptocurrency')}</p>
                    <p>Service: {data.get('service_description')}</p>
                    <p>Transaction ID: {data.get('transaction_id', 'N/A')}</p>
                    <p>Date: {data.get('payment_date')}</p>
                </div>
                <p>Your service will be processed shortly. You will receive another confirmation once complete.</p>
                <p style="font-size: 12px; color: #cccccc; margin-top: 30px;">
                    Resilience | Discretion | Independence<br>
                    This is an automated message from Nomadly Offshore Domains.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _generate_registration_confirmation_html(self, data: Dict[str, Any]) -> str:
        """Generate domain registration confirmation email HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #001f3f; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #003d7a; padding: 30px; border-radius: 10px;">
                <h1 style="color: #00d4aa; margin-bottom: 20px;">🏴‍☠️ Nomadly Offshore Domains</h1>
                <h2 style="color: #ffffff;">🎉 Domain Registered Successfully!</h2>
                <p>Dear {data.get('user_name', 'Valued Customer')},</p>
                <p>Congratulations! Your domain <strong>{data.get('domain_name')}</strong> has been successfully registered.</p>
                <div style="background-color: #001f3f; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Registration Details:</strong></p>
                    <p>Domain: {data.get('domain_name')}</p>
                    <p>Expires: {data.get('expires_at', '').strftime('%Y-%m-%d') if data.get('expires_at') else 'N/A'}</p>
                    <p>Nameservers: {data.get('nameserver_mode', 'Cloudflare').title()}</p>
                    <p>Price: ${data.get('registration_price')}</p>
                    <p>Registered: {data.get('registration_date')}</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{data.get('management_url', '#')}" style="background-color: #00d4aa; color: #001f3f; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Manage Domain</a>
                </div>
                <p>Your domain is now active and ready for use. You can manage DNS records, nameservers, and other settings through your dashboard.</p>
                <p style="font-size: 12px; color: #cccccc; margin-top: 30px;">
                    Resilience | Discretion | Independence<br>
                    Welcome to the Nomadly Offshore family!
                </p>
            </div>
        </body>
        </html>
        """
    
    def _generate_wallet_credit_html(self, data: Dict[str, Any]) -> str:
        """Generate wallet credit notification email HTML"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0a4d3a; color: #ffffff; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #0f5f4a; padding: 30px; border-radius: 10px;">
                <h1 style="color: #00d4aa; margin-bottom: 20px;">🏴‍☠️ Nomadly Offshore Domains</h1>
                <h2 style="color: #ffffff;">💰 Wallet Credited</h2>
                <p>Dear {data.get('user_name', 'Valued Customer')},</p>
                <p>Your wallet has been credited with <strong>${data.get('credited_amount')}</strong>.</p>
                <div style="background-color: #0a4d3a; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Credit Details:</strong></p>
                    <p>Amount Credited: ${data.get('credited_amount')}</p>
                    <p>Previous Balance: ${data.get('previous_balance')}</p>
                    <p>New Balance: ${data.get('new_balance')}</p>
                    <p>Reason: {data.get('credit_reason')}</p>
                    <p>Date: {data.get('credit_date')}</p>
                </div>
                <p>This credit can be used for future domain registrations, renewals, and DNS services.</p>
                <p style="font-size: 12px; color: #cccccc; margin-top: 30px;">
                    Resilience | Discretion | Independence<br>
                    This is an automated message from Nomadly Offshore Domains.
                </p>
            </div>
        </body>
        </html>
        """
    
    # Email Validation and Rate Limiting
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _check_rate_limit(self, telegram_id: int) -> bool:
        """Check if user has exceeded email rate limit"""
        # This would integrate with actual rate limiting storage
        # For business logic structure, implementing the interface
        return True  # Would check against actual rate limit data
    
    def _record_email_sent(self, telegram_id: int) -> None:
        """Record email sent for rate limiting purposes"""
        # This would record in actual rate limiting storage
        pass
    
    def _send_via_email_provider(self, to_email: str, to_name: Optional[str], 
                                 subject: str, html_content: str, priority: str) -> Optional[str]:
        """Send email via actual email provider (Brevo, SendGrid, etc.)"""
        # This would integrate with actual email service
        # For business logic structure, implementing the interface
        logger.info(f"Email would be sent to {to_email}: {subject}")
        return f"email_{datetime.utcnow().timestamp()}"  # Mock email ID
    
    # Email Analytics
    
    def get_email_statistics(self, telegram_id: Optional[int] = None) -> Dict[str, Any]:
        """Get email sending statistics"""
        try:
            # This would integrate with actual email tracking
            # For business logic structure, implementing the interface
            
            if telegram_id:
                user = self.user_repo.get_by_telegram_id(telegram_id)
                if not user:
                    return {"error": "User not found"}
                
                return {
                    "user_id": telegram_id,
                    "emails_sent_today": 0,  # Would be from actual tracking
                    "emails_sent_total": 0,  # Would be from actual tracking
                    "rate_limit_remaining": self.EMAIL_RATE_LIMIT_PER_USER,
                    "last_email_sent": None  # Would be from actual tracking
                }
            else:
                return {
                    "total_emails_sent_today": 0,  # Would be from actual tracking
                    "total_emails_sent": 0,  # Would be from actual tracking
                    "delivery_rate": 0.95,  # Would be calculated from actual data
                    "bounce_rate": 0.02  # Would be calculated from actual data
                }
                
        except Exception as e:
            logger.error(f"Error getting email statistics: {e}")
            return {"error": f"Statistics retrieval failed: {str(e)}"}