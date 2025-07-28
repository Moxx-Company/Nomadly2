#!/usr/bin/env python3
"""
Security Module for Nomadly2 Bot
Implements rate limiting, input validation, and security measures
"""

import time
import hashlib
import secrets
from typing import Dict, Optional, List
from collections import defaultdict, deque
import re
import html

class RateLimiter:
    """Rate limiting system to prevent spam and abuse"""
    
    def __init__(self):
        self.user_requests = defaultdict(deque)
        self.blocked_users = {}  # user_id: unblock_time
        
        # Rate limits
        self.max_requests_per_minute = 20
        self.max_requests_per_hour = 100
        self.block_duration = 300  # 5 minutes
    
    def is_rate_limited(self, user_id: int) -> bool:
        """Check if user is rate limited"""
        current_time = time.time()
        
        # Check if user is currently blocked
        if user_id in self.blocked_users:
            if current_time < self.blocked_users[user_id]:
                return True
            else:
                del self.blocked_users[user_id]
        
        # Clean old requests (older than 1 hour)
        user_requests = self.user_requests[user_id]
        while user_requests and current_time - user_requests[0] > 3600:
            user_requests.popleft()
        
        # Count requests in last minute and hour
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        requests_last_minute = sum(1 for req_time in user_requests if req_time > minute_ago)
        requests_last_hour = len(user_requests)
        
        # Check limits
        if requests_last_minute >= self.max_requests_per_minute:
            self.blocked_users[user_id] = current_time + self.block_duration
            return True
        
        if requests_last_hour >= self.max_requests_per_hour:
            self.blocked_users[user_id] = current_time + self.block_duration
            return True
        
        # Record this request
        user_requests.append(current_time)
        return False
    
    def get_remaining_requests(self, user_id: int) -> Dict[str, int]:
        """Get remaining requests for user"""
        current_time = time.time()
        user_requests = self.user_requests[user_id]
        
        minute_ago = current_time - 60
        requests_last_minute = sum(1 for req_time in user_requests if req_time > minute_ago)
        requests_last_hour = len(user_requests)
        
        return {
            'per_minute': max(0, self.max_requests_per_minute - requests_last_minute),
            'per_hour': max(0, self.max_requests_per_hour - requests_last_hour)
        }

class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # HTML escape
        text = html.escape(text)
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        return text[:1000]
    
    @staticmethod
    def validate_domain(domain: str) -> bool:
        """Validate domain name format"""
        if not domain or len(domain) > 253:
            return False
        
        # Domain regex pattern
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 254:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address"""
        if not ip:
            return False
        
        # IPv4 pattern
        ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        # IPv6 pattern (simplified)
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        
        return bool(re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip))
    
    @staticmethod
    def sanitize_dns_record_content(record_type: str, content: str) -> Optional[str]:
        """Sanitize DNS record content based on type"""
        if not content:
            return None
        
        content = content.strip()
        
        if record_type == 'A':
            return content if InputValidator.validate_ip_address(content) else None
        elif record_type == 'CNAME':
            return content if InputValidator.validate_domain(content) else None
        elif record_type == 'MX':
            # Format: priority domain
            parts = content.split()
            if len(parts) == 2 and parts[0].isdigit() and InputValidator.validate_domain(parts[1]):
                return content
            return None
        elif record_type == 'TXT':
            # TXT records can contain various content, just limit length
            return content[:500]
        else:
            return content[:200]

class SecurityManager:
    """Main security manager"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.admin_users = set()  # Admin user IDs
        self.suspicious_ips = set()
    
    def check_user_access(self, user_id: int) -> bool:
        """Check if user has access (not rate limited)"""
        return not self.rate_limiter.is_rate_limited(user_id)
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_users
    
    def add_admin(self, user_id: int):
        """Add admin user"""
        self.admin_users.add(user_id)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_data(self, data: str) -> str:
        """Hash sensitive data"""
        return hashlib.sha256(data.encode()).hexdigest()

# Global security manager instance
security_manager = SecurityManager()