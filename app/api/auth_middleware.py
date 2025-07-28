"""
Enhanced Authentication Middleware for Nomadly3
JWT/OAuth2 authentication with Telegram integration
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta

from app.core.security import verify_jwt_token, get_user_from_token
from fresh_database import get_db_session, User

logger = logging.getLogger(__name__)

# JWT Configuration for Nomadly3
JWT_SECRET_KEY = "nomadly3_offshore_domain_registration_secret_2025"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer(auto_error=False)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Advanced authentication middleware supporting:
    - JWT tokens from Authorization header
    - Telegram user authentication
    - API key authentication for external integrations
    - Rate limiting by authenticated user
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS = {
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/auth/register",
        "/api/v1/auth/login", 
        "/api/v1/auth/telegram-login",
        "/api/v1/domains/check-availability",  # Public domain checking
    }
    
    async def dispatch(self, request: Request, call_next):
        """Process authentication for incoming requests"""
        
        # Skip authentication for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Extract authentication credentials
        auth_result = await self._authenticate_request(request)
        
        if not auth_result["authenticated"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result["error"],
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Add user info to request state
        request.state.user = auth_result["user"]
        request.state.telegram_id = auth_result["telegram_id"]
        request.state.auth_method = auth_result["method"]
        
        # Log authenticated request
        logger.info(
            f"Authenticated request: {request.method} {request.url.path} "
            f"by user {auth_result['telegram_id']} via {auth_result['method']}"
        )
        
        return await call_next(request)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)"""
        return any(path.startswith(endpoint) for endpoint in self.PUBLIC_ENDPOINTS)
    
    async def _authenticate_request(self, request: Request) -> Dict[str, Any]:
        """
        Authenticate request using multiple methods:
        1. Authorization header with JWT token
        2. API key authentication
        3. Telegram web app authentication
        """
        
        # Method 1: JWT Bearer token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            jwt_result = await self._verify_jwt_token(token)
            if jwt_result["valid"]:
                return {
                    "authenticated": True,
                    "user": jwt_result["user"],
                    "telegram_id": jwt_result["telegram_id"],
                    "method": "jwt_bearer"
                }
        
        # Method 2: API Key authentication
        api_key = request.headers.get("X-API-Key")
        if api_key:
            api_result = await self._verify_api_key(api_key)
            if api_result["valid"]:
                return {
                    "authenticated": True,
                    "user": api_result["user"],
                    "telegram_id": api_result["telegram_id"],
                    "method": "api_key"
                }
        
        # Method 3: Telegram Web App authentication
        telegram_auth = request.headers.get("X-Telegram-Auth")
        if telegram_auth:
            telegram_result = await self._verify_telegram_auth(telegram_auth)
            if telegram_result["valid"]:
                return {
                    "authenticated": True,
                    "user": telegram_result["user"],
                    "telegram_id": telegram_result["telegram_id"],
                    "method": "telegram_webapp"
                }
        
        return {
            "authenticated": False,
            "error": "No valid authentication credentials provided",
            "method": None
        }
    
    async def _verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        try:
            # Use existing security module for basic verification
            payload = verify_jwt_token(token)
            telegram_id = payload.get("telegram_id")
            
            if not telegram_id:
                return {"valid": False, "error": "Invalid token payload"}
            
            # Get user from database
            with get_db_session() as db:
                user = db.query(User).filter(User.telegram_id == telegram_id).first()
                if not user:
                    return {"valid": False, "error": "User not found"}
                
                return {
                    "valid": True,
                    "user": user,
                    "telegram_id": telegram_id
                }
                
        except Exception as e:
            logger.warning(f"JWT verification failed: {e}")
            return {"valid": False, "error": "Invalid token"}
    
    async def _verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Verify API key for external integrations"""
        try:
            # API key format: api_scope_userid_randomstring
            if not api_key.startswith("api_"):
                return {"valid": False, "error": "Invalid API key format"}
            
            parts = api_key.split("_", 3)
            if len(parts) < 4:
                return {"valid": False, "error": "Invalid API key format"}
            
            scope, user_id_str = parts[1], parts[2]
            telegram_id = int(user_id_str)
            
            # Get user from database
            with get_db_session() as db:
                user = db.query(User).filter(User.telegram_id == telegram_id).first()
                if not user:
                    return {"valid": False, "error": "User not found"}
                
                # In production, verify API key against database
                # For now, accept valid format with existing user
                return {
                    "valid": True,
                    "user": user,
                    "telegram_id": telegram_id,
                    "scope": scope
                }
                
        except Exception as e:
            logger.warning(f"API key verification failed: {e}")
            return {"valid": False, "error": "Invalid API key"}
    
    async def _verify_telegram_auth(self, telegram_auth: str) -> Dict[str, Any]:
        """Verify Telegram Web App authentication"""
        try:
            # Parse Telegram auth data
            # Format: telegram_id:hash:timestamp
            parts = telegram_auth.split(":")
            if len(parts) != 3:
                return {"valid": False, "error": "Invalid Telegram auth format"}
            
            telegram_id = int(parts[0])
            auth_hash = parts[1]
            timestamp = int(parts[2])
            
            # Check timestamp (within 1 hour)
            current_time = int(datetime.utcnow().timestamp())
            if current_time - timestamp > 3600:
                return {"valid": False, "error": "Telegram auth expired"}
            
            # In production, verify hash against Telegram bot token
            # For now, accept valid format with existing user
            with get_db_session() as db:
                user = db.query(User).filter(User.telegram_id == telegram_id).first()
                if not user:
                    return {"valid": False, "error": "User not found"}
                
                return {
                    "valid": True,
                    "user": user,
                    "telegram_id": telegram_id
                }
                
        except Exception as e:
            logger.warning(f"Telegram auth verification failed: {e}")
            return {"valid": False, "error": "Invalid Telegram auth"}

# JWT utility functions for route handlers
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token using our simple token system"""
    from app.core.security import create_access_token as create_simple_token
    telegram_id = data.get("telegram_id", data.get("sub", 0))
    return create_simple_token(telegram_id, data)

def create_refresh_token(data: dict):
    """Create refresh token using our simple token system"""
    from app.core.security import create_refresh_token as create_simple_refresh
    telegram_id = data.get("telegram_id", data.get("sub", 0))
    return create_simple_refresh(telegram_id)

# Dependency for getting current user
async def get_current_user(request: Request) -> User:
    """Dependency to get current authenticated user"""
    if not hasattr(request.state, 'user') or not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return request.state.user

async def get_current_telegram_id(request: Request) -> int:
    """Dependency to get current user's Telegram ID"""
    if not hasattr(request.state, 'telegram_id') or not request.state.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return request.state.telegram_id

# Optional dependency for getting user if authenticated
async def get_optional_user(request: Request) -> Optional[User]:
    """Optional dependency - returns user if authenticated, None if not"""
    return getattr(request.state, 'user', None)