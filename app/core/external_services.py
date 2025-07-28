"""
External Service Integration Interfaces for Nomadly3
Core layer interfaces for all external service integrations
"""

import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

# Cloudflare DNS Management Interface
class CloudflareServiceInterface(ABC):
    """Interface for Cloudflare DNS management operations"""
    
    @abstractmethod
    async def create_zone(self, domain_name: str, account_id: str = None) -> Dict[str, Any]:
        """Create a new DNS zone in Cloudflare"""
        pass
    
    @abstractmethod
    async def get_zone_nameservers(self, zone_id: str) -> List[str]:
        """Get nameservers for a Cloudflare zone"""
        pass
    
    @abstractmethod
    async def create_dns_record(self, zone_id: str, record_type: str, name: str, 
                               content: str, ttl: int = 1, priority: int = None) -> Dict[str, Any]:
        """Create a DNS record in Cloudflare zone"""
        pass
    
    @abstractmethod
    async def update_dns_record(self, zone_id: str, record_id: str, 
                               updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a DNS record in Cloudflare zone"""
        pass
    
    @abstractmethod
    async def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """Delete a DNS record from Cloudflare zone"""
        pass
    
    @abstractmethod
    async def list_dns_records(self, zone_id: str, record_type: str = None) -> List[Dict[str, Any]]:
        """List DNS records in a Cloudflare zone"""
        pass

# OpenProvider Domain Registration Interface
class OpenProviderServiceInterface(ABC):
    """Interface for OpenProvider domain registration operations"""
    
    @abstractmethod
    async def check_domain_availability(self, domain_name: str) -> Dict[str, Any]:
        """Check if domain is available for registration"""
        pass
    
    @abstractmethod
    async def create_contact(self, contact_data: Dict[str, Any]) -> str:
        """Create contact handle for domain registration"""
        pass
    
    @abstractmethod
    async def register_domain(self, domain_name: str, contact_handle: str, 
                             period: int = 1, nameservers: List[str] = None) -> Dict[str, Any]:
        """Register a domain with OpenProvider"""
        pass
    
    @abstractmethod
    async def update_nameservers(self, domain_id: str, nameservers: List[str]) -> Dict[str, Any]:
        """Update nameservers for a domain"""
        pass
    
    @abstractmethod
    async def get_domain_info(self, domain_id: str) -> Dict[str, Any]:
        """Get domain information from OpenProvider"""
        pass
    
    @abstractmethod
    async def renew_domain(self, domain_id: str, period: int = 1) -> Dict[str, Any]:
        """Renew a domain registration"""
        pass

# FastForex Currency Conversion Interface
class FastForexServiceInterface(ABC):
    """Interface for FastForex currency conversion operations"""
    
    @abstractmethod
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get current exchange rate between currencies"""
        pass
    
    @abstractmethod
    async def convert_amount(self, amount: Decimal, from_currency: str, 
                            to_currency: str) -> Dict[str, Any]:
        """Convert amount from one currency to another"""
        pass
    
    @abstractmethod
    async def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        pass

# Brevo Email Service Interface
class BrevoServiceInterface(ABC):
    """Interface for Brevo email service operations"""
    
    @abstractmethod
    async def send_transactional_email(self, to_email: str, to_name: str, 
                                      template_id: int, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send transactional email using Brevo template"""
        pass
    
    @abstractmethod
    async def send_email(self, to_email: str, to_name: str, subject: str, 
                        html_content: str, sender_email: str = None, 
                        sender_name: str = None) -> Dict[str, Any]:
        """Send custom email via Brevo"""
        pass
    
    @abstractmethod
    async def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """Get delivery status of sent email"""
        pass
    
    @abstractmethod
    async def create_template(self, template_name: str, subject: str, 
                             html_content: str) -> Dict[str, Any]:
        """Create email template in Brevo"""
        pass

# Telegram Bot Notification Interface
class TelegramServiceInterface(ABC):
    """Interface for Telegram bot notification operations"""
    
    @abstractmethod
    async def send_message(self, chat_id: int, text: str, 
                          reply_markup: Any = None, parse_mode: str = "HTML") -> Dict[str, Any]:
        """Send message to Telegram user"""
        pass
    
    @abstractmethod
    async def send_notification(self, user_id: int, notification_type: str, 
                               data: Dict[str, Any]) -> Dict[str, Any]:
        """Send structured notification to user"""
        pass
    
    @abstractmethod
    async def edit_message(self, chat_id: int, message_id: int, text: str, 
                          reply_markup: Any = None) -> Dict[str, Any]:
        """Edit existing message"""
        pass
    
    @abstractmethod
    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete message"""
        pass

# External Service Manager
class ExternalServiceManager:
    """Central manager for all external service integrations"""
    
    def __init__(self):
        self.cloudflare: Optional[CloudflareServiceInterface] = None
        self.openprovider: Optional[OpenProviderServiceInterface] = None
        self.fastforex: Optional[FastForexServiceInterface] = None
        self.brevo: Optional[BrevoServiceInterface] = None
        self.telegram: Optional[TelegramServiceInterface] = None
    
    def register_cloudflare(self, service: CloudflareServiceInterface):
        """Register Cloudflare service implementation"""
        self.cloudflare = service
        logger.info("Cloudflare service registered")
    
    def register_openprovider(self, service: OpenProviderServiceInterface):
        """Register OpenProvider service implementation"""
        self.openprovider = service
        logger.info("OpenProvider service registered")
    
    def register_fastforex(self, service: FastForexServiceInterface):
        """Register FastForex service implementation"""
        self.fastforex = service
        logger.info("FastForex service registered")
    
    def register_brevo(self, service: BrevoServiceInterface):
        """Register Brevo service implementation"""
        self.brevo = service
        logger.info("Brevo service registered")
    
    def register_telegram(self, service: TelegramServiceInterface):
        """Register Telegram service implementation"""
        self.telegram = service
        logger.info("Telegram service registered")
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get status of all registered services"""
        return {
            "cloudflare": self.cloudflare is not None,
            "openprovider": self.openprovider is not None,
            "fastforex": self.fastforex is not None,
            "brevo": self.brevo is not None,
            "telegram": self.telegram is not None
        }
    
    def validate_all_services_registered(self) -> bool:
        """Validate that all required services are registered"""
        status = self.get_service_status()
        return all(status.values())

# Global service manager instance
external_services = ExternalServiceManager()