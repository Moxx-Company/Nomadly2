#!/usr/bin/env python3
"""
Input Sanitization Utilities for Enhanced Security
Provides comprehensive input cleaning and validation
"""

import re
import html
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Comprehensive input sanitization utility"""
    
    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML entities to prevent XSS"""
        if not isinstance(text, str):
            text = str(text)
        return html.escape(text, quote=True)
    
    @staticmethod
    def clean_input(user_input: str) -> str:
        """Clean and sanitize user input"""
        if not isinstance(user_input, str):
            user_input = str(user_input)
        
        # Strip whitespace
        cleaned = user_input.strip()
        
        # Remove null bytes
        cleaned = cleaned.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        cleaned = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
        
        # Limit length
        if len(cleaned) > 5000:
            cleaned = cleaned[:5000]
            logger.warning(f"Input truncated to 5000 characters")
        
        return cleaned
    
    @staticmethod
    def sanitize_domain_input(domain: str) -> str:
        """Sanitize domain name input"""
        if not isinstance(domain, str):
            domain = str(domain)
        
        # Clean basic input
        domain = InputSanitizer.clean_input(domain)
        
        # Convert to lowercase
        domain = domain.lower()
        
        # Remove any protocols
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'^ftp://', '', domain)
        
        # Remove trailing slashes and paths
        domain = domain.split('/')[0]
        
        # Remove invalid characters for domains
        domain = re.sub(r'[^a-z0-9.-]', '', domain)
        
        return domain
    
    @staticmethod
    def sanitize_ip_input(ip: str) -> str:
        """Sanitize IP address input"""
        if not isinstance(ip, str):
            ip = str(ip)
        
        # Clean basic input
        ip = InputSanitizer.clean_input(ip)
        
        # Remove any @ symbol (common in DNS records)
        ip = ip.replace('@', '').strip()
        
        # Only allow numbers, dots, and colons (IPv4/IPv6)
        ip = re.sub(r'[^0-9.:]', '', ip)
        
        return ip
    
    @staticmethod
    def sanitize_email_input(email: str) -> str:
        """Sanitize email address input"""
        if not isinstance(email, str):
            email = str(email)
        
        # Clean basic input
        email = InputSanitizer.clean_input(email)
        
        # Convert to lowercase
        email = email.lower()
        
        # Only allow valid email characters
        email = re.sub(r'[^a-z0-9@._+-]', '', email)
        
        return email
    
    @staticmethod
    def prevent_command_injection(command_input: str) -> str:
        """Prevent command injection by removing dangerous characters"""
        if not isinstance(command_input, str):
            command_input = str(command_input)
        
        # Remove dangerous command characters
        dangerous_chars = ['&', '|', ';', '$', '`', '(', ')', '{', '}', '[', ']', '<', '>', '\\']
        for char in dangerous_chars:
            command_input = command_input.replace(char, '')
        
        return command_input
    
    @staticmethod
    def safe_string_format(template: str, **kwargs) -> str:
        """Safe string formatting to prevent injection"""
        try:
            # Sanitize all string values
            safe_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    safe_kwargs[key] = InputSanitizer.escape_html(value)
                else:
                    safe_kwargs[key] = value
            
            return template.format(**safe_kwargs)
        except Exception as e:
            logger.error(f"Safe string formatting error: {e}")
            return template


# Global sanitizer instance
_input_sanitizer = InputSanitizer()


def get_input_sanitizer():
    """Get the global input sanitizer instance"""
    return _input_sanitizer


def clean_input(text: str) -> str:
    """Quick access to input cleaning"""
    return _input_sanitizer.clean_input(text)


def escape_html(text: str) -> str:
    """Quick access to HTML escaping"""
    return _input_sanitizer.escape_html(text)


def sanitize_domain(domain: str) -> str:
    """Quick access to domain sanitization"""
    return _input_sanitizer.sanitize_domain_input(domain)


def sanitize_ip(ip: str) -> str:
    """Quick access to IP sanitization"""
    return _input_sanitizer.sanitize_ip_input(ip)


def sanitize_email(email: str) -> str:
    """Quick access to email sanitization"""
    return _input_sanitizer.sanitize_email_input(email)