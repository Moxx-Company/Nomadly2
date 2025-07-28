"""
Main FastAPI Application for Nomadly3 API Layer
Complete FastAPI router configuration with modular structure
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .step6_middleware_integration import setup_step6_middleware, validate_step6_implementation
from .routes.auth_routes import auth_router
from .routes.domain_routes import domain_router
from .routes.dns_routes import dns_router
from .routes.payment_routes import payment_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Nomadly3 Domain Registration API",
    description="""
    ## Nomadly3 - Offshore Domain Registration Platform API
    
    A comprehensive API for enterprise-level domain registration and management with advanced security features.
    
    ### Features
    - **Domain Management**: Register, update, and manage domains with OpenProvider integration
    - **Advanced DNS**: Complete DNS record management with Cloudflare integration
    - **Geo-blocking**: Country/continent-based access control with pre-built templates
    - **Cryptocurrency Payments**: Multi-currency payment processing with BlockBee
    - **Wallet System**: User balance management and transaction tracking
    - **Security**: JWT authentication, rate limiting, and comprehensive logging
    
    ### Authentication
    All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.
    Include the token in the Authorization header: `Bearer <token>`
    """,
    version="1.0.0",
    contact={
        "name": "Nameword Offshore Services",
        "email": "api@nameword.offshore",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://nameword.offshore/license",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and token management",
        },
        {
            "name": "Domain Management", 
            "description": "Domain registration, updates, and portfolio management",
        },
        {
            "name": "DNS Management",
            "description": "DNS records, geo-blocking, and security templates",
        },
        {
            "name": "Payment Processing",
            "description": "Cryptocurrency payments, wallet management, and transactions",
        },
    ]
)

# Configure Step 6 - Complete API Middleware Layer
setup_step6_middleware(app)

# Validate Step 6 implementation
step6_validation = validate_step6_implementation()

# Include routers with proper prefixes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(domain_router, prefix="/api/v1")  
app.include_router(dns_router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    """API root endpoint with basic information"""
    return {
        "success": True,
        "message": "Nomadly3 Domain Registration API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "domains": "/api/v1/domains", 
            "dns": "/api/v1/dns",
            "payments": "/api/v1/payments",
            "documentation": "/docs",
            "openapi": "/openapi.json"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test database connectivity
        from ..core.database import get_db_session
        db_session = get_db_session()
        
        # Test basic query using SQLAlchemy text
        from sqlalchemy import text
        result = db_session.execute(text("SELECT 1 as health_check"))
        db_healthy = result.fetchone()[0] == 1
        db_session.close()
        
        # Test external services (basic connectivity)
        from ..core.config import config
        
        services_status = {
            "database": db_healthy,
            "cloudflare_api": bool(config.CLOUDFLARE_API_TOKEN),
            "openprovider_api": bool(config.OPENPROVIDER_USERNAME and config.OPENPROVIDER_PASSWORD),
            "blockbee_api": bool(config.BLOCKBEE_API_KEY),
            "brevo_api": bool(config.BREVO_API_KEY),
            "fastforex_api": bool(config.FASTFOREX_API_KEY)
        }
        
        all_healthy = all(services_status.values())
        
        return {
            "success": True,
            "status": "healthy" if all_healthy else "degraded",
            "services": services_status,
            "timestamp": "2025-07-23T09:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "status": "unhealthy",
                "error": "Health check failed",
                "timestamp": "2025-07-23T09:30:00Z"
            }
        )

@app.get("/api/v1", tags=["Health"])
async def api_info():
    """API version information and available endpoints"""
    return {
        "success": True,
        "api_version": "v1",
        "message": "Nomadly3 API v1 - Operational",
        "available_endpoints": {
            "auth": {
                "POST /auth/register": "Register new user account",
                "POST /auth/login": "User authentication", 
                "GET /auth/me": "Get current user profile",
                "POST /auth/refresh": "Refresh JWT token",
                "POST /auth/logout": "User logout"
            },
            "domains": {
                "GET /domains/": "List user domains with pagination",
                "POST /domains/check-availability": "Check domain availability",
                "POST /domains/register": "Register new domain",
                "GET /domains/{domain_id}": "Get domain details",
                "PUT /domains/{domain_id}": "Update domain settings",
                "DELETE /domains/{domain_id}": "Remove domain from account",
                "POST /domains/{domain_id}/renew": "Renew domain registration"
            },
            "dns": {
                "GET /dns/{domain_id}/records": "List DNS records",
                "POST /dns/{domain_id}/records": "Create DNS record",
                "PUT /dns/{domain_id}/records/{record_id}": "Update DNS record",
                "DELETE /dns/{domain_id}/records/{record_id}": "Delete DNS record",
                "POST /dns/{domain_id}/records/bulk": "Bulk create DNS records",
                "GET /dns/{domain_id}/geo-blocking": "Get geo-blocking status",
                "POST /dns/{domain_id}/geo-blocking": "Configure geo-blocking",
                "GET /dns/templates/geo-blocking": "Get geo-blocking templates",
                "POST /dns/{domain_id}/geo-blocking/template": "Apply geo-blocking template",
                "DELETE /dns/{domain_id}/geo-blocking": "Remove geo-blocking"
            },
            "payments": {
                "POST /payments/initiate": "Initiate cryptocurrency payment",
                "GET /payments/{payment_id}": "Get payment status",
                "POST /payments/{payment_id}/confirm": "Confirm payment manually",
                "GET /payments/": "Get payment history",
                "GET /payments/wallet/balance": "Get wallet balance",
                "POST /payments/wallet/deduct": "Deduct from wallet",
                "GET /payments/supported-currencies": "Get supported cryptocurrencies",
                "POST /payments/webhook/blockbee": "BlockBee webhook handler",
                "POST /payments/{payment_id}/cancel": "Cancel payment",
                "GET /payments/stats/summary": "Get payment statistics"
            }
        },
        "authentication": "Bearer JWT token required for all endpoints except /auth/register and /auth/login",
        "rate_limiting": "120 requests per minute per IP",
        "documentation": "/docs"
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup initialization"""
    logger.info("🚀 Starting Nomadly3 FastAPI Application")
    logger.info("✅ All routers configured:")
    logger.info("   - Authentication: /api/v1/auth")
    logger.info("   - Domain Management: /api/v1/domains")
    logger.info("   - DNS Management: /api/v1/dns")
    logger.info("   - Payment Processing: /api/v1/payments")
    logger.info("✅ Middleware configured: logging, security, rate limiting")
    logger.info("✅ Health checks available: /health")
    logger.info("✅ API documentation: /docs")
    logger.info("🏴‍☠️ Nomadly3 API ready for offshore domain operations!")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown cleanup"""
    logger.info("🛑 Shutting down Nomadly3 FastAPI Application")
    logger.info("✅ Cleanup completed")

if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info",
        access_log=True
    )