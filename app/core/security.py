"""
Security module for Nomadly3 API
Simple authentication utilities that work with fresh database
"""

import os
import hashlib
import secrets
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a simple token (compatible with JWT expectations)"""
    telegram_id = data.get("telegram_id", 0)
    timestamp = str(int(datetime.utcnow().timestamp()))
    token_data = f"{telegram_id}:{timestamp}"
    return secrets.token_urlsafe(32) + ":" + token_data

def create_access_token(telegram_id: int, additional_data: Optional[Dict[str, Any]] = None) -> str:
    """Create a simple access token for a user"""
    data = {"telegram_id": telegram_id}
    if additional_data:
        data.update(additional_data)
    return create_jwt_token(data)

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Simple token verification"""
    try:
        # Split token to extract telegram_id
        if ":" in token:
            parts = token.split(":")
            if len(parts) >= 3:
                telegram_id = int(parts[-2])
                timestamp = int(parts[-1])
                
                # Check if token is not expired (24 hours)
                current_time = int(datetime.utcnow().timestamp())
                if current_time - timestamp < 86400:  # 24 hours
                    return {"telegram_id": telegram_id}
        
        raise ValueError("Invalid token")
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise ValueError("Invalid token")

def create_refresh_token(telegram_id: int) -> str:
    """Create a refresh token for a user"""
    return create_access_token(telegram_id)

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_user_from_token(token: str) -> Optional[int]:
    """Extract telegram_id from a valid token"""
    try:
        payload = verify_jwt_token(token)
        return payload.get("telegram_id")
    except ValueError:
        return None

def is_token_expired(token: str) -> bool:
    """Check if a token is expired without raising an exception"""
    try:
        verify_jwt_token(token)
        return False
    except ValueError as e:
        return "expired" in str(e).lower()

def create_api_key(user_id: int, scope: str = "full") -> str:
    """Create an API key for external integrations"""
    return f"api_{scope}_{user_id}_{secrets.token_urlsafe(16)}"

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(64)

def validate_domain_input(domain: str) -> bool:
    """Validate domain name input"""
    import re
    # Basic domain validation
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain.lower()))

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    import re
    # Keep only alphanumeric, spaces, dots, hyphens, underscores
    return re.sub(r'[^\w\s.-]', '', text)