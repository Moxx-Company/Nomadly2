"""
Enhanced Input Validation System for Nomadly2
Provides comprehensive validation for all user inputs and API parameters
"""

import re
import ipaddress
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class InputValidator:
    """Comprehensive input validation system"""
    
    # Regular expressions for common patterns
    DOMAIN_PATTERN = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    PHONE_PATTERN = re.compile(
        r'^\+?[1-9]\d{1,14}$'  # E.164 format
    )
    
    CRYPTO_ADDRESS_PATTERNS = {
        'bitcoin': re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$'),
        'ethereum': re.compile(r'^0x[a-fA-F0-9]{40}$'),
        'litecoin': re.compile(r'^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$'),
        'dogecoin': re.compile(r'^D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$'),
    }
    
    @staticmethod
    def validate_domain(domain: str, allow_subdomains: bool = True) -> bool:
        """Validate domain name format"""
        if not domain or not isinstance(domain, str):
            return False
        
        domain = domain.lower().strip()
        
        if len(domain) > 253:
            return False
        
        if not allow_subdomains:
            # Only allow second-level domains
            parts = domain.split('.')
            if len(parts) != 2:
                return False
        
        return bool(InputValidator.DOMAIN_PATTERN.match(domain))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            return False
        
        email = email.lower().strip()
        
        if len(email) > 320:  # RFC 5321 limit
            return False
        
        return bool(InputValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove spaces and common separators
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        return bool(InputValidator.PHONE_PATTERN.match(cleaned_phone))
    
    @staticmethod
    def validate_ip_address(ip: str, version: Optional[int] = None) -> bool:
        """Validate IP address (IPv4 or IPv6)"""
        if not ip or not isinstance(ip, str):
            return False
        
        try:
            ip_obj = ipaddress.ip_address(ip.strip())
            
            if version == 4:
                return isinstance(ip_obj, ipaddress.IPv4Address)
            elif version == 6:
                return isinstance(ip_obj, ipaddress.IPv6Address)
            
            return True  # Valid IPv4 or IPv6
            
        except ValueError:
            return False
    
    @staticmethod
    def validate_crypto_address(address: str, currency: str) -> bool:
        """Validate cryptocurrency address format"""
        if not address or not isinstance(address, str):
            return False
        
        currency = currency.lower()
        pattern = InputValidator.CRYPTO_ADDRESS_PATTERNS.get(currency)
        
        if not pattern:
            logger.warning(f"No validation pattern for currency: {currency}")
            return len(address.strip()) > 20  # Basic length check
        
        return bool(pattern.match(address.strip()))
    
    @staticmethod
    def validate_dns_record_content(record_type: str, content: str) -> bool:
        """Validate DNS record content based on record type"""
        if not content or not isinstance(content, str):
            return False
        
        content = content.strip()
        record_type = record_type.upper()
        
        if record_type == 'A':
            return InputValidator.validate_ip_address(content, version=4)
        
        elif record_type == 'AAAA':
            return InputValidator.validate_ip_address(content, version=6)
        
        elif record_type == 'CNAME':
            return InputValidator.validate_domain(content)
        
        elif record_type == 'MX':
            # Format: "priority domain" or just "domain"
            parts = content.split()
            if len(parts) == 2:
                try:
                    priority = int(parts[0])
                    return 0 <= priority <= 65535 and InputValidator.validate_domain(parts[1])
                except ValueError:
                    return False
            elif len(parts) == 1:
                return InputValidator.validate_domain(parts[0])
            return False
        
        elif record_type == 'TXT':
            # TXT records can contain almost anything, but check reasonable limits
            return len(content) <= 255
        
        elif record_type == 'NS':
            return InputValidator.validate_domain(content)
        
        else:
            logger.warning(f"Unknown DNS record type for validation: {record_type}")
            return True  # Allow unknown types
    
    @staticmethod
    def validate_ttl(ttl: Union[str, int]) -> bool:
        """Validate DNS TTL value"""
        try:
            ttl_int = int(ttl)
            return 60 <= ttl_int <= 604800  # 1 minute to 1 week
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255, 
                       allow_special_chars: bool = True) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes and control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
        
        # Remove HTML/XML tags
        value = re.sub(r'<[^>]+>', '', value)
        
        # Remove potentially dangerous characters if not allowed
        if not allow_special_chars:
            value = re.sub(r'[<>"\'\&]', '', value)
        
        # Truncate to max length
        if len(value) > max_length:
            value = value[:max_length]
        
        return value.strip()
    
    @staticmethod
    def validate_order_id(order_id: str) -> bool:
        """Validate order ID format"""
        if not order_id or not isinstance(order_id, str):
            return False
        
        # Order IDs should be alphanumeric with optional hyphens/underscores
        pattern = re.compile(r'^[a-zA-Z0-9_-]{8,50}$')
        return bool(pattern.match(order_id))
    
    @staticmethod
    def validate_telegram_id(telegram_id: Union[str, int]) -> bool:
        """Validate Telegram user ID"""
        try:
            tid = int(telegram_id)
            return 1 <= tid <= 9999999999  # Reasonable Telegram ID range
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_amount(amount: Union[str, int, float], min_amount: float = 0.01, 
                       max_amount: float = 10000.00) -> bool:
        """Validate monetary amount"""
        try:
            amount_float = float(amount)
            return min_amount <= amount_float <= max_amount
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_json_payload(payload: Any, required_fields: List[str] = None) -> bool:
        """Validate JSON payload structure"""
        if not isinstance(payload, dict):
            return False
        
        if required_fields:
            for field in required_fields:
                if field not in payload:
                    return False
        
        return True

