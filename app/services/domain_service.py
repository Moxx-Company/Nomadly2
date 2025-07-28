"""
Domain Service for Nomadly3 - Business Logic Layer
Pure Python layer handling domain registration business logic
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field

from ..repositories.domain_repo import DomainRepository
from ..repositories.user_repo import UserRepository
from ..repositories.external_integration_repo import (
    OpenProviderIntegrationRepository, CloudflareIntegrationRepository
)
from ..models.openprovider_models import OpenProviderContact
from ..core.config import config

logger = logging.getLogger(__name__)

@dataclass
class DomainAvailabilityResult:
    """Result of domain availability check"""
    domain: str
    available: bool
    price: Optional[Decimal] = None
    premium: bool = False
    error: Optional[str] = None
    alternative_suggestions: List[str] = field(default_factory=list)

@dataclass
class DomainRegistrationRequest:
    """Domain registration request data"""
    domain_name: str
    telegram_id: int
    nameserver_mode: str  # 'cloudflare' or 'custom'
    custom_nameservers: Optional[List[str]] = None
    technical_email: Optional[str] = None
    auto_renew: bool = True
    registration_period: int = 1  # years

@dataclass
class DomainExpiryAlert:
    """Domain expiry alert data"""
    domain_id: int
    domain_name: str
    expires_at: datetime
    days_until_expiry: int
    user_telegram_id: int
    user_email: Optional[str]
    alert_type: str  # 'warning', 'urgent', 'expired'

class DomainService:
    """Service for domain-related business logic"""
    
    def __init__(self, db_session, domain_repo=None, user_repo=None,
                 openprovider_repo=None, cloudflare_repo=None):
        """Initialize with dependency injection flexibility"""
        if domain_repo:
            self.domain_repo = domain_repo
        else:
            self.domain_repo = DomainRepository(db_session)
            
        if user_repo:
            self.user_repo = user_repo
        else:
            self.user_repo = UserRepository(db_session)
            
        self.openprovider_repo = openprovider_repo or OpenProviderIntegrationRepository()
        self.cloudflare_repo = cloudflare_repo or CloudflareIntegrationRepository()
        
        # Business logic constants
        self.OFFSHORE_PRICE_MULTIPLIER = Decimal('3.3')
        self.MIN_DOMAIN_LENGTH = 2
        self.MAX_DOMAIN_LENGTH = 63
        self.SUPPORTED_TLDS = ['.com', '.net', '.org', '.info', '.biz', '.me', '.co', '.io']
        self.EXPIRY_WARNING_DAYS = [30, 15, 7, 3, 1]  # Days before expiry to send alerts
    
    # Domain Availability Checks
    
    def check_domain_availability(self, domain_name: str) -> DomainAvailabilityResult:
        """
        Check if domain is available for registration
        Pure business logic for domain validation and availability
        """
        try:
            # Validate domain format
            validation_error = self._validate_domain_format(domain_name)
            if validation_error:
                return DomainAvailabilityResult(
                    domain=domain_name,
                    available=False,
                    error=validation_error
                )
            
            # Check if domain already exists in our system
            existing_domain = self.domain_repo.get_by_domain_name(domain_name)
            if existing_domain:
                return DomainAvailabilityResult(
                    domain=domain_name,
                    available=False,
                    error="Domain already registered in our system"
                )
            
            # Calculate pricing with offshore multiplier
            base_price = self._get_base_domain_price(domain_name)
            offshore_price = base_price * self.OFFSHORE_PRICE_MULTIPLIER
            
            # Generate alternative suggestions if premium
            is_premium = self._is_premium_domain(domain_name)
            alternatives = self._generate_domain_alternatives(domain_name) if is_premium else []
            
            return DomainAvailabilityResult(
                domain=domain_name,
                available=True,
                price=offshore_price,
                premium=is_premium,
                alternative_suggestions=alternatives
            )
            
        except Exception as e:
            logger.error(f"Error checking domain availability for {domain_name}: {e}")
            return DomainAvailabilityResult(
                domain=domain_name,
                available=False,
                error=f"Availability check failed: {str(e)}"
            )
    
    def bulk_check_availability(self, domain_names: List[str]) -> List[DomainAvailabilityResult]:
        """Check availability for multiple domains"""
        results = []
        for domain in domain_names:
            results.append(self.check_domain_availability(domain))
        return results
    
    def calculate_domain_pricing(self, domain_name: str, years: int = 1) -> Dict[str, Any]:
        """
        Calculate domain pricing with offshore multiplier
        Pure business logic method for pricing calculations
        """
        try:
            # Validate inputs
            if years < 1 or years > 10:
                return {
                    "success": False,
                    "error": "Registration period must be between 1-10 years"
                }
            
            # Get base price for domain
            base_price = self._get_base_domain_price(domain_name)
            
            # Apply offshore multiplier (3.3x)
            offshore_price = base_price * self.OFFSHORE_PRICE_MULTIPLIER
            
            # Calculate multi-year pricing
            annual_price = offshore_price
            total_price = annual_price * years
            
            # Check if premium domain
            is_premium = self._is_premium_domain(domain_name)
            
            # Calculate potential savings for multi-year
            discount_rate = Decimal('0.05') if years >= 3 else Decimal('0.02') if years >= 2 else Decimal('0.00')
            discount_amount = total_price * discount_rate
            final_price = total_price - discount_amount
            
            return {
                "success": True,
                "domain_name": domain_name,
                "base_price_usd": float(base_price),
                "offshore_multiplier": float(self.OFFSHORE_PRICE_MULTIPLIER),
                "annual_price_usd": float(annual_price),
                "registration_years": years,
                "subtotal_usd": float(total_price),
                "discount_rate": float(discount_rate),
                "discount_amount_usd": float(discount_amount),
                "total_price_usd": float(final_price),
                "is_premium": is_premium,
                "currency": "USD",
                "offshore_hosting_optimized": True
            }
            
        except Exception as e:
            logger.error(f"Error calculating domain pricing for {domain_name}: {e}")
            return {
                "success": False,
                "error": f"Pricing calculation failed: {str(e)}"
            }
    
    # Domain Registration Business Logic
    
    def prepare_domain_registration(self, request: DomainRegistrationRequest) -> Dict[str, Any]:
        """
        Prepare domain registration with all business validations
        Returns registration preparation result
        """
        try:
            # Validate user exists and has sufficient balance
            user = self.user_repo.get_by_telegram_id(request.telegram_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Check domain availability
            availability = self.check_domain_availability(request.domain_name)
            if not availability.available:
                return {"success": False, "error": availability.error}
            
            # Validate user balance
            if availability.price and not user.has_sufficient_balance(availability.price):
                return {
                    "success": False,
                    "error": f"Insufficient balance. Required: ${availability.price}, Available: ${user.balance_usd}"
                }
            
            # Calculate expiry date
            expiry_date = self._calculate_expiry_date(request.registration_period)
            
            # Validate nameserver configuration
            nameserver_validation = self._validate_nameserver_config(
                request.nameserver_mode, 
                request.custom_nameservers
            )
            if not nameserver_validation["valid"]:
                return {"success": False, "error": nameserver_validation["error"]}
            
            return {
                "success": True,
                "domain_name": request.domain_name,
                "price": availability.price,
                "expiry_date": expiry_date,
                "user_id": user.telegram_id,
                "nameserver_mode": request.nameserver_mode,
                "custom_nameservers": request.custom_nameservers,
                "technical_email": request.technical_email,
                "registration_period": request.registration_period
            }
            
        except Exception as e:
            logger.error(f"Error preparing domain registration: {e}")
            return {"success": False, "error": f"Registration preparation failed: {str(e)}"}
    
    def process_domain_registration(self, preparation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process domain registration after payment confirmation
        """
        try:
            # Create domain registration record
            domain = self.domain_repo.create_domain(
                telegram_id=preparation_data["user_id"],
                domain_name=preparation_data["domain_name"],
                expires_at=preparation_data["expiry_date"],
                price_paid=preparation_data["price"],
                nameserver_mode=preparation_data["nameserver_mode"],
                payment_method="crypto"
            )
            
            if not domain:
                return {"success": False, "error": "Failed to create domain record"}
            
            # Set custom nameservers if provided
            if preparation_data.get("custom_nameservers"):
                self.domain_repo.update_nameservers(
                    domain.id,
                    preparation_data["custom_nameservers"],
                    "custom"
                )
            
            logger.info(f"Domain registered successfully: {domain.domain_name} for user {domain.telegram_id}")
            
            return {
                "success": True,
                "domain_id": domain.id,
                "domain_name": domain.domain_name,
                "expires_at": domain.expires_at,
                "nameserver_mode": domain.nameserver_mode
            }
            
        except Exception as e:
            logger.error(f"Error processing domain registration: {e}")
            return {"success": False, "error": f"Registration processing failed: {str(e)}"}
    
    # Expiry Date Calculation
    
    def _calculate_expiry_date(self, registration_period: int) -> datetime:
        """Calculate domain expiry date based on registration period"""
        return datetime.utcnow() + timedelta(days=365 * registration_period)
    
    def calculate_renewal_expiry(self, current_expiry: datetime, renewal_period: int) -> datetime:
        """Calculate new expiry date for domain renewal"""
        return current_expiry + timedelta(days=365 * renewal_period)
    
    def get_days_until_expiry(self, domain_id: int) -> Optional[int]:
        """Get days until domain expires"""
        domain = self.domain_repo.get_by_id(domain_id)
        if domain:
            return domain.days_until_expiry
        return None
    
    # Domain Expiry Management & Email Alerts
    
    def get_expiring_domains_for_alerts(self) -> List[DomainExpiryAlert]:
        """
        Get domains that need expiry alerts sent
        Business logic for determining which domains need alerts
        """
        alerts = []
        
        for warning_days in self.EXPIRY_WARNING_DAYS:
            expiring_domains = self.domain_repo.get_expiring_domains(warning_days)
            
            for domain in expiring_domains:
                days_left = domain.days_until_expiry
                if days_left is not None and days_left == warning_days:
                    alert_type = self._determine_alert_type(days_left)
                    
                    alerts.append(DomainExpiryAlert(
                        domain_id=int(domain.id),
                        domain_name=str(domain.domain_name),
                        expires_at=domain.expires_at,
                        days_until_expiry=days_left,
                        user_telegram_id=int(domain.telegram_id),
                        user_email=getattr(domain, 'technical_email', None),
                        alert_type=alert_type
                    ))
        
        return alerts
    
    def _determine_alert_type(self, days_until_expiry: int) -> str:
        """Determine alert type based on days until expiry"""
        if days_until_expiry <= 0:
            return "expired"
        elif days_until_expiry <= 3:
            return "urgent"
        else:
            return "warning"
    
    def mark_expired_domains(self) -> int:
        """Mark expired domains and return count"""
        return self.domain_repo.mark_expired_domains()
    
    # Domain Renewal Business Logic
    
    def prepare_domain_renewal(self, domain_id: int, renewal_period: int = 1) -> Dict[str, Any]:
        """Prepare domain renewal with business validations"""
        try:
            domain = self.domain_repo.get_by_id(domain_id)
            if not domain:
                return {"success": False, "error": "Domain not found"}
            
            if str(domain.status) != "active":
                return {"success": False, "error": "Cannot renew inactive domain"}
            
            # Calculate renewal price and new expiry
            renewal_price = self._get_base_domain_price(str(domain.domain_name)) * self.OFFSHORE_PRICE_MULTIPLIER
            new_expiry = self.calculate_renewal_expiry(domain.expires_at, renewal_period)
            
            # Check user balance
            user = self.user_repo.get_by_telegram_id(int(domain.telegram_id))
            if not user or not user.has_sufficient_balance(renewal_price):
                return {
                    "success": False,
                    "error": f"Insufficient balance for renewal. Required: ${renewal_price}"
                }
            
            return {
                "success": True,
                "domain_id": domain_id,
                "domain_name": domain.domain_name,
                "current_expiry": domain.expires_at,
                "new_expiry": new_expiry,
                "renewal_price": renewal_price,
                "renewal_period": renewal_period
            }
            
        except Exception as e:
            logger.error(f"Error preparing domain renewal: {e}")
            return {"success": False, "error": f"Renewal preparation failed: {str(e)}"}
    
    async def renew_domain(self, domain_id: int, renewal_years: int = 1) -> dict:
        """Renew domain registration"""
        try:
            # Get domain info
            domain = await self.domain_repo.get_by_id(domain_id)
            if not domain:
                raise Exception("Domain not found")
            
            # Calculate renewal price
            renewal_price = await self.calculate_renewal_price(domain.domain_name, renewal_years)
            
            # Process renewal with OpenProvider
            renewal_result = await self.openprovider_api.renew_domain(
                domain.openprovider_domain_id,
                renewal_years
            )
            
            # Update domain expiry
            new_expiry = domain.expires_at + timedelta(days=365 * renewal_years)
            await self.domain_repo.update_domain_expiry(domain_id, new_expiry)
            
            return {
                "success": True,
                "domain_name": domain.domain_name,
                "renewed_years": renewal_years,
                "new_expiry": new_expiry,
                "cost": renewal_price
            }
            
        except Exception as e:
            logger.error(f"Domain renewal failed: {e}")
            raise Exception(f"Could not renew domain: {str(e)}")
    
    async def calculate_renewal_price(self, domain_name: str, years: int = 1) -> float:
        """Calculate domain renewal price"""
        try:
            # Extract TLD
            tld = domain_name.split('.')[-1]
            
            # Base pricing (simplified)
            base_prices = {
                'com': 15.00,
                'net': 18.00,
                'org': 16.00,
                'info': 12.00,
                'biz': 14.00
            }
            
            base_price = base_prices.get(tld, 20.00)  # Default price
            offshore_multiplier = 3.3  # Offshore premium
            
            return base_price * offshore_multiplier * years
            
        except Exception as e:
            logger.error(f"Price calculation failed: {e}")
            return 50.00  # Default fallback price
    
    async def validate_domain_format(self, domain_name: str) -> bool:
        """Validate domain name format"""
        import re
        
        # Domain format validation regex
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,})$'
        
        if not re.match(domain_pattern, domain_name):
            return False
        
        # Check for valid TLD
        tld = domain_name.split('.')[-1].lower()
        valid_tlds = ['com', 'net', 'org', 'info', 'biz', 'me', 'co', 'io']
        
        return tld in valid_tlds
    
    def process_domain_renewal(self, domain_id: int, new_expiry_date: datetime, price_paid: Decimal) -> bool:
        """Process domain renewal after payment"""
        return self.domain_repo.renew_domain(domain_id, new_expiry_date, price_paid)
    
    # Domain Portfolio Management
    
    def get_user_domain_portfolio(self, telegram_id: int) -> Dict[str, Any]:
        """Get comprehensive user domain portfolio with analytics"""
        try:
            user = self.user_repo.get_by_telegram_id(telegram_id)
            if not user:
                return {"error": "User not found"}
            
            domains = self.domain_repo.get_user_domains(telegram_id)
            
            # Calculate portfolio analytics
            total_domains = len(domains)
            active_domains = len([d for d in domains if d.is_active])
            expired_domains = len([d for d in domains if d.is_expired])
            expiring_soon = len([d for d in domains if d.days_until_expiry and d.days_until_expiry <= 30])
            
            # Group domains by status
            domains_by_status = {
                "active": [d for d in domains if d.is_active],
                "expired": [d for d in domains if d.is_expired],
                "suspended": [d for d in domains if str(d.status) == "suspended"]
            }
            
            return {
                "user_id": telegram_id,
                "portfolio_stats": {
                    "total_domains": total_domains,
                    "active_domains": active_domains,
                    "expired_domains": expired_domains,
                    "expiring_soon": expiring_soon
                },
                "domains_by_status": domains_by_status,
                "domains": domains
            }
            
        except Exception as e:
            logger.error(f"Error getting user domain portfolio: {e}")
            return {"error": f"Portfolio retrieval failed: {str(e)}"}
    
    # Domain Validation Helpers
    
    def _validate_domain_format(self, domain_name: str) -> Optional[str]:
        """Validate domain name format - returns error message if invalid"""
        if not domain_name:
            return "Domain name cannot be empty"
        
        # Check length
        if len(domain_name) < self.MIN_DOMAIN_LENGTH:
            return f"Domain name too short (minimum {self.MIN_DOMAIN_LENGTH} characters)"
        
        if len(domain_name) > self.MAX_DOMAIN_LENGTH:
            return f"Domain name too long (maximum {self.MAX_DOMAIN_LENGTH} characters)"
        
        # Check for valid TLD
        has_valid_tld = any(domain_name.lower().endswith(tld) for tld in self.SUPPORTED_TLDS)
        if not has_valid_tld:
            return f"Unsupported TLD. Supported: {', '.join(self.SUPPORTED_TLDS)}"
        
        # Check domain format with regex
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        if not re.match(domain_pattern, domain_name):
            return "Invalid domain format"
        
        return None
    
    def _validate_nameserver_config(self, mode: str, custom_nameservers: Optional[List[str]]) -> Dict[str, Any]:
        """Validate nameserver configuration"""
        if mode not in ["cloudflare", "custom"]:
            return {"valid": False, "error": "Invalid nameserver mode"}
        
        if mode == "custom":
            if not custom_nameservers or len(custom_nameservers) < 2:
                return {"valid": False, "error": "Custom mode requires at least 2 nameservers"}
            
            # Validate nameserver format
            for ns in custom_nameservers:
                if not self._is_valid_nameserver(ns):
                    return {"valid": False, "error": f"Invalid nameserver format: {ns}"}
        
        return {"valid": True}
    
    def _is_valid_nameserver(self, nameserver: str) -> bool:
        """Validate individual nameserver format"""
        ns_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        return bool(re.match(ns_pattern, nameserver))
    
    def _get_base_domain_price(self, domain_name: str) -> Decimal:
        """Get base price for domain (before offshore multiplier)"""
        # Business logic for pricing based on TLD
        tld = '.' + domain_name.split('.')[-1].lower()
        
        base_prices = {
            '.com': Decimal('15.00'),
            '.net': Decimal('18.00'),
            '.org': Decimal('16.00'),
            '.info': Decimal('12.00'),
            '.biz': Decimal('14.00'),
            '.me': Decimal('25.00'),
            '.co': Decimal('30.00'),
            '.io': Decimal('35.00')
        }
        
        return base_prices.get(tld, Decimal('15.00'))  # Default price
    
    def _is_premium_domain(self, domain_name: str) -> bool:
        """Determine if domain is premium based on business rules"""
        domain_part = domain_name.split('.')[0].lower()
        
        # Premium indicators
        if len(domain_part) <= 3:  # Short domains are premium
            return True
        
        premium_keywords = ['crypto', 'bitcoin', 'finance', 'money', 'bank', 'trade']
        if any(keyword in domain_part for keyword in premium_keywords):
            return True
        
        return False
    
    def _generate_domain_alternatives(self, domain_name: str) -> List[str]:
        """Generate alternative domain suggestions"""
        domain_part = domain_name.split('.')[0]
        tld = '.' + domain_name.split('.')[-1]
        
        alternatives = []
        
        # Try different TLDs
        for alt_tld in ['.net', '.org', '.info', '.biz']:
            if alt_tld != tld:
                alternatives.append(f"{domain_part}{alt_tld}")
        
        # Try domain variations
        variations = [
            f"{domain_part}app{tld}",
            f"{domain_part}pro{tld}",
            f"my{domain_part}{tld}",
            f"get{domain_part}{tld}"
        ]
        
        alternatives.extend(variations)
        return alternatives[:5]  # Return top 5 suggestions