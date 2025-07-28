"""
Middleware for Nomadly3 FastAPI Application
Authentication, logging, and request processing middleware
"""

import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging
    Tracks API usage, performance, and errors
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())[:8]
        
        # Start timing
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"in {process_time:.3f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            # Calculate processing time for errors
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"Error {request_id}: {str(e)} "
                f"in {process_time:.3f}s"
            )
            
            # Return error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "request_id": request_id
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time": f"{process_time:.3f}"
                }
            )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers
    Implements CORS, security headers, and rate limiting preparation
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "font-src 'self' data:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        # CORS headers for API access
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, Accept, Origin"
        )
        response.headers["Access-Control-Max-Age"] = "86400"
        
        return response

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Enhanced rate limiting middleware
    Prevents API abuse with user-specific and IP-based limiting
    Supports different limits for authenticated vs anonymous users
    """
    
    def __init__(self, app, 
                 authenticated_calls_per_minute: int = 120,
                 anonymous_calls_per_minute: int = 60,
                 domain_registration_calls_per_hour: int = 10):
        super().__init__(app)
        self.authenticated_limit = authenticated_calls_per_minute
        self.anonymous_limit = anonymous_calls_per_minute
        self.domain_reg_limit = domain_registration_calls_per_hour
        self.request_counts = {}  # In production, use Redis
        self.domain_reg_counts = {}  # Track domain registration attempts
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier (authenticated user or IP)
        client_identifier = self._get_client_identifier(request)
        is_authenticated = hasattr(request.state, 'telegram_id') and request.state.telegram_id
        
        # Determine rate limits based on authentication status
        calls_per_minute = self.authenticated_limit if is_authenticated else self.anonymous_limit
        
        # Current minute window
        current_minute = int(time.time() // 60)
        key = f"{client_identifier}:{current_minute}"
        
        # Clean old entries
        self._cleanup_old_entries(current_minute)
        
        # Check general rate limit
        current_count = self.request_counts.get(key, 0)
        
        if current_count >= calls_per_minute:
            logger.warning(
                f"Rate limit exceeded for {client_identifier} "
                f"({'authenticated' if is_authenticated else 'anonymous'})"
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "retry_after": 60,
                    "limit_type": "general"
                },
                headers={"Retry-After": "60"}
            )
        
        # Special rate limiting for domain registration endpoints
        if self._is_domain_registration_endpoint(request.url.path):
            domain_reg_result = self._check_domain_registration_limit(client_identifier)
            if not domain_reg_result["allowed"]:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "error": "Domain registration rate limit exceeded",
                        "retry_after": 3600,  # 1 hour
                        "limit_type": "domain_registration"
                    },
                    headers={"Retry-After": "3600"}
                )
        
        # Increment counters
        self.request_counts[key] = current_count + 1
        if self._is_domain_registration_endpoint(request.url.path):
            self._increment_domain_registration_count(client_identifier)
        
        # Process request
        response = await call_next(request)
        
        # Add enhanced rate limit headers
        response.headers["X-RateLimit-Limit"] = str(calls_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, calls_per_minute - self.request_counts[key])
        )
        response.headers["X-RateLimit-Reset"] = str((current_minute + 1) * 60)
        response.headers["X-RateLimit-Type"] = "authenticated" if is_authenticated else "anonymous"
        
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Use telegram_id if authenticated, otherwise IP
        if hasattr(request.state, 'telegram_id') and request.state.telegram_id:
            return f"user_{request.state.telegram_id}"
        return request.client.host if request.client else "unknown"
    
    def _is_domain_registration_endpoint(self, path: str) -> bool:
        """Check if endpoint is related to domain registration"""
        domain_reg_endpoints = [
            "/api/v1/domains/register",
            "/api/v1/domains/renew",
            "/api/v1/payments/initiate"
        ]
        return any(path.startswith(endpoint) for endpoint in domain_reg_endpoints)
    
    def _check_domain_registration_limit(self, client_identifier: str) -> dict:
        """Check domain registration specific rate limits"""
        current_hour = int(time.time() // 3600)
        hour_key = f"{client_identifier}:domain_reg:{current_hour}"
        
        current_count = self.domain_reg_counts.get(hour_key, 0)
        return {
            "allowed": current_count < self.domain_reg_limit,
            "current_count": current_count,
            "limit": self.domain_reg_limit
        }
    
    def _increment_domain_registration_count(self, client_identifier: str):
        """Increment domain registration counter"""
        current_hour = int(time.time() // 3600)
        hour_key = f"{client_identifier}:domain_reg:{current_hour}"
        self.domain_reg_counts[hour_key] = self.domain_reg_counts.get(hour_key, 0) + 1
    
    def _cleanup_old_entries(self, current_minute: int):
        """Remove entries older than 2 minutes"""
        cutoff = current_minute - 2
        keys_to_remove = [
            key for key in self.request_counts.keys()
            if int(key.split(':')[1]) < cutoff
        ]
        for key in keys_to_remove:
            del self.request_counts[key]

class APIVersioningMiddleware(BaseHTTPMiddleware):
    """
    API versioning middleware
    Handles API version routing and compatibility
    """
    
    def __init__(self, app, default_version: str = "v1"):
        super().__init__(app)
        self.default_version = default_version
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract version from header or URL
        api_version = request.headers.get("X-API-Version", self.default_version)
        
        # Add version to request state
        request.state.api_version = api_version
        
        # Process request
        response = await call_next(request)
        
        # Add version header to response
        response.headers["X-API-Version"] = api_version
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware
    Standardizes error responses and logging
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
            
        except HTTPException as http_exc:
            # Handle FastAPI HTTP exceptions
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            logger.warning(
                f"HTTP Exception {request_id}: {http_exc.status_code} - {http_exc.detail}"
            )
            
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "success": False,
                    "error": http_exc.detail,
                    "status_code": http_exc.status_code,
                    "request_id": request_id
                }
            )
            
        except ValueError as val_err:
            # Handle validation errors
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            logger.error(f"Validation Error {request_id}: {str(val_err)}")
            
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": "Invalid request data",
                    "details": str(val_err),
                    "request_id": request_id
                }
            )
            
        except Exception as exc:
            # Handle unexpected errors
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            logger.error(
                f"Unexpected Error {request_id}: {type(exc).__name__} - {str(exc)}",
                exc_info=True
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "request_id": request_id
                }
            )

class DatabaseMiddleware(BaseHTTPMiddleware):
    """
    Database connection middleware
    Ensures proper database session management
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Database session is handled by dependency injection
        # This middleware ensures cleanup and monitoring
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log database performance if needed
            db_time = time.time() - start_time
            if db_time > 1.0:  # Log slow database operations
                logger.warning(
                    f"Slow database operation: {request.method} {request.url.path} "
                    f"took {db_time:.3f}s"
                )
            
            return response
            
        except Exception as e:
            # Log database-related errors
            if "database" in str(e).lower() or "sql" in str(e).lower():
                logger.error(f"Database error: {str(e)}")
            raise

# Middleware configuration helper
def setup_middleware(app):
    """
    Configure all middleware for the application
    Order matters - later middleware wraps earlier ones
    
    Execution order (first to last):
    1. RequestLoggingMiddleware - logs all requests
    2. SecurityHeadersMiddleware - adds security headers and CORS
    3. RateLimitingMiddleware - enforces rate limits
    4. APIVersioningMiddleware - handles API versioning
    5. ErrorHandlingMiddleware - handles errors and exceptions
    6. DatabaseMiddleware - monitors database performance
    """
    
    # Add middleware in reverse order (last added = first executed)
    app.add_middleware(DatabaseMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(APIVersioningMiddleware, default_version="v1")
    app.add_middleware(
        RateLimitingMiddleware, 
        authenticated_calls_per_minute=120,  # 2 per second for authenticated users
        anonymous_calls_per_minute=60,       # 1 per second for anonymous users
        domain_registration_calls_per_hour=10  # Domain registration limit
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Enhanced middleware stack configured successfully")
    logger.info("Rate limits: 120/min (auth), 60/min (anon), 10/hour (domain reg)")