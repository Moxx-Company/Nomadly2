"""
Enhanced CORS Middleware for Nomadly3
Comprehensive CORS handling for domain registration API
"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class EnhancedCORSMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware for Nomadly3 domain registration API
    Supports multiple origins, preflight handling, and secure headers
    """
    
    # Allowed origins for domain registration API
    PRODUCTION_ORIGINS = [
        "https://nomadly.offshore",
        "https://app.nomadly.offshore", 
        "https://admin.nomadly.offshore",
    ]
    
    DEVELOPMENT_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://*.replit.dev",
        "https://*.replit.app",
    ]
    
    # Telegram Web App origins
    TELEGRAM_ORIGINS = [
        "https://web.telegram.org",
        "https://webk.telegram.org",
        "https://webz.telegram.org",
        "tg://resolve",
    ]
    
    def __init__(self, app, allow_development: bool = True):
        super().__init__(app)
        self.allowed_origins = self.PRODUCTION_ORIGINS.copy()
        
        if allow_development:
            self.allowed_origins.extend(self.DEVELOPMENT_ORIGINS)
        
        # Always allow Telegram Web App origins for bot integration
        self.allowed_origins.extend(self.TELEGRAM_ORIGINS)
        
        logger.info(f"CORS configured with {len(self.allowed_origins)} allowed origins")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle CORS for incoming requests"""
        
        origin = request.headers.get("origin")
        
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            return self._handle_preflight(request, origin or "")
        
        # Process the actual request
        response = await call_next(request)
        
        # Add CORS headers to response
        self._add_cors_headers(response, origin or "")
        
        return response
    
    def _handle_preflight(self, request: Request, origin: str) -> JSONResponse:
        """Handle CORS preflight OPTIONS requests"""
        
        # Check if origin is allowed
        if not self._is_origin_allowed(origin):
            logger.warning(f"CORS preflight blocked for origin: {origin}")
            return JSONResponse(
                status_code=403,
                content={"error": "CORS policy violation"},
                headers={"Access-Control-Allow-Origin": "null"}
            )
        
        # Get requested method and headers
        requested_method = request.headers.get("access-control-request-method")
        requested_headers = request.headers.get("access-control-request-headers", "")
        
        # Validate requested method
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        if requested_method and requested_method not in allowed_methods:
            return JSONResponse(
                status_code=405,
                content={"error": "Method not allowed"},
                headers={"Access-Control-Allow-Origin": origin}
            )
        
        # Create preflight response
        preflight_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(allowed_methods),
            "Access-Control-Allow-Headers": self._get_allowed_headers(requested_headers),
            "Access-Control-Max-Age": "86400",  # 24 hours
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers"
        }
        
        logger.info(f"CORS preflight approved for {origin} - method: {requested_method}")
        
        return JSONResponse(
            status_code=200,
            content={"status": "preflight_ok"},
            headers=preflight_headers
        )
    
    def _add_cors_headers(self, response: Response, origin: str):
        """Add CORS headers to response"""
        
        if not self._is_origin_allowed(origin):
            # Don't add CORS headers for disallowed origins
            return
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Expose-Headers"] = (
            "X-Request-ID, X-Process-Time, X-RateLimit-Limit, "
            "X-RateLimit-Remaining, X-RateLimit-Reset, X-API-Version"
        )
        response.headers["Vary"] = "Origin"
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if not origin:
            return False
        
        # Check exact matches
        if origin in self.allowed_origins:
            return True
        
        # Check wildcard patterns for Replit domains
        if any(pattern in self.allowed_origins for pattern in ["*.replit.dev", "*.replit.app"]):
            if origin.endswith(".replit.dev") or origin.endswith(".replit.app"):
                return True
        
        return False
    
    def _get_allowed_headers(self, requested_headers: str) -> str:
        """Get allowed headers for CORS"""
        
        # Standard allowed headers for domain registration API
        standard_headers = [
            "Content-Type",
            "Authorization", 
            "X-Requested-With",
            "X-API-Key",
            "X-Telegram-Auth",
            "X-API-Version",
            "Accept",
            "Origin",
            "DNT",
            "User-Agent",
            "Cache-Control",
            "Keep-Alive"
        ]
        
        # Add any specifically requested headers that are safe
        if requested_headers:
            requested_list = [h.strip() for h in requested_headers.split(",")]
            safe_requested = [h for h in requested_list if self._is_header_safe(h)]
            standard_headers.extend(safe_requested)
        
        return ", ".join(set(standard_headers))  # Remove duplicates
    
    def _is_header_safe(self, header: str) -> bool:
        """Check if a requested header is safe to allow"""
        header_lower = header.lower()
        
        # Block potentially dangerous headers
        blocked_headers = [
            "host", "connection", "upgrade", "sec-", "proxy-",
            "x-forwarded-", "x-real-ip", "x-original"
        ]
        
        return not any(blocked in header_lower for blocked in blocked_headers)

def setup_cors(app):
    """
    Setup CORS for the FastAPI application
    This is called during app initialization
    """
    
    # Use FastAPI's built-in CORS middleware for simpler cases
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://nomadly.offshore",
            "https://app.nomadly.offshore",
            "https://admin.nomadly.offshore",
            "http://localhost:3000",
            "http://localhost:8000",
            "https://web.telegram.org",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-API-Key", 
            "X-Telegram-Auth",
            "X-Requested-With",
            "Accept",
            "Origin"
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Process-Time", 
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-API-Version"
        ]
    )
    
    logger.info("CORS middleware configured for domain registration API")