class SecurityValidator:
    """Security-focused input validation"""
    
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bunion\b.*\bselect\b)",
        r"(\bor\b.*=.*\bor\b)",
        r"(\band\b.*=.*\band\b)"
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>"
    ]
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """Check for potential SQL injection patterns"""
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return True
        
        return False
    
    @staticmethod
    def check_xss_attempt(value: str) -> bool:
        """Check for potential XSS patterns"""
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        
        for pattern in SecurityValidator.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"Potential XSS detected: {pattern}")
                return True
        
        return False
    
    @staticmethod
    def is_safe_input(value: str) -> bool:
        """Comprehensive safety check for user input"""
        if SecurityValidator.check_sql_injection(value):
            return False
        
        if SecurityValidator.check_xss_attempt(value):
            return False
        
        # Check for excessive length (potential DoS)
        if len(value) > 10000:
            logger.warning(f"Excessively long input detected: {len(value)} characters")
            return False
        
        return True

def validate_user_input(input_type: str, value: Any, **kwargs) -> Dict[str, Any]:
    """
    Main validation function that returns detailed validation results
    
    Args:
        input_type: Type of input to validate (domain, email, phone, etc.)
        value: The value to validate
        **kwargs: Additional validation parameters
    
    Returns:
        Dict with 'valid' boolean and optional 'error' message
    """
    try:
        # Security check first
        if isinstance(value, str) and not SecurityValidator.is_safe_input(value):
            return {
                'valid': False,
                'error': 'Input contains potentially unsafe content',
                'error_code': 'SECURITY_VIOLATION'
            }
        
        # Type-specific validation
        if input_type == 'domain':
            valid = InputValidator.validate_domain(value, kwargs.get('allow_subdomains', True))
            error = 'Invalid domain format' if not valid else None
        
        elif input_type == 'email':
            valid = InputValidator.validate_email(value)
            error = 'Invalid email format' if not valid else None
        
        elif input_type == 'phone':
            valid = InputValidator.validate_phone(value)
            error = 'Invalid phone number format' if not valid else None
        
        elif input_type == 'ip_address':
            valid = InputValidator.validate_ip_address(value, kwargs.get('version'))
            error = 'Invalid IP address format' if not valid else None
        
        elif input_type == 'crypto_address':
            currency = kwargs.get('currency', '')
            valid = InputValidator.validate_crypto_address(value, currency)
            error = f'Invalid {currency} address format' if not valid else None
        
        elif input_type == 'dns_record':
            record_type = kwargs.get('record_type', 'A')
            valid = InputValidator.validate_dns_record_content(record_type, value)
            error = f'Invalid {record_type} record content' if not valid else None
        
        elif input_type == 'ttl':
            valid = InputValidator.validate_ttl(value)
            error = 'TTL must be between 60 and 604800 seconds' if not valid else None
        
        elif input_type == 'order_id':
            valid = InputValidator.validate_order_id(value)
            error = 'Invalid order ID format' if not valid else None
        
        elif input_type == 'telegram_id':
            valid = InputValidator.validate_telegram_id(value)
            error = 'Invalid Telegram ID' if not valid else None
        
        elif input_type == 'amount':
            min_amt = kwargs.get('min_amount', 0.01)
            max_amt = kwargs.get('max_amount', 10000.00)
            valid = InputValidator.validate_amount(value, min_amt, max_amt)
            error = f'Amount must be between {min_amt} and {max_amt}' if not valid else None
        
        else:
            return {
                'valid': False,
                'error': f'Unknown input type: {input_type}',
                'error_code': 'UNKNOWN_TYPE'
            }
        
        result = {'valid': valid}
        if error:
            result['error'] = error
            result['error_code'] = 'VALIDATION_FAILED'
        
        return result
        
    except Exception as e:
        logger.error(f"Validation error for {input_type}: {e}")
        return {
            'valid': False,
            'error': 'Validation system error',
            'error_code': 'SYSTEM_ERROR'
        